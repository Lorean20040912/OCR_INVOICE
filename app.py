import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from config import Config
from ocr_processor import OCRProcessor
from one_c_integration import OneCIntegration

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ocr_processor = OCRProcessor()
one_c_integration = OneCIntegration()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_invoice():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Step 1: OCR Processing
            extracted_data = ocr_processor.process_invoice(file_path)
            
            if not extracted_data:
                return jsonify({'error': 'Could not extract data from invoice'}), 422
            
            # Step 2: 1C Integration
            one_c_result = one_c_integration.send_invoice(extracted_data)
            
            return jsonify({
                'success': True,
                'extracted_data': extracted_data,
                'one_c_result': one_c_result
            })
            
        except Exception as e:
            logger.error(f"Error processing invoice: {str(e)}")
            return jsonify({'error': str(e)}), 500
        finally:
            # Optional: Clean up uploaded file
            # os.remove(file_path)
            pass
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', '1c_connection': one_c_integration.verify_connection()})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
