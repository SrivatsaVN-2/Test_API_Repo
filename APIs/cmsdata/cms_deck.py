import requests
from tests.androidtv.pages.utility.system_logger import Logger
from typing import Optional, Dict


log_handler = Logger()
log = log_handler.setup_logger("stbt.HomeAPI")

config = {
    "AT": {
        "name": "at-prod",
        "natco": "AUSTRIA",
        "natCo_code": "at",
        "natCo_key": "AnKvxgMw8sLtT3tf4kvW0tQOL4D2PnGr",
        "category_id": "60ac9d5f474da90001121e94",
        "language": 'de'
    },
    "PL": {
        "name": "pl-prod",
        "natco": "POLAND",
        "natCo_code": "pl",
        "natCo_key": "ZEKonTXF53fURQ3RYRIzCERiW5xPakDg",
        "category_id": "60ddb6bcfde35f0001ea4f8d",
        "language": 'pl'
    },
    "HR": {
        "name": "hr-prod",
        "natco": "CROATIA",
        "natCo_code": "hr",
        "natCo_key": "DL2PuVN2Z0RkrGKZruHR5m8o48EYWxNU",
        "category_id": "6125074623d00100013dcf8b",
        "language": 'hr'
    },
    "HU": {
        "name": "hu-prod",
        "natco": "HUNGARY",
        "natCo_code": "hu",
        "natCo_key": "y6QxnROyzlUJuutPzZgI3MKs00D9NOVX",
        "category_id": "5faa10997d77830001cb8af1",
        "language": 'hu'
    },
    "ME": {
        "name": "me-prod",
        "natco": "MONTENEGRO",
        "natCo_code": "me",
        "natCo_key": "Ly6c3k3OrpIuuOzUHHPtFQSUiBDuP1xz",
        "category_id": "63294c81ebaccc0001f53926",
        "language": 'me'
    },
    "MKT": {
        "name": "mk-prod",
        "natco": "MACEDONIA",
        "natCo_code": "mk",
        "natCo_key": "EX4nIiUGCH3OFJyoqm4eNf8O1JtJmfwN",
        "category_id": "62ea6fa8991d2700019b328a",
        "language": 'mk'
    },
}


class CMSDeckAPIClient:

    def __init__(self, base_url: str = None, natco: str = None):
        self.base_url = base_url if base_url else 'https://cms-cdn.yo-digital.com'

    def get_deck_components(self, country: str, size: int = 1, content_type: str = None, category_id: str = None, environment: str = "PRODUCTION") -> Optional[Dict]:
        """
        Fetch deck components from the CMS API.
        """
        log.info(f"Fetching deck components for country: {country}, size: {size}")
        url = f"{self.base_url}/tvdeck/components"
        cout = config[country]
        params = {
            "natco_key": cout['natCo_key'],
            "category_id": cout['category_id'],
            "environment": environment,
            "country": cout['natco']
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            resp = response.json()
            _data = []
            for item in resp.get("items", []):
                _data.append(
                    item['languages'][cout['language']]['title']
                )
            if size > 1:
                return _data[1:size + 1]
            return _data[1]
        except requests.RequestException as e:
            log.info("Error fetching deck components: %s", str(e))
            return None
        
    def get_menu_navigations(self, country: str):
        
        url = f"{self.base_url}/tvdeck/categories"
        cout = config[country]
        params = {
            "natco_key": cout['natCo_key']
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            resp = response.json()
            count_press = 0
            for item in resp.get("items", []):
                if item['is_enabled'] == True:
                    count_press +=1 
            return {
                "button": "Press Right",
                "count": count_press
            }
        except requests.RequestException as e:
            log.info("Error fetching deck components: %s", str(e))
            return None
