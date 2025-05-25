from flask import Flask, request, jsonify
import os
import logging
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Import MediaPipe tasks
try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import text
    MEDIAPIPE_AVAILABLE = True
    logger.info("MediaPipe Tasks successfully imported")
except ImportError as e:
    MEDIAPIPE_AVAILABLE = False
    logger.error(f"Failed to import MediaPipe Tasks: {e}")

# Path to the model file
MODEL_PATH = os.environ.get("MODEL_PATH", "./models/gemma-3n-E2B-it-litert-preview.task")

# Child-friendly prompt template that will be injected for all queries
CHILD_FRIENDLY_PROMPT = """
IMPORTANT INSTRUCTION: The following content may involve or be for children.
You must respond using sanitized, simple language appropriate for young audiences.
Ensure all content is educational, safe, and easily understandable.
Avoid complex terminology and keep explanations straightforward.

User query: {query}
"""

# Global variables for model
generator = None
model_loaded = False
model_lock = threading.Lock()

# Initialize the text generator
def initialize_model():
    global generator, model_loaded

    if not MEDIAPIPE_AVAILABLE:
        logger.error("Cannot initialize model: MediaPipe Tasks not available")
        return False

    try:
        with model_lock:
            if not os.path.exists(MODEL_PATH):
                logger.error(f"Model file not found at {MODEL_PATH}")
                return False

            logger.info(f"Loading model from {MODEL_PATH}")
            base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
            options = text.TextGeneratorOptions(
                max_output_tokens=256,
                temperature=0.5
            )
            generator = text.TextGenerator.create_from_options(base_options, options)
            model_loaded = True
            logger.info("Model loaded successfully!")
            return True
    except Exception as e:
        logger.error(f"Error initializing model: {e}")
        return False

# Initialize model in a separate thread to avoid blocking app startup
threading.Thread(target=initialize_model).start()

@app.route('/generate', methods=['POST'])
def generate_text():
    global generator, model_loaded

    if not MEDIAPIPE_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'MediaPipe Tasks not available on this system'
        }), 500

    if not model_loaded:
        return jsonify({
            'success': False,
            'error': 'Model not loaded yet or failed to load'
        }), 503

    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'No prompt provided'
            }), 400

        user_input = data['prompt']

        # Always apply child-friendly prompt injection
        full_prompt = CHILD_FRIENDLY_PROMPT.format(query=user_input)
        logger.info(f"Processing prompt: {user_input[:50]}...")

        # Generate response using the model
        with model_lock:
            response = generator.generate(full_prompt)

        return jsonify({
            'success': True,
            'response': response.text
        })

    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'mediapipe_available': MEDIAPIPE_AVAILABLE,
        'model_loaded': model_loaded,
        'model_path': MODEL_PATH
    })

@app.route('/reload_model', methods=['POST'])
def reload_model():
    success = initialize_model()
    return jsonify({
        'success': success,
        'model_loaded': model_loaded
    })

if __name__ == '__main__':
    # Run the Flask app on the Raspberry Pi's network interface
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)