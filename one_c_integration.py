import logging
import requests
from config import Config

logger = logging.getLogger(__name__)


class OneCIntegration:
    def __init__(self):
        self.base_url = (Config.ONE_C_API_URL or "").rstrip("/")
        self.username = Config.ONE_C_USERNAME
        self.password = Config.ONE_C_PASSWORD

    def _auth(self):
        return (self.username, self.password) if self.username and self.password else None

    def verify_connection(self) -> bool:
        """Verifică endpoint-ul /ping (dacă există)."""
        try:
            if not self.base_url:
                return False
            url = f"{self.base_url}/ping"
            resp = requests.get(url, auth=self._auth(), timeout=10)
            return resp.status_code == 200
        except Exception as e:
            logger.warning(f"1C ping failed: {e}")
            return False

    def send_invoice(self, invoice_data: dict) -> dict:
        """Trimite factura la 1C. Returnează dict cu cheile: success, one_c_id (opțional), message/error."""
        try:
            if not self.base_url:
                return {'success': False, 'error': 'ONE_C_API_URL nu este configurat'}

            # Construiește URL-ul pentru endpoint-ul de facturi
            url = f"{self.base_url}/invoices"

            # Payload generic; adaptează dacă API-ul 1C așteaptă alt format
            payload = {
                'invoice_number': invoice_data.get('invoice_number'),
                'invoice_date': invoice_data.get('invoice_date'),
                'contractor': invoice_data.get('contractor'),
                'idno': invoice_data.get('idno'),
                'total_amount': invoice_data.get('total_amount'),
                'delivery_date': invoice_data.get('delivery_date'),
                'vat_amount': invoice_data.get('vat_amount'),
                'confidence': invoice_data.get('confidence'),
            }

            resp = requests.post(url, json=payload, auth=self._auth(), timeout=30)
            if resp.status_code >= 200 and resp.status_code < 300:
                data = {}
                try:
                    data = resp.json()
                except Exception:
                    pass
                return {
                    'success': True,
                    'one_c_id': data.get('id') or data.get('Ref') or data.get('ref'),
                    'message': 'Trimis cu succes în 1C'
                }

            return {
                'success': False,
                'error': f"Eroare API: {resp.status_code} - {resp.text[:300]}"
            }

        except requests.RequestException as e:
            logger.error(f"Eroare conexiune 1C: {e}")
            return {'success': False, 'error': f'Conexiune eșuată: {e}'}
        except Exception as e:
            logger.error(f"Eroare generală 1C: {e}")
            return {'success': False, 'error': str(e)}


