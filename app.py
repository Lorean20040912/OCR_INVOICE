# app.py (versiune completă cu toate metodele de export)
from flask import Flask, request, jsonify, send_from_directory, send_file
try:
    from flask_cors import CORS
except Exception:
    def CORS(app, *args, **kwargs):
        return app
from werkzeug.utils import secure_filename
import os
import uuid
from ocr_processor import OCRProcessor
from one_c_integration import OneCIntegration
from export_handler_clean import ExportHandler
from config import Config
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Configurează Azure OCR (dacă nu e deja în env)
os.environ.setdefault('AZURE_VISION_ENDPOINT', 'https://facturi-ocr.cognitiveservices.azure.com/')
os.environ.setdefault('AZURE_VISION_KEY', '6tRq5nqi1FsTCF21SCxsuIdJwbTnF7IEY6CvmkKAyDSNZfwYktAQJQQJ99CEAC5RqLJXJ3w3AAALACOGnp2i')

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
    logger.info("Upload request received")

    if 'files' not in request.files:
        logger.error("No files in request")
        return jsonify({'error': 'Nu au fost găsite fișiere'}), 400

    files = request.files.getlist('files')
    logger.info(f"Received {len(files)} files")

    processed_invoices = []

    for file in files:
        if file and allowed_file(file.filename):
            try:
                # Salvează fișierul
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                logger.info(f"File saved: {filepath}")

                # Procesează cu OCR (prioritar Azure Document Intelligence, apoi fallback la OCR existent)
                try:
                    invoice_data = analyze_invoice_via_azure_di(filepath)
                    if not invoice_data:
                        invoice_data = ocr_processor.process_invoice(filepath)
                except Exception as ocr_error:
                    logger.error(f"OCR error for {filename}: {str(ocr_error)}")
                    invoice_data = {
                        'invoice_number': None,
                        'invoice_date': None,
                        'contractor': None,
                        'idno': None,
                        'total_amount': None,
                        'delivery_date': None,
                        'vat_amount': None,
                        'confidence': 0.0
                    }

                if invoice_data:
                    invoice_data['file_path'] = filepath
                    invoice_data['original_filename'] = filename
                    invoice_data['status'] = 'pending'
                    invoice_data['unique_id'] = str(uuid.uuid4())
                    # pentru preview în frontend
                    server_filename = os.path.basename(filepath)
                    invoice_data['server_filename'] = server_filename
                    invoice_data['preview_url'] = f"/api/image/{server_filename}"
                    processed_invoices.append(invoice_data)
                    logger.info(f"Invoice processed: {filename}")
                else:
                    logger.warning(f"Nu s-au putut extrage date din {filename}")

            except Exception as e:
                logger.error(f"Eroare la procesarea {filename}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                continue

    logger.info(f"Processed {len(processed_invoices)} invoices")
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

def analyze_invoice_via_azure_di(file_path: str):
    """
    Analizează factura folosind Azure Document Intelligence (prebuilt-invoice) via REST.
    Returnează dict cu câmpurile standard sau None dacă nu poate analiza.
    """
    try:
        import os, time, requests
        endpoint = os.environ.get('AZURE_DOCUMENTINTELLIGENCE_ENDPOINT') or os.environ.get('AZURE_VISION_ENDPOINT')
        key = os.environ.get('AZURE_DOCUMENTINTELLIGENCE_KEY') or os.environ.get('AZURE_VISION_KEY')
        if not endpoint or not key or not os.path.isfile(file_path):
            return None

        url = endpoint.rstrip('/') + '/formrecognizer/documentModels/prebuilt-invoice:analyze?api-version=2023-07-31'
        with open(file_path, 'rb') as f:
            data = f.read()

        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/octet-stream',
        }
        r = requests.post(url, headers=headers, data=data, timeout=45)
        if r.status_code not in (200, 202):
            logger.warning(f"Azure DI analyze POST status {r.status_code}: {r.text[:200]}")
            return None

        op_loc = r.headers.get('Operation-Location') or r.headers.get('operation-location')
        result = None
        if op_loc:
            deadline = time.time() + 75
            while time.time() < deadline:
                g = requests.get(op_loc, headers={'Ocp-Apim-Subscription-Key': key}, timeout=45)
                jr = {}
                try:
                    jr = g.json()
                except Exception:
                    pass
                status = (jr.get('status') or '').lower()
                if status == 'succeeded':
                    result = jr
                    break
                if status == 'failed':
                    logger.warning(f"Azure DI analyze failed: {jr}")
                    return None
                time.sleep(1.2)
        else:
            # Uneori răspunsul vine direct
            try:
                result = r.json()
            except Exception:
                result = None

        if not result:
            return None

        analyze = result.get('analyzeResult') or {}
        docs = analyze.get('documents') or []
        if not docs:
            return None
        doc = docs[0]
        fields = doc.get('fields') or {}

        def _get_str(name):
            f = fields.get(name) or {}
            return f.get('valueString') or f.get('content')

        def _get_date(name):
            f = fields.get(name) or {}
            return f.get('valueDate') or f.get('content')

        def _get_curr_amount(name):
            f = fields.get(name) or {}
            cur = f.get('valueCurrency') or {}
            return cur.get('amount')

        def _conf(name):
            f = fields.get(name) or {}
            return f.get('confidence')

        def _norm_date(val):
            # întoarce 'YYYY-MM-DD' sau None
            if not val:
                return None
            s = str(val).strip()
            # încerci mai întâi ISO
            from datetime import datetime
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(s, fmt).date().isoformat()
                except Exception:
                    continue
            # încearcă fromisoformat (poate include timp)
            try:
                return datetime.fromisoformat(s).date().isoformat()
            except Exception:
                pass
            # dacă nu se poate, returnează stringul original
            return s

        invoice_number = _get_str('InvoiceId')
        invoice_date = _norm_date(_get_date('InvoiceDate') or _get_str('InvoiceDate'))

        # identificare furnizor robustă
        vendor_name = _get_str('VendorName')
        customer_name = _get_str('CustomerName')
        vendor_tax = _get_str('VendorTaxId') or _get_str('VendorId')
        customer_tax = _get_str('CustomerId')  # uneori CustomerId e cod fiscal în modele
        full_content = (analyze.get('content') or '').strip()

        contractor = None
        # 1) dacă VendorName e clar și diferit de CustomerName, folosește-l
        if vendor_name and (not customer_name or vendor_name.strip().lower() != (customer_name or '').strip().lower()):
            contractor = vendor_name.strip()
        # 2) dacă VendorName lipsă dar avem VendorTaxId, preferăm tot ce avem ca vendor
        elif vendor_tax and vendor_name:
            contractor = vendor_name.strip()
        # 3) fallback: caută în conținut după etichete uzuale (RO/RU/EN)
        elif full_content:
            import re
            patterns = [
                r'(?:^|\n)\s*(?:FURNIZOR(?:UL)?|VÂNZĂTOR|VÎNZĂTOR|VINZĂTOR|SUPPLIER|PROVIDER)\s*[:\-]?\s*(.+)',
                r'(?:^|\n)\s*(?:PRESTATOR|EMITENT)\s*[:\-]?\s*(.+)',
            ]
            found = None
            for pat in patterns:
                m = re.search(pat, full_content, flags=re.IGNORECASE)
                if m:
                    line = m.group(1).strip()
                    # ia doar prima linie până la sfârșit de linie
                    candidate = line.splitlines()[0].strip(" \t:-")
                    # curăță delimitatoare comune
                    candidate = re.sub(r'\s{2,}', ' ', candidate)
                    # evită a eticheta cumpărătorul
                    if not re.search(r'^(?:CUMP[ĂA]R[ĂA]TOR|CUMPARATOR|CLIENT|BUYER)\b', candidate, flags=re.IGNORECASE):
                        found = candidate
                        break
            if found:
                contractor = found
        # 4) ultim fallback: folosește VendorName dacă există, altfel CustomerName
        if not contractor:
            contractor = vendor_name or customer_name

        idno = _get_str('VendorTaxId') or _get_str('CustomerId') or _get_str('VendorId')
        total_amount = _get_curr_amount('InvoiceTotal')
        vat_amount = _get_curr_amount('TotalTax')

        confidences = list(filter(lambda x: x is not None, [
            _conf('InvoiceId'), _conf('InvoiceDate'), _conf('VendorName'),
            _conf('VendorTaxId'), _conf('CustomerId'), _conf('InvoiceTotal'), _conf('TotalTax')
        ]))
        confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0

        return {
            'invoice_number': invoice_number,
            'invoice_date': invoice_date,
            'contractor': contractor,
            'idno': idno,
            'total_amount': total_amount,
            'delivery_date': None,
            'vat_amount': vat_amount,
            'confidence': confidence
        }
    except Exception as e:
        logger.error(f"Azure DI exception: {str(e)}")
        return None

