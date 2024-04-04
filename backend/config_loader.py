import os
from dotenv import load_dotenv
import json

class AppConfig:
    def __init__(self):
        load_dotenv()

        self.astra_db_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.astra_db_id = os.getenv("ASTRA_DB_ID")

        self.load_from_json('config.json')

    def load_from_json(self, filepath):
        try:
            with open(filepath) as config_file:
                json_config = json.load(config_file)
                for key, value in json_config.items():
                    setattr(self, key, value)
        except FileNotFoundError:
            print(f"{filepath} not found, skipping file-based configuration.")
