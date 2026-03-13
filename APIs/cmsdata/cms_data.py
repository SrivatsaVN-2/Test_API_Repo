import json
from typing import Dict, Optional
from tests.androidtv.pages.utility.system_logger import Logger
from tests.androidtv.pages.utility.utils import Utils
from tests.androidtv.pages.utility.stbconfig import STBConfig
from tests.androidtv.api.cmsdata.cms_data_handler import CMSDataHandler

# Initialize logger
log = Logger().setup_logger("CMS.Test")


class CMSApiClient:
    def __init__(self, config_manager=None, natco: str = None):
        """Initialize CMS API Client"""
        self.config_manager = config_manager  # Can be None now
        self.natco = natco
        self.cms_handler = CMSDataHandler()

    def get_cms_config(self) -> Optional[Dict]:
        """
        Get CMS configuration data - uses STB config file for bootstrap

        Returns:
            Optional[Dict]: CMS configuration if successful
        """
        try:
            return self.cms_handler.process_cms_data(self.natco)
        except Exception as e:
            log.error("Error getting CMS config: %s", str(e))
            return None

    def get_cms_config_for_channel_serial(self) -> Optional[Dict]:
        """
        Get CMS configuration data specifically for showChannelSerialNumber - uses TV config file

        Returns:
            Optional[Dict]: CMS configuration if successful
        """
        try:
            return self.cms_handler.process_cms_data_for_channel_serial(self.natco)
        except Exception as e:
            log.error(
                "Error getting CMS config for showChannelSerialNumber: %s", str(e)
            )
            return None

    def print_json_config(self, config: Dict) -> None:
        """
        Print configuration as formatted JSON

        Args:
            config (Dict): CMS configuration
        """
        try:
            formatted_json = json.dumps(config, indent=2)
            for line in formatted_json.split("\n"):
                log.info(line)
        except Exception as e:
            log.error("Error printing JSON config: %s", str(e))

    def validate_config_details(self, config: Dict) -> bool:
        """
        Validate configuration details

        Args:
            config (Dict): CMS configuration

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Validate version
            global_config = config.get("global", {})
            config_instance = global_config.get("configInstance", {})

            if not config_instance:
                log.error("Missing config instance")
                return False

            # Validate GDC settings
            gdc = config.get("gdc", {})
            if not gdc.get("endpoint"):
                log.error("Missing GDC endpoint configuration")
                return False

            # Validate modules
            modules = config.get("modules", {})
            if not modules.get("settings"):
                log.error("Missing module settings")
                return False

            return True

        except Exception as e:
            log.error("Error validating config: %s", str(e))
            return False

    def get_channel_serial_config(self) -> bool:
        """
        Get channel serial number configuration from CMS - uses TV config file

        Returns:
            bool: True if serial numbers should be shown, False otherwise
        """
        try:
            cms_config = self.get_cms_config_for_channel_serial()  # Uses TV config
            if cms_config:
                show_serial = (
                    cms_config.get("modules", {})
                    .get("mytv", {})
                    .get("myChannels", {})
                    .get("showChannelSerialNumber", False)
                )
                return show_serial
            return False
        except Exception as e:
            log.error("Error getting serial number config: %s", str(e))
            return False

    def get_move_to_home_screen_config(self) -> Dict:
        """
        Get move to home screen configuration from CMS - uses TV config file

        Returns:
            Dict: Configuration with 'enabled' and 'timeout_minutes' keys
        """
        default_config = {
            "enabled": False,
            "timeout_minutes": 480,
            "action": "player",
        }

        try:
            cms_config = self.get_cms_config_for_channel_serial()  # Uses TV config
            if cms_config:
                global_config = cms_config.get("global", {})

                is_enabled = global_config.get(
                    "isMoveToHomeScreenOnStandbyEnabled", False
                )
                timeout_minutes = global_config.get(
                    "moveToHomeScreenOnStandbyTimeoutInMinutes", 480
                )

                # Determine action based on configuration and timeout
                if not is_enabled:
                    action = "player"
                elif timeout_minutes > 2:
                    action = "player"
                else:
                    action = "home"

                config = {
                    "enabled": is_enabled,
                    "timeout_minutes": timeout_minutes,
                    "action": action,
                }

                return config

            log.warning("No CMS config found, returning default configuration")
            return default_config

        except Exception as e:
            log.error("Error getting move to home screen config: %s", str(e))
            return default_config

    def check_bootstrap_type(self, config: Dict) -> str:
        """
        Checks the bootstrap type from the CMS configuration

        Args:
            config (Dict): CMS configuration

        Returns:
            str: Bootstrap type, either "player" or "home"
        """
        try:
            # Get the bootstrap configuration
            bootstrap = config.get("modules", {}).get("bootstrap", {})
            cta = bootstrap.get("cta", "")
            launch_cta = bootstrap.get("launchCta", "")

            # Check the bootstrap type
            if "magiotv://player/" in cta or "magiotv://player/" in launch_cta:
                return "player"
            elif "magiotv://home" in cta or "magiotv://home" in launch_cta:
                return "home"
            else:
                return "unknown"

        except Exception as e:
            log.error("Error checking bootstrap: %s", str(e))
            return "unknown"

    def get_cms_navigation_decision(
        self, scenario: str, return_config: bool = False
    ) -> Dict:
        """
        Single parametrized function to get navigation decisions for all CMS scenarios

        Args:
            scenario (str): Type of scenario - "standby", "restart", "channel_serial"
            return_config (bool): If True, returns detailed config info along with decision

        Returns:
            Dict: Contains 'action', 'scenario', and optionally detailed config information
        """
        result = {"scenario": scenario, "config_used": None}

        try:
            if scenario == "standby":
                # Use standby logic with move-to-home configuration (api_key_tv)
                config = self.get_move_to_home_screen_config()
                result["config_used"] = "move_to_home_screen" if return_config else None

                if not config["enabled"]:
                    result["action"] = "player"
                elif config["timeout_minutes"] > 2:
                    # If timeout is greater than 2 minutes, return player
                    result["action"] = "player"
                else:
                    # Feature is enabled and timeout is 2 minutes or less, return home
                    result["action"] = "home"

                if return_config:
                    result["config_details"] = config

            elif scenario == "restart":
                # Use bootstrap logic (api_key_tv_stb)
                cms_config = self.get_cms_config()
                result["config_used"] = "bootstrap" if return_config else None

                if cms_config:
                    bootstrap_type = self.check_bootstrap_type(cms_config)
                    if bootstrap_type == "home":
                        result["action"] = "home"
                    elif bootstrap_type == "player":
                        result["action"] = "player"
                    else:
                        result["action"] = "player"

                    if return_config:
                        bootstrap_config = cms_config.get("modules", {}).get(
                            "bootstrap", {}
                        )
                        result["config_details"] = {
                            "bootstrap_type": bootstrap_type,
                            "cta": bootstrap_config.get("cta", ""),
                            "launchCta": bootstrap_config.get("launchCta", ""),
                        }
                else:
                    result["action"] = "player"

            elif scenario == "channel_serial":
                # Use channel serial configuration (api_key_tv) - return actual boolean value
                show_serial = self.get_channel_serial_config()
                result["action"] = show_serial  # Return actual boolean value
                result["config_used"] = "channel_serial" if return_config else None

                if return_config:
                    result["config_details"] = {"showChannelSerialNumber": show_serial}

            else:
                # Invalid scenario
                log.error(
                    "Invalid scenario: %s. Valid scenarios are: standby, restart, channel_serial",
                    scenario,
                )
                result["error"] = f"Invalid scenario: {scenario}"

            return result

        except Exception as e:
            result["error"] = str(e)
            return result

    def get_adjusted_timeout_for_nfr(
        self, buffer_secs: int = 20, default_secs: int = 180
    ) -> int:
        """
        Returns a reduced timeout for NFR based on CMS move-to-home configuration.

        If the CMS timeout is enabled and set to 2 minutes or less, this function
        returns (CMS timeout in seconds - buffer). Otherwise, returns a default timeout.

        Args:
            buffer_secs (int): Seconds to subtract from CMS timeout for early detection.
            default_secs (int): Fallback timeout if CMS config is missing or invalid.

        Returns:
            int: Adjusted timeout in seconds
        """
        try:
            config = self.get_move_to_home_screen_config()
            if config.get("enabled"):
                timeout_minutes = config.get("timeout_minutes", 0)
                if timeout_minutes <= 2:
                    adjusted = max(30, (timeout_minutes * 60) - buffer_secs)
                    log.info(
                        "Adjusting timeout based on CMS config: %s seconds", adjusted
                    )
                    return adjusted
            return default_secs
        except Exception as e:
            log.error("Error determining adjusted timeout: %s", str(e))
            return default_secs


def test_cms_configuration():
    """
    Test CMS configuration for current device only and return enabled rail titles
    """
    log.info("=== Testing Current Device CMS Configuration ===")

    try:
        Utils().collect_and_validate_device_info()
        # Get full NatCo name including SDMC/SEI variants
        full_natco = STBConfig().fdn_natco
        log.info("Detected device NatCo: %s", full_natco)

        # For API calls, use base natco (split on space to handle HU SDMC/HU SEI)
        api_natco = full_natco.split(" ", maxsplit=1)[0]
        cms_api_client = CMSApiClient(config_manager=None, natco=api_natco)

        # Debug information
        log.info("API NatCo: %s", api_natco)
        if hasattr(STBConfig, "cms_release_info"):
            log.info("CMS Release Info: %s", STBConfig.cms_release_info)

        # Try to get natco details first for debugging
        try:
            natco_details = cms_api_client.cms_handler.get_natco_details(api_natco)
            version = cms_api_client.cms_handler.get_version_info(api_natco)

            if natco_details and version:
                test_url = f"https://cms-cdn.yo-digital.com/cdn/{natco_details['api_key']}/{version}/config.json"
                log.info("Trying URL: %s", test_url)

        except Exception as debug_e:
            log.error("Debug info error: %s", str(debug_e))

        # Test CMS configuration
        cms_config = cms_api_client.get_cms_config()

        if cms_config:
            cms_api_client.validate_config_details(cms_config)

            log.info("--- Standby Scenario ---")
            standby_result = cms_api_client.get_cms_navigation_decision("standby")
            log.info("Standby: %s", standby_result["action"])

            log.info("--- Restart Scenario ---")
            restart_result = cms_api_client.get_cms_navigation_decision("restart")
            log.info("Restart: %s", restart_result["action"])

            log.info("--- Channel Serial Scenario ---")
            channel_serial_result = cms_api_client.get_cms_navigation_decision(
                "channel_serial"
            )
            log.info("Channel serial: %s", channel_serial_result["action"])

            log.info("--- Testing get_adjusted_timeout_for_nfr() ---")
            adjusted_timeout = cms_api_client.get_adjusted_timeout_for_nfr()
            log.info("Adjusted NFR Timeout (secs): %s", adjusted_timeout)

            log.info("=== Summary ===")
            all_results = {
                "standby": standby_result["action"],
                "restart": restart_result["action"],
                "channel_serial": channel_serial_result["action"],
                "adjusted_timeout_secs": adjusted_timeout,
            }
            log.info("All results summary: %s", all_results)

        else:
            log.error("Failed to retrieve CMS configuration")

        return cms_config

    except Exception as e:
        log.error("Error testing CMS configuration: %s", str(e))
        raise
