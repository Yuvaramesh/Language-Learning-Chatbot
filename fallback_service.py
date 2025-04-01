import json
import random
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# A collection of generic responses for different languages and proficiency levels
GENERIC_RESPONSES = {
    "en": {  # English
        "beginner": [
            "Hello! How are you today?",
            "Nice to meet you! What is your name?",
            "The weather is nice today, isn't it?",
            "I like learning languages too. It's fun!",
            "What do you like to do in your free time?"
        ],
        "intermediate": [
            "I'd love to hear more about your interests. What kinds of activities do you enjoy?",
            "Have you been learning English for a long time? What methods do you find most helpful?",
            "What's your favorite book or movie? Why do you like it?",
            "If you could travel anywhere in the world, where would you go and why?",
            "What kind of music do you enjoy listening to? Do you have a favorite artist?"
        ],
        "advanced": [
            "I find the cultural aspects of language learning fascinating. How has learning English changed your perspective?",
            "What motivated you to learn English? Was it for personal or professional reasons?",
            "Some people argue that language shapes how we think. What's your opinion on this theory?",
            "What challenges have you faced while learning English, and how have you overcome them?",
            "If you could implement one change to improve language education in schools, what would it be?"
        ]
    },
    "es": {  # Spanish
        "beginner": [
            "¡Hola! ¿Cómo estás hoy?",
            "¡Mucho gusto! ¿Cómo te llamas?",
            "Hace buen tiempo hoy, ¿verdad?",
            "A mí también me gusta aprender idiomas. ¡Es divertido!",
            "¿Qué te gusta hacer en tu tiempo libre?"
        ],
        "intermediate": [
            "Me encantaría saber más sobre tus intereses. ¿Qué tipo de actividades disfrutas?",
            "¿Has estado aprendiendo español por mucho tiempo? ¿Qué métodos te parecen más útiles?",
            "¿Cuál es tu libro o película favorita? ¿Por qué te gusta?",
            "Si pudieras viajar a cualquier lugar del mundo, ¿a dónde irías y por qué?",
            "¿Qué tipo de música te gusta escuchar? ¿Tienes un artista favorito?"
        ],
        "advanced": [
            "Encuentro fascinantes los aspectos culturales del aprendizaje de idiomas. ¿Cómo ha cambiado tu perspectiva el aprender español?",
            "¿Qué te motivó a aprender español? ¿Fue por razones personales o profesionales?",
            "Algunas personas argumentan que el idioma moldea nuestra forma de pensar. ¿Cuál es tu opinión sobre esta teoría?",
            "¿Qué desafíos has enfrentado mientras aprendías español, y cómo los has superado?",
            "Si pudieras implementar un cambio para mejorar la educación de idiomas en las escuelas, ¿cuál sería?"
        ]
    },
    "fr": {  # French
        "beginner": [
            "Bonjour ! Comment allez-vous aujourd'hui ?",
            "Enchanté ! Comment vous appelez-vous ?",
            "Il fait beau aujourd'hui, n'est-ce pas ?",
            "J'aime aussi apprendre des langues. C'est amusant !",
            "Qu'aimez-vous faire pendant votre temps libre ?"
        ],
        "intermediate": [
            "J'aimerais en savoir plus sur vos intérêts. Quelles activités aimez-vous ?",
            "Apprenez-vous le français depuis longtemps ? Quelles méthodes trouvez-vous les plus utiles ?",
            "Quel est votre livre ou film préféré ? Pourquoi l'aimez-vous ?",
            "Si vous pouviez voyager n'importe où dans le monde, où iriez-vous et pourquoi ?",
            "Quel genre de musique aimez-vous écouter ? Avez-vous un artiste préféré ?"
        ],
        "advanced": [
            "Je trouve fascinants les aspects culturels de l'apprentissage des langues. Comment l'apprentissage du français a-t-il changé votre perspective ?",
            "Qu'est-ce qui vous a motivé à apprendre le français ? Était-ce pour des raisons personnelles ou professionnelles ?",
            "Certains soutiennent que la langue façonne notre façon de penser. Quelle est votre opinion sur cette théorie ?",
            "Quels défis avez-vous rencontrés en apprenant le français, et comment les avez-vous surmontés ?",
            "Si vous pouviez mettre en œuvre un changement pour améliorer l'enseignement des langues dans les écoles, quel serait-il ?"
        ]
    },
    "de": {  # German
        "beginner": [
            "Hallo! Wie geht es Ihnen heute?",
            "Schön, Sie kennenzulernen! Wie heißen Sie?",
            "Das Wetter ist heute schön, nicht wahr?",
            "Ich lerne auch gerne Sprachen. Es macht Spaß!",
            "Was machen Sie gerne in Ihrer Freizeit?"
        ],
        "intermediate": [
            "Ich würde gerne mehr über Ihre Interessen erfahren. Welche Aktivitäten gefallen Ihnen?",
            "Lernen Sie schon lange Deutsch? Welche Methoden finden Sie am hilfreichsten?",
            "Was ist Ihr Lieblingsbuch oder -film? Warum gefällt es Ihnen?",
            "Wenn Sie überall auf der Welt reisen könnten, wohin würden Sie gehen und warum?",
            "Welche Art von Musik hören Sie gerne? Haben Sie einen Lieblingskünstler?"
        ],
        "advanced": [
            "Ich finde die kulturellen Aspekte des Sprachenlernens faszinierend. Wie hat das Deutschlernen Ihre Perspektive verändert?",
            "Was hat Sie motiviert, Deutsch zu lernen? War es aus persönlichen oder beruflichen Gründen?",
            "Manche Leute behaupten, dass Sprache beeinflusst, wie wir denken. Was halten Sie von dieser Theorie?",
            "Welchen Herausforderungen sind Sie beim Deutschlernen begegnet, und wie haben Sie sie überwunden?",
            "Wenn Sie eine Änderung zur Verbesserung des Sprachunterrichts in Schulen umsetzen könnten, welche wäre das?"
        ]
    },
    "it": {  # Italian
        "beginner": [
            "Ciao! Come stai oggi?",
            "Piacere di conoscerti! Come ti chiami?",
            "Il tempo è bello oggi, vero?",
            "Anche a me piace imparare le lingue. È divertente!",
            "Cosa ti piace fare nel tempo libero?"
        ],
        "intermediate": [
            "Mi piacerebbe sapere di più sui tuoi interessi. Che tipo di attività ti piacciono?",
            "Stai imparando l'italiano da molto tempo? Quali metodi trovi più utili?",
            "Qual è il tuo libro o film preferito? Perché ti piace?",
            "Se potessi viaggiare ovunque nel mondo, dove andresti e perché?",
            "Che tipo di musica ti piace ascoltare? Hai un artista preferito?"
        ],
        "advanced": [
            "Trovo affascinanti gli aspetti culturali dell'apprendimento delle lingue. Come ha cambiato la tua prospettiva imparare l'italiano?",
            "Cosa ti ha motivato a imparare l'italiano? È stato per ragioni personali o professionali?",
            "Alcuni sostengono che la lingua influenzi il nostro modo di pensare. Qual è la tua opinione su questa teoria?",
            "Quali sfide hai affrontato mentre imparavi l'italiano, e come le hai superate?",
            "Se potessi implementare un cambiamento per migliorare l'insegnamento delle lingue nelle scuole, quale sarebbe?"
        ]
    }
}

