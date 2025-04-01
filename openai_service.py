import os
import json
import logging
from openai import OpenAI
from rate_limiter import openai_limiter
import fallback_service

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
openai = OpenAI(api_key=OPENAI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Flag to control whether to use OpenAI API or fallback
# Setting to False to use the fallback service instead of OpenAI API
USE_OPENAI_API = False

def get_initial_message(native_language, target_language, proficiency_level, conversation_context):
    """Generate an initial message for the conversation based on user settings."""
    
    # If we're not using the OpenAI API, use the fallback service directly
    if not USE_OPENAI_API:
        return fallback_service.get_initial_message(native_language, target_language, proficiency_level, conversation_context)
    
    system_message = f"""
    I am a language learning assistant for a conversation in {target_language}.
    The user's native language is {native_language} and their proficiency level is {proficiency_level}.
    The conversation context is: {conversation_context}.
    
    I will:
    1. Maintain a natural conversation in {target_language}
    2. Keep responses appropriate for their {proficiency_level} level
    3. Gently correct mistakes without interrupting the flow
    4. Use vocabulary and grammar structures appropriate for their level
    5. Stay in context of {conversation_context}
    """
    
    # Create a welcoming initial message in the target language
    try:
        # Apply rate limiting before making the API call
        openai_limiter.wait_if_needed()
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Start a conversation in {target_language} for a {proficiency_level} level learner in the context of {conversation_context}. Make it welcoming and engaging, encourage them to respond."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating initial message: {e}")
        # Use fallback service if API call fails
        return fallback_service.get_initial_message(native_language, target_language, proficiency_level, conversation_context)

def process_message(user_message, target_language, proficiency_level, conversation_history):
    """Process a user message, detect errors, and generate a response with corrections."""
    
    # If we're not using the OpenAI API, use the fallback service directly
    if not USE_OPENAI_API:
        return fallback_service.process_message(user_message, target_language, proficiency_level, conversation_history)
    
    system_prompt = f"""
    You are a language learning assistant for {target_language} at {proficiency_level} level.
    Your task is to:
    1. Maintain a natural conversation with the learner
    2. Identify any language mistakes in their message
    3. Generate corrections with explanations
    4. Respond naturally to continue the conversation
    
    Format your response as JSON with the following structure:
    {{
        "response": "Your natural conversational response in {target_language}",
        "corrections": [
            {{
                "original": "incorrect phrase or word",
                "corrected": "correct phrase or word",
                "explanation": "brief explanation of the correction in the learner's native language"
            }}
        ]
    }}
    
    If there are no corrections needed, return an empty array for "corrections".
    """
    
    try:
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for message in conversation_history:
            messages.append({"role": message["role"], "content": message["content"]})
        
        # Add instruction to analyze the latest message
        messages.append({
            "role": "user", 
            "content": f"Please analyze my message for errors and respond accordingly: {user_message}"
        })
        
        # Apply rate limiting before making the API call
        openai_limiter.wait_if_needed()
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        response_data = json.loads(response.choices[0].message.content)
        
        # Validate response format
        if "response" not in response_data:
            response_data["response"] = "I'm sorry, I couldn't generate a proper response. Let's continue our conversation."
        
        if "corrections" not in response_data:
            response_data["corrections"] = []
            
        return response_data
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        # Use fallback service if API call fails
        return fallback_service.process_message(user_message, target_language, proficiency_level, conversation_history)

def generate_session_feedback(conversation_history, mistakes, target_language, proficiency_level):
    """Generate comprehensive feedback at the end of a session."""
    
    # If we're not using the OpenAI API, use the fallback service directly
    if not USE_OPENAI_API:
        return fallback_service.generate_session_feedback(conversation_history, mistakes, target_language, proficiency_level)
    
    system_prompt = f"""
    You are a language learning coach for {target_language} at {proficiency_level} level.
    Review the conversation history and mistakes to provide comprehensive feedback.
    
    Generate feedback in JSON format with the following structure:
    {{
        "overall_assessment": "An overall assessment of the learner's performance",
        "strengths": ["Strength 1", "Strength 2", ...],
        "areas_for_improvement": ["Area 1", "Area 2", ...],
        "common_mistakes": {{
            "grammar": ["Grammar mistake pattern 1", ...],
            "vocabulary": ["Vocabulary issue 1", ...],
            "sentence_structure": ["Structure issue 1", ...]
        }},
        "suggested_exercises": ["Exercise 1", "Exercise 2", ...],
        "next_level_goals": ["Goal 1", "Goal 2", ...]
    }}
    """
    
    try:
        # Create message structure for the API
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history summary
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        messages.append({
            "role": "user", 
            "content": f"Here is the conversation history:\n{conversation_text}\n\nAnd here are the mistakes that were corrected:\n{json.dumps(mistakes, indent=2)}\n\nPlease provide comprehensive feedback."
        })
        
        # Apply rate limiting before making the API call
        openai_limiter.wait_if_needed()
        
        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        feedback = json.loads(response.choices[0].message.content)
        
        # Ensure all expected keys exist
        expected_keys = ["overall_assessment", "strengths", "areas_for_improvement", 
                        "common_mistakes", "suggested_exercises", "next_level_goals"]
        
        for key in expected_keys:
            if key not in feedback:
                feedback[key] = [] if key != "overall_assessment" and key != "common_mistakes" else ""
        
        if "common_mistakes" in feedback and not isinstance(feedback["common_mistakes"], dict):
            feedback["common_mistakes"] = {
                "grammar": [],
                "vocabulary": [],
                "sentence_structure": []
            }
            
        return feedback
    except Exception as e:
        logging.error(f"Error generating session feedback: {e}")
        # Use fallback service if API call fails
        return fallback_service.generate_session_feedback(conversation_history, mistakes, target_language, proficiency_level)
