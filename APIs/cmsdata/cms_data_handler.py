from typing import Optional, Dict
import json, requests, os

"""
from tests.androidtv.pages.adb.adb import ADBCommand
from tests.androidtv.pages.utility.system_logger import Logger
from tests.androidtv.pages.utility.stbconfig import STBConfig
"""
from APIs.dtdl.Interface import Interface

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
    def __init__(self):
        self.base_url = "cms-cdn.yo-digital.com/cdn"
        self.tvdeck_base_url = "cms-cdn.yo-digital.com/tvdeck"
        self.adb_command = ADBCommand()
        self.config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "cms_natco_data.json"
        )
        self.original_natco = None
        self.interface = Interface()

    def _map_natco(self, natco: str) -> str:
        self.original_natco = natco
        mapped_natco = NATCO_MAPPING.get(natco)
        if mapped_natco:
            return mapped_natco
        log.warning("No mapping found for NatCo: %s", natco)
        return natco

    def load_natco_config(self) -> Dict:
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            log.error(
                "Failed to load NatCo config from %s: %s", self.config_path, str(e)
            )
            return {}

    def _get_natco_details_from_config(
        self, natco: str, env: str = "production", use_stb_api_key: bool = False
    ) -> Optional[Dict]:
        try:
            self.original_natco = None
            config_data = self.load_natco_config()

            if natco == "HU":
                if hasattr(Interface.STBConfig, "fdn_natco") and Interface.STBConfig.fdn_natco in [
                    "HU SDMC",
                    "HU SEI",
                ]:
                    self.original_natco = Interface.STBConfig.fdn_natco
                else:
                    adb_info = self.adb_command.collect_version_info("HU SDMC")
                    if adb_info and adb_info[0]:
                        self.original_natco = "HU SDMC"
                    else:
                        adb_info = self.adb_command.collect_version_info("HU SEI")
                        if adb_info and adb_info[0]:
                            self.original_natco = "HU SEI"
                if self.original_natco:
                    config = next(
                        (
                            item
                            for item in config_data
                            if item["name"] == "hu-prod-tv"
                            and item["env"] == "production"
                        ),
                        None,
                    )
                    if config:
                        api_key = (
                            config.get("api_key_tv_stb") or config.get("api_key_tv")
                            if use_stb_api_key
                            else config.get("api_key_tv")
                            or config.get("api_key_tv_stb")
                        )
                        if api_key:
                            result = config.copy()
                            result["api_key"] = api_key
                            return result
            else:
                mapped_natco = self._map_natco(natco)
                natco_config = next(
                    (
                        item
                        for item in config_data
                        if item["natCo"] == mapped_natco
                        and item["env"] == env
                        and "standalone" not in item["name"]
                        and "prod-tv" in item["name"]
                    ),
                    None,
                )
                if natco_config:
                    self.original_natco = natco
                    api_key = (
                        natco_config.get("api_key_tv_stb")
                        or natco_config.get("api_key_tv")
                        if use_stb_api_key
                        else natco_config.get("api_key_tv")
                        or natco_config.get("api_key_tv_stb")
                    )
                    if api_key:
                        result = natco_config.copy()
                        result["api_key"] = api_key
                        return result
            return None
        except Exception as e:
            log.error("Error getting NatCo details from config: %s", str(e))
            return None

    def get_natco_details_for_channel_serial(
        self, natco: str, env: str = "production"
    ) -> Optional[Dict]:
        try:
            return self._get_natco_details_from_config(
                natco, env, use_stb_api_key=False
            )
        except Exception as e:
            log.error(
                "Error getting NatCo details for showChannelSerialNumber: %s", str(e)
            )
            return None

    def get_natco_details_for_bootstrap(
        self, natco: str, env: str = "production"
    ) -> Optional[Dict]:
        try:
            return self._get_natco_details_from_config(natco, env, use_stb_api_key=True)
        except Exception as e:
            log.error("Error getting NatCo details for bootstrap: %s", str(e))
            return None

    def get_natco_details(self, natco: str, env: str = "production") -> Optional[Dict]:
        try:
            return self.get_natco_details_for_bootstrap(natco, env)
        except Exception as e:
            log.error("Error getting general NatCo details: %s", str(e))
            return None

    def get_cms_config(self, api_key: str, version: str) -> Optional[Dict]:
        try:
            url = f"https://{self.base_url}/{api_key}/{version}/config.json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error("Failed to fetch CMS config: %s", str(e))
            return None

    def get_tvdeck_components(
        self,
        natco_key: str,
        category_id: str,
        environment: str = "PRODUCTION",
        country: str = None,
    ) -> Optional[Dict]:
        try:
            url = f"https://{self.tvdeck_base_url}/components"
            params = {
                "natco_key": natco_key,
                "category_id": category_id,
                "environment": environment,
                "country": country.upper() if country else "",
            }
            params = {k: v for k, v in params.items() if v}
            log.info(
                "Fetching TV deck components from: %s with params: %s", url, params
            )
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            log.info(
                "Successfully fetched TV deck components for %s", country or natco_key
            )
            return data
        except requests.exceptions.RequestException as e:
            log.error("Failed to fetch TV deck components: %s", str(e))
            return None

    def get_tvdeck_components_for_natco(
        self, natco: str, env: str = "production"
    ) -> Optional[Dict]:
        try:
            natco_details = self._get_natco_details_from_config(natco, env)
            if not natco_details:
                log.error("No configuration found for NatCo: %s", natco)
                return None
            natco_key = natco_details.get("natco_key")
            category_id = natco_details.get("category_id")
            if not natco_key or not category_id:
                log.warning("TV deck configuration missing for NatCo: %s", natco)
                return None
            environment = "PRODUCTION" if env == "production" else "STAGING"
            country = natco_details.get("natCo", natco)
            return self.get_tvdeck_components(
                natco_key, category_id, environment, country
            )
        except Exception as e:
            log.error(
                "Error getting TV deck components for NatCo %s: %s", natco, str(e)
            )
            return None

    def validate_config(self, config: Dict) -> bool:
        required_sections = [
            "gdc",
            "modules",
            "global",
            "version",
            "translationVersion",
        ]
        try:
            return all(section in config for section in required_sections)
        except Exception as e:
            log.error("Config validation failed: %s", str(e))
            return False

    def validate_tvdeck_components(self, components: Dict) -> bool:
        try:
            if not isinstance(components, dict):
                return False
            items = components.get("items", [])
            if not isinstance(items, list):
                return False
            return True
        except Exception as e:
            log.error("TV deck components validation failed: %s", str(e))
            return False

    def get_version_info(self, natco: str) -> Optional[str]:
        """Get One TV version information with version correction"""
        try:
            if hasattr(Interface.STBConfig, "cms_release_info"):
                version = Interface.STBConfig.cms_release_info
            else:
                natco_for_version = (
                    self.original_natco if self.original_natco else natco
                )
                result = self.adb_command.collect_version_info(natco_for_version)
                version = result[2] if result and len(result) > 2 else None

            return version
        except Exception as e:
            log.error("Failed to get version info: %s", str(e))
            return None

    def process_cms_data(self, natco: str, env: str = "production") -> Optional[Dict]:
        try:
            natco_details = self.get_natco_details(natco, env)
            if not natco_details:
                log.error("No configuration found for NatCo: %s", natco)
                return None
            version = self.get_version_info(natco)
            if not version:
                log.error("Failed to get version information")
                return None
            config = self.get_cms_config(natco_details["api_key"], version)
            if not config:
                return None
            if not self.validate_config(config):
                log.error("Invalid configuration structure")
                return None
            return config
        except Exception as e:
            log.error("Error processing CMS data: %s", str(e))
            return None

    def process_cms_data_for_channel_serial(
        self, natco: str, env: str = "production"
    ) -> Optional[Dict]:
        try:
            natco_details = self.get_natco_details_for_channel_serial(natco, env)
            if not natco_details:
                log.error(
                    "No configuration found for showChannelSerialNumber for NatCo: %s",
                    natco,
                )
                return None
            version = self.get_version_info(natco)
            if not version:
                log.error(
                    "Failed to get version information for showChannelSerialNumber"
                )
                return None
            config = self.get_cms_config(natco_details["api_key"], version)
            if not config:
                return None
            if not self.validate_config(config):
                log.error("Invalid configuration structure for showChannelSerialNumber")
                return None
            return config
        except Exception as e:
            log.error(
                "Error processing CMS data for showChannelSerialNumber: %s", str(e)
            )
            return None

    def process_tvdeck_data(
        self, natco: str, env: str = "production"
    ) -> Optional[Dict]:
        try:
            components = self.get_tvdeck_components_for_natco(natco, env)
            if not components:
                return None
            if not self.validate_tvdeck_components(components):
                log.error("Invalid TV deck components structure")
                return None
            return components
        except Exception as e:
            log.error("Error processing TV deck data: %s", str(e))
            return None