# Default responses for languages not in our dictionary
DEFAULT_RESPONSES = {
    "beginner": [
        "Hello! How are you today?",
        "Nice to meet you! What is your name?",
        "The weather is nice today, isn't it?",
        "I like learning languages too. It's fun!",
        "What do you like to do in your free time?"
    ],
    "intermediate": [
        "I'd love to hear more about your interests. What kinds of activities do you enjoy?",
        "Have you been learning this language for a long time? What methods do you find most helpful?",
        "What's your favorite book or movie? Why do you like it?",
        "If you could travel anywhere in the world, where would you go and why?",
        "What kind of music do you enjoy listening to? Do you have a favorite artist?"
    ],
    "advanced": [
        "I find the cultural aspects of language learning fascinating. How has learning this language changed your perspective?",
        "What motivated you to learn this language? Was it for personal or professional reasons?",
        "Some people argue that language shapes how we think. What's your opinion on this theory?",
        "What challenges have you faced while learning this language, and how have you overcome them?",
        "If you could implement one change to improve language education in schools, what would it be?"
    ]
}

# Simple corrections for common mistakes in different languages
COMMON_CORRECTIONS = {
    "en": [
        {"original": "I has", "corrected": "I have", "explanation": "For the first person singular ('I'), we use 'have' not 'has'."},
        {"original": "They is", "corrected": "They are", "explanation": "For plural subjects, we use 'are' not 'is'."},
        {"original": "We was", "corrected": "We were", "explanation": "For plural subjects, we use 'were' not 'was'."},
        {"original": "He don't", "corrected": "He doesn't", "explanation": "For third person singular, we use 'doesn't' not 'don't'."},
        {"original": "She have", "corrected": "She has", "explanation": "For third person singular, we use 'has' not 'have'."}
    ],
    "es": [
        {"original": "Yo tiene", "corrected": "Yo tengo", "explanation": "For the first person singular, we use 'tengo' not 'tiene'."},
        {"original": "Tú tienes", "corrected": "Tú tienes", "explanation": "Correct! 'Tú tienes' is the correct form for the second person singular."},
        {"original": "Yo soy feliz", "corrected": "Yo soy feliz", "explanation": "Correct! 'Yo soy feliz' is grammatically correct."},
        {"original": "Ellos es", "corrected": "Ellos son", "explanation": "For plural subjects, we use 'son' not 'es'."},
        {"original": "Nosotros voy", "corrected": "Nosotros vamos", "explanation": "For first person plural, we use 'vamos' not 'voy'."}
    ],
    "fr": [
        {"original": "Je suis heureuse", "corrected": "Je suis heureuse", "explanation": "Correct! 'Je suis heureuse' is grammatically correct for a female speaker."},
        {"original": "Tu as", "corrected": "Tu as", "explanation": "Correct! 'Tu as' is the correct form for the second person singular."},
        {"original": "Il avoir", "corrected": "Il a", "explanation": "We use the conjugated form 'a' not the infinitive 'avoir'."},
        {"original": "Nous sommes", "corrected": "Nous sommes", "explanation": "Correct! 'Nous sommes' is grammatically correct."},
        {"original": "Ils est", "corrected": "Ils sont", "explanation": "For plural subjects, we use 'sont' not 'est'."}
    ],
    "de": [
        {"original": "Ich bin", "corrected": "Ich bin", "explanation": "Correct! 'Ich bin' is grammatically correct."},
        {"original": "Du bist", "corrected": "Du bist", "explanation": "Correct! 'Du bist' is the correct form for the second person singular."},
        {"original": "Er haben", "corrected": "Er hat", "explanation": "For third person singular, we use 'hat' not 'haben'."},
        {"original": "Wir sind", "corrected": "Wir sind", "explanation": "Correct! 'Wir sind' is grammatically correct."},
        {"original": "Sie ist", "corrected": "Sie ist", "explanation": "Correct! 'Sie ist' is grammatically correct for 'she is'."}
    ],
    "it": [
        {"original": "Io è", "corrected": "Io sono", "explanation": "For the first person singular, we use 'sono' not 'è'."},
        {"original": "Tu sei", "corrected": "Tu sei", "explanation": "Correct! 'Tu sei' is the correct form for the second person singular."},
        {"original": "Lui sono", "corrected": "Lui è", "explanation": "For third person singular, we use 'è' not 'sono'."},
        {"original": "Noi siamo", "corrected": "Noi siamo", "explanation": "Correct! 'Noi siamo' is grammatically correct."},
        {"original": "Loro è", "corrected": "Loro sono", "explanation": "For plural subjects, we use 'sono' not 'è'."}
    ]
}

