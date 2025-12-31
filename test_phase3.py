import unittest
from unittest.mock import patch, MagicMock
from src.brain import detect_intent, generate_visualization

# Mock profile for testing
MOCK_PROFILE = {
    "columns": ["region", "sales", "date"],
    "dtypes": {"region": "object", "sales": "int64", "date": "object"},
    "row_count": 100
}

class TestBrainPhase3(unittest.TestCase):
    
    @patch('src.brain.call_llm')
    def test_intent_detection_related(self, mock_llm):
        """Test that related queries are detected correctly."""
        # Mock LLM response for intent
        mock_json = '{"is_related": true, "is_visualization": true, "needs_clarification": false, "rationale": "related"}'
        mock_llm.return_value = mock_json
        
        result = detect_intent(MOCK_PROFILE, "Show sales by region")
        self.assertTrue(result['is_related'])
        self.assertFalse(result['needs_clarification'])

    @patch('src.brain.call_llm')
    def test_intent_detection_unrelated(self, mock_llm):
        """Test that unrelated queries are rejected."""
        mock_json = '{"is_related": false, "is_visualization": false, "needs_clarification": false, "rationale": "unrelated"}'
        mock_llm.return_value = mock_json
        
        result = detect_intent(MOCK_PROFILE, "Write a poem about dogs")
        self.assertFalse(result['is_related'])

    @patch('src.brain.call_llm')
    def test_pipeline_success(self, mock_llm):
        """Test the full flow from query to code generation."""
        # This mock needs to handle two calls:
        # 1. Intent Detection
        # 2. Code Generation
        
        def side_effect(prompt):
            if "Determine if the user wants" in prompt:
                return '{"is_related": true, "needs_clarification": false}'
            else:
                return "```python\ndf.plot()\n```"
                
        mock_llm.side_effect = side_effect
        
        result = generate_visualization(MOCK_PROFILE, "Plot sales")
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['code'], 'df.plot()')

    @patch('src.brain.call_llm')
    def test_pipeline_clarification(self, mock_llm):
        """Test that unclear queries return a skip message."""
        mock_llm.return_value = '{"is_related": true, "needs_clarification": true, "clarification_message": "What columns?"}'
        
        result = generate_visualization(MOCK_PROFILE, "Show me something weird")
        self.assertEqual(result['status'], 'skipped')
        self.assertIn("What columns?", result['message'])

if __name__ == '__main__':
    unittest.main()
