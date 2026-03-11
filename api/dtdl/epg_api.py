import datetime
import re
from typing import Any, List, Optional

import pytz




class EpgApiClient:

    def __init__(self, data_interface):
        """
        API client receives DataInterface from STBT repo.
        """

        self.data_interface = data_interface
        self.language = data_interface.language
        self.APIQuery = data_interface.APIQuery
        self.station_to_channel_map = {}
        self.channels = []

        # Injected later by interface layer if needed
        self.api_library = None

    def _initialize_station_channel_map(self) -> List[APIQuery.Channel]:

        channel_client = self.api_library.channel_api

        channels = channel_client.get_subscribed_channels(
            APIQuery.ChannelDesc(size=1000)
        )

        self.channels = []
        self.station_to_channel_map = {}

        for channel in channels:

            if channel.station_id and channel.channel_number:
                self.station_to_channel_map[channel.station_id] = channel.channel_number
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

        params = self.data_interface.get_params("EPG_SCHEDULE_PARAM")

        params["date"] = date
        params["hour_offset"] = hour_offset

        if station_ids:
            params["station_ids"] = ",".join(station_ids)

        if channel_numbers:
            params["channel_numbers"] = ",".join(map(str, channel_numbers))

        response_data = self.data_interface.request(
            method="GET",
            endpoint="EPG_SCHEDULE",
            params=params,
            headers_type="BFF_OTHER",
            requires_auth=True,
        )

        if not self.station_to_channel_map:
            self._initialize_station_channel_map()

        return response_data