def get_initial_message(native_language, target_language, proficiency_level, conversation_context):
    """Generate a fallback initial message for the conversation."""
    logger.info(f"Using fallback service for initial message: {target_language}, {proficiency_level}")
    
    # Default welcome message based on the target language
    welcome_messages = {
        "en": f"Welcome to your English conversation practice! Let's talk about {conversation_context}. How are you today?",
        "es": f"¡Bienvenido a tu práctica de conversación en español! Hablemos sobre {conversation_context}. ¿Cómo estás hoy?",
        "fr": f"Bienvenue à votre pratique de conversation en français ! Parlons de {conversation_context}. Comment allez-vous aujourd'hui ?",
        "de": f"Willkommen zu Ihrer deutschen Konversationsübung! Lass uns über {conversation_context} sprechen. Wie geht es Ihnen heute?",
        "it": f"Benvenuto alla tua pratica di conversazione in italiano! Parliamo di {conversation_context}. Come stai oggi?"
    }
    
    # Return welcome message in the target language, or default to English
    return welcome_messages.get(target_language.lower(), 
                               f"Welcome to your {target_language} conversation practice! Let's talk about {conversation_context}. How are you today?")

def process_message(user_message, target_language, proficiency_level, conversation_history):
    """Process a user message with fallback responses."""
    logger.info(f"Using fallback service for processing message: {target_language}, {proficiency_level}")
    
    # Get language-specific responses or default to English if language not supported
    responses = GENERIC_RESPONSES.get(target_language.lower(), DEFAULT_RESPONSES)
    # Make sure we have a valid proficiency level, defaulting to "intermediate"
    level = proficiency_level.lower() if proficiency_level else "intermediate"
    level_responses = responses.get(level, responses.get("intermediate", []))
    
    # Make sure we have a valid list of responses before selecting randomly
    if not level_responses:
        level_responses = ["Hello! How are you today?"]
    
    # Select a random response
    response = random.choice(level_responses)
    
    # Look for potential corrections - very basic pattern matching
    corrections = []
    
    # Get language-specific corrections or default to empty list
    language_corrections = COMMON_CORRECTIONS.get(target_language.lower(), [])
    
    # Simple check if any known error patterns exist in the user message
    for correction in language_corrections:
        if correction["original"].lower() in user_message.lower():
            corrections.append(correction)
    
    return {
        "response": response,
        "corrections": corrections
    }

