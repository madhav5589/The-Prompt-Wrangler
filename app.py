from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Import existing modules
from security import SecurityValidator
from conversations import ConversationManager
from llm_provider import LLMProvider
from schema import extract_structured_data
import prompts as pr

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Initialize session defaults
def init_session():
    session.setdefault('view_mode', 'input')
    session.setdefault('show_conversations', False)
    session.setdefault('clinical_note', '')
    session.setdefault('project_name', 'Clinical Data Extraction')

@app.route('/')
def index():
    init_session()
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get available providers and their configurations"""
    return jsonify({
        'providers': LLMProvider.PROVIDERS,
        'system_prompt': pr.SYSTEM_PROMPT
    })

@app.route('/api/check-api-key', methods=['POST'])
def check_api_key():
    """Check if API key is available for a provider"""
    data = request.json
    provider = data.get('provider')
    
    if not provider or provider not in LLMProvider.PROVIDERS:
        return jsonify({'error': 'Invalid provider'}), 400
    
    api_key = LLMProvider.get_api_key(provider)
    return jsonify({
        'has_key': bool(api_key),
        'env_key': LLMProvider.PROVIDERS[provider]['env_key']
    })

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get conversation history"""
    conversations = ConversationManager.load_conversations()
    return jsonify(conversations)

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """Extract structured data from clinical note"""
    data = request.json
    
    provider = data.get('provider')
    model = data.get('model')
    clinical_note = data.get('clinical_note', '')
    project_name = data.get('project_name', '')
    temperature = float(data.get('temperature', 0.3))
    max_tokens = int(data.get('max_tokens', 512))
    
    if not clinical_note.strip():
        return jsonify({'error': 'Clinical note is required'}), 400
    
    # Security validation
    safe, why = SecurityValidator.is_safe(clinical_note)
    if not safe:
        return jsonify({'error': f'Security Alert: {why}'}), 400
    
    # Check API key
    api_key = LLMProvider.get_api_key(provider)
    if not api_key:
        return jsonify({'error': f'{provider} API key missing'}), 400
    
    # Prepare messages
    messages = [
        {"role": "system", "content": pr.SYSTEM_PROMPT},
        {"role": "user", "content": f"Extract structured data from this clinical note:\n\n{clinical_note}"}
    ]
    
    # Make API request
    start_time = time.time()
    success, result = LLMProvider.make_request(
        provider, model, messages, temperature, max_tokens
    )
    elapsed = time.time() - start_time
    
    if not success:
        return jsonify({'error': result.get('error', 'Unknown error')}), 500
    
    # Extract structured data
    structured_data = extract_structured_data(result['content'])
    
    # Prepare response
    response_data = {
        'structured_data': structured_data,
        'provider': provider,
        'model': model,
        'elapsed': elapsed,
        'usage': result.get('usage', {}),
        'timestamp': datetime.now().isoformat(),
        'raw_response': result['content']
    }
    
    # Save conversation
    ConversationManager.save_conversation({
        'project_name': project_name,
        'provider': provider,
        'model': model,
        'system_prompt': pr.SYSTEM_PROMPT,
        'clinical_note': clinical_note,
        'response': result['content'],
        'structured_data': structured_data,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'response_time': elapsed,
        'token_usage': result.get('usage', {})
    })
    
    return jsonify(response_data)

@app.route('/api/session', methods=['POST'])
def new_session():
    """Clear session for new session"""
    session.clear()
    init_session()
    return jsonify({'status': 'success'})

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example clinical notes"""
    examples = [
        {
            'name': 'ALS Patient Care',
            'content': '''Patient is non-ambulatory and requires hospital bed with trapeze bar and side rails. Diagnosis: late-stage ALS. Order submitted by Dr. Cuddy.'''
        },
        {
            'name': 'Oxygen Therapy',
            'content': '''Patient diagnosed with COPD, SpO2 measured at 87% on room air. Needs portable oxygen concentrator for use during exertion and sleep. Dr. Chase signed the order.'''
        },
        {
            'name': 'Asthma Treatment',
            'content': '''Asthma diagnosis confirmed. Prescribing nebulizer with mouthpiece and tubing. Dr. Foreman completed the documentation.'''
        }
    ]
    return jsonify(examples)

if __name__ == '__main__':
    app.run(debug=True, port=5000)