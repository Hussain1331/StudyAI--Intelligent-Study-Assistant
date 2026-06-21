# 🧠 StudyAI — Intelligent AI Study Assistant

An AI-powered study companion built using **Streamlit**, **OpenRouter LLMs**, and **PDF-based learning workflows**.

StudyAI helps students upload study notes, generate summaries, create revision notes, practice MCQs, take quizzes, and interact with an AI tutor through a modern chat interface.

---

## 🚀 Features

### 📂 PDF-Based Learning

* Upload PDF notes and study materials
* Automatic text extraction
* Context-aware AI responses
* Persistent PDF session support

### 💬 AI Tutor Chat

* Ask questions directly from uploaded notes
* Concept explanations
* Doubt solving
* Exam preparation assistance
* Personalized learning support

### 📝 Smart Study Tools

* Chapter Summaries
* Revision Notes Generation
* MCQ Generation
* Interactive Quiz Mode

### 🎨 Modern User Interface

* Clean and responsive design
* Fixed chat interface
* Custom sidebar
* Streamlit-powered interactive experience

---

## 🛠️ Tech Stack

### Frontend

* Streamlit
* HTML
* CSS

### AI & NLP

* OpenRouter API
* OpenAI Python SDK
* Llama 3
* Gemma
* Mistral

### Document Processing

* PyPDF
* LangChain Text Splitters

---

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/Hussain1331/StudyAI--Intelligent-Study-Assistant.git
cd StudyAI--Intelligent-Study-Assistant
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure API Key

Create a file:

```text
.streamlit/secrets.toml
```

Add your OpenRouter API key:

```toml
OPENROUTER_API_KEY="YOUR_API_KEY"
```

### Run the Application

```bash
streamlit run app.py
```

---

## 📚 How It Works

1. Upload a PDF containing study notes.
2. StudyAI extracts and processes the text.
3. Ask questions about your notes.
4. Generate summaries and revision material.
5. Practice with AI-generated MCQs.
6. Test your understanding using Quiz Mode.

---

## 🎯 Future Improvements

* Vector Database Integration
* Retrieval-Augmented Generation (RAG)
* Flashcard Generation
* Multi-PDF Support
* Voice Assistant
* Progress Tracking Dashboard
* Study Analytics


### Skills

* Python
* Artificial Intelligence
* Machine Learning
* Streamlit
* OpenRouter APIs


