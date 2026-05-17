import os
import re
import json
import time
import logging
import urllib.request
from typing import Optional, Dict

# pytesseract este opțional
try:
    import pytesseract  # type: ignore
except Exception:
    pytesseract = None

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Motoare OCR suportate:
      - azure (implici dacă AZURE_VISION_ENDPOINT + AZURE_VISION_KEY sunt setate)
      - tesseract (fallback dacă este instalat)
      - mock (dacă nu e disponibil nimic)
    OpenCV/Numpy NU sunt importate global; se folosesc doar dacă există și doar la nevoie (lazy).
    """

    def __init__(self, engine: Optional[str] = None):
        self.azure_endpoint = os.getenv("AZURE_VISION_ENDPOINT")
        self.azure_key = os.getenv("AZURE_VISION_KEY")
        self.compare_all_default = os.getenv("OCR_COMPARE_ALL", "0").lower() in ("1", "true", "yes")

        if engine:
            self.primary_engine = engine.lower()
        else:
            if self.azure_endpoint and self.azure_key:
                self.primary_engine = "azure"
            elif pytesseract is not None:
                self.primary_engine = "tesseract"
            else:
                self.primary_engine = "mock"

        # Config Tesseract (Windows path implicit, dacă există)
        if pytesseract is not None and os.name == "nt":
            default_path = os.environ.get("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
            if os.path.exists(default_path):
                try:
                    pytesseract.pytesseract.tesseract_cmd = default_path
                except Exception:
                    pass

        self.tesseract_config = "--psm 6 --oem 3 -l ron"

    def process_invoice(self, file_path: str, compare_all: Optional[bool] = None) -> Optional[dict]:
        compare = self.compare_all_default if compare_all is None else compare_all

        text = self._run_engine(self.primary_engine, file_path)
        if not text:
            logger.warning("Motorul principal a returnat text gol; folosesc date mock pentru continuitate")
            result = self._generate_mock_data(file_path)
            result["ocr_engine"] = "mock"
            if compare:
                result["comparisons"] = self._collect_comparisons(file_path, include_primary=True)
            return result

        result = self.extract_invoice_data(text)
        result["raw_text"] = text
        result["ocr_engine"] = self.primary_engine

        if compare:
            result["comparisons"] = self._collect_comparisons(file_path, include_primary=False)

        return result

    # ==== RULARE MOTOARE ====
    def _run_engine(self, engine: str, file_path: str) -> str:
        try:
            eng = engine.lower()
            if eng == "azure":
                return self._azure_read(file_path)
            if eng == "tesseract":
                return self._tesseract_read(file_path)
            return ""
        except Exception as e:
            logger.error(f"Eroare motor '{engine}': {e}")
            return ""

    def _azure_read(self, file_path: str) -> str:
        if not (self.azure_endpoint and self.azure_key):
            return ""

        url = self.azure_endpoint.rstrip("/") + "/vision/v3.2/read/analyze"
        with open(file_path, "rb") as f:
            data = f.read()

        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Ocp-Apim-Subscription-Key": self.azure_key,
                "Content-Type": "application/octet-stream",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            op_loc = resp.headers.get("Operation-Location") or resp.headers.get("operation-location")

        if not op_loc:
            return ""

        deadline = time.time() + 60
        status = "running"
        last_payload = None
        while time.time() < deadline and status in ("running", "notstarted", "notStarted"):
            time.sleep(1.0)
            get_req = urllib.request.Request(
                op_loc,
                headers={"Ocp-Apim-Subscription-Key": self.azure_key},
                method="GET",
            )
            with urllib.request.urlopen(get_req, timeout=30) as g:
                last_payload = json.loads(g.read().decode("utf-8"))
            status = (last_payload.get("status") or "").lower()
            if status == "succeeded":
                analyze = last_payload.get("analyzeResult", {}) or {}
                if isinstance(analyze.get("content"), str):
                    return analyze["content"]
                lines_out = []
                for page in analyze.get("readResults", []):
                    for line in page.get("lines", []):
                        txt = line.get("text")
                        if txt:
                            lines_out.append(txt)
                for page in analyze.get("pages", []):
                    for line in page.get("lines", []):
                        txt = line.get("content") or line.get("text")
                        if txt:
                            lines_out.append(txt)
                return "\n".join(lines_out)

            if status == "failed":
                break

        return ""

    def _tesseract_read(self, file_path: str) -> str:
        if pytesseract is None:
            return ""

        # Dacă avem PIL, îl folosim ca să evităm complet OpenCV/NumPy
        try:
            from PIL import Image  # type: ignore
        except Exception:
            Image = None

        if Image is not None:
            try:
                with Image.open(file_path) as img:
                    # Convertim în L (grayscale) pentru rezultat mai stabil
                    img = img.convert("L")
                    txt = pytesseract.image_to_string(img, config=self.tesseract_config)
                    return txt.strip()
            except Exception:
                return ""

        # Dacă nu există PIL, încercăm lazy OpenCV NUMAI dacă e instalat corect
        try:
            import cv2  # type: ignore
            img = cv2.imread(file_path)
            if img is None:
                return ""
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            txt = pytesseract.image_to_string(gray, config=self.tesseract_config)
            return txt.strip()
        except Exception:
            return ""

    # ==== COMPARAȚIE ====
    def _collect_comparisons(self, file_path: str, include_primary: bool) -> Dict[str, dict]:
        engines = ["azure", "tesseract"]
        out: Dict[str, dict] = {}
        for eng in engines:
            if not include_primary and eng == self.primary_engine:
                continue
            txt = self._run_engine(eng, file_path)
            if not txt:
                out[eng] = {"available": False}
                continue
            data = self.extract_invoice_data(txt)
            out[eng] = {
                "available": True,
                "ocr_engine": eng,
                "confidence": data.get("confidence", 0.0),
                "invoice_number": data.get("invoice_number"),
                "invoice_date": data.get("invoice_date"),
                "idno": data.get("idno"),
                "total_amount": data.get("total_amount"),
            }
        return out

    # ==== EXTRAGERE DATE ====
    def extract_invoice_data(self, text: str) -> dict:
        data = {
            "invoice_number": None,
            "invoice_date": None,
            "contractor": None,
            "idno": None,
            "total_amount": None,
            "delivery_date": None,
            "vat_amount": None,
            "confidence": 0.0,
        }
        try:
            inv_patterns = [
                r"(?:FACT|Factur|Nr\.?|Invoice|#|Factură)\s*[-:]*\s*([A-Z0-9\-/]+)",
                r"(?:inv|invoice)[\s\-:]*(\d+[-/]\d+)",
                r"(?:factur[aă]|nr)[\s\-:]*(\d+)",
                r"([A-Z]{1,3}\d{2,4}[/-]\d{1,6})",
                r"(\d{3,}[-/]\d{2,})",
            ]
            for p in inv_patterns:
                m = re.search(p, text, re.IGNORECASE)
                if m:
                    data["invoice_number"] = m.group(1)
                    break

            date_patterns = [
                r"(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})",
                r"(\d{4}[\.\/\-]\d{1,2}[\.\/\-]\d{1,2})",
            ]
            for p in date_patterns:
                m = re.search(p, text)
                if m:
                    data["invoice_date"] = self._normalize_date(m.group(1))
                    break

            contractor_patterns = [
                r"(?:s\.?r\.?l\.?|srl|sa)\s+([a-zA-ZĂÂÎȘȚăâîșț\s]{3,50})",
                r"([A-ZĂÂÎȘȚ][a-zA-ZĂÂÎȘȚăâîșț\s]{3,50})\s+(?:s\.?r\.?l\.?|srl|sa)",
                r"(?:furnizor|vânzător)[:\s]+([a-zA-ZĂÂÎȘȚăâîșț\s]{3,50})",
            ]
            for p in contractor_patterns:
                m = re.search(p, text, re.IGNORECASE)
                if m:
                    data["contractor"] = m.group(1).strip()
                    break

            m = re.search(r"\b(\d{13})\b", text)
            if m:
                data["idno"] = m.group(1)

            amt_patterns = [
                r"(?:total(?:\s+general)?|suma|amount)[:\s]+([\d\.\, ]+)",
                r"\b(\d+[.,]\d{2})\s*(?:MDL|RON|EUR|USD|LEI)\b",
            ]
            for p in amt_patterns:
                m = re.search(p, text, re.IGNORECASE | re.MULTILINE)
                if m:
                    val = m.group(1).replace(" ", "").replace(",", ".")
                    try:
                        data["total_amount"] = float(val)
                    except Exception:
                        data["total_amount"] = val
                    break

            filled = sum(1 for k, v in data.items() if k != "confidence" and v not in (None, ""))
            data["confidence"] = filled / (len(data) - 1)
        except Exception as e:
            logger.error(f"Eroare la extragerea datelor: {e}")
        return data

    def _normalize_date(self, date_str: str) -> str:
        s = date_str.replace("/", "-").replace(".", "-").strip()
        parts = s.split("-")
        if len(parts) == 3:
            a, b, c = parts
            if len(a) == 4:
                year, month, day = a, b, c
            else:
                day, month, year = a, b, c
                if len(year) == 2:
                    year = ("20" if int(year) < 50 else "19") + year
            return f"{year.zfill(4)}-{month.zfill(2)}-{day.zfill(2)}"
        return s

    def _generate_mock_data(self, file_path: str) -> dict:
        from datetime import datetime
        import random
        return {
            "invoice_number": f"FACT-{datetime.now().year}-{random.randint(1000, 9999)}",
            "invoice_date": datetime.now().strftime("%Y-%m-%d"),
            "contractor": "SRL COMPANIA EXEMPLU",
            "idno": f"{random.randint(10**12, 10**13 - 1)}",
            "total_amount": round(random.uniform(100, 5000), 2),
            "delivery_date": datetime.now().strftime("%Y-%m-%d"),
            "vat_amount": round(random.uniform(20, 500), 2),
            "confidence": 0.5,
        }