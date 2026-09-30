# PULPNET: Transformer-Based Campus Info Chatbot for IIT Kanpur 🎓

![Model](https://img.shields.io/badge/Model-BERT%20%7C%20SentenceTransformers-8b5cf6?style=for-the-badge)
![Vector Search](https://img.shields.io/badge/Vector%20Search-FAISS-00d2ff?style=for-the-badge)
![Frontend](https://img.shields.io/badge/Frontend-Streamlit-ff4b4b?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**PULPNET** is an intelligent, transformer-driven conversational assistant designed to answer user queries regarding **IIT Kanpur (IITK)** campus life, academic programs, student media (Vox Populi), hostels/halls of residence, career placement statistics (SPO/ICS), library infrastructure, and research incubation (SIIC).

---

## 🚀 Key Features

- **Transformer Semantic Search**: Dense vector embeddings powered by Hugging Face `sentence-transformers` (`all-MiniLM-L6-v2` BERT bi-encoder) for context retrieval.
- **FAISS Vector Index**: High-speed nearest-neighbor search via `faiss.IndexFlatIP` (cosine similarity on L2-normalized 384-dimensional embeddings).
- **RAG Architecture**: Retrieval-Augmented Generation pipeline linking user queries directly to source documents with confidence scoring—no model fine-tuning needed.
- **Low-Resource Optimized**: Runs completely on CPU (`faiss-cpu`, lightweight transformer) with sub-second response times.
- **IIT Kanpur Knowledge Base**: Comprehensive dataset spanning Vox Populi student journal, Gymkhana, DOAA academic rules, Hall 1-14 hostels, SPO placements, and PK Kelkar library.
- **Modern Streamlit UI**: Glassmorphism dark-themed user interface with interactive query chips, category filtering, persistent session state, and expandable source citations.
- **Automated NLP Pipeline & Scraper**: Extensible web scraping and preprocessing framework (`src/scraper.py`) for maintaining and expanding knowledge base entries.

---

## 📁 Repository Structure

```
campus-info-bot/
├── app.py                      # Main Streamlit web application
├── requirements.txt            # Dependency specification (including faiss-cpu)
├── README.md                   # Project documentation & execution guide
├── .gitignore                  # Git ignore rules for clean repository
├── Final_Project_Pulpnet.pdf   # Project specification document
├── data/
│   └── iitk_campus_kb.json     # Processed IIT Kanpur knowledge base
└── src/
    ├── __init__.py             # Package init
    ├── scraper.py              # Web scraper & KB builder
    └── rag_engine.py           # Transformer RAG search engine with FAISS
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 2. Install Dependencies
Install all required libraries using:
```bash
pip install -r requirements.txt
```

### 3. Generate / Update Knowledge Base (Optional)
To run the automated scraper and generate the structured dataset (`data/iitk_campus_kb.json`):
```bash
python -m src.scraper
```

---

## 💻 Running the Streamlit App Locally

Launch the interactive web application with:
```bash
streamlit run app.py
```
*(or `python -m streamlit run app.py`)*

Once executed, open your web browser and navigate to:
```
http://localhost:8501
```

---

## 🤖 Model & RAG Pipeline Architecture

```
                               ┌─────────────────────────────┐
                               │     User Query (Streamlit)  │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
┌───────────────────────────┐    ┌───────────────────────────┐
│ IIT Kanpur Knowledge Base │───►│  SentenceTransformer      │
│ (data/iitk_campus_kb.json)│    │  (BERT Bi-Encoder:        │
└───────────────────────────┘    │   all-MiniLM-L6-v2)       │
                                 └──────────────┬──────────────┘
                                              │
                                              ▼
                                 ┌───────────────────────────┐
                                 │  FAISS Vector Index       │
                                 │  (IndexFlatIP - 384 dim)  │
                                 └──────────────┬──────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │  Top-K Context Retrieval &  │
                               │  Score Synthesis            │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │  Context-Aware Response +   │
                               │  Source Citations & Match % │
                               └─────────────────────────────┘
```

1. **Preprocessing & Embedding**: Knowledge base chunks are encoded into 384-dimensional L2-normalized vectors via `all-MiniLM-L6-v2`.
2. **FAISS Indexing**: Embeddings are indexed into a FAISS `IndexFlatIP` structure for ultra-fast vector similarity search.
3. **Retrieval**: At query time, the user prompt is projected into the embedding space, and FAISS returns the top nearest document matches.
4. **Answer Synthesis**: Context is formulated into an accurate response along with direct source references and relevance confidence scores.

---

## 📌 Example Queries to Try

- 🏢 *"Tell me about Halls of Residence and hostel life at IIT Kanpur"*
- 📰 *"What is Vox Populi and what articles does it publish?"*
- 💼 *"What are the placement statistics and top recruiters at IIT Kanpur?"*
- 📚 *"What facilities are available at PK Kelkar Library?"*
- 🎓 *"Explain the CPI grading system and academic programs at IITK"*
- 🚀 *"What is SIIC and how does innovation work at IIT Kanpur?"*

---

## 📄 License & Credits

Developed for the **PULPNET Final Project: Build a Transformer-Based Chatbot**.  
Data sourced from official IIT Kanpur web portals, Vox Populi student journal, SPO/ICS, and Gymkhana archives.
