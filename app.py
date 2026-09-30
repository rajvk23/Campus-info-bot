import streamlit as st
import os
import time
from src.rag_engine import IITKChatbotRAG
from src.scraper import build_knowledge_base

# ---------------------------------------------------------
# Page Configuration & Modern Custom CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="PULPNET | IIT Kanpur Transformer Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Dark glassmorphism container theme */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Main Title Styling */
    .title-banner {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    
    .subtitle-text {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    /* Badge styles */
    .badge-transformer {
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.4);
        color: #c084fc;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    .badge-category {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.4);
        color: #60a5fa;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Card styling */
    .card-glass {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .card-glass:hover {
        border-color: rgba(139, 92, 246, 0.3);
    }

    /* Source Citation Card */
    .source-card {
        background: rgba(15, 23, 42, 0.8);
        border-left: 4px solid #8b5cf6;
        padding: 10px 14px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
    }

    /* Quick Prompt Buttons */
    div.stButton > button {
        background: rgba(30, 41, 59, 0.8);
        color: #e2e8f0;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        width: 100%;
        text-align: left;
    }

    div.stButton > button:hover {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        color: #ffffff;
        border-color: transparent;
        transform: translateY(-2px);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Load RAG Model Engine (Cached)
# ---------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_rag_engine():
    kb_file = "data/iitk_campus_kb.json"
    if not os.path.exists(kb_file):
        build_knowledge_base(kb_file)
    return IITKChatbotRAG(kb_file)

with st.spinner("🤖 Initializing PULPNET Transformer Engine..."):
    rag_engine = load_rag_engine()

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am **PULPNET**, your AI campus assistant for **IIT Kanpur** ⚡\n\nAsk me anything about academics, hostel life, Vox Populi student journal, placement statistics, PK Kelkar library, or student Gymkhana festivals!",
            "confidence": 100.0,
            "sources": []
        }
    ]

# ---------------------------------------------------------
# Sidebar UI Components
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://www.iitk.ac.in/assets/images/logo.png", width=70)
    st.markdown("### 🎓 PULPNET Dashboard")
    st.markdown(
        """<div class="badge-transformer">✨ Transformer Model Active</div>""",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    # Category Filter
    st.markdown("#### 🔍 Filter Knowledge Category")
    category_filter = st.selectbox(
        "Select Category",
        ["All", "Academics", "Facilities & Hostels", "Student Life & Media", "Placements & Internships", "Research & Innovation", "General Information"]
    )
    
    st.markdown("---")
    st.markdown("#### 📊 Knowledge Base Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Docs", len(rag_engine.documents))
    with col2:
        st.metric("Categories", 6)
        
    st.markdown("---")
    st.markdown("#### ⚙️ Control Panel")
    if st.button("🔄 Clear Chat History"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

    if st.button("📚 Re-build Knowledge Base"):
        with st.spinner("Scraping and building updated KB..."):
            build_knowledge_base()
            st.cache_resource.clear()
            st.success("Knowledge Base successfully updated!")
            time.sleep(1)
            st.rerun()

    with st.expander("ℹ️ About PULPNET"):
        st.write("""
        **PULPNET** is an open-source Transformer-based Conversational QA system for IIT Kanpur.
        
        - **Embedding Model**: Hugging Face Sentence Transformers / Neural TF-IDF Matrix
        - **Data Sources**: Vox Populi, IITK DOAA, SPO/ICS, Gymkhana, PK Kelkar Library, SIIC.
        - **Architecture**: RAG (Retrieval-Augmented Generation) pipeline.
        """)

# ---------------------------------------------------------
# Main Chat UI & Header
# ---------------------------------------------------------
st.markdown('<div class="title-banner">PULPNET : IIT Kanpur AI Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Intelligent Transformer-Powered Campus Assistant | Real-Time Knowledge Retrieval</div>', unsafe_allow_html=True)

# Quick Suggestion Chips
st.markdown("##### 💡 Suggested Queries")
chip_cols = st.columns(3)
quick_query = None

with chip_cols[0]:
    if st.button("🏢 Halls 1-14 & Hostel Life"):
        quick_query = "Tell me about Halls of Residence and hostel facilities at IIT Kanpur"
    if st.button("📰 Vox Populi Student Journal"):
        quick_query = "What is Vox Populi and what articles does it publish?"

with chip_cols[1]:
    if st.button("💼 Placements & Average Package"):
        quick_query = "What are the placement statistics and top recruiters at IIT Kanpur?"
    if st.button("📚 PK Kelkar Library Facilities"):
        quick_query = "What facilities are available at PK Kelkar Library?"

with chip_cols[2]:
    if st.button("🎓 Academic Grading & DOAA"):
        quick_query = "Explain the CPI grading system and academic programs at IITK"
    if st.button("🚀 SIIC Startup Incubator"):
        quick_query = "What is SIIC and how does innovation work at IIT Kanpur?"

st.markdown("---")

# Display Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display confidence badge & sources for assistant responses
        if msg["role"] == "assistant" and msg.get("confidence", 0) > 0:
            if msg.get("confidence") < 100:
                st.markdown(
                    f"""<div style="margin-top: 8px;">
                        <span class="badge-category">Match Confidence: {msg['confidence']}%</span>
                    </div>""",
                    unsafe_allow_html=True
                )
            
            if msg.get("sources"):
                with st.expander("📌 View Source Citations & References"):
                    for src in msg["sources"]:
                        st.markdown(
                            f"""<div class="source-card">
                                <strong>[{src['category']}] <a href="{src['url']}" target="_blank" style="color: #a78bfa; text-decoration: underline;">{src['title']}</a></strong><br>
                                <span style="color: #cbd5e1; font-size: 0.85rem;">{src['snippet']}</span>
                            </div>""",
                            unsafe_allow_html=True
                        )

# Handle Input
prompt = st.chat_input("Ask PULPNET a question about IIT Kanpur...")

if quick_query:
    prompt = quick_query

if prompt:
    # Add User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching Knowledge Base with Transformer Embeddings..."):
            response_data = rag_engine.answer_query(prompt, category_filter=category_filter)
            
            # Simulated typing effect
            answer_text = response_data["answer"]
            st.markdown(answer_text)
            
            confidence = response_data["confidence"]
            sources = response_data["sources"]
            
            if confidence > 0 and confidence < 100:
                st.markdown(
                    f"""<div style="margin-top: 8px;">
                        <span class="badge-category">Match Confidence: {confidence}%</span>
                    </div>""",
                    unsafe_allow_html=True
                )
            
            if sources:
                with st.expander("📌 View Source Citations & References"):
                    for src in sources:
                        st.markdown(
                            f"""<div class="source-card">
                                <strong>[{src['category']}] <a href="{src['url']}" target="_blank" style="color: #a78bfa; text-decoration: underline;">{src['title']}</a></strong><br>
                                <span style="color: #cbd5e1; font-size: 0.85rem;">{src['snippet']}</span>
                            </div>""",
                            unsafe_allow_html=True
                        )
            
            # Append assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer_text,
                "confidence": confidence,
                "sources": sources
            })
