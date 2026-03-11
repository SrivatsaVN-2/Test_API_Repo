import datetime
import re
from typing import Any, List, Optional

import pytz

from .base_api_client import BaseApiClient
from .models.api_query import APIQuery


def get_device_timezone(default_timezone="Europe/Lisbon"):
    """
    Device timezone will be injected through BaseApiClient config
    """
    return default_timezone


class EpgApiClient(BaseApiClient):

    def __init__(self, config_manager, natco: str):

        super().__init__(config_manager, natco)

        self.station_to_channel_map = {}
        self.channels = []

        # This will be injected by STBT interface layer
        self.api_library = None

        self._initialize_station_channel_map()

    def _initialize_station_channel_map(self) -> List[APIQuery.Channel]:

        channel_client = self.api_library.channel_api

        channels = channel_client.get_subscribed_channels(
            APIQuery.ChannelDesc(size=1000)
        )

        self.channels = []
        self.station_to_channel_map = {}

        for channel in channels:

            if (
                channel.station_id is not None
                and channel.channel_number is not None
            ):
                self.station_to_channel_map[channel.station_id] = (
                    channel.channel_number
                )

                self.channels.append(channel)

        return self.channels

    def get_channel_for_station(self, station_id: str) -> Optional[int]:

        if not self.station_to_channel_map:
            self._initialize_station_channel_map()

        return self.station_to_channel_map.get(station_id)

    def get_schedule(
        self,
        date: Optional[str] = None,
        hour_offset: int = 21,
        station_ids: Optional[List[str]] = None,
        channel_numbers: Optional[List[int]] = None,
        is_adult: Optional[bool] = None,
    ) -> dict[str, Any]:

        valid_offsets = [0, 3, 6, 9, 12, 15, 18, 21]

        if hour_offset not in valid_offsets:
            hour_offset = 21

        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        endpoint = self.config_manager.get_endpoint(self.language, "EPG_SCHEDULE")

        url = f"{base_url}{endpoint}"

        params = self.config_manager.get_param(
            self.language,
            "EPG_SCHEDULE_PARAM"
        ).copy()

        params["date"] = date
        params["hour_offset"] = hour_offset

        if station_ids:
            params["station_ids"] = ",".join(station_ids)

        if channel_numbers:
            params["channel_numbers"] = ",".join(map(str, channel_numbers))

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")

        if self.access_token:

            headers.update(
                {
                    "bff_token": self.access_token,
                    "Authorization": f"Bearer {self.access_token}",
                }
            )

        response_data = self.make_request(
            "GET",
            url,
            headers=headers,
            params=params,
            requires_adult_token=is_adult,
        )

        if not self.station_to_channel_map:
            self._initialize_station_channel_map()

        return response_data
