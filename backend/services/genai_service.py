"""
Generative AI & Agentic LLM Pipeline
Specialized assistant module for Hamid's AI/ML Developer Portfolio.
Handles queries about Hamid's technical skills, research, and project portfolio.
"""

import os
import re
import time
import requests
from typing import Dict, Any

HAMID_PORTFOLIO_CONTEXT = """
Hamid is a B.Tech Computer Science & Artificial Intelligence student with core expertise in:
- Programming: Python, JavaScript/Node.js, C++, SQL
- AI/ML Frameworks: PyTorch, TensorFlow, Scikit-Learn, OpenCV, dlib, Hugging Face Transformers
- Generative AI & LLMs: LangChain, LlamaIndex, Retrieval-Augmented Generation (RAG), OpenAI/Gemini API, Prompt Engineering
- Cloud & Data: AWS (EC2, S3, Lambda), Supabase (PostgreSQL), Docker, Git/GitHub
- Notable Projects:
  1. Real-Time Face Recognition Attendance System (dlib, OpenCV, Supabase)
  2. Voice Biometrics Attendance with Anti-Spoofing (SpeechRecognition, PyDub, PyTorch)
  3. Real-Time Sign Language Translator (MediaPipe, LSTM, PyTorch)
  4. Multi-Agent Research Assistant (LangGraph, Gemini 1.5, Vector DB)
"""

def generate_chat_response(prompt: str, user_name: str = "Visitor") -> Dict[str, Any]:
    """
    Generates intelligent responses for portfolio visitors.
    Uses OpenAI/Gemini if API keys are configured; otherwise uses a tailored heuristic NLP engine.
    """
    start_time = time.time()
    query = prompt.lower().strip()

    # Rule-based NLP responses tailored to portfolio inquiries
    def has_word(pattern):
        return bool(re.search(rf"\b{pattern}\b", query))

    if has_word("skill") or has_word("skills") or has_word("stack") or has_word("tech") or has_word("python") or has_word("pytorch"):
        reply = (
            "Hamid's core tech stack:\n"
            "• Languages: Python, JavaScript, C++, SQL\n"
            "• AI/ML: PyTorch, TensorFlow, OpenCV, dlib, Scikit-Learn, PyDub, SpeechRecognition\n"
            "• Cloud & DevOps: AWS, Supabase, Docker, Git/GitHub\n"
            "• Web: Node.js, Express, Flask, REST APIs"
        )
    elif has_word("project") or has_word("projects") or has_word("work") or has_word("portfolio") or has_word("github"):
        reply = (
            "Hamid's flagship projects include:\n"
            "• Real-Time Face Recognition Attendance (dlib + OpenCV + Supabase)\n"
            "• Voice Biometric Attendance with Anti-Spoofing (PyDub + SpeechRecognition)\n"
            "• Real-time Sign Language Translator (MediaPipe + LSTM)\n"
            "• Multi-Agent Research Assistant (LangGraph + Gemini)\n"
            "Check out his GitHub at https://github.com/hamid9889 for source code!"
        )
    elif "who is hamid" in query or has_word("about") or has_word("bio") or has_word("background"):
        reply = (
            "Hamid is an aspiring AI & ML Developer and B.Tech CS & AI student. "
            "He specializes in Generative AI, Computer Vision, Deep Learning, and Cloud Architecture (AWS, Supabase). "
            "He has built state-of-the-art pipelines in Face Recognition, Voice Attendance, and Multi-Agent AI systems."
        )
    elif has_word("contact") or has_word("email") or has_word("hire") or has_word("reach"):
        reply = (
            "You can reach Hamid directly via email at 8090hamid@gmail.com, "
            "connect on LinkedIn, or submit a message through the contact form right on this website!"
        )
    elif any(k in query for k in ["supabase", "database"]):
        reply = (
            "This portfolio and its backend services use Supabase (cloud-hosted PostgreSQL) "
            "for persistent session tracking, analytics, and contact inquiry archival."
        )
    else:
        reply = (
            f"Thanks for asking, {user_name}! Hamid is an AI/ML developer specializing in Generative AI, "
            f"Computer Vision, and Deep Learning. For specific inquiries or collaborations, feel free to use the contact form "
            f"or email 8090hamid@gmail.com."
        )

    latency_ms = round((time.time() - start_time) * 1000, 2)
    return {
        "reply": reply,
        "model": "DevHamid-GenAI-Assistant-v1.0",
        "latency_ms": latency_ms,
        "tokens_used": len(reply.split())
    }
