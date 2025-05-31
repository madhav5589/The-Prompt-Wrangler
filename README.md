# The Prompt Wrangler: AI Powered Clinical Data Extraction Tool

## Overview
The Prompt Wrangler is a lightweight web tool for extracting structured clinical data from unstructured notes using LLMs (Large Language Models). It features a clean, user-friendly interface, supports multiple providers (DeepSeek, OpenAI, Claude), and allows users to tweak prompts and model parameters for optimal results.

## Features

- **Multi-Provider AI Support**: OpenAI GPT, Anthropic Claude, DeepSeek models
- **Real-time Extraction**: Extract structured medical data from clinical notes
- **Conversation History**: Save and review previous conversations and extractions
- **Security Validation**: Input sanitization and Content filtering for harmful prompts, CORS protection
- **Example Notes**: Pre-loaded medical note templates
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites
- Python 3.7+
- Flask 2.0+
- Valid API key for at least one LLM provider
- Modern web browser
  
## Quick Start
1. Clone this Repository
2. Install Dependencies - `pip install -r requirements.txt`
3. Set API keys as environment variables for LLM providers you wish to use:
  Edit `.env` file by adding your API key(s):
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ANTHROPIC_API_KEY=your_anthropic_api_key_here
    DEEPSEEK_API_KEY=your_deepseek_api_key_here
    ```
4. Start the App
    ```bash
    python app.py
    ```
5. Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

### Run Unit Tests
```bash
python -m unittest test_app.py
```
Make sure to have the required environment variables set (in .env file) before running tests.

## Usage

1. **Select AI Provider**: Choose from OpenAI, Anthropic, or DeepSeek
2. **Configure Settings**: Adjust temperature and max tokens
3. **Enter Clinical Note**: Type or paste medical text
4. **Extract Data**: Click "Extract Data" to process
5. **Review Results**: View structured fields and raw JSON
6. **View History**: Toggle conversation history to see past extractions

For more detailed usage instructions and features, please refer to [images](static/images) folder.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Optional* |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional* |
| `DEEPSEEK_API_KEY` | DeepSeek API key | Optional* |

*At least one API key is required for the application to function.

## Approach
- **MVP Focus:**
  - Simple, uncluttered UI with collapsible/closable sidebar for focus.
  - Editable system/user prompts and clinical note input.
  - Model parameter controls (temperature, max tokens).
  - Supports DeepSeek, OpenAI, Claude (Anthropic) with easy provider/model switching.
  - Displays structured output, token usage, and response time.
  - Input validation and basic error handling.
  - Conversation/session history (optional, toggleable).
- **Backend:**
  - Flask API routes for config, extraction, session, and examples.
  - Modular provider support via `llm_provider.py`.
  - Security validation for clinical notes.
  - Conversation management and persistence.
- **Frontend:**
  - Responsive, accessible, and visually clean (custom CSS, no frameworks).
  - All controls and feedback are immediate and intuitive.


## Future Enhancements (with more time)
- **Security:**
  - More robust input sanitization and rate limiting.
  - User authentication and role-based access.
  - Audit logging for sensitive data access.
- **Customer Obsession & User Friendliness:**
  - More detailed error messages and troubleshooting tips.
  - In-app onboarding/help and tooltips for all controls.
  - Export results (CSV, JSON, PDF) and shareable session links.
  - Side-by-side comparison of two prompt versions.
  - Accessibility improvements (WCAG compliance).
- **LLM/Feature Expansion:**
  - Dynamic max token limits based on selected model.
  - Support for additional LLM providers and custom endpoints.
  - Add “LLM says how to improve this prompt” feature.
  - Real-time streaming of LLM responses.
- **Enterprise/Production Readiness:**
  - Dockerization and cloud deployment guides.
  - Integration with EHR/EMR systems.
  - Usage analytics and admin dashboard.

## Troubleshooting

### Common Issues

1. **"API key missing" error**
   - Ensure your `.env` file exists and contains valid API keys
   - Restart the application after adding keys

2. **"Module not found" error**
   - Run `pip install -r requirements.txt`
   - Ensure you're in the correct directory

3. **Port already in use**
   - Change port in `app.py`: `app.run(debug=True, port=5001)`

### Debug Mode

The application runs in debug mode by default. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## License

This project is for assessment purposes.

## Contact & Contributions
For questions, suggestions, or contributions, please open an issue or pull request.
