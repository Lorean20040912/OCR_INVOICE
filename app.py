# app.py (versiune completă cu toate metodele de export)
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from ocr_processor import OCRProcessor
from one_c_integration import OneCIntegration
from export_handler import ExportHandler
from config import Config
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Inițializare servicii
ocr_processor = OCRProcessor()
one_c = OneCIntegration()
export_handler = ExportHandler()

# Creează directoare
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Primește și procesează fișierele încărcate"""
    if 'files' not in request.files:
        return jsonify({'error': 'Nu au fost găsite fișiere'}), 400

    files = request.files.getlist('files')
    processed_invoices = []

    for file in files:
        if file and allowed_file(file.filename):
            try:
                # Salvează fișierul
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
                file.save(filepath)

                # Procesează cu OCR
                invoice_data = ocr_processor.process_invoice(filepath)

                if invoice_data:
                    invoice_data['file_path'] = filepath
                    invoice_data['original_filename'] = filename
                    invoice_data['status'] = 'pending'
                    invoice_data['unique_id'] = str(uuid.uuid4())
                    processed_invoices.append(invoice_data)
                else:
                    logger.warning(f"Nu s-au putut extrage date din {filename}")

            except Exception as e:
                logger.error(f"Eroare la procesarea {filename}: {str(e)}")
                continue

    return jsonify({
        'success': True,
        'invoices': processed_invoices
    })

@app.route('/api/send-to-1c', methods=['POST'])
def send_to_1c():
    """
    Trimite factura - încearcă API, apoi fallback la export
    """
    data = request.json
    use_api = data.get('use_api', True)
    export_format = data.get('export_format', 'json')

    result = {'success': False}

    try:
        # Încearcă API dacă este activat
        if use_api:
            try:
                api_result = one_c.send_invoice(data)

                if api_result['success']:
                    result = {
                        'success': True,
                        'one_c_id': api_result.get('one_c_id'),
                        'method': 'API',
                        'message': 'Trimis cu succes prin API'
                    }
                else:
                    raise Exception(api_result.get('error', 'API a eșuat'))

            except Exception as api_error:
                logger.warning(f"API indisponibil: {str(api_error)}. Folosim export...")
                # Continuăm cu export
                use_api = False

        # Dacă API nu funcționează sau nu este activat, folosim export
        if not use_api:
            export_result = export_invoice(data, export_format)

            if export_result['success']:
                result = {
                    'success': True,
                    'method': export_format.upper(),
                    'file': export_result.get('file'),
                    'message': f'Exportat cu succes ca {export_format.upper()}'
                }
            else:
                result = {
                    'success': False,
                    'error': export_result.get('error')
                }

        # Șterge fișierul după procesare cu succes
        if result['success'] and 'file_path' in data:
            try:
                os.remove(data['file_path'])
            except:
                pass

        return jsonify(result)

    except Exception as e:
        logger.error(f"Eroare generală: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export', methods=['POST'])
def export_invoice_route():
    """Exportă direct într-un format specific"""
    data = request.json
    export_format = data.get('format', 'json')

    result = export_invoice(data, export_format)

    if result['success']:
        return send_file(
            result['file'],
            as_attachment=True,
            download_name=os.path.basename(result['file'])
        )
    else:
        return jsonify(result), 500

def export_invoice(invoice_data, format_type):
    """Helper pentru export în diferite formate"""
    if format_type == 'json':
        return export_handler.export_to_json(invoice_data)
    elif format_type == 'xml':
        return export_handler.export_to_xml(invoice_data)
    elif format_type == 'dbf':
        # Încearcă DBF real, dacă nu merge folosește CSV
        try:
            return export_handler.export_to_true_dbf(invoice_data)
        except:
            return export_handler.export_to_dbf_csv(invoice_data)
    else:
        return {'success': False, 'error': 'Format necunoscut'}

@app.route('/api/image/<path:filename>')
def serve_image(filename):
    """Servește imaginea facturii pentru preview"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)

@app.route('/api/config/test-1c', methods=['GET'])
def test_1c_connection():
    """Testează conexiunea la 1C"""
    is_connected = one_c.verify_connection()
    return jsonify({'connected': is_connected})

@app.route('/api/exports/<path:filename>')
def download_export(filename):
    """Descarcă fișier exportat"""
    return send_from_directory(export_handler.export_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
