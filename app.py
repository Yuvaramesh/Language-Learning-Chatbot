import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import gemini_service
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "language_learning_chatbot_secret")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///language_learning.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with SQLAlchemy
db.init_app(app)

with app.app_context():
    # Import models
    import models
    db.create_all()

# Available languages and proficiency levels
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean'
}

PROFICIENCY_LEVELS = {
    'beginner': 'Beginner (A1-A2)',
    'intermediate': 'Intermediate (B1-B2)',
    'advanced': 'Advanced (C1-C2)'
}

CONVERSATION_CONTEXTS = {
    'casual': 'Casual Conversation',
    'business': 'Business Meeting',
    'travel': 'Travel Situation',
    'restaurant': 'At a Restaurant',
    'shopping': 'Shopping Experience',
    'academic': 'Academic Discussion'
}

# Routes
@app.route('/')
def index():
    return render_template('index.html', 
                          languages=LANGUAGES, 
                          proficiency_levels=PROFICIENCY_LEVELS,
                          conversation_contexts=CONVERSATION_CONTEXTS)

@app.route('/start_chat', methods=['POST'])
def start_chat():
    # Get language settings from form
    native_language = request.form.get('native_language')
    target_language = request.form.get('target_language')
    proficiency_level = request.form.get('proficiency_level')
    conversation_context = request.form.get('conversation_context')
    
    if not all([native_language, target_language, proficiency_level, conversation_context]):
        return redirect(url_for('index'))
    
    # Store session data
    session['native_language'] = native_language
    session['target_language'] = target_language
    session['proficiency_level'] = proficiency_level
    session['conversation_context'] = conversation_context
    session['conversation_history'] = []
    session['mistakes'] = []
    session['session_start'] = datetime.now().isoformat()
    
    # Create a new conversation in the database
    with app.app_context():
        try:
            conversation = models.Conversation(
                native_language=native_language,
                target_language=target_language,
                proficiency_level=proficiency_level,
                conversation_context=conversation_context,
                start_time=datetime.now()
            )
            db.session.add(conversation)
            db.session.commit()
            session['conversation_id'] = conversation.id
            
            # Initialize with a system message
            initial_message = gemini_service.get_initial_message(
                native_language, 
                target_language, 
                proficiency_level, 
                conversation_context
            )
            
            # Add system message to history
            session['conversation_history'] = [
                {"role": "system", "content": initial_message},
                {"role": "assistant", "content": initial_message}
            ]
            
            return redirect(url_for('chat'))
        except Exception as e:
            logging.error(f"Error creating conversation: {e}")
            return render_template('index.html', 
                          languages=LANGUAGES, 
                          proficiency_levels=PROFICIENCY_LEVELS,
                          conversation_contexts=CONVERSATION_CONTEXTS,
                          error="Failed to start conversation. Please try again.")

@app.route('/chat')
def chat():
    if 'conversation_id' not in session:
        return redirect(url_for('index'))
        
    native_language = session.get('native_language')
    target_language = session.get('target_language')
    proficiency_level = session.get('proficiency_level')
    conversation_context = session.get('conversation_context')
    
    return render_template('chat.html',
                          native_language=LANGUAGES.get(native_language),
                          target_language=LANGUAGES.get(target_language),
                          proficiency_level=PROFICIENCY_LEVELS.get(proficiency_level),
                          conversation_context=CONVERSATION_CONTEXTS.get(conversation_context),
                          conversation_history=session.get('conversation_history', []))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'conversation_id' not in session:
        return jsonify({"error": "No active conversation"}), 400
        
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message.strip():
        return jsonify({"error": "Message cannot be empty"}), 400
    
    # Add user message to history
    conversation_history = session.get('conversation_history', [])
    conversation_history.append({"role": "user", "content": user_message})
    
    try:
        # Get response from Gemini with corrections
        response_data = gemini_service.process_message(
            user_message,
            session.get('target_language'),
            session.get('proficiency_level'),
            conversation_history
        )
        
        # Add assistant message to history
        conversation_history.append({"role": "assistant", "content": response_data["response"]})
        session['conversation_history'] = conversation_history
        
        # Save message to database
        conversation_id = session.get('conversation_id')
        with app.app_context():
            message = models.Message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                timestamp=datetime.now()
            )
            db.session.add(message)
            
            # Save response
            message = models.Message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_data["response"],
                timestamp=datetime.now()
            )
            db.session.add(message)
            
            # If there are corrections, save them
            if response_data.get("corrections"):
                for correction in response_data["corrections"]:
                    mistake = models.Mistake(
                        conversation_id=conversation_id,
                        original_text=correction["original"],
                        corrected_text=correction["corrected"],
                        explanation=correction["explanation"],
                        timestamp=datetime.now()
                    )
                    db.session.add(mistake)
                    
                    # Also store in session for review
                    session_mistakes = session.get('mistakes', [])
                    session_mistakes.append(correction)
                    session['mistakes'] = session_mistakes
                    
            db.session.commit()
        
        return jsonify(response_data)
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/end_session', methods=['POST'])
def end_session():
    if 'conversation_id' not in session:
        return redirect(url_for('index'))
    
    conversation_id = session.get('conversation_id')
    
    # End the conversation in the database
    with app.app_context():
        conversation = models.Conversation.query.get(conversation_id)
        if conversation:
            conversation.end_time = datetime.now()
            db.session.commit()
    
    # Generate feedback report
    try:
        feedback = gemini_service.generate_session_feedback(
            session.get('conversation_history', []),
            session.get('mistakes', []),
            session.get('target_language'),
            session.get('proficiency_level')
        )
        
        session['feedback'] = feedback
        return redirect(url_for('review'))
    except Exception as e:
        logging.error(f"Error generating feedback: {e}")
        return redirect(url_for('review'))

@app.route('/review')
def review():
    if 'conversation_id' not in session:
        return redirect(url_for('index'))
    
    return render_template('review.html',
                          native_language=LANGUAGES.get(session.get('native_language')),
                          target_language=LANGUAGES.get(session.get('target_language')),
                          proficiency_level=PROFICIENCY_LEVELS.get(session.get('proficiency_level')),
                          conversation_context=CONVERSATION_CONTEXTS.get(session.get('conversation_context')),
                          mistakes=session.get('mistakes', []),
                          feedback=session.get('feedback', {}))

@app.route('/new_session', methods=['POST'])
def new_session():
    session.clear()
    return redirect(url_for('index'))

@app.route('/architecture')
def architecture():
    """Display the system architecture diagram and explanation."""
    return render_template('architecture.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
