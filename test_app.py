import unittest
from app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The Prompt Wrangler', response.data)

    def test_extract_route_post(self):
        # Only test OpenAI if API key is present
        import os
        if not os.getenv('OPENAI_API_KEY'):
            self.skipTest('OPENAI_API_KEY not set, skipping OpenAI test')
        payload = {
            'provider': 'OpenAI',
            'model': 'gpt-3.5-turbo',
            'clinical_note': 'Patient is a 45-year-old male with hypertension.',
            'project_name': 'Clinical Data Extraction',
            'temperature': 0.3,
            'max_tokens': 512
        }
        response = self.app.post('/api/extract', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn('structured_data', data)
        self.assertIn('provider', data)
        self.assertIn('elapsed', data)
        self.assertIn('usage', data)
        self.assertIn('timestamp', data)
        self.assertIn('raw_response', data)

    def test_extract_route_post_deepseek(self):
        # Test /api/extract with DeepSeek provider only (no OpenAI/Anthropic)
        payload = {
            'provider': 'DeepSeek',
            'model': 'deepseek-chat',
            'clinical_note': 'Patient is a 45-year-old male with hypertension.',
            'project_name': 'Clinical Data Extraction',
            'temperature': 0.3,
            'max_tokens': 512
        }
        response = self.app.post('/api/extract', json=payload)
        # Accept 200 (success) or 400 (missing API key) for CI/dev environments
        print (f"Response status code: {response.status_code}")
        self.assertIn(response.status_code, [200, 400])
        if response.status_code == 200:
            self.assertTrue(response.is_json)
            data = response.get_json()
            self.assertIn('structured_data', data)
            self.assertIn('provider', data)
            self.assertIn('elapsed', data)
            self.assertIn('usage', data)
            self.assertIn('timestamp', data)
            self.assertIn('raw_response', data)
        else:
            # Should be missing API key error
            data = response.get_json()
            self.assertIn('error', data)
            self.assertIn('DeepSeek', data['error'])

if __name__ == '__main__':
    unittest.main()
