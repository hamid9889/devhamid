"""
Unit Tests for AI/ML & Generative AI Pipeline Services
Validates Face Recognition, Speech Recognition, and GenAI Portfolio Assistant.
"""

import sys
import unittest
from pathlib import Path

# Add workspace root and backend directory to sys.path
root_path = Path(__file__).parent.parent
backend_path = root_path / "backend"
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from backend.services.face_recognition_service import face_pipeline
    from backend.services.speech_service import speech_pipeline
    from backend.services.genai_service import generate_chat_response
    from backend.services.supabase_client import get_visitor_count, record_visit
except ImportError:
    from services.face_recognition_service import face_pipeline  # type: ignore
    from services.speech_service import speech_pipeline  # type: ignore
    from services.genai_service import generate_chat_response  # type: ignore
    from services.supabase_client import get_visitor_count, record_visit  # type: ignore

class TestAiMlPipelines(unittest.TestCase):

    def test_face_recognition_pipeline(self):
        """Test Face Recognition verification with mock base64 image data."""
        dummy_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
        res = face_pipeline.verify_face(dummy_base64, target_name="Hamid")
        self.assertIn("matched", res)
        self.assertIn("confidence", res)
        print("[PASS] Face Recognition Pipeline test passed:", res.get("identified_as", "Checked"))

    def test_speech_pipeline(self):
        """Test Speech Recognition pipeline with simulated audio buffer."""
        dummy_audio = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        res = speech_pipeline.transcribe_audio(dummy_audio)
        self.assertIn("success", res)
        self.assertIn("transcript", res)
        print("[PASS] Speech Recognition Pipeline test passed:", res.get("transcript", "Checked")[:50])

    def test_genai_chat_pipeline(self):
        """Test Generative AI Portfolio Assistant with skill query."""
        res = generate_chat_response("What skills and frameworks does Hamid use?", user_name="Recruiter")
        self.assertIn("reply", res)
        self.assertIn("Python", res["reply"])
        self.assertIn("PyTorch", res["reply"])
        print("[PASS] GenAI Assistant Chat test passed. Latency:", res.get("latency_ms"), "ms")

    def test_supabase_client_fallback(self):
        """Test Supabase client with deduplicated visitor recording."""
        count = get_visitor_count()
        self.assertGreaterEqual(count, 1482)
        visit_res = record_visit("test-python-visitor", "127.0.0.1", "PythonUnitTest")
        self.assertIn("count", visit_res)
        self.assertIn("isNewVisit", visit_res)
        print("[PASS] Supabase Analytics test passed. Current count:", visit_res["count"])

if __name__ == '__main__':
    unittest.main()
