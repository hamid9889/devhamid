"""
Unit & Integration Tests for Flask Developer Portfolio Backend
Tests:
  1. Contact Form API: POST /contact (validation & successful dispatch)
  2. Projects API: GET /projects (name, description, stars, forks, link)
  3. Visitor Counter API: GET /visits (returns count and increments)
  4. Health Check API: GET /health
"""

import sys
import unittest
from pathlib import Path

# Add backend and workspace root to sys.path
root_dir = Path(__file__).parent.parent
backend_dir = root_dir / "backend"
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.app import app

class TestFlaskPortfolioBackend(unittest.TestCase):

    def setUp(self):
        """Create test client before each test."""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_health_check(self):
        """Test GET /health returns 200 and healthy status."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'healthy')
        print("[PASS] GET /health returned healthy status.")

    def test_contact_form_validation_failure(self):
        """Test POST /contact with invalid data returns status: error."""
        response = self.client.post('/contact', json={
            "name": "",
            "email": "invalid-email",
            "message": "hi"
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'error')
        print("[PASS] POST /contact correctly rejected invalid payload.")

    def test_contact_form_success(self):
        """Test POST /contact with valid data returns status: success."""
        response = self.client.post('/contact', json={
            "name": "Jane Recruiter",
            "email": "recruiter@example.com",
            "message": "Hello Hamid, we would like to interview you for an AI/ML role."
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'success')
        print("[PASS] POST /contact succeeded with status: success.")

    def test_test_email_route(self):
        """Test GET /test-email returns status: success JSON."""
        response = self.client.get('/test-email')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get('status'), 'success')
        print("[PASS] GET /test-email succeeded with status: success.")

    def test_projects_api(self):
        """Test GET /projects returns list with name, description, stars, forks, link."""
        response = self.client.get('/projects')
        self.assertEqual(response.status_code, 200)
        projects = response.get_json()
        self.assertIsInstance(projects, list)
        self.assertGreater(len(projects), 0)

        first_project = projects[0]
        self.assertIn('name', first_project)
        self.assertIn('description', first_project)
        self.assertIn('stars', first_project)
        self.assertIn('forks', first_project)
        self.assertIn('link', first_project)
        print(f"[PASS] GET /projects returned {len(projects)} repositories with valid schema.")

    def test_visits_counter_api(self):
        """Test GET /visits returns count and increments."""
        res1 = self.client.get('/visits')
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertIn('count', data1)
        initial_count = data1['count']

        res2 = self.client.get('/visits')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(data2['count'], initial_count + 1)
        print(f"[PASS] GET /visits incremented count from {initial_count} to {data2['count']}.")

if __name__ == '__main__':
    unittest.main()
