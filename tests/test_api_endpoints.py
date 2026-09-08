"""
Test FastAPI HTTP API Endpoints
"""

import io
import unittest
from starlette.testclient import TestClient
from backend.main import app


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("status"), "ok")

    def test_check_text_endpoint(self):
        payload = {"text": "This are a bad sentence. I will recieve the package tommorow."}
        response = self.client.post("/api/check", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("issues", data)
        self.assertIn("statistics", data)
        self.assertIn("tone_analysis", data)
        self.assertIn("corrected_text", data)
        self.assertEqual(data["corrected_text"], "This is a bad sentence. I will receive the package tomorrow.")

    def test_dictionary_endpoints(self):
        # Add word
        res_add = self.client.post("/api/dictionary/add", json={"word": "FastAPIWord"})
        self.assertEqual(res_add.status_code, 200)
        self.assertTrue(res_add.json().get("success"))

        # Get dictionary
        res_get = self.client.get("/api/dictionary")
        self.assertEqual(res_get.status_code, 200)
        self.assertIn("fastapiword", res_get.json().get("words"))

        # Remove word
        res_del = self.client.delete("/api/dictionary/FastAPIWord")
        self.assertEqual(res_del.status_code, 200)

    def test_auth_endpoints(self):
        # Login with demo credentials
        res_login = self.client.post("/api/auth/login", json={
            "email": "demo@grammacheck.ai",
            "password": "password123"
        })
        self.assertEqual(res_login.status_code, 200)
        data = res_login.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["user"]["email"], "demo@grammacheck.ai")

        # Signup new user
        res_signup = self.client.post("/api/auth/signup", json={
            "name": "Jordan Smith",
            "email": "jordan@example.com",
            "password": "secretpassword",
            "plan": "Pro"
        })
        self.assertEqual(res_signup.status_code, 200)
        self.assertEqual(res_signup.json()["user"]["name"], "Jordan Smith")

    def test_document_upload_endpoint(self):
        payload = {
            "filename": "test_doc.txt",
            "text": "This is an uploaded test document for grammar checking.",
            "file_size_str": "1.2 KB",
            "file_size_bytes": 55,
            "file_type": "TXT"
        }
        res = self.client.post("/api/upload", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["filename"], "test_doc.txt")
        self.assertEqual(data["word_count"], 9)

    def test_history_endpoints(self):
        # Post history item
        payload = {
            "title": "Test sentence check",
            "original_text": "This are a test sentence.",
            "corrected_text": "This is a test sentence.",
            "word_count": 5,
            "char_count": 25,
            "score": 85,
            "issues_count": 1,
            "tone": "Neutral"
        }
        res_post = self.client.post("/api/history", json=payload)
        self.assertEqual(res_post.status_code, 200)
        self.assertTrue(res_post.json().get("success"))
        item_id = res_post.json()["entry"]["id"]

        # Get history
        res_get = self.client.get("/api/history")
        self.assertEqual(res_get.status_code, 200)
        self.assertGreaterEqual(res_get.json()["count"], 1)

        # Delete history item
        res_del = self.client.delete(f"/api/history/{item_id}")
        self.assertEqual(res_del.status_code, 200)


if __name__ == "__main__":
    unittest.main()
