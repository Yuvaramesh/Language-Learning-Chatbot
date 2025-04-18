# Language Learning Chatbot


### ✅  Overview – Language Learning Chatbot

**Language Learning Chatbot** is a python -based language learning app where users interact through a chatbot to improve their language skills. It features:
- Real-time conversation
- Error detection and logging
- Personalized feedback with visual analytics


### ✅ Tech Stack

- **Language:** Python  
- **Web Framework:** Flask  
- **AI Service:** Gemini API (instead of OpenAI)  
- **Database:** SQLite  
- **Error Tracking:** Flashcards


### ✅ System Design

- **User Interface:** Chat interface for user input and AI responses  
- **Flask:** UI rendering, user interaction  
- **Gemini Backend:** Handles conversation logic and error detection  
- **Mistake Logging:** Custom Python logic that logs grammar or spelling issues to SQLite  
- **SQLite Database:** Stores user messages, errors, and corrections  
- **Feedback Module:** Extracts trends from the DB and generates insights  
- **Flasshcards:** Displays error categories, frequency, and progress
