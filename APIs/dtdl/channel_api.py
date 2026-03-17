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
            super().__init__(interface=interface)

            self.interface = interface
            self.channel_desc = APIQuery.ChannelDesc()

            # ✅ NATCO from interface
            
            self.natco = (self.interface.natco_config.get("natco") or "").upper()

            # ✅ CMS Integration
            self.cms_client = self._init_cms_client()

            self.channel_mapping = {}
            self.temp_channels_size = 1000

            if self.natco not in self.SKIP_HU_NATCOS:
                self._initialize_channel_mapping()

        except Exception as e:
            log.error("Error initializing ChannelApiClient: %s", str(e))
            self.channel_mapping = {}

    # =====================================================
    # 🔹 CMS CLIENT
    # =====================================================

    def _init_cms_client(self):
        try:
            from tests.Test_API_Repo.APIs.cmsdata.cms_data import CMSApiClient
            return CMSApiClient(interface=self.interface)
        except Exception:
            log.warning("CMS client not available")
            return None

    # =====================================================
    # 🔹 CHANNEL MAPPING
    # =====================================================

    def _initialize_channel_mapping(self):
        try:
            use_serial = False

            if self.cms_client:
                try:
                    use_serial = self.cms_client.get_channel_serial_config()
                except Exception:
                    pass

            if not use_serial:
                self.channel_mapping = {}
                return

            all_channels = self._fetch_api_data("CHANNEL", is_adult=True)

            channel_numbers = [
                ch.get("channel_number")
                for ch in all_channels
                if ch.get("channel_number") is not None
            ]

            self.channel_mapping = {
                num: idx + 1
                for idx, num in enumerate(sorted(channel_numbers))
            }

        except Exception as e:
            log.error("Channel mapping failed: %s", str(e))
            self.channel_mapping = {}

    def map_channel_number(self, number: int, to_serial=True):
        try:
            if self.natco in self.SKIP_HU_NATCOS:
                return number

            if not self.channel_mapping:
                return number

            if to_serial:
                return self.channel_mapping.get(number, number)

            reverse = {v: k for k, v in self.channel_mapping.items()}
            return reverse.get(number, number)

        except Exception:
            return number

    # =====================================================
    # 🔹 API FETCH
    # =====================================================

    def _fetch_api_data(self, api_type, recursion_depth=None, is_adult=False):

        config = {
            "CHANNEL": ("CHANNEL_INFO", "ADULT_INFO" if is_adult else "CHANNEL_INFO"),
            "SUBSCRIPTION": ("SUBSCRIPTION_URL", "SUBSCRIPTION_INFO"),
            "FAVORITES": ("FAVORITE_CHANNELS", "CHANNEL_INFO"),
        }

        endpoint_key, param_key = config[api_type]

        base = self.config_manager.get_endpoint(self.language, "BASE")
        endpoint = self.config_manager.get_endpoint(self.language, endpoint_key)

        url = f"{base}{endpoint}"

        params = self.config_manager.get_param(self.language, param_key)

        response = self.make_request(
            "GET",
            url,
            params=params,
            requires_adult_token=is_adult,
        )

        return self._extract_data_from_response(response)

    def _extract_data_from_response(self, response_data, recursion_depth=None):
        return response_data.get("channels", []) if response_data else []

    # =====================================================
    # 🔹 CHANNEL OBJECT
    # =====================================================

    def _create_channel_object(self, ch, api_type, skip_serial_mapping=False):

        original = ch.get("channel_number")

        if self.natco in self.SKIP_HU_NATCOS or skip_serial_mapping:
            mapped = original
        else:
            mapped = (
                self.map_channel_number(original)
                if original else original
            )

        return APIQuery.Channel(
            channel_number=mapped,
            station_id=ch.get("station_id"),
            title=ch.get("title"),
            is_adult=ch.get("is_adult", False),
            is_audio=ch.get("is_audio", False),
            is_subscribed=(
                True if api_type in ["SUBSCRIPTION", "FAVORITES"]
                else ch.get("is_subscribed")
            ),
            description=ch.get("description"),
        )

    # =====================================================
    # 🔹 FILTER
    # =====================================================

    def _filter_channel_data(self, channel_data, desc, api_type):

        result = []

        for ch in channel_data:
            num = ch.get("channel_number")
            title = ch.get("title")

            if num is None:
                continue

            mapped = self.map_channel_number(num)

            if desc.exclude_channel_number == mapped:
                continue

            if desc.is_audio is True and not ch.get("is_audio"):
                continue

            if desc.is_adult is False and ch.get("is_adult"):
                continue

            if desc.title and title != desc.title:
                continue

            result.append(self._create_channel_object(ch, api_type))

        result.sort(key=lambda x: x.channel_number or 0)

        if desc.select_random and result:
            return [random.choice(result)]

        return result[: desc.size or len(result)]

    # =====================================================
    # 🔹 PUBLIC APIs
    # =====================================================

    def get_channels(self, desc=None):
        desc = desc or self.channel_desc

        data = self._fetch_api_data(
            "CHANNEL",
            is_adult=(desc.is_adult is not False),
        )

        return self._filter_channel_data(data, desc, "CHANNEL")

    def get_subscribed_channels(self, desc=None, is_adult=None):
        desc = desc or self.channel_desc

        data = self._fetch_api_data("SUBSCRIPTION", is_adult=is_adult)

        return self._filter_channel_data(data, desc, "SUBSCRIPTION")

    def get_favorite_channels(self, desc=None):
        desc = desc or self.channel_desc

        data = self._fetch_api_data("FAVORITES")

        return self._filter_channel_data(data, desc, "FAVORITES")

    # =====================================================
    # 🔹 UTILITIES
    # =====================================================

    def get_first_channel_number(self):
        channels = self.get_subscribed_channels(
            APIQuery.ChannelDesc(size=1000)
        )

        nums = [ch.channel_number for ch in channels if ch.channel_number]

        return str(min(nums)) if nums else False

    def get_invalid_channel_number(self):

        all_channels = self._fetch_api_data("CHANNEL", is_adult=True)

        nums = [ch["channel_number"] for ch in all_channels if ch.get("channel_number")]

        if not nums:
            raise AssertionError("No channels available")

        missing = self.get_missing_channels(nums)

        if missing:
            return str(random.choice(missing))

        return str(max(nums) + random.randint(1, 50))

    def get_missing_channels(self, nums: List[int]):

        nums = sorted(nums)

        missing = []

        for i in range(len(nums) - 1):
            if nums[i + 1] - nums[i] > 1:
                missing.extend(range(nums[i] + 1, nums[i + 1]))

        return missing
