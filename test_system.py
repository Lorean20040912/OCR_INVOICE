import unittest
from unittest.mock import MagicMock, patch
from ocr_processor import OCRProcessor
from one_c_integration import OneCIntegration
import os

class TestInvoiceSystem(unittest.TestCase):
    
    @patch('google.cloud.vision.ImageAnnotatorClient')
    def test_ocr_processor_init(self, mock_client):
        processor = OCRProcessor()
        self.assertIsNotNone(processor)
        mock_client.assert_called_once()

    def test_one_c_format(self):
        integration = OneCIntegration()
        invoice_data = {
            'invoice_number': 'FAC123',
            'invoice_date': '2023-10-27',
            'contractor': 'Test Client',
            'idno': '1234567890123',
            'total_amount': '1500.50',
            'delivery_date': '2023-10-28',
            'vat_amount': '300.10'
        }
        formatted = integration._format_for_1c(invoice_data)
        self.assertEqual(formatted['Номер'], 'FAC123')
        self.assertEqual(formatted['СуммаДокумента'], 1500.50)
        self.assertEqual(formatted['Контрагент']['IDNO'], '1234567890123')

    @patch('requests.post')
    def test_one_c_send_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': '1C-REF-001'}
        mock_post.return_value = mock_response
        
        integration = OneCIntegration()
        result = integration.send_invoice({'invoice_number': '123'})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['one_c_id'], '1C-REF-001')

    def test_date_normalization(self):
        processor = OCRProcessor.__new__(OCRProcessor)
        self.assertEqual(processor._normalize_date('27.10.2023'), '2023-10-27')
        self.assertEqual(processor._normalize_date('27/10/23'), '2023-10-27')
        self.assertEqual(processor._normalize_date('01-01-2024'), '2024-01-01')

if __name__ == '__main__':
    unittest.main()
