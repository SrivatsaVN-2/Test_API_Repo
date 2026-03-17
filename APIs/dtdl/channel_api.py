# channel_api.py

import random
import string
from typing import Dict, List, Optional, Union

from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger

log = Logger().setup_logger("Channel.API")


class ChannelApiClient(BaseApiClient):

    SKIP_HU_NATCOS = ["HU SEI", "HU SDMC"]

    def __init__(self, interface):
        try:
            # ✅ Correct initialization
            super().__init__(interface=interface)

            self.interface = interface
            self.channel_desc = APIQuery.ChannelDesc()

            # ✅ FIX: Get natco from interface (not global / static)
            self.natco = (interface.get_natco() or "").upper()

            # Optional CMS (safe import)
            try:
                from tests.Test_API_Repo.APIs.cms.cms_api_client import CMSApiClient
                self.cms_client = CMSApiClient(interface)
            except Exception:
                self.cms_client = None

            self.channel_mapping = {}
            self.temp_channels_size = 1000

            if self.natco not in self.SKIP_HU_NATCOS:
                self._initialize_channel_mapping()

        except Exception as e:
            log.error("Error initializing ChannelApiClient: %s", str(e))
            self.channel_mapping = {}

    # =====================================================
    # 🔹 CHANNEL MAPPING (fixed natco usage + duplicate loop removed)
    # =====================================================

    def _initialize_channel_mapping(self) -> None:
        try:
            natco_name = self.natco

            use_serial = False
            if self.cms_client:
                use_serial = self.cms_client.get_channel_serial_config()

            if not use_serial:
                self.channel_mapping = {}
                return

            all_channels = self._fetch_api_data("CHANNEL", None, is_adult=True)

            if not all_channels:
                self.channel_mapping = {}
                return

            # ❌ removed duplicate loop bug
            channel_numbers = [
                ch.get("channel_number")
                for ch in all_channels
                if ch.get("channel_number") is not None
            ]

            if not channel_numbers:
                self.channel_mapping = {}
                return

            self.channel_mapping = {
                api_num: idx + 1
                for idx, api_num in enumerate(sorted(channel_numbers))
            }

        except Exception as e:
            log.error("Error initializing mapping: %s", str(e))
            self.channel_mapping = {}

    # =====================================================
    # 🔹 FIXED NATCO USAGE
    # =====================================================

    def map_channel_number(self, number: int, to_serial: bool = True) -> int:
        try:
            natco_name = self.natco

            if natco_name in self.SKIP_HU_NATCOS:
                return number

            if not self.channel_mapping:
                return number

            if to_serial:
                return self.channel_mapping.get(number, number)

            reverse = {v: k for k, v in self.channel_mapping.items()}
            return reverse.get(number, number)

        except Exception as e:
            log.error("Mapping error: %s", str(e))
            return number

    # =====================================================
    # 🔹 FETCH API (headers cleaned — base handles auth)
    # =====================================================

    def _fetch_api_data(
        self,
        api_type: str,
        recursion_depth: Optional[int] = None,
        is_adult: bool = False,
    ) -> List[Dict]:

        endpoint_config = {
            "CHANNEL": {
                "endpoint": "CHANNEL_INFO",
                "param_type": "ADULT_INFO" if is_adult else "CHANNEL_INFO",
            },
            "SUBSCRIPTION": {
                "endpoint": "SUBSCRIPTION_URL",
                "param_type": "SUBSCRIPTION_INFO",
            },
            "FAVORITES": {
                "endpoint": "FAVORITE_CHANNELS",
                "param_type": "CHANNEL_INFO",
            },
        }

        assert api_type in endpoint_config, f"Invalid API type: {api_type}"

        config = endpoint_config[api_type]

        try:
            base_url = self.config_manager.get_endpoint(self.language, "BASE")
            endpoint = self.config_manager.get_endpoint(
                self.language, config["endpoint"]
            )

            url = f"{base_url}{endpoint}"

            params = self.config_manager.get_param(
                self.language, config["param_type"]
            )

            # ✅ Let BaseApiClient manage headers + auth
            response_data = self.make_request(
                "GET",
                url,
                params=params,
                requires_adult_token=is_adult,
            )

            return self._extract_data_from_response(
                response_data, recursion_depth
            )

        except Exception as e:
            log.error("Failed API call %s: %s", api_type, str(e))
            raise AssertionError(f"{api_type} API failed")

    # =====================================================
    # 🔹 FIXED get_natco_config USAGE → interface
    # =====================================================

    def _create_channel_object(self, ch, api_type, skip_serial_mapping=False):

        original_number = ch.get("channel_number")

        natco_name = self.natco
        should_skip = natco_name in self.SKIP_HU_NATCOS or skip_serial_mapping

        if should_skip:
            mapped = original_number
        else:
            mapped = (
                self.map_channel_number(original_number, True)
                if self.channel_mapping and original_number
                else original_number
            )

        is_subscribed = (
            True
            if api_type in ["SUBSCRIPTION", "FAVORITES"]
            else ch.get("is_subscribed", None)
        )

        return APIQuery.Channel(
            channel_number=mapped,
            station_id=ch.get("station_id"),
            title=ch.get("title"),
            is_adult=ch.get("is_adult", False),
            is_audio=ch.get("is_audio", False),
            is_subscribed=is_subscribed,
            description=ch.get("description"),
        )