@app.route('/api/reprocess', methods=['POST'])
def reprocess_ocr():
    """
    Reprocesează OCR pentru un fișier deja încărcat pe server.
    Acceptă:
      - file_path: calea completă către fișier (dacă este cunoscută)
      - server_filename: numele fișierului din folderul UPLOAD_FOLDER
    """
    try:
        data = request.json or {}
        file_path = data.get('file_path')
        server_filename = data.get('server_filename')

        if not file_path and server_filename:
            file_path = os.path.join(Config.UPLOAD_FOLDER, server_filename)

        if not file_path or not os.path.isfile(file_path):
            return jsonify({'success': False, 'error': 'Fișierul nu există pe server'}), 400

        invoice_data = analyze_invoice_via_azure_di(file_path)
        if not invoice_data:
            invoice_data = ocr_processor.process_invoice(file_path) or {}

        invoice_data['file_path'] = file_path
        invoice_data['server_filename'] = os.path.basename(file_path)
        invoice_data['preview_url'] = f"/api/image/{invoice_data['server_filename']}"
        invoice_data['status'] = invoice_data.get('status') or 'pending'
        invoice_data['unique_id'] = data.get('unique_id') or str(uuid.uuid4())

        return jsonify({'success': True, 'invoice': invoice_data})
    except Exception as e:
        logger.error(f"Reprocess OCR error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
