import json
from typing import Dict, Optional

from tests.Test_API_Repo.Utilities.Loggers import Logger
from tests.Test_API_Repo.APIs.cmsdata.cms_data_handler import CMSDataHandler

log = Logger().setup_logger("CMS.Test")


class CMSApiClient:
    def __init__(self, interface):
        """
        Initialize CMS API Client using Interface (single source of truth)
        """

        if not interface:
            raise ValueError("Interface instance is required")

        # -----------------------------------
        # 🔹 Core dependency
        # -----------------------------------
        self.interface = interface

        # -----------------------------------
        # 🔹 Get natco from Interface
        # -----------------------------------
        self.natco = (self.interface.natco_config.get("natco") or "").split(" ")[0]

        # -----------------------------------
        # 🔹 CMS handler
        # -----------------------------------
        self.cms_handler = CMSDataHandler()

    # =====================================================
    # 🔹 CMS CONFIG FETCH
    # =====================================================

    def get_cms_config(self) -> Optional[Dict]:
        try:
            return self.cms_handler.process_cms_data(self.natco)
        except Exception as e:
            log.error("Error getting CMS config: %s", str(e))
            return None

    def get_cms_config_for_channel_serial(self) -> Optional[Dict]:
        try:
            return self.cms_handler.process_cms_data_for_channel_serial(self.natco)
        except Exception as e:
            log.error("Error getting CMS serial config: %s", str(e))
            return None

    # =====================================================
    # 🔹 UTILITIES
    # =====================================================

    def print_json_config(self, config: Dict) -> None:
        try:
            formatted_json = json.dumps(config, indent=2)
            for line in formatted_json.split("\n"):
                log.info(line)
        except Exception as e:
            log.error("Error printing JSON config: %s", str(e))

    def validate_config_details(self, config: Dict) -> bool:
        try:
            global_config = config.get("global", {})
            config_instance = global_config.get("configInstance", {})

            if not config_instance:
                log.error("Missing config instance")
                return False

            if not config.get("gdc", {}).get("endpoint"):
                log.error("Missing GDC endpoint")
                return False

            if not config.get("modules", {}).get("settings"):
                log.error("Missing module settings")
                return False

            return True

        except Exception as e:
            log.error("Validation error: %s", str(e))
            return False

    # =====================================================
    # 🔹 CHANNEL SERIAL CONFIG
    # =====================================================

    def get_channel_serial_config(self) -> bool:
        try:
            cms_config = self.get_cms_config_for_channel_serial()

            if cms_config:
                return (
                    cms_config.get("modules", {})
                    .get("mytv", {})
                    .get("myChannels", {})
                    .get("showChannelSerialNumber", False)
                )

            return False

        except Exception as e:
            log.error("Error getting serial config: %s", str(e))
            return False

    # =====================================================
    # 🔹 MOVE TO HOME CONFIG
    # =====================================================

    def get_move_to_home_screen_config(self) -> Dict:
        default_config = {
            "enabled": False,
            "timeout_minutes": 480,
            "action": "player",
        }

        try:
            cms_config = self.get_cms_config_for_channel_serial()

            if cms_config:
                global_config = cms_config.get("global", {})

                enabled = global_config.get(
                    "isMoveToHomeScreenOnStandbyEnabled", False
                )
                timeout = global_config.get(
                    "moveToHomeScreenOnStandbyTimeoutInMinutes", 480
                )

                action = "home" if enabled and timeout <= 2 else "player"

                return {
                    "enabled": enabled,
                    "timeout_minutes": timeout,
                    "action": action,
                }

            return default_config

        except Exception as e:
            log.error("Error getting move-to-home config: %s", str(e))
            return default_config

    # =====================================================
    # 🔹 BOOTSTRAP
    # =====================================================

    def check_bootstrap_type(self, config: Dict) -> str:
        try:
            bootstrap = config.get("modules", {}).get("bootstrap", {})

            cta = bootstrap.get("cta", "")
            launch_cta = bootstrap.get("launchCta", "")

            if "magiotv://player/" in cta or "magiotv://player/" in launch_cta:
                return "player"
            elif "magiotv://home" in cta or "magiotv://home" in launch_cta:
                return "home"

            return "unknown"

        except Exception as e:
            log.error("Bootstrap error: %s", str(e))
            return "unknown"

    # =====================================================
    # 🔹 DECISION ENGINE
    # =====================================================

    def get_cms_navigation_decision(self, scenario: str, return_config=False) -> Dict:

        result = {"scenario": scenario}

        try:
            if scenario == "standby":

                config = self.get_move_to_home_screen_config()

                result["action"] = config["action"]

                if return_config:
                    result["config"] = config

            elif scenario == "restart":

                cms_config = self.get_cms_config()

                if cms_config:
                    bootstrap_type = self.check_bootstrap_type(cms_config)
                    result["action"] = (
                        "home" if bootstrap_type == "home" else "player"
                    )
                else:
                    result["action"] = "player"

            elif scenario == "channel_serial":

                result["action"] = self.get_channel_serial_config()

            else:
                result["error"] = f"Invalid scenario: {scenario}"

            return result

        except Exception as e:
            return {"error": str(e)}

    # =====================================================
    # 🔹 TIMEOUT ADJUSTMENT
    # =====================================================

    def get_adjusted_timeout_for_nfr(
        self, buffer_secs=20, default_secs=180
    ) -> int:

        try:
            config = self.get_move_to_home_screen_config()

            if config.get("enabled") and config.get("timeout_minutes", 0) <= 2:
                return max(30, (config["timeout_minutes"] * 60) - buffer_secs)

            return default_secs

        except Exception as e:
            log.error("Timeout calc error: %s", str(e))
            return default_secs
