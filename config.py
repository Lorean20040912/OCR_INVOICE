import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Google Cloud Vision API
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

    # 1C API Configuration
    ONE_C_API_URL = os.getenv('ONE_C_API_URL')
    ONE_C_USERNAME = os.getenv('ONE_C_USERNAME')
    ONE_C_PASSWORD = os.getenv('ONE_C_PASSWORD')

    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}