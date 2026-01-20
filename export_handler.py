# export_handler.py
import json
import xml.etree.ElementTree as ET
import csv
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class ExportHandler:
    """Gestionează exportul facturilor în diferite formate"""

    def __init__(self, export_folder='exports'):
        self.export_folder = export_folder
        os.makedirs(export_folder, exist_ok=True)

    def export_to_json(self, invoice_data, filename=None):
        """
        Export în JSON - cel mai bun pentru API-uri moderne și 1C 8.3+
        Avantaje:
        - Ușor de citit și editat
        - Suport nativ în majoritatea limbajelor
        - Structură flexibilă
        """
        if not filename:
            filename = f"invoice_{invoice_data.get('invoice_number', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = os.path.join(self.export_folder, filename)

        # Structură optimizată pentru 1C
        export_data = {
            "Invoice": {
                "Number": invoice_data.get('invoice_number'),
                "Date": invoice_data.get('invoice_date'),
                "Contractor": {
                    "Name": invoice_data.get('contractor'),
                    "IDNO": invoice_data.get('idno')
                },
                "Amounts": {
                    "Total": float(invoice_data.get('total_amount', 0) or 0),
                    "VAT": float(invoice_data.get('vat_amount', 0) or 0),
                    "Currency": "MDL"
                },
                "DeliveryDate": invoice_data.get('delivery_date'),
                "ProcessedDate": datetime.now().isoformat(),
                "OCRConfidence": invoice_data.get('confidence', 0)
            }
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Export JSON reușit: {filepath}")
            return {'success': True, 'file': filepath, 'format': 'JSON'}
        except Exception as e:
            logger.error(f"Eroare export JSON: {str(e)}")
            return {'success': False, 'error': str(e)}

    def export_to_xml(self, invoice_data, filename=None):
        """
        Export în XML - compatibil cu 1C 8.x și sisteme vechi
        Avantaje:
        - Standard pentru schimb de date între sisteme
        - Suport excelent în 1C
        - Validare prin schema XML
        """
        if not filename:
            filename = f"invoice_{invoice_data.get('invoice_number', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"

        filepath = os.path.join(self.export_folder, filename)

        try:
            # Creează structura XML
            root = ET.Element('Invoice')

            # Informații de bază
            ET.SubElement(root, 'Number').text = str(invoice_data.get('invoice_number', ''))
            ET.SubElement(root, 'Date').text = invoice_data.get('invoice_date', '')

            # Contragent
            contractor = ET.SubElement(root, 'Contractor')
            ET.SubElement(contractor, 'Name').text = invoice_data.get('contractor', '')
            ET.SubElement(contractor, 'IDNO').text = invoice_data.get('idno', '')

            # Sume
            amounts = ET.SubElement(root, 'Amounts')
            ET.SubElement(amounts, 'Total').text = str(invoice_data.get('total_amount', 0) or 0)
            ET.SubElement(amounts, 'VAT').text = str(invoice_data.get('vat_amount', 0) or 0)
            ET.SubElement(amounts, 'Currency').text = 'MDL'

            # Date suplimentare
            ET.SubElement(root, 'DeliveryDate').text = invoice_data.get('delivery_date', '')
            ET.SubElement(root, 'ProcessedDate').text = datetime.now().isoformat()
            ET.SubElement(root, 'OCRConfidence').text = str(invoice_data.get('confidence', 0))

            # Formatează și salvează
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")  # Formatare frumoasă (Python 3.9+)

            tree.write(filepath, encoding='utf-8', xml_declaration=True)

            logger.info(f"Export XML reușit: {filepath}")
            return {'success': True, 'file': filepath, 'format': 'XML'}
        except Exception as e:
            logger.error(f"Eroare export XML: {str(e)}")
            return {'success': False, 'error': str(e)}

    def export_to_dbf_csv(self, invoice_data, filename=None):
        """
        Export în CSV compatibil cu DBF - pentru 1C 7.7 și import manual
        Avantaje:
        - Compatibil cu versiuni vechi de 1C
        - Poate fi deschis în Excel
        - Ușor de convertit în DBF cu tool-uri gratuite

        Notă: Pentru DBF real, folosește biblioteca 'dbf' sau 'dbfread'
        pip install dbf
        """
        if not filename:
            filename = f"invoice_{invoice_data.get('invoice_number', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = os.path.join(self.export_folder, filename)

        try:
            # Structură compatibilă cu DBF (nume scurte de coloane, max 10 caractere)
            fieldnames = [
                'NUMINV',      # Număr factură
                'DATAINV',     # Data facturii
                'FURNIZOR',    # Furnizor
                'IDNO',        # IDNO
                'SUMA',        # Suma totală
                'TVA',         # TVA
                'DATALIVRARE', # Data livrării
                'DATAPROC'     # Data procesării
            ]

            row_data = {
                'NUMINV': invoice_data.get('invoice_number', ''),
                'DATAINV': invoice_data.get('invoice_date', ''),
                'FURNIZOR': (invoice_data.get('contractor', '') or '')[:50],  # Limitează lungimea
                'IDNO': invoice_data.get('idno', ''),
                'SUMA': invoice_data.get('total_amount', 0) or 0,
                'TVA': invoice_data.get('vat_amount', 0) or 0,
                'DATALIVRARE': invoice_data.get('delivery_date', ''),
                'DATAPROC': datetime.now().strftime('%Y-%m-%d')
            }

            with open(filepath, 'w', newline='', encoding='cp1251') as f:  # cp1251 pentru compatibilitate
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(row_data)

            logger.info(f"Export CSV/DBF reușit: {filepath}")
            return {
                'success': True,
                'file': filepath,
                'format': 'CSV',
                'note': 'Poate fi importat în Excel sau convertit în DBF'
            }
        except Exception as e:
            logger.error(f"Eroare export CSV: {str(e)}")
            return {'success': False, 'error': str(e)}

    def export_to_true_dbf(self, invoice_data, filename=None):
        """
        Export în DBF real folosind biblioteca dbf
        Necesită: pip install dbf
        """
        try:
            from dbf import Table
        except ImportError:
            return {
                'success': False,
                'error': 'Biblioteca dbf nu este instalată. Rulează: pip install dbf'
            }

        if not filename:
            filename = f"invoice_{invoice_data.get('invoice_number', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dbf"

        filepath = os.path.join(self.export_folder, filename)

        try:
            # Creează tabel DBF
            table = Table(
                filepath,
                'NUMINV C(20); DATAINV D; FURNIZOR C(100); IDNO C(13); SUMA N(15,2); TVA N(15,2); DATALIVRARE D'
            )

            table.open(mode='read-write')

            # Parse date
            try:
                invoice_date = datetime.strptime(invoice_data.get('invoice_date', '2024-01-01'), '%Y-%m-%d').date()
            except:
                invoice_date = datetime(2024, 1, 1).date()

            try:
                delivery_date = datetime.strptime(invoice_data.get('delivery_date', '2024-01-01'), '%Y-%m-%d').date()
            except:
                delivery_date = datetime(2024, 1, 1).date()

            # Adaugă înregistrare
            table.append({
                'NUMINV': invoice_data.get('invoice_number', ''),
                'DATAINV': invoice_date,
                'FURNIZOR': invoice_data.get('contractor', ''),
                'IDNO': invoice_data.get('idno', ''),
                'SUMA': float(invoice_data.get('total_amount', 0) or 0),
                'TVA': float(invoice_data.get('vat_amount', 0) or 0),
                'DATALIVRARE': delivery_date
            })

            table.close()

            logger.info(f"Export DBF real reușit: {filepath}")
            return {'success': True, 'file': filepath, 'format': 'DBF'}
        except Exception as e:
            logger.error(f"Eroare export DBF: {str(e)}")
            return {'success': False, 'error': str(e)}
