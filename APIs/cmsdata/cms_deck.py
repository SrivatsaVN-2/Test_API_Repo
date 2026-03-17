import requests
from typing import Optional, Dict

from tests.androidtv.pages.utility.system_logger import Logger

log = Logger().setup_logger("API.CMSDeck")


class CMSDeckAPIClient:
    """
    API Repo version → fully driven by Interface
    """

    def __init__(self, interface, base_url: str = None):
        if not interface:
            raise ValueError("Interface is required")

        self.interface = interface
        self.base_url = base_url or "https://cms-cdn.yo-digital.com"

        # Pull natco info from Interface
        self.stb_config = interface.STBConfig
        self.natco = getattr(self.stb_config, "fdn_natco", "")
        self.language = interface.language

    # =====================================================
    # 🔹 INTERNAL HELPERS
    # =====================================================

    def _get_natco_config(self) -> Dict:
        """
        Fetch natco config from interface
        """
        natco_config = self.interface.natco_config

        if not natco_config:
            raise ValueError("natco_config missing in Interface")

        return natco_config

    # =====================================================
    # 🔹 DECK COMPONENTS
    # =====================================================

    def get_deck_components(
        self,
        size: int = 1,
        content_type: str = None,
        category_id: str = None,
        environment: str = "PRODUCTION",
    ) -> Optional[Dict]:
        """
        Fetch deck components using Interface-driven data
        """

        try:
            natco_config = self._get_natco_config()

            url = f"{self.base_url}/tvdeck/components"

            params = {
                "natco_key": natco_config.get("natco_key"),
                "category_id": category_id or natco_config.get("category_id"),
                "environment": environment,
                "country": natco_config.get("natco"),
            }

            log.info(f"Fetching deck components → {params}")

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            resp = response.json()

            titles = []
            for item in resp.get("items", []):
                try:
                    lang = natco_config.get("language", self.language)
                    title = item.get("languages", {}).get(lang, {}).get("title")
                    if title:
                        titles.append(title)
                except Exception:
                    continue

            if not titles:
                return None

            return titles[1 : size + 1] if size > 1 else titles[1]

        except Exception as e:
            log.error(f"Error fetching deck components: {e}")
            return None

    # =====================================================
    # 🔹 MENU NAVIGATION
    # =====================================================

    def get_menu_navigations(self) -> Optional[Dict]:
        """
        Get navigation steps based on CMS categories
        """

        try:
            natco_config = self._get_natco_config()

            url = f"{self.base_url}/tvdeck/categories"

            params = {
                "natco_key": natco_config.get("natco_key")
            }

            log.info(f"Fetching menu navigation → {params}")

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            resp = response.json()

            count_press = sum(
                1 for item in resp.get("items", []) if item.get("is_enabled")
            )

            return {
                "button": "Press Right",
                "count": count_press,
            }

        except Exception as e:
            log.error(f"Error fetching menu navigation: {e}")
            return None
