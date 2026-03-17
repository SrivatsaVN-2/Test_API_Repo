from typing import Optional, Dict
import json, requests, os

from tests.Test_API_Repo.APIs.dtdl.Interface import Interface
from tests.androidtv.pages.utility.system_logger import Logger

log = Logger().setup_logger("CMS.Data")


NATCO_MAPPING = {
    "ME": "Montenegro",
    "HR": "Croatia",
    "HU": "Hungary",
    "HU SDMC": "Hungary",
    "HU SEI": "Hungary",
    "AT": "Austria",
    "PL": "Poland",
    "MKT": "Macedonia",
}


class CMSDataHandler:
    def __init__(self, interface: Interface):
        """
        API Repo version → fully driven by Interface
        """
        self.interface = interface

        self.base_url = "cms-cdn.yo-digital.com/cdn"
        self.tvdeck_base_url = "cms-cdn.yo-digital.com/tvdeck"

        self.config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "cms_natco_data.json",
        )

        self.original_natco = None

    # =====================================================
    # 🔹 NATCO HELPERS
    # =====================================================

    def _map_natco(self, natco: str) -> str:
        self.original_natco = natco
        return NATCO_MAPPING.get(natco, natco)

    def _get_natco_from_interface(self) -> str:
        """
        Safely get natco from interface
        """
        try:
            return getattr(self.interface.STBConfig, "fdn_natco", "")
        except Exception:
            return ""

    # =====================================================
    # 🔹 CONFIG LOADER
    # =====================================================

    def load_natco_config(self) -> Dict:
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            log.error(f"Failed to load NatCo config: {e}")
            return {}

    # =====================================================
    # 🔹 NATCO DETAILS
    # =====================================================

    def _get_natco_details_from_config(
        self, natco: str, env: str = "production", use_stb_api_key: bool = False
    ) -> Optional[Dict]:
        try:
            config_data = self.load_natco_config()

            mapped_natco = self._map_natco(natco)

            natco_config = next(
                (
                    item
                    for item in config_data
                    if item["natCo"] == mapped_natco
                    and item["env"] == env
                    and "prod-tv" in item["name"]
                ),
                None,
            )

            if not natco_config:
                return None

            api_key = (
                natco_config.get("api_key_tv_stb")
                if use_stb_api_key
                else natco_config.get("api_key_tv")
            ) or natco_config.get("api_key_tv")

            if not api_key:
                return None

            result = natco_config.copy()
            result["api_key"] = api_key

            return result

        except Exception as e:
            log.error(f"Error getting NatCo config: {e}")
            return None

    # =====================================================
    # 🔹 VERSION (FROM INTERFACE ONLY)
    # =====================================================

    def get_version_info(self) -> Optional[str]:
        """
        API repo → NO ADB → use interface data only
        """
        try:
            return getattr(self.interface.STBConfig, "cms_release_info", None)
        except Exception as e:
            log.error(f"Failed to get version: {e}")
            return None

    # =====================================================
    # 🔹 CMS FETCH
    # =====================================================

    def get_cms_config(self, api_key: str, version: str) -> Optional[Dict]:
        try:
            url = f"https://{self.base_url}/{api_key}/{version}/config.json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.error(f"CMS fetch failed: {e}")
            return None

    # =====================================================
    # 🔹 MAIN ENTRY
    # =====================================================

    def process_cms_data(self, natco: str, env: str = "production") -> Optional[Dict]:
        try:
            natco_details = self._get_natco_details_from_config(natco, env)
            if not natco_details:
                log.error(f"No config for NatCo: {natco}")
                return None

            version = self.get_version_info()
            if not version:
                log.error("Missing CMS version")
                return None

            config = self.get_cms_config(natco_details["api_key"], version)

            return config

        except Exception as e:
            log.error(f"CMS processing failed: {e}")
            return None

    # =====================================================
    # 🔹 CHANNEL SERIAL CONFIG
    # =====================================================

    def process_cms_data_for_channel_serial(
        self, natco: str, env: str = "production"
    ) -> Optional[Dict]:
        return self.process_cms_data(natco, env)
