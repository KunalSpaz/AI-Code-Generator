# AI-Code-Generator
**Transform your ideas into production-ready code instantly**

An intelligent code generation platform powered by GPT-4o that creates optimized, well-documented code across multiple programming languages. Built with FastAPI and Streamlit for seamless development workflow integration.

## 🎯 Why Choose AI Code Generator?

- **Instant Code Creation**: Generate complete, working code from natural language descriptions
- **Smart Optimization**: Automatically produces algorithms with optimal time/space complexity
- **Multi-Language Mastery**: Native support for Python, JavaScript, Java, and C++
- **Production Ready**: Includes comprehensive documentation, error handling, and best practices
- **Developer Friendly**: Clean UI with syntax highlighting, download options, and persistent sessions

## Features

- **Multi-language Support**: Python, JavaScript, Java, C++
- **Task Types**: Generate, Explain, Refactor, Debug code
- **Complexity Analysis**: Automatic Big-O time/space complexity analysis
- **Documentation**: Auto-generated Markdown documentation
- **Download Options**: Download generated code and documentation
- **Conversation History**: Persistent chat sessions
- **Optimal Algorithms**: Uses best practices and optimal complexity

## Project Structure

```
Code Generator/
├── backend/
│   ├── main.py              # FastAPI app with LangGraph agent
│   ├── requirements.txt     # Backend dependencies
│   └── .env                 # Environment variables
└── ui/
    ├── streamlit_app.py     # Streamlit chat interface
    └── requirements.txt     # UI dependencies
```

## Setup Instructions

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Edit `backend/.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_openai_key_here
```

### 3. UI Setup

```bash
cd ui
pip install -r requirements.txt
```

## Running the Application

### 1. Start Backend Server

```bash
cd backend
python main.py
```

The FastAPI server will start on http://localhost:8000

### 2. Start UI

In a new terminal:
```bash
cd ui
streamlit run streamlit_app.py
```

The Streamlit app will open in your browser at http://localhost:8501

## Usage

1. **Language Selection**: Choose target language from sidebar (auto-detect available)
2. **Ask Questions**: Type requests like:
   - "Generate a binary search algorithm in Python"
   - "Explain this sorting code"
   - "Refactor this function for better performance"
   - "Debug this recursive function"

3. **View Results**: 
   - Generated code with syntax highlighting
   - Complexity analysis in expandable section
   - Documentation with usage examples
   - Download buttons for code and docs

4. **New Questions**: Use sidebar button to start fresh conversation

## API Endpoints

- `GET /`: Health check
- `POST /api/chat`: Main chat endpoint
  - Request: `{message, conversation_id?, language?}`
  - Response: `{conversation_id, message, code, complexity, docs, language}`

## Dependencies

### Backend
- FastAPI 0.115.0
- LangGraph 0.2.45
- LangChain 0.3.15
- OpenAI integration
- Python-dotenv

### UI  
- Streamlit 1.39.0
- Requests 2.32.3

## Architecture

The application uses LangGraph to orchestrate a multi-step AI workflow:

1. **Router**: Detects language and task type
2. **Code Generator**: Creates optimal code using GPT-4o
3. **Complexity Analyzer**: Analyzes Big-O complexity
4. **Documentation Generator**: Creates Markdown docs
5. **Persistence**: Maintains conversation state

All components are production-ready with proper error handling, type hints, and async support.
