"""
Data Schemas and Validation Models (Python)
Provides structured interfaces for Contact inquiries, Analytics,
and AI/ML pipelines (Face Recognition, Speech Recognition, and Generative AI).
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class ContactMessage:
    name: str
    email: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "pending"

    def is_valid(self) -> tuple[bool, str]:
        if not self.name or len(self.name.strip()) < 2:
            return False, "Name must be at least 2 characters."
        if not self.email or "@" not in self.email:
            return False, "A valid email address is required."
        if not self.message or len(self.message.strip()) < 10:
            return False, "Message must be at least 10 characters."
        return True, ""

@dataclass
class VisitorAnalytics:
    total_visits: int
    last_visit_at: str
    is_new_visit: bool = False

@dataclass
class FaceVerificationRequest:
    image_base64: str
    target_name: Optional[str] = None
    tolerance: float = 0.6

@dataclass
class FaceVerificationResult:
    matched: bool
    confidence: float
    detected_faces_count: int
    identified_as: Optional[str] = None
    error: Optional[str] = None

@dataclass
class SpeechTranscriptionRequest:
    audio_data_base64: str
    audio_format: str = "wav"  # wav, mp3, ogg
    language: str = "en-US"

@dataclass
class SpeechTranscriptionResult:
    transcript: str
    confidence: float
    duration_seconds: float
    success: bool
    error: Optional[str] = None

@dataclass
class GenAIQueryRequest:
    prompt: str
    context: Optional[str] = None
    model: str = "gemini-pro"
    max_tokens: int = 500

@dataclass
class GenAIResponse:
    reply: str
    tokens_used: int
    model: str
    latency_ms: float
