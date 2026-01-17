import io
import re
from google.cloud import vision
from PIL import Image
from pdf2image import convert_from_path
import logging

logger = logging.getLogger(__name__)


class OCRProcessor:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def process_invoice(self, file_path):
        """Procesează factura și extrage datele necesare"""
        try:
            # Convertește PDF în imagine dacă este necesar
            if file_path.lower().endswith('.pdf'):
                import os
                base_dir = os.path.dirname(os.path.abspath(__file__))
                poppler_path = os.path.join(base_dir, 'Release-25.12.0-0', 'poppler-25.12.0', 'Library', 'bin')
                images = convert_from_path(file_path, first_page=1, last_page=1, poppler_path=poppler_path)
                image = images[0]

                # Convertește la bytes pentru Vision API
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                content = img_byte_arr.getvalue()
            else:
                with io.open(file_path, 'rb') as image_file:
                    content = image_file.read()

            # Apelează Google Cloud Vision API
            image = vision.Image(content=content)

            # OCR text detection
            response = self.client.text_detection(image=image)
            texts = response.text_annotations

            if not texts:
                return None

            full_text = texts[0].description

            # Extrage datele din text
            extracted_data = self._extract_invoice_data(full_text)

            # Document text detection pentru structură mai bună
            document = self.client.document_text_detection(image=image)

            # Încearcă să îmbunătățească extragerea cu informații structurale
            if document.full_text_annotation:
                self._enhance_extraction(extracted_data, document.full_text_annotation)

            return extracted_data

        except Exception as e:
            logger.error(f"Eroare la procesare OCR: {str(e)}")
            raise

    def _extract_invoice_data(self, text):
        """Extrage datele specifice din textul OCR - adaptat pentru Moldova"""
        data = {
            'invoice_number': None,
            'invoice_date': None,
            'contractor': None,
            'idno': None,  # IDNO în loc de CUI
            'total_amount': None,
            'delivery_date': None,
            'vat_amount': None,
            'confidence': 0.0
        }

        # Regex patterns pentru datele din Republica Moldova
        patterns = {
            'invoice_number': r'(?:FACTURA|FACT(?:URA)?\.?|ФАКТУРА)\s*(?:NR\.?|NUMĂR|№)?\s*:?\s*([A-Z0-9\-/]+)',
            'invoice_date': r'(?:DATA|DATE|ДАТА)?\s*:?\s*(\d{1,2}[\./-]\d{1,2}[\./-]\d{2,4})',
            'idno': r'(?:IDNO|I\.D\.N\.O\.?|COD\s+FISCAL)\s*:?\s*(\d{13})',  # IDNO are 13 cifre
            'total_amount': r'(?:TOTAL|TOTAL\s+(?:GENERAL|DE\s+PLATA)|ИТОГО)\s*:?\s*([\d\.,]+)',
            'delivery_date': r'(?:DATA\s+LIVRARE|LIVRARE|ДАТА\s+ПОСТАВКИ)\s*:?\s*(\d{1,2}[\./-]\d{1,2}[\./-]\d{2,4})',
            'vat_amount': r'(?:TVA|T\.V\.A\.?|НДС)\s*:?\s*([\d\.,]+)'
        }

        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()

                # Normalizează valorile
                if field in ['total_amount', 'vat_amount']:
                    value = value.replace(',', '.')
                elif field in ['invoice_date', 'delivery_date']:
                    value = self._normalize_date(value)

                data[field] = value

        # Extrage numele companiei (de obicei primele linii după antet)
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):
            if re.search(r'S\.?R\.?L|S\.?A\.|I\.?P\.|ÎCS|ООО|SRL|ÎM', line, re.IGNORECASE):
                # Ia liniile anterioare ca nume companie
                contractor_parts = []
                for j in range(max(0, i - 2), i + 1):
                    if lines[j].strip() and not re.search(r'FACTURA|ФАКТУРА|NR\.|№|DATA|ДАТА', lines[j], re.IGNORECASE):
                        contractor_parts.append(lines[j].strip())
                data['contractor'] = ' '.join(contractor_parts)
                break

        # Calculează confidence score bazat pe câmpuri completate
        filled_fields = sum(1 for v in data.values() if v is not None)
        data['confidence'] = filled_fields / (len(data) - 1)  # -1 pentru câmpul confidence

        return data

    def _normalize_date(self, date_str):
        """Normalizează datele în format ISO (YYYY-MM-DD)"""
        # Înlocuiește separatori
        date_str = date_str.replace('/', '-').replace('.', '-')

        parts = date_str.split('-')
        if len(parts) == 3:
            day, month, year = parts

            # Convertește anul la 4 cifre
            if len(year) == 2:
                year = '20' + year if int(year) < 50 else '19' + year

            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        return date_str

    def _enhance_extraction(self, data, full_text_annotation):
        """Îmbunătățește extragerea folosind informații structurale"""
        pass