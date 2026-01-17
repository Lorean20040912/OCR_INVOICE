import requests
from requests.auth import HTTPBasicAuth
import logging
from config import Config

logger = logging.getLogger(__name__)


class OneCIntegration:
    def __init__(self):
        self.api_url = Config.ONE_C_API_URL
        self.auth = HTTPBasicAuth(Config.ONE_C_USERNAME, Config.ONE_C_PASSWORD)

    def send_invoice(self, invoice_data):
        """Trimite factura în 1C prin API"""
        try:
            # Formatează datele pentru 1C
            payload = self._format_for_1c(invoice_data)

            # Trimite request
            response = requests.post(
                self.api_url,
                json=payload,
                auth=self.auth,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            response.raise_for_status()

            result = response.json()
            logger.info(f"Factură trimisă cu succes în 1C: {result}")

            return {
                'success': True,
                'one_c_id': result.get('id') or result.get('Ref'),
                'message': 'Factură înregistrată cu succes'
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Eroare la trimiterea în 1C: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _format_for_1c(self, invoice_data):
        """Formatează datele pentru API-ul 1C - adaptat pentru Moldova"""
        return {
            'Номер': invoice_data.get('invoice_number'),
            'Дата': invoice_data.get('invoice_date'),
            'Контрагент': {
                'Наименование': invoice_data.get('contractor'),
                'IDNO': invoice_data.get('idno')  # IDNO pentru Moldova
            },
            'СуммаДокумента': float(invoice_data.get('total_amount', 0)),
            'ДатаПоставки': invoice_data.get('delivery_date'),
            'НДС': float(invoice_data.get('vat_amount', 0))
        }

    def verify_connection(self):
        """Verifică conexiunea la 1C"""
        try:
            if not self.api_url or '/' not in self.api_url:
                return False
            test_url = self.api_url.rsplit('/', 1)[0] + '/ping'
            response = requests.get(test_url, auth=self.auth, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Eroare la verificarea conexiunii 1C: {str(e)}")
            return False


