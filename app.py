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


@app.route('/api/image/<path:filename>', methods=['GET'])
def serve_uploaded_preview(filename):
    """Servește fișierele încărcate (PNG/JPG/PDF) pentru previzualizare și descărcare."""
    try:
        safe_name = os.path.basename(filename or "")
        if not safe_name:
            return jsonify({'error': 'Nume fișier invalid'}), 400

        # FIX: convertim Path la string explicit
        upload_dir = str(Config.UPLOAD_FOLDER)
        file_path = os.path.join(upload_dir, safe_name)

        if not os.path.isfile(file_path):
            logger.warning(f"Preview 404 pentru: {file_path}")
            return jsonify({'error': 'Fișierul nu a fost găsit'}), 404

        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        resp = send_file(
            file_path,
            mimetype=mime_type or 'application/octet-stream',
            as_attachment=False,
            conditional=True,
        )
        resp.headers['Cache-Control'] = 'public, max-age=3600'
        resp.headers['Accept-Ranges'] = 'bytes'
        return resp
    except Exception as e:
        logger.error(f"Eroare la servirea fișierului {filename}: {e}")
        return jsonify({'error': 'Eroare internă'}), 500


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

def export_to_xlsx_local(invoice_data: dict) -> dict:
    """
    Generează un XLSX minimal (OOXML) fără dependențe externe.
    Scrie câmpurile cheie într-un singur sheet (Sheet1).
    Returnează dict {'success': True, 'file': <path>} sau {'success': False, 'error': ...}
    """
    try:
        import zipfile
        from io import BytesIO
        from datetime import datetime

        os.makedirs(export_handler.export_folder, exist_ok=True)

        # Rânduri cheie -> valoare
        rows = [
            ("Invoice Number", str(invoice_data.get("invoice_number") or "")),
            ("Invoice Date", str(invoice_data.get("invoice_date") or "")),
            ("Supplier", str(invoice_data.get("contractor") or "")),
            ("Tax ID", str(invoice_data.get("idno") or "")),
            ("Total Amount", str(invoice_data.get("total_amount") or "")),
            ("VAT Amount", str(invoice_data.get("vat_amount") or "")),
            ("Original File", str(invoice_data.get("original_filename") or "")),
        ]

        # Construcție XML-uri OOXML minime
        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
"""
        rels_root = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""
        wb = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Sheet1" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
"""
        wb_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""
        styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
  <borders count="1"><border/></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/></cellXfs>
</styleSheet>
"""
        # Sheet1 cu două coloane: Cheie, Valoare
        def xl_row(ridx: int, key: str, val: str) -> str:
            # r începe de la 1, coloanele A și B
            key = (key or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            val = (val or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            return f'<row r="{ridx}"><c r="A{ridx}" t="inlineStr"><is><t>{key}</t></is></c><c r="B{ridx}" t="inlineStr"><is><t>{val}</t></is></c></row>'

        rows_xml = "\n".join([xl_row(i + 1, k, v) for i, (k, v) in enumerate(rows)])
        sheet1 = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    {rows_xml}
  </sheetData>
</worksheet>
"""

        # Nume fișier
        base = invoice_data.get("invoice_number") or "export"
        safe = "".join(ch for ch in str(base) if ch.isalnum() or ch in ("-", "_")).strip() or "export"
        out_path = os.path.join(export_handler.export_folder, f"{safe}.xlsx")

        # Scrie pachetul XLSX
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", rels_root)
            zf.writestr("xl/workbook.xml", wb)
            zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)
            zf.writestr("xl/styles.xml", styles)
            zf.writestr("xl/worksheets/sheet1.xml", sheet1)

        return {"success": True, "file": out_path}
    except Exception as e:
        logger.error(f"export_to_xlsx_local error: {e}")
        return {"success": False, "error": str(e)}

def export_to_zip1c(invoice_data: dict) -> dict:
    """
    Creează un pachet ZIP pentru 1C ce conține:
      - invoice.xlsx (datele facturii)
      - params.xml (parametri simplificați cu o cheie GUID)
    """
    try:
        import zipfile
        from datetime import datetime

        os.makedirs(export_handler.export_folder, exist_ok=True)

        # 1) Creează XLSX
        xres = export_to_xlsx_local(invoice_data)
        if not xres.get("success"):
            return xres
        xlsx_path = xres["file"]

        # 2) Generează params.xml cu o "cheie" (GUID) și meta minimale
        guid = str(uuid.uuid4())
        today = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        params_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ExchangeParameters>
  <Program>OCR-Invoice-Processor</Program>
  <ExchangeType>Invoice</ExchangeType>
  <Guid>{guid}</Guid>
  <CreatedAt>{today}</CreatedAt>
  <FileFormat>XLSX</FileFormat>
  <Comment>Parametri de conectare/sincronizare - exemplu simplificat</Comment>
</ExchangeParameters>
"""

        # 3) Construiește ZIP
        bundle_name = f"invoice_bundle_{guid[:8]}.zip"
        bundle_path = os.path.join(export_handler.export_folder, bundle_name)
        with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(xlsx_path, arcname="invoice.xlsx")
            zf.writestr("params.xml", params_xml)

        return {"success": True, "file": bundle_path}
    except Exception as e:
        logger.error(f"export_to_zip1c error: {e}")
        return {"success": False, "error": str(e)}

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
    elif format_type == 'xlsx':
        return export_to_xlsx_local(invoice_data)
    elif format_type in ('zip', 'zip1c'):
        return export_to_zip1c(invoice_data)
    else:
        return {'success': False, 'error': 'Format necunoscut'}

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
    Config.create_directories()
    app.run(debug=True, port=5000, use_reloader=False)
