import os
import json
import logging
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini API with your API key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Default model for Gemini - using the latest as of April 2025
MODEL_NAME = "gemini-1.5-pro"

def get_initial_message(native_language, target_language, proficiency_level, conversation_context):
    """Generate an initial message for the conversation based on user settings."""
    logger.info(f"Generating initial message using Gemini: {target_language}, {proficiency_level}")
    
    system_prompt = f"""
    I am a language learning assistant for a conversation in {target_language}.
    The user's native language is {native_language} and their proficiency level is {proficiency_level}.
    The conversation context is: {conversation_context}.
    
    I will:
    1. Maintain a natural conversation in {target_language}
    2. Keep responses appropriate for their {proficiency_level} level
    3. Gently correct mistakes without interrupting the flow
    4. Use vocabulary and grammar structures appropriate for their level
    5. Stay in context of {conversation_context}
    
    Start a conversation in {target_language} for a {proficiency_level} level learner in the context of {conversation_context}. 
    Make it welcoming and engaging, encourage them to respond.
    """
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(system_prompt)
        
        return response.text
    except Exception as e:
        logger.error(f"Error generating initial message with Gemini: {e}")
        # Use fallback if Gemini fails
        return f"Welcome to your {target_language} conversation practice! Let's talk about {conversation_context}. How are you today?"

def process_message(user_message, target_language, proficiency_level, conversation_history):
    """Process a user message, detect errors, and generate a response with corrections."""
    logger.info(f"Processing message using Gemini: {target_language}, {proficiency_level}")
    
    # Build conversation history in the format Gemini expects
    chat_history = []
    for message in conversation_history:
        role = "user" if message["role"] == "user" else "model"
        chat_history.append({"role": role, "parts": [message["content"]]})
    
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
    
    Analyze this message for errors and respond accordingly: {user_message}
    """
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # If we have conversation history, create a chat
        if chat_history:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(system_prompt)
        else:
            response = model.generate_content(system_prompt)
        
        # Try to parse the response as JSON
        try:
            # Extract JSON from the response text if needed
            response_text = response.text
            
            # Sometimes the model outputs markdown code blocks, so try to extract JSON
            if "```json" in response_text and "```" in response_text:
                json_part = response_text.split("```json")[1].split("```")[0].strip()
                response_data = json.loads(json_part)
            elif "```" in response_text:
                json_part = response_text.split("```")[1].split("```")[0].strip()
                response_data = json.loads(json_part)
            else:
                response_data = json.loads(response_text)
                
            # Validate response format
            if "response" not in response_data:
                response_data["response"] = "I'm sorry, I couldn't generate a proper response. Let's continue our conversation."
            
            if "corrections" not in response_data:
                response_data["corrections"] = []
                
            return response_data
        except json.JSONDecodeError:
            # If JSON parsing fails, create a properly formatted response
            logger.warning(f"Failed to parse Gemini response as JSON. Raw response: {response.text}")
            return {
                "response": response.text,
                "corrections": []
            }
    except Exception as e:
        logger.error(f"Error processing message with Gemini: {e}")
        return {
            "response": "I'm sorry, I encountered an error processing your message. Let's continue our conversation.",
            "corrections": []
        }

def generate_session_feedback(conversation_history, mistakes, target_language, proficiency_level):
    """Generate comprehensive feedback at the end of a session."""
    logger.info(f"Generating session feedback using Gemini: {target_language}, {proficiency_level}")
    
    # Format conversation history and mistakes
    conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    mistakes_text = json.dumps(mistakes, indent=2)
    
    system_prompt = f"""
    You are a language learning coach for {target_language} at {proficiency_level} level.
    Review the conversation history and mistakes to provide comprehensive feedback.
    
    Here is the conversation history:
    {conversation_text}
    
    And here are the mistakes that were corrected:
    {mistakes_text}
    
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
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(system_prompt)
        
        # Try to parse the response as JSON
        try:
            # Extract JSON from the response text if needed
            response_text = response.text
            
            # Sometimes the model outputs markdown code blocks, so try to extract JSON
            if "```json" in response_text and "```" in response_text:
                json_part = response_text.split("```json")[1].split("```")[0].strip()
                feedback = json.loads(json_part)
            elif "```" in response_text:
                json_part = response_text.split("```")[1].split("```")[0].strip()
                feedback = json.loads(json_part)
            else:
                feedback = json.loads(response_text)
            
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
        except json.JSONDecodeError:
            # If JSON parsing fails, create a properly formatted response
            logger.warning(f"Failed to parse Gemini response as JSON for session feedback. Raw response: {response.text}")
            return {
                "overall_assessment": "You've made good progress in your language learning journey.",
                "strengths": ["Willingness to communicate"],
                "areas_for_improvement": ["Continue practicing regularly"],
                "common_mistakes": {
                    "grammar": [],
                    "vocabulary": [],
                    "sentence_structure": []
                },
                "suggested_exercises": ["Regular practice sessions"],
                "next_level_goals": ["Improve your vocabulary"]
            }
    except Exception as e:
        logger.error(f"Error generating session feedback with Gemini: {e}")
        return {
            "overall_assessment": "Unable to generate a complete assessment at this time.",
            "strengths": [],
            "areas_for_improvement": [],
            "common_mistakes": {
                "grammar": [],
                "vocabulary": [],
                "sentence_structure": []
            },
            "suggested_exercises": [],
            "next_level_goals": []
        }