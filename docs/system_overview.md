# System Overview

## Project Description
This is a template repository for a Telegram AI bot that integrates ChatGPT (OpenAI) with Google Maps to provide personalized beer pub recommendations. The bot engages users in conversational interactions to gather their location and preferences, then suggests nearby craft beer establishments.

## Core Features

### 1. Telegram Bot Integration
- Built using `python-telegram-bot` library
- Supports basic commands:
  - `/start`: Greets the user and provides initial instructions
  - `/help`: Displays available bot functionalities
- Handles user messages through an AI-driven dialog system

### 2. AI-Powered Conversation
- Utilizes OpenAI's GPT-3.5-turbo model via LangChain
- Implements conversational flow using LangGraph for state management
- Collects user information step-by-step:
  - Country of residence
  - City of residence
  - Preference for craft beer (yes/no)
- Maintains conversation history and context across interactions

### 3. Memory and Persistence
- Uses LangGraph's InMemoryStore for persisting user preferences
- Namespaces data by user ID for personalized experiences
- Supports conversation memory across multiple interactions

### 4. Location-Based Recommendations
- Integrates with Google Places API for location search
- Finds nearby beer pubs based on user's city and country
- Generates shareable Google Maps links for recommended locations

### 5. Response Formatting
- Uses Jinja2 templates for HTML-formatted responses
- Provides user-friendly messages with clickable links
- Handles both intermediate dialog responses and final recommendations

### 6. Development and Testing Tools
- Console-based testing script (`scripts/chat.py`) for simulating conversations
- Docker containerization for easy deployment
- Makefile with build and run commands
- Environment-based configuration for API keys

## Architecture

### Components
- `src/app.py`: Main Telegram bot application
- `src/ai_agent.py`: AI conversation logic using LangGraph
- `src/google_api.py`: Google Places API integration
- `scripts/chat.py`: Console testing interface

### Dependencies
- `python-telegram-bot`: Telegram API integration
- `openai`: OpenAI API client
- `langchain`: LLM framework
- `langchain-openai`: OpenAI integration for LangChain
- `langgraph`: Graph-based AI workflows
- `jinja2`: Template rendering
- `beautifulsoup4`: HTML parsing (for testing)

### Environment Variables
- `TG_BOT_TOKEN`: Telegram bot token
- `OPENAI_API_KEY`: OpenAI API key
- `GOOGLE_API_KEY`: Google Places API key

### Deployment
- Docker-based deployment with `Dockerfile` and `docker-compose.yml`
- Supports both development and production environments

## Usage Flow
1. User starts conversation with `/start`
2. Bot asks for country, city, and craft beer preference through natural conversation
3. Once information is collected, bot queries Google Places API for nearby beer pubs
4. Bot responds with a formatted recommendation including a Google Maps link
5. User preferences are stored for future interactions

## Future Enhancements
- Support for additional location-based services
- Enhanced memory with semantic search capabilities
- Multi-language support
- Integration with more AI models
- Advanced user preference learning