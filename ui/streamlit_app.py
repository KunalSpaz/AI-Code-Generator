import streamlit as st
import requests
import json
from typing import Dict, Any
from datetime import datetime
import urllib.parse

# Page config with enhanced styling
st.set_page_config(
    page_title="🚀 Code Generator Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .code-container {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .execution-result {
        background-color: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .execution-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .share-badge {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
        background-color: #f1f3f4;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "language" not in st.session_state:
    st.session_state.language = "auto"
if "history" not in st.session_state:
    st.session_state.history = []

# Check for shared code in URL
query_params = st.query_params
if "share" in query_params:
    share_id = query_params["share"][0]
    try:
        response = requests.get(f"http://localhost:8000/api/shared/{share_id}")
        if response.status_code == 200:
            shared_code = response.json()
            st.session_state.shared_code = shared_code
    except:
        pass

# Enhanced Sidebar
with st.sidebar:
    st.markdown('<div class="main-header"><h2>🚀 Code Generator Pro</h2></div>', unsafe_allow_html=True)
    
    # Language selector with icons
    language_options = {
        "auto": "🔍 Auto-detect",
        "python": "🐍 Python", 
        "javascript": "🟨 JavaScript",
        "java": "☕ Java",
        "cpp": "⚡ C++"
    }
    
    selected_lang = st.selectbox(
        "Programming Language",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=list(language_options.keys()).index(st.session_state.language)
    )
    st.session_state.language = selected_lang
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat", use_container_width=True):
            if st.session_state.messages:
                st.session_state.history.append({
                    "conversation_id": st.session_state.conversation_id,
                    "messages": st.session_state.messages.copy(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()
    
    with col2:
        if st.button("📚 Examples", use_container_width=True):
            st.session_state.show_examples = True
    
    st.divider()
    
    # Quick examples
    st.markdown("### 🎯 Quick Examples")
    examples = [
        "Binary search algorithm in Python",
        "REST API with Express.js",
        "Merge sort in Java",
        "Graph traversal in C++",
        "Dynamic programming solution"
    ]
    
    for example in examples:
        if st.button(f"💡 {example}", key=f"example_{example}", use_container_width=True):
            # Trigger code generation by setting the query in session state
            st.session_state.trigger_query = example
            st.rerun()

# Main header
st.markdown('<div class="main-header"><h1>🚀 AI Code Generator Pro</h1><p>Generate and Share Code with AI</p></div>', unsafe_allow_html=True)

# Handle shared code display
if hasattr(st.session_state, 'shared_code'):
    st.success(f"📤 Viewing shared code: **{st.session_state.shared_code['title']}**")
    st.code(st.session_state.shared_code['code'], language=st.session_state.shared_code['language'])
    if st.session_state.shared_code['description']:
        st.info(st.session_state.shared_code['description'])
    
    if st.button("💬 Start New Chat with This Code"):
        st.session_state.messages = [
            {"role": "user", "content": f"Explain this {st.session_state.shared_code['language']} code"},
            {"role": "assistant", "content": f"Here's the shared {st.session_state.shared_code['language']} code:", 
             "code": st.session_state.shared_code['code'], "language": st.session_state.shared_code['language']}
        ]
        del st.session_state.shared_code
        st.rerun()

# Create enhanced tabs
tab1, tab2, tab3 = st.tabs(["💬 Current Chat", "📚 History", "🌐 Shared Codes"])

with tab1:
    # Display chat messages with enhanced styling
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                st.write(message["content"])
                
                if "code" in message and message["code"]:
                    # Enhanced code display with execution
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.code(message["code"], language=message.get("language", "python"))
                    
                    with col2:
                        # Action buttons
                        file_extensions = {"python": ".py", "javascript": ".js", "java": ".java", "cpp": ".cpp"}
                        ext = file_extensions.get(message.get("language", "python"), ".txt")
                        
                        st.download_button(
                            "📥 Download",
                            data=message["code"],
                            file_name=f"code{ext}",
                            mime="text/plain",
                            key=f"download_{i}",
                            use_container_width=True
                        )
                        
                        # Generate Tests button
                        if st.button("🧪 Generate Tests", key=f"tests_{i}", use_container_width=True):
                            st.session_state[f"generate_tests_{i}"] = True
                            st.rerun()
                        
                        # Share button
                        if st.button("🔗 Share", key=f"share_{i}", use_container_width=True):
                            st.session_state[f"share_modal_{i}"] = True
                    
                    # Generate Tests modal
                    if st.session_state.get(f"generate_tests_{i}", False):
                        with st.expander("🧪 Unit Tests", expanded=True):
                            with st.spinner("Generating unit tests..."):
                                try:
                                    response = requests.post(
                                        "http://localhost:8000/api/generate-tests",
                                        json={
                                            "code": message["code"],
                                            "language": message["language"]
                                        }
                                    )
                                    
                                    if response.status_code == 200:
                                        result = response.json()
                                        st.success("✅ Tests generated successfully!")
                                        st.code(result["tests"], language=result["language"])
                                        
                                        # Download tests
                                        test_ext = {"python": "_test.py", "javascript": ".test.js", "java": "Test.java", "cpp": "_test.cpp"}
                                        test_file = test_ext.get(result["language"], "_test.txt")
                                        
                                        st.download_button(
                                            "📥 Download Tests",
                                            data=result["tests"],
                                            file_name=f"test{test_file}",
                                            mime="text/plain",
                                            key=f"download_tests_{i}"
                                        )
                                    else:
                                        st.error("Failed to generate tests")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            
                            if st.button("❌ Close", key=f"close_tests_{i}"):
                                st.session_state[f"generate_tests_{i}"] = False
                                st.rerun()
                    
                    # Share modal
                    if st.session_state.get(f"share_modal_{i}", False):
                        with st.expander("🔗 Share Code", expanded=True):
                            title = st.text_input("Title:", key=f"share_title_{i}", value="My Code Snippet")
                            description = st.text_area("Description (optional):", key=f"share_desc_{i}")
                            
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button("🚀 Share", key=f"share_btn_{i}"):
                                    try:
                                        response = requests.post(
                                            "http://localhost:8000/api/share",
                                            json={
                                                "code": message["code"],
                                                "language": message["language"],
                                                "title": title,
                                                "description": description
                                            }
                                        )
                                        
                                        if response.status_code == 200:
                                            result = response.json()
                                            st.success("✅ Code shared successfully!")
                                            st.markdown(f'<div class="share-badge">Share ID: {result["share_id"]}</div>', unsafe_allow_html=True)
                                            st.code(result["share_url"])
                                            st.balloons()
                                        else:
                                            st.error("Failed to share code")
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                            
                            with col2:
                                if st.button("❌ Cancel", key=f"cancel_share_{i}"):
                                    st.session_state[f"share_modal_{i}"] = False
                                    st.rerun()
                
                # Expandable sections for complexity and docs
                if "complexity" in message and message["complexity"]:
                    with st.expander("📊 Complexity Analysis"):
                        st.write(message["complexity"])
                
                if "docs" in message and message["docs"]:
                    with st.expander("📖 Documentation"):
                        st.markdown(message["docs"])
                        st.download_button(
                            "📥 Download Docs",
                            data=message["docs"],
                            file_name="documentation.md",
                            mime="text/markdown",
                            key=f"docs_{i}"
                        )

    # Enhanced chat input
    if prompt := st.chat_input("🤖 Ask me to generate, explain, refactor, or debug code..."):
        pass  # Will be processed below
    
    # Check if there's a triggered query from quick examples
    if hasattr(st.session_state, 'trigger_query'):
        prompt = st.session_state.trigger_query
        del st.session_state.trigger_query
    
    # Process the prompt
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("🤔 **Thinking and generating code...**")
            
            try:
                request_data = {
                    "message": prompt,
                    "conversation_id": st.session_state.conversation_id,
                    "language": None if st.session_state.language == "auto" else st.session_state.language
                }
                
                response = requests.post(
                    "http://localhost:8000/api/chat",
                    json=request_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.conversation_id = result["conversation_id"]
                    thinking_placeholder.empty()
                    
                    st.success(f"✨ Generated {result['language']} code:")
                    
                    if result["code"]:
                        # Display code with action buttons
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.code(result["code"], language=result["language"])
                        
                        with col2:
                            # Action buttons
                            file_extensions = {"python": ".py", "javascript": ".js", "java": ".java", "cpp": ".cpp"}
                            ext = file_extensions.get(result["language"], ".txt")
                            
                            st.download_button(
                                "📥 Download",
                                data=result["code"],
                                file_name=f"code{ext}",
                                mime="text/plain",
                                key="download_new",
                                use_container_width=True
                            )
                            
                            if st.button("🧪 Generate Tests", key="tests_new", use_container_width=True):
                                st.session_state.generate_tests_new = True
                                st.rerun()
                            
                            if st.button("🔗 Share", key="share_new", use_container_width=True):
                                st.session_state.share_modal_new = True
                                st.rerun()
                    
                    if result["complexity"]:
                        with st.expander("📊 Complexity Analysis"):
                            st.write(result["complexity"])
                    
                    if result["docs"]:
                        with st.expander("📖 Documentation"):
                            st.markdown(result["docs"])
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Generated {result['language']} code:",
                        "code": result["code"],
                        "complexity": result["complexity"],
                        "docs": result["docs"],
                        "language": result["language"]
                    })
                    
                else:
                    thinking_placeholder.empty()
                    st.error(f"❌ API Error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                thinking_placeholder.empty()
                st.error("❌ Cannot connect to backend. Make sure the server is running on http://localhost:8000")
            except Exception as e:
                thinking_placeholder.empty()
                st.error(f"❌ Error: {str(e)}")

with tab2:
    # Enhanced history view
    if st.session_state.history:
        st.markdown("### 📚 Previous Conversations")
        
        for i, conversation in enumerate(reversed(st.session_state.history)):
            with st.expander(f"💬 Conversation {len(st.session_state.history) - i} - {conversation['timestamp']}"):
                for message in conversation["messages"]:
                    with st.chat_message(message["role"]):
                        if message["role"] == "user":
                            st.write(message["content"])
                        else:
                            st.write(message["content"])
                            if "code" in message and message["code"]:
                                st.code(message["code"], language=message.get("language", "python"))
                
                if st.button(f"🔄 Restore Conversation {len(st.session_state.history) - i}", key=f"restore_{i}"):
                    st.session_state.messages = conversation["messages"].copy()
                    st.session_state.conversation_id = conversation["conversation_id"]
                    st.success("✅ Conversation restored!")
                    st.rerun()
    else:
        st.info("📝 No previous conversations yet. Start chatting to build your history!")

with tab3:
    # Shared codes gallery
    st.markdown("### 🌐 Community Shared Codes")
    
    try:
        response = requests.get("http://localhost:8000/api/shared")
        if response.status_code == 200:
            shared_codes = response.json()["shared_codes"]
            
            if shared_codes:
                for code in reversed(shared_codes[-10:]):  # Show last 10
                    with st.expander(f"🔗 {code['title']} ({code['language']}) - {code['created_at']}"):
                        if code['description']:
                            st.write(code['description'])
                        st.code(code['code'], language=code['language'])
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            share_url = f"http://localhost:8501?share={code['share_id']}"
                            st.code(share_url)
                        with col2:
                            if st.button(f"📋 Copy Link", key=f"copy_{code['share_id']}"):
                                st.success("Link copied to clipboard!")
            else:
                st.info("🎯 No shared codes yet. Be the first to share!")
        else:
            st.error("Failed to load shared codes")
    except Exception as e:
        st.error(f"Error loading shared codes: {str(e)}")

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;">
    <h3>🚀 Code Generator Pro</h3>
    <p>💡 Generate optimal algorithms • 🔍 Explain existing code • ⚡ Refactor for performance • 🐛 Debug issues • 🔗 Share with community</p>
</div>
""", unsafe_allow_html=True)