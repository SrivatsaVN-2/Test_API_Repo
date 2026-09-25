# mobile_channel_api.py
#
# Channel API client for the mobile touchpoint. Minimal - doesn't replicate
# channel_api.py's (STB) serial-number remapping (CMS/remote-control specific,
# not relevant to a mobile UI) or its filtering machinery (title/audio/random
# selection) - not needed for "list the channels".
#
# IMPORTANT (confirmed empirically, not assumed from STB's code): the full
# channel list (CHANNEL_INFO) does NOT carry a working per-channel
# "is_subscribed" flag - it's absent from every channel in the real response.
# Subscription status has to be computed by diffing two separate endpoints:
# CHANNEL_INFO (all channels, 317 for test777) vs SUBSCRIPTION_URL (only
# subscribed ones, 246 for test777) - matched by station_id.

from Test_API_Repo.APIs.dtdl.mobile_base_api_client import MobileBaseApiClient
from Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.MobileChannel")


class MobileChannelApiClient(MobileBaseApiClient):

    def get_channels(self):
        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        endpoint = self.config_manager.get_endpoint(self.language, "CHANNEL_INFO")
        url = f"{base_url}{endpoint}"

        params = self.config_manager.get_param(self.language, "CHANNEL_INFO")

        log.info("Fetching full channel list")
        response = self.make_request("GET", url, params=params)

        return (response or {}).get("channels", [])

    def get_subscribed_channels(self):
        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        endpoint = self.config_manager.get_endpoint(self.language, "SUBSCRIPTION_URL")
        url = f"{base_url}{endpoint}"

        params = self.config_manager.get_param(self.language, "SUBSCRIPTION_INFO")

        log.info("Fetching subscribed channel list")
        response = self.make_request("GET", url, params=params)

        return (response or {}).get("channels", [])

    def get_unsubscribed_channels(self):
        all_channels = self.get_channels()
        subscribed = self.get_subscribed_channels()

        subscribed_ids = {
            ch.get("station_id") or ch.get("channel_number") for ch in subscribed
        }

        return [
            ch for ch in all_channels
            if (ch.get("station_id") or ch.get("channel_number")) not in subscribed_ids
        ]