def generate_session_feedback(conversation_history, mistakes, target_language, proficiency_level):
    """Generate fallback comprehensive feedback at the end of a session."""
    logger.info(f"Using fallback service for session feedback: {target_language}, {proficiency_level}")
    
    # Default feedback categories
    strengths = ["Good effort in maintaining conversation", "Willingness to communicate"]
    areas_for_improvement = ["Continue practicing regularly"]
    
    # Add more specific feedback based on the number of mistakes
    if mistakes and len(mistakes) > 0:
        areas_for_improvement.append("Work on grammar and sentence structure")
        
        # Count the number of times each mistake type occurs
        grammar_mistakes = []
        vocabulary_mistakes = []
        
        for mistake in mistakes:
            if "verb conjugation" in mistake.get("explanation", "").lower() or "tense" in mistake.get("explanation", "").lower():
                grammar_mistakes.append("Verb conjugation and tenses")
            elif "article" in mistake.get("explanation", "").lower() or "gender" in mistake.get("explanation", "").lower():
                grammar_mistakes.append("Article usage and gender agreement")
            else:
                vocabulary_mistakes.append("Word choice and vocabulary")
        
        # Remove duplicates
        grammar_mistakes = list(set(grammar_mistakes))
        vocabulary_mistakes = list(set(vocabulary_mistakes))
    else:
        grammar_mistakes = []
        vocabulary_mistakes = []
    
    return {
        "overall_assessment": f"You've shown dedication in practicing {target_language}. Continue engaging in conversations to build fluency.",
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement,
        "common_mistakes": {
            "grammar": grammar_mistakes,
            "vocabulary": vocabulary_mistakes,
            "sentence_structure": ["Practice constructing more complex sentences"]
        },
        "suggested_exercises": [
            f"Daily reading practice in {target_language}",
            "Language exchange with native speakers",
            "Listen to podcasts or watch videos in the target language"
        ],
        "next_level_goals": [
            "Build more complex vocabulary",
            "Master more advanced grammar structures",
            "Improve pronunciation and fluency"
        ]
    }