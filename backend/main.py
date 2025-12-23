import os
import uuid
import subprocess
import tempfile
import json
import time
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

# Validate API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your_openai_key_here":
    raise ValueError("Please set a valid OPENAI_API_KEY in the .env file")

print(f"Using API key: {api_key[:10]}...{api_key[-4:]}")

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    language: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    code: str
    complexity: str
    docs: str
    language: str

class ShareRequest(BaseModel):
    code: str
    language: str
    title: str
    description: Optional[str] = ""

class TestRequest(BaseModel):
    code: str
    language: str

class TestResponse(BaseModel):
    tests: str
    language: str

class ShareResponse(BaseModel):
    share_id: str
    share_url: str

class SharedCode(BaseModel):
    share_id: str
    code: str
    language: str
    title: str
    description: str
    created_at: str

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)

# In-memory storage for shared code (use database in production)
shared_codes: Dict[str, Dict] = {}

# Prompts
CODE_GEN_PROMPT = """You are an expert {language} programmer. 

Task: {query}

Requirements:
- Write clean, readable {language} code
- Use proper naming conventions for {language}
- Add clear comments explaining the logic
- Include proper error handling where appropriate
- Use the most efficient algorithm with optimal time/space complexity
- Follow {language} best practices and coding standards

Return ONLY the code without markdown formatting or explanations."""

COMPLEXITY_PROMPT = "Analyze this {language} code and provide:\n\n{code}\n\n1. Time Complexity: O(?)\n2. Space Complexity: O(?)\n3. Brief explanation (2-3 sentences) of why this complexity is achieved.\n\nProvide a clear, concise analysis."

DOCS_PROMPT = "Create clear documentation for this {language} code:\n\n{code}\n\nInclude:\n1. Overview of what the code does\n2. Function/method descriptions\n3. Usage example\n4. Complexity: {complexity}\n\nKeep it concise and user-friendly."

TEST_PROMPT = """Generate comprehensive unit tests for this {language} code:

{code}

Requirements:
- Use appropriate testing framework ({framework})
- Cover edge cases and normal cases
- Include setup and teardown if needed
- Add clear test names and assertions
- Follow {language} testing best practices

Return ONLY the test code without markdown formatting or explanations."""

# Processing functions
async def detect_language_and_task(message: str, provided_language: str) -> tuple[str, str]:
    message_lower = message.lower()
    
    # Use provided language or detect
    if provided_language and provided_language != "auto":
        language = provided_language
    else:
        language_map = {
            "python": "python", "py": "python",
            "javascript": "javascript", "js": "javascript", "node": "javascript",
            "java": "java",
            "c++": "cpp", "cpp": "cpp", "c": "cpp"
        }
        
        language = "python"  # default
        for key, lang in language_map.items():
            if key in message_lower:
                language = lang
                break
    
    # Detect task type
    task_type = "generate"
    if any(word in message_lower for word in ["explain", "understand", "what does"]):
        task_type = "explain"
    elif any(word in message_lower for word in ["refactor", "improve", "optimize"]):
        task_type = "refactor"
    elif any(word in message_lower for word in ["debug", "fix", "error", "bug"]):
        task_type = "debug"
    
    return language, task_type

async def generate_code(query: str, language: str) -> str:
    prompt = CODE_GEN_PROMPT.format(language=language, query=query)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content

async def analyze_complexity(code: str, language: str) -> str:
    prompt = COMPLEXITY_PROMPT.format(language=language, code=code)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content

async def generate_docs(code: str, complexity: str, language: str) -> str:
    prompt = DOCS_PROMPT.format(code=code, complexity=complexity, language=language)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content

async def generate_tests(code: str, language: str) -> str:
    # Determine testing framework based on language
    frameworks = {
        "python": "pytest or unittest",
        "javascript": "Jest or Mocha",
        "java": "JUnit",
        "cpp": "Google Test or Catch2"
    }
    framework = frameworks.get(language, "appropriate testing framework")
    
    prompt = TEST_PROMPT.format(language=language, code=code, framework=framework)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Process the request step by step
        language, task_type = await detect_language_and_task(request.message, request.language)
        code = await generate_code(request.message, language)
        complexity = await analyze_complexity(code, language)
        docs = await generate_docs(code, complexity, language)
        
        return ChatResponse(
            conversation_id=conversation_id,
            message=request.message,
            code=code,
            complexity=complexity,
            docs=docs,
            language=language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/share", response_model=ShareResponse)
async def share_code(request: ShareRequest) -> ShareResponse:
    try:
        share_id = str(uuid.uuid4())[:8]
        
        shared_codes[share_id] = {
            "share_id": share_id,
            "code": request.code,
            "language": request.language,
            "title": request.title,
            "description": request.description,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return ShareResponse(
            share_id=share_id,
            share_url=f"http://localhost:8501?share={share_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-tests", response_model=TestResponse)
async def generate_tests_endpoint(request: TestRequest) -> TestResponse:
    try:
        tests = await generate_tests(request.code, request.language)
        return TestResponse(tests=tests, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/shared/{share_id}", response_model=SharedCode)
async def get_shared_code(share_id: str) -> SharedCode:
    if share_id not in shared_codes:
        raise HTTPException(status_code=404, detail="Shared code not found")
    
    return SharedCode(**shared_codes[share_id])

@app.get("/api/shared")
async def list_shared_codes():
    return {"shared_codes": list(shared_codes.values())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)