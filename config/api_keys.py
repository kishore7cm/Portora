import os
from dotenv import load_dotenv

load_dotenv()

def load_keys():
    return {
        "api_key": os.getenv('APCA_API_KEY_ID'),
        "secret_key": os.getenv('APCA_API_SECRET_KEY'),
        "base_url": os.getenv("APCA_API_BASE_URL"),
        "twelve_api_key": os.getenv('TWELVE_DATA_API_KEY'),
        "openai_api_key":os.getenv('OPENAI_API_KEY')
    }