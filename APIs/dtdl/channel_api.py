# channel_api.py
# API client specific for channel-related operations

import random
import string
from typing import Dict, List, Optional, Union

from APIs.dtdl.Interface import Interface
from APIs.dtdl.base_api_client import BaseApiClient
from APIs.dtdl.config_manager import Config_Manager
from Utilities.Queries import APIQuery

"""
from tests.androidtv.api.cmsdata.cms_data import CMSApiClient
from tests.androidtv.api.dtdl.base_api_client import BaseApiClient
from tests.androidtv.api.dtdl.interface import Interface
from tests.androidtv.libraries.datatype import APIQuery
from tests.androidtv.pages.helper import get_natco_config
from tests.androidtv.pages.utility.stbconfig import STBConfig
from tests.androidtv.pages.utility.system_logger import Logger
from tests.androidtv.pages.utility.utils import Utils
"""
log = Logger().setup_logger("Channel.API")


class ChannelApiClient(BaseApiClient):
    """
    Client for interacting with channel-related API endpoints.

    This class handles retrieving channel information, subscribed channels,
    favorite channels, and mapping between channel numbers and serial numbers.
    """

    SKIP_HU_NATCOS = ["HU SEI", "HU SDMC"]

    def __init__(self, config_manager, natco: str = None):
        """
        Initialize the ChannelApiClient with the given configuration manager and NatCo abbreviation.
        Args:
            config_manager (ConfigManager): Configuration manager for the API client
            natco (str): NatCo abbreviation used to fetch content
        """
        try:
            super().__init__(config_manager, natco)
            #self.natco = (
                #natco.upper() if natco else get_natco_config().get("natco", "").upper())
            self.interface = Interface()
            self.natco = Interface.natco_config
            self.channel_desc = APIQuery.ChannelDesc()
            self.cms_client = CMSApiClient(config_manager, natco)
            self.channel_mapping = {}
            self.temp_channels_size = 1000
            if self.natco not in self.SKIP_HU_NATCOS:
                self._initialize_channel_mapping()
        except Exception as e:
            log.error("Error initializing ChannelApiClient: %s", str(e))
            self.channel_mapping = {}
            self.temp_channels_size = 1000

    def _initialize_channel_mapping(self) -> None:
        """
        Initialize the channel mapping for the current NatCo.
        This method retrieves the channel data from the API and maps the channel numbers
        to their corresponding serial numbers. Includes both adult and non-adult channels.
        to their corresponding serial numbers. Includes both adult and non-adult channels.
        """
        try:
            natco_name = self.natco.upper()
            use_serial = self.cms_client.get_channel_serial_config()
            if not use_serial:
                self.channel_mapping = {}
                return

            # Fetch all channels including adult channels
            all_channels = self._fetch_api_data("CHANNEL", None, is_adult=True)
            if not all_channels:
                log.error(
                    "No channel data retrieved for mapping for %s", natco_name)
                self.channel_mapping = {}
                return
            channel_numbers = [
                ch.get("channel_number")
                for ch in all_channels
                for ch in all_channels
                if ch.get("channel_number") is not None
            ]
            if not channel_numbers:
                log.error(
                    "No valid channel numbers found in channel data for %s", natco_name
                )
                self.channel_mapping = {}
                return

            # Create mapping for all channels (sorted by channel number)

            # Create mapping for all channels (sorted by channel number)
            self.channel_mapping = {
                api_num: serial_num + 1
                for serial_num, api_num in enumerate(sorted(channel_numbers))
            }
        except Exception as e:
            log.error(
                "Error initializing channel mapping for %s: %s", natco_name, str(
                    e)
            )
            self.channel_mapping = {}

    def map_channel_number(self, number: int, to_serial: bool = True) -> int:
        """
        Map a channel number to its serial representation or vice versa.
        Args:
            number (int): The channel number to map.
            to_serial (bool): If True, map to serial number; otherwise, map to channel number.
        Returns:
            int: The mapped channel number or the original number if mapping is not applicable.
        """
        try:
            natco_name = natco.upper()

            # Skip mapping for certain NatCos only

            # Skip mapping for certain NatCos only
            if natco_name in self.SKIP_HU_NATCOS:
                return number

            if not self.channel_mapping:
                return number

            if to_serial:
                mapped_number = self.channel_mapping.get(number, number)
                return mapped_number
            else:
                reverse_mapping = {v: k for k,
                                   v in self.channel_mapping.items()}
                mapped_number = reverse_mapping.get(number, number)
                log.debug(
                    "Reverse mapping %d to channel %d for %s",
                    number,
                    mapped_number,
                    natco_name,
                )
                return mapped_number
        except Exception as e:
            log.error("Error mapping number %d for %s: %s",
                      number, natco_name, str(e))
            return number

    def _extract_data_from_response(
        self,
        response_data: Dict,
        recursion_depth: Optional[int] = None,
    ) -> List[Dict]:
        """
        Extract data from a nested data structure.
        Args:
            response_data (Dict): The data structure to search through
            recursion_depth (Optional[int]): The maximum depth to search
        Returns:
            List[Dict]: The extracted data as a list of dictionaries
        """
        try:
            if recursion_depth is None:
                recursion_depth = 1
            extracted_data = []
            channels = response_data.get("channels", [])
            for channel in channels:
                channel_data = {}
                try:
                    for key, value in channel.items():
                        channel_data[key] = value
                    if channel_data:
                        extracted_data.append(channel_data)
                except Exception as channel_error:
                    log.error("Error processing channel data: %s",
                              str(channel_error))
                    continue
            return extracted_data
        except Exception as e:
            log.error("Error extracting data from response: %s", str(e))
            return []

    def _fetch_api_data(
        self,
        api_type: str,
        recursion_depth: Optional[int] = None,
        is_adult: bool = False,
    ) -> List[Dict]:
        """
        Fetch the API data for a given API type.
        Args:
            api_type (str): The type of API to call (e.g. CHANNEL, SUBSCRIPTION, etc.)
            recursion_depth (Optional[int]): The maximum depth to search for data
            is_adult (bool): Whether to use adult-specific parameters and headers
        Returns:
            List[Dict]: The extracted data as a list of dictionaries
        """
        endpoint_config = {
            "CHANNEL": {
                "endpoint": "CHANNEL_INFO",
                "header_type": "OTHER",
                "param_type": "ADULT_INFO" if is_adult else "CHANNEL_INFO",
            },
            "SUBSCRIPTION": {
                "endpoint": "SUBSCRIPTION_URL",
                "header_type": "BFF_OTHER",
                "param_type": "SUBSCRIPTION_INFO",
            },
            "FAVORITES": {
                "endpoint": "FAVORITE_CHANNELS",
                "header_type": "BFF_OTHER",
                "param_type": "CHANNEL_INFO",
            },
        }
        assert (
            api_type in endpoint_config
        ), f"Invalid API type: {api_type}. Valid types: {list(endpoint_config.keys())}"

        config = endpoint_config[api_type]
        try:
            base_url = self.config_manager.get_endpoint(self.language, "BASE")
            endpoint = self.config_manager.get_endpoint(
                self.language, config["endpoint"]
            )
            assert base_url, f"Base URL not configured for language: {self.language}"
            assert endpoint, f"Endpoint not configured for {config['endpoint']}"

            url = f"{base_url}{endpoint}"

            # Use BFF_OTHER header type for adult content requests
            header_type = "BFF_OTHER" if is_adult else config["header_type"]
            headers = self.config_manager.get_header(
                self.language, header_type)

            # Use BFF_OTHER header type for adult content requests
            header_type = "BFF_OTHER" if is_adult else config["header_type"]
            headers = self.config_manager.get_header(
                self.language, header_type)

            params = self.config_manager.get_param(
                self.language, config["param_type"])
            assert headers, f"Headers not configured for {header_type}"
            assert params, f"Parameters not configured for {config['param_type']}"

            # Make request with adult token if needed
            response_data = self.make_request(
                "GET",
                url,
                headers=headers,
                params=params,
                requires_adult_token=is_adult,
            )
            assert (
                response_data is not None
            ), f"No response received from {api_type} API"
            extracted_data = self._extract_data_from_response(
                response_data, recursion_depth
            )
            return extracted_data

        except AssertionError:
            raise
        except Exception as e:
            log.error("Failed to fetch %s data: %s", api_type, str(e))
            raise AssertionError(f"API call failed for {api_type}: {str(e)}")

    def _filter_channel_data(self, channel_data, channel_desc, api_type):
        """
        Filter the channel data based on various criteria and return a list of
        filtered channels.
        Args:
            channel_data (List[Dict]): A list of dictionaries containing channel data.
            channel_desc (APIQuery.ChannelDesc): An object containing the filter criteria.
            api_type (str): The type of API call (e.g., CHANNEL, SUBSCRIPTION, FAVORITES).
        Returns:
            List[APIQuery.Channel]: A list of filtered channels.
        """
        filtered_channels = []
        adult_filtered_count = 0

        adult_filtered_count = 0

        for ch in channel_data:
            ch_name = ch.get("title")
            ch_num = ch.get("channel_number")
            ch_is_audio = ch.get("is_audio", False)
            ch_is_adult = ch.get("is_adult", False)

            # Skip if channel number is missing
            if ch_num is None:
                continue

            natco_name = get_natco_config().get("natco", "").upper()
            if natco_name in self.SKIP_HU_NATCOS:
                mapped_ch_num = ch_num
            else:
                mapped_ch_num = (
                    self.map_channel_number(ch_num, to_serial=True)
                    if self.channel_mapping and ch_num
                    else ch_num
                )
            if (
                channel_desc.exclude_channel_number is not None
                and mapped_ch_num == channel_desc.exclude_channel_number
            ):
                continue  # Skip this channel if it matches the exclude number

            # Check multiple exclude channels
            if (
                channel_desc.exclude_channel_numbers
                and mapped_ch_num in channel_desc.exclude_channel_numbers
            ):
                continue  # Skip this channel if it's in the exclude list

            # Apply title length filtering
            if api_type != "FAVORITES" and ch_name:
                if (
                    channel_desc.min_length is not None
                    and len(ch_name) < channel_desc.min_length
                ) or (
                    channel_desc.max_length is not None
                    and len(ch_name) > channel_desc.max_length
                ):
                    continue
            elif api_type != "FAVORITES":
                if (
                    channel_desc.min_length is not None
                    or channel_desc.max_length is not None
                ):
                    continue

            # Apply audio filter
            # Apply audio filter
            if channel_desc.is_audio is True and not ch_is_audio:
                continue
            if channel_desc.is_audio is False and ch_is_audio:
                continue

            # Apply adult content filtering

            # Apply adult content filtering
            if channel_desc.is_adult is False and ch_is_adult:
                continue  # Skip adult channels when requesting non-adult only

            if ch_is_adult:
                adult_filtered_count += 1

            # Apply other filters
            if channel_desc.title and ch_name != channel_desc.title:
                continue
            if (
                channel_desc.station_id
                and ch.get("station_id") != channel_desc.station_id
            ):
                continue
            if channel_desc.select_alpha and ch_name:
                if not (
                    isinstance(ch_name, str)
                    and all(c in string.ascii_letters for c in ch_name)
                ):
                    continue

            # Apply limiter filter based on channel number ranges
            limiter = channel_desc.limiter

            limit_number = (
                limiter[0]
                if type(limiter) == tuple or type(limiter) == list
                else limiter
            )
            if limit_number is not None:
                limit_number = (
                    limiter[0]
                    if type(limiter) == tuple or type(limiter) == list
                    else limiter
                )
                if limit_number == 1 and (ch_num >= 0 and ch_num < 9):
                    channel_obj = self._create_channel_object(
                        ch, api_type, skip_serial_mapping=True
                    )
                    filtered_channels.append(channel_obj)
                if limit_number == 2 and (ch_num > 9 and ch_num < 100):
                    channel_obj = self._create_channel_object(
                        ch, api_type, skip_serial_mapping=True
                    )
                    filtered_channels.append(channel_obj)
                if limit_number == 3 and (ch_num > 99 and ch_num < 1000):
                    channel_obj = self._create_channel_object(
                        ch, api_type, skip_serial_mapping=True
                    )
                    filtered_channels.append(channel_obj)
            elif limit_number is None:
                channel_obj = self._create_channel_object(
                    ch, api_type, skip_serial_mapping=True
                )
                filtered_channels.append(channel_obj)

            # Create channel object with skip_serial_mapping flag

        # Sort filtered channels by original channel number to ensure consistent ordering
        filtered_channels.sort(
            key=lambda x: x.channel_number if x.channel_number else 0
        )

        natco_name = get_natco_config().get("natco", "").upper()
        if (
            self.channel_mapping
            and filtered_channels
            and natco_name not in self.SKIP_HU_NATCOS
        ):
            for index, channel in enumerate(filtered_channels):
                channel.channel_number = index + 1

        # Handle first/last channel requests AFTER filtering and serial mapping
        if channel_desc.first_channel:
            if not filtered_channels:
                log.info(
                    "No filtered %s data available for first channel.", api_type.lower()
                )
                return []
            log.info(
                "Returning first channel from %d filtered channels: %s",
                len(filtered_channels),
                filtered_channels[0].channel_number,
            )
            return [filtered_channels[0]]

        if channel_desc.last_channel:
            if not filtered_channels:
                log.info(
                    "No filtered %s data available for last channel.", api_type.lower()
                )
                return []
            log.info(
                "Returning last channel from %d filtered channels: %s",
                len(filtered_channels),
                filtered_channels[-1].channel_number,
            )
            return [filtered_channels[-1]]

        try:
            # Apply exclude_first_last BEFORE any selection logic
            if channel_desc.exclude_first_last and len(filtered_channels) > 2:
                log.info(
                    "Excluding first and last channels from filtered results.")
                filtered_channels = filtered_channels[1:-1]

            channels_size = (
                self.temp_channels_size
                if channel_desc.select_random
                else channel_desc.size
            )
            num_to_return = min(channel_desc.size, len(filtered_channels))

            if channel_desc.select_random:
                # Select a random subset of channels from the filtered list
                available_channels = filtered_channels[:channels_size].copy()
                # Exclude first and last if the flag is set and we have enough channels
                if channel_desc.exclude_first_last and len(available_channels) > 2:
                    log.info(
                        "Excluding first and last channels for random selection.")
                    available_channels = available_channels[1:-1]

                selected_channels = []
                for _ in range(num_to_return):
                    if not available_channels:
                        break
                    random_index = Utils().generate_random_index(
                        len(available_channels)
                    )
                    if 0 <= random_index < len(available_channels):
                        selected_channel = available_channels.pop(random_index)
                        selected_channels.append(selected_channel)
                        STBConfig.api_channel_number = selected_channel.title
                    else:
                        log.error(
                            "Invalid random index: %d (list length: %d) for %s",
                            random_index,
                            len(available_channels),
                            api_type,
                        )
                return selected_channels
            else:
                return filtered_channels[:num_to_return]
        except Exception as e:
            log.error("Error selecting channels for %s: %s", api_type, str(e))
            return []

    def _filter_adult_only_channel_data(self, channel_data, channel_desc, api_type):
        """
        Filter the channel data to return ONLY adult channels (is_adult=True).
        This is different from the regular filter which returns ALL channels when is_adult=True.
        """
        filtered_channels = []

        for ch in channel_data:
            ch_name = ch.get("title")
            ch_num = ch.get("channel_number")
            ch_is_audio = ch.get("is_audio", False)
            ch_is_adult = ch.get("is_adult", False)

            # Skip if channel number is missing
            if ch_num is None:
                continue

            # ONLY include channels that are actually adult channels
            if not ch_is_adult:
                continue

            # Map the original channel number to serial for comparison
            mapped_ch_num = (
                self.map_channel_number(ch_num, to_serial=True)
                if self.channel_mapping and ch_num
                else ch_num
            )

            # Apply exclusion filters
            if (
                channel_desc.exclude_channel_number is not None
                and mapped_ch_num == channel_desc.exclude_channel_number
            ):
                continue

            if (
                channel_desc.exclude_channel_numbers
                and mapped_ch_num in channel_desc.exclude_channel_numbers
            ):
                continue
            if api_type != "FAVORITES" and ch_name:
                if (
                    channel_desc.min_length is not None
                    and len(ch_name) < channel_desc.min_length
                ) or (
                    channel_desc.max_length is not None
                    and len(ch_name) > channel_desc.max_length
                ):
                    continue

            if channel_desc.is_audio is True and not ch_is_audio:
                continue
            if channel_desc.is_audio is False and ch_is_audio:
                continue

            if channel_desc.title and ch_name != channel_desc.title:
                continue
            if (
                channel_desc.station_id
                and ch.get("station_id") != channel_desc.station_id
            ):
                continue
            if channel_desc.select_alpha and ch_name:
                if not (
                    isinstance(ch_name, str)
                    and all(c in string.ascii_letters for c in ch_name)
                ):
                    continue

            # Create channel object and add to filtered list
            channel_obj = self._create_channel_object(ch, api_type)
            filtered_channels.append(channel_obj)

        # Handle random selection and size limiting
        try:
            # Apply exclude_first_last BEFORE any selection logic
            if channel_desc.exclude_first_last and len(filtered_channels) > 2:
                log.info(
                    "Excluding first and last adult channels from filtered results."
                )
                filtered_channels = filtered_channels[1:-1]

            num_to_return = min(channel_desc.size, len(filtered_channels))

            if channel_desc.select_random:
                available_channels = filtered_channels.copy()

                selected_channels = []
                for _ in range(num_to_return):
                    if not available_channels:
                        break
                    random_index = Utils().generate_random_index(
                        len(available_channels)
                    )
                    if 0 <= random_index < len(available_channels):
                        selected_channel = available_channels.pop(random_index)
                        selected_channels.append(selected_channel)
                return selected_channels
            else:
                return filtered_channels[:num_to_return]
        except Exception as e:
            log.error("Error selecting adult-only channels: %s", str(e))
            return []

    def _create_channel_object(self, ch, api_type, skip_serial_mapping=False):
        """
        Create an APIQuery.Channel object from the provided channel data and API type.
        Args:
            ch (dict): The channel data containing various channel attributes.
            api_type (str): The type of API call (e.g., CHANNEL, SUBSCRIPTION, FAVORITES).
            skip_serial_mapping (bool): If True, preserve original numbers for later consecutive mapping.
        Returns:
            APIQuery.Channel: An instance of APIQuery.Channel with the mapped channel data.
        """
        # Get the original channel number from API response
        original_channel_number = ch.get("channel_number")

        # Check if this is a skip NatCo
        natco_name = get_natco_config().get("natco", "").upper()
        should_skip_mapping = natco_name in self.SKIP_HU_NATCOS or skip_serial_mapping

        if should_skip_mapping:
            mapped_num = original_channel_number
        else:
            # Normal operation: apply serial mapping immediately
            mapped_num = (
                self.map_channel_number(
                    original_channel_number, to_serial=True)
                if self.channel_mapping and original_channel_number
                else original_channel_number
            )

        is_subscribed = (
            True
            if api_type in ["SUBSCRIPTION", "FAVORITES"]
            else ch.get("is_subscribed", None)
        )
        return APIQuery.Channel(
            channel_number=mapped_num,
            station_id=ch.get("station_id"),
            title=ch.get("title"),
            is_adult=ch.get("is_adult", False),
            genres=ch.get("genres", []),
            channel_logo=ch.get("channel_logo"),
            cta=ch.get("cta"),
            media_pid=ch.get("media_pid"),
            is_catchup_enabled=ch.get("is_catchup_enabled", False),
            is_restricted=ch.get("is_restricted", False),
            entitlements=ch.get("entitlements", {}),
            is_free_to_air=ch.get("is_free_to_air", True),
            is_audio=ch.get("is_audio", False),
            channel_id=ch.get("channel_id"),
            quality=ch.get("quality"),
            distribution_types=ch.get("distribution_types", []),
            distribution_urls=ch.get("distribution_urls", {}),
            is_iptv=ch.get("is_iptv", False),
            type=ch.get("type"),
            lowLatency=ch.get("lowLatency", False),
            video_src_dash=ch.get("video_src_dash"),
            video_src_m3u=ch.get("video_src_m3u"),
            pid_dash=ch.get("pid_dash"),
            pid_m3u=ch.get("pid_m3u"),
            is_subscribed=is_subscribed,
            description=ch.get("description"),
        )

    def get_channels(
        self, channel_desc: APIQuery.ChannelDesc = None
    ) -> List[APIQuery.Channel]:
        """
        Retrieve a list of channel information based on ChannelDesc parameters.
        Args:
            channel_desc (APIQuery.ChannelDesc, optional): Channel description with filtering and selection parameters.
                If None, uses default parameters.
        Returns:
            List[APIQuery.Channel]: List of Channel objects that match the criteria.
        """
        try:
            channel_desc = channel_desc or self.channel_desc
            is_adult_request = (
                channel_desc.is_adult is True or channel_desc.is_adult is None
            )

            # Fetch data with adult parameters if requesting adult access or all channels
            channel_data = self._fetch_api_data(
                "CHANNEL", None, is_adult_request)

            # Filter the data
            filtered_channels = self._filter_channel_data(
                channel_data, channel_desc, "CHANNEL"
            )

            return filtered_channels

        except AssertionError:
            raise
        except Exception as e:
            log.error("Error retrieving channel data: %s", str(e))
            raise AssertionError(f"Failed to get channels: {str(e)}")

    def get_adult_only_channels(
        self, channel_desc: APIQuery.ChannelDesc = None
    ) -> List[APIQuery.Channel]:
        """
        Retrieve only adult channels (channels where is_adult=True).
        Args:
            channel_desc (APIQuery.ChannelDesc, optional): Channel description with filtering parameters.
                If None, uses default parameters.
        Returns:
            List[APIQuery.Channel]: List of Channel objects that are adult channels only.
        """
        try:
            if channel_desc:
                adult_only_desc = APIQuery.ChannelDesc(
                    channel_number=channel_desc.channel_number,
                    title=channel_desc.title,
                    is_audio=channel_desc.is_audio,
                    is_adult=True,
                    station_id=channel_desc.station_id,
                    min_length=channel_desc.min_length,
                    max_length=channel_desc.max_length,
                    select_alpha=channel_desc.select_alpha,
                    select_random=channel_desc.select_random,
                    size=channel_desc.size,
                    exclude_channel_number=channel_desc.exclude_channel_number,
                    exclude_channel_numbers=channel_desc.exclude_channel_numbers,
                )
            else:
                adult_only_desc = APIQuery.ChannelDesc(
                    is_adult=True, size=1000)

            log.info("Fetching adult-only channels")
            channel_data = self._fetch_api_data("CHANNEL", None, True)
            filtered_channels = self._filter_adult_only_channel_data(
                channel_data, adult_only_desc, "CHANNEL"
            )
            return filtered_channels

        except AssertionError:
            raise
        except Exception as e:
            log.error("Error retrieving adult-only channels: %s", str(e))
            raise AssertionError(
                f"Failed to get adult-only channels: {str(e)}")

    def get_all_channels_including_adult(
        self, channel_desc: APIQuery.ChannelDesc = None
    ) -> List[APIQuery.Channel]:
        """
        Retrieve all channels including both adult and non-adult channels.
        Args:
            channel_desc (APIQuery.ChannelDesc, optional): Channel description with filtering and selection parameters.
                If None, uses default parameters. The is_adult filter will be ignored.
        Returns:
            List[APIQuery.Channel]: List of all Channel objects (adult and non-adult).
        """
        try:
            # Create a copy of channel_desc and set is_adult to None to include all channels
            if channel_desc:
                # Create a new ChannelDesc with all same parameters but is_adult=None
                all_channels_desc = APIQuery.ChannelDesc(
                    channel_number=channel_desc.channel_number,
                    title=channel_desc.title,
                    is_audio=channel_desc.is_audio,
                    is_adult=None,  # This will include all channels
                    station_id=channel_desc.station_id,
                    min_length=channel_desc.min_length,
                    max_length=channel_desc.max_length,
                    select_alpha=channel_desc.select_alpha,
                    select_random=channel_desc.select_random,
                    size=channel_desc.size,
                )
            else:
                all_channels_desc = APIQuery.ChannelDesc(is_adult=None)

            log.info("Fetching all channels including adult content")

            # Always use adult API access to get complete channel list
            channel_data = self._fetch_api_data("CHANNEL", None, True)

            # Filter the data (with is_adult=None, all channels will be included)
            filtered_channels = self._filter_channel_data(
                channel_data, all_channels_desc, "CHANNEL"
            )
            return filtered_channels

        except Exception as e:
            log.error("Error retrieving all channels including adult: %s", str(e))
            return []

    def get_subscribed_channels(
        self, channel_desc: APIQuery.ChannelDesc = None, is_adult: bool = None
    ) -> List[APIQuery.Channel]:
        """
        Retrieve a list of subscription channel information based on ChannelDesc parameters.
        Args:
            channel_desc (APIQuery.ChannelDesc, optional): Channel description with filtering parameters.
                If None, uses default parameters.
        Returns:
            List[APIQuery.Channel]: List of Channel objects that match the criteria.
        """
        try:
            channel_desc = channel_desc or self.channel_desc
            if channel_desc and channel_desc.first_channel and STBConfig.first_channel:
                return [STBConfig.first_channel]
            if channel_desc and channel_desc.last_channel and STBConfig.last_channel:
                return [STBConfig.last_channel]
            subscription_data = self._fetch_api_data(
                "SUBSCRIPTION", is_adult=is_adult)
            # ToDo: for now if the first or last channel is true, we won't check for any other description parameters.
            if channel_desc.first_channel:
                if not subscription_data:
                    log.info("No subscription data available.")
                    return []
                channel_obj = self._create_channel_object(
                    subscription_data[0], "SUBSCRIPTION"
                )
                # Store the channel object in the STB config
                STBConfig.first_channel = channel_obj
                return [channel_obj] if channel_obj else []
            if channel_desc.last_channel:
                channel_obj = self._create_channel_object(
                    subscription_data[-1], "SUBSCRIPTION"
                )
                # Store the channel object in the STB config
                STBConfig.last_channel = channel_obj
                return [channel_obj] if channel_obj else []

            return self._filter_channel_data(
                subscription_data, channel_desc, "SUBSCRIPTION"
            )
        except Exception as e:
            log.error("Error retrieving subscription data: %s", str(e))
            return []

    def get_favorite_channels(
        self, channel_desc: APIQuery.ChannelDesc = None
    ) -> List[APIQuery.Channel]:
        """
        Retrieves a list of favorite channel information based on ChannelDesc parameters.
        Args:
            channel_desc (APIQuery.ChannelDesc, optional): Channel description with filtering parameters.
                If None, uses default parameters.
        Returns:
            List[APIQuery.Channel]: List of Channel objects that match the criteria.
        """
        try:
            channel_desc = channel_desc or self.channel_desc
            favorite_data = self._fetch_api_data("FAVORITES")
            return self._filter_channel_data(favorite_data, channel_desc, "FAVORITES")
        except AssertionError:
            raise
        except Exception as e:
            log.error("Error retrieving favorite channel data: %s", str(e))
            raise AssertionError(f"Failed to get favorite channels: {str(e)}")

    def get_first_channel_number(self) -> Union[str, bool]:
        """
        Retrieves the first channel number from the list of subscribed channels.
        If no subscription info is found, it returns False.
        """
        try:
            subscribed_channels = self.get_subscribed_channels(
                APIQuery.ChannelDesc(channel_number=True, size=1000)
            )
            subscribed_channel_numbers = [
                ch.channel_number
                for ch in subscribed_channels
                if ch.channel_number is not None
            ]
            if not subscribed_channel_numbers:
                log.info("No subscription info found.")
                return False
            first_channel_number = min(subscribed_channel_numbers)
            return str(first_channel_number)
        except AssertionError:
            raise
        except Exception as e:
            log.error("Error while getting first channel number: %s", str(e))
            raise AssertionError(
                f"Failed to get first channel number: {str(e)}")

    def get_missing_channels(self, channel_numbers: List[int]) -> List[int]:
        """
        Retrieves a list of channel numbers that are missing from the provided list of channel numbers.
        The method takes a list of channel numbers and returns a list of channel numbers that are not present
        in the original list.
        """
        try:
            assert isinstance(
                channel_numbers, list), "Channel numbers must be a list"
            assert channel_numbers, "Channel numbers list cannot be empty"

            sorted_channels = sorted(channel_numbers)
            missing_numbers = []
            for i in range(len(sorted_channels) - 1):
                current = sorted_channels[i]
                next_channel = sorted_channels[i + 1]
                if next_channel - current > 1:
                    missing_range = range(current + 1, next_channel)
                    missing_numbers.extend(missing_range)
            return missing_numbers
        except AssertionError:
            raise
        except Exception as e:
            log.error("Error finding missing channels: %s", str(e))
            raise AssertionError(f"Failed to find missing channels: {str(e)}")

    def get_invalid_channel_number(self) -> str:
        """
        Retrieves a channel number that is not present in the list of all available channels.
        This method is used to validate the handling of invalid channel numbers in the UI.
        """
        try:
            # Fetch all channels including adult channels for complete mapping
            all_channels = self._fetch_api_data("CHANNEL", None, is_adult=True)

            if self.natco not in self.SKIP_HU_NATCOS:
                for ch in all_channels:
                    ch_num = ch.get("channel_number")
                    mapped_num = self.map_channel_number(
                        ch_num, to_serial=True)
                    ch["channel_number"] = mapped_num
            assert (
                all_channels
            ), "No channel information available for invalid channel calculation"

            all_channel_numbers = [ch["channel_number"] for ch in all_channels]
            assert (
                all_channel_numbers
            ), "No channel numbers available for invalid channel calculation"

            missing_numbers = self.get_missing_channels(all_channel_numbers)
            if not missing_numbers:
                max_channel = max(all_channel_numbers)
                offset = Utils().generate_random_number()
                non_existing_number = max_channel + offset
            else:
                non_existing_number = random.choice(missing_numbers)
            assert (
                non_existing_number is not None
            ), "Failed to generate invalid channel number"
            assert (
                non_existing_number not in all_channel_numbers
            ), "Generated number is not actually invalid"

            return str(non_existing_number)
        except AssertionError:
            raise
        except Exception as e:
            log.error("Error in get_invalid_channel_number: %s", str(e))
            raise AssertionError(
                f"Failed to get invalid channel number: {str(e)}")

    def get_channel_number_by_index(self, index: int) -> Union[str, bool]:
        """
        Retrieves the channel number at the given 1-based index from the list of subscribed channels.
        Channels are sorted by channel number in ascending order.

        Args:
            index (int): The 1-based position of the desired channel in the sorted list.

        Returns:
            Union[str, bool]: The channel number as a string, or False if the list is empty or index is out of range.
        """
        try:
            assert (
                isinstance(index, int) and index >= 1
            ), f"Index must be a positive integer, got: {index}"

            subscribed_channels = self.get_subscribed_channels(
                APIQuery.ChannelDesc(channel_number=True, size=1000)
            )
            subscribed_channel_numbers = sorted(
                [
                    ch.channel_number
                    for ch in subscribed_channels
                    if ch.channel_number is not None
                ]
            )

            if not subscribed_channel_numbers:
                log.info("No subscription info found.")
                return False

            if index > len(subscribed_channel_numbers):
                log.info(
                    "Index %d is out of range. Total channels: %d.",
                    index,
                    len(subscribed_channel_numbers),
                )
                return False

            return str(subscribed_channel_numbers[index - 1])
        except AssertionError as e:
            log.error("Error while getting subscription info: %s", e)
            raise
        except Exception as e:
            log.error("Error while getting channel by index: %s", str(e))
            raise AssertionError(
                f"Failed to get channel by index {index}: {str(e)}")

    def get_channel_order(self) -> List[int]:
        """
        Fetches channel order directly from the CHANNEL_ORDER API and returns the list.
        """
        try:
            log.info("Fetching channel order data")

            base_url = self.config_manager.get_endpoint(self.language, "BASE")
            endpoint = self.config_manager.get_endpoint(
                self.language, "CHANNEL_ORDER")
            assert base_url, f"Base URL not configured for language: {self.language}"
            assert endpoint, "Endpoint not configured for CHANNEL_ORDER"

            url = f"{base_url}{endpoint}"

            headers = self.config_manager.get_header(self.language, "OTHER")
            params = self.config_manager.get_param(
                self.language, "CHANNEL_INFO")
            assert headers, "Headers not configured for OTHER"
            assert params, "Parameters not configured for CHANNEL_ORDER"

            response_data = self.make_request(
                "GET",
                url,
                headers=headers,
                params=params,
                requires_adult_token=False,
            )
            assert response_data is not None, "No response received from CHANNEL_ORDER API"
            assert isinstance(
                response_data, dict), f"Unexpected response type: {type(response_data)}"

            channel_order = response_data.get("channel_order", [])
            assert isinstance(
                channel_order, list), f"channel_order is not a list: {type(channel_order)}"

            return channel_order

        except AssertionError:
            raise
        except Exception as e:
            log.error("Error retrieving channel order data: %s", str(e))
            raise AssertionError(f"Failed to get channel order data: {str(e)}")

    def channel_order_is_sorted(self) -> dict:
        """
        Checks whether the channel order list is sorted in ascending order.

        Returns:
            dict: {
                "channel_number": list[int],
                "is_sorted": bool
            }
        """
        try:
            channel_order = self.get_channel_order()

            # Efficient O(n) check for ascending order
            sorted = all(
                channel_order[i] <= channel_order[i + 1]
                for i in range(len(channel_order) - 1)
            )

            return {
                "channel_number": channel_order,
                "is_sorted": sorted
            }

        except AssertionError:
            raise
        except Exception as e:
            log.error("Error checking if channel order is sorted: %s", str(e))
            raise AssertionError(
                f"Failed to validate channel order sorting: {str(e)}")

    def get_channel_order(self) -> List[int]:
        """
        Fetches channel order directly from the CHANNEL_ORDER API and returns the list.
        """
        try:
            log.info("Fetching channel order data")

            base_url = self.config_manager.get_endpoint(self.language, "BASE")
            endpoint = self.config_manager.get_endpoint(self.language, "CHANNEL_ORDER")
            assert base_url, f"Base URL not configured for language: {self.language}"
            assert endpoint, "Endpoint not configured for CHANNEL_ORDER"

            url = f"{base_url}{endpoint}"

            headers = self.config_manager.get_header(self.language, "OTHER")
            params = self.config_manager.get_param(self.language, "CHANNEL_INFO")
            assert headers, "Headers not configured for OTHER"
            assert params, "Parameters not configured for CHANNEL_ORDER"

            response_data = self.make_request(
                "GET",
                url,
                headers=headers,
                params=params,
                requires_adult_token=False,
            )
            print("respose data testing :", response_data)
            assert response_data is not None, "No response received from CHANNEL_ORDER API"
            assert isinstance(response_data, dict), f"Unexpected response type: {type(response_data)}"

            channel_order = response_data.get("channel_order", [])
            print("channel order data testing :",channel_order)
            assert isinstance(channel_order, list), f"channel_order is not a list: {type(channel_order)}"

            return channel_order

        except AssertionError:
            raise
        except Exception as e:
            log.error("Error retrieving channel order data: %s", str(e))
            raise AssertionError(f"Failed to get channel order data: {str(e)}")

    def channel_order_is_sorted(self) -> dict:
        """
        Checks whether the channel order list is sorted in ascending order.

        Returns:
            dict: {
                "channel_number": list[int],
                "is_sorted": bool
            }
        """
        try:
            channel_order = self.get_channel_order()

            # Efficient O(n) check for ascending order
            sorted = all(
                channel_order[i] <= channel_order[i + 1]
                for i in range(len(channel_order) - 1)
            )

            return {
                "channel_number" : channel_order,
                "is_sorted": sorted
            }

        except AssertionError:
            raise
        except Exception as e:
            log.error("Error checking if channel order is sorted: %s", str(e))
            raise AssertionError(f"Failed to validate channel order sorting: {str(e)}")


def test_channel_apis() -> List[APIQuery.Channel]:
    """Test basic channel API functionality and return a list of Channel objects."""

    Utils().collect_and_validate_device_info()
    channelApiClient = Interface().channel_api
    log.info("-----------Channel API Results------------------")

    # Test: Get all channel info (both is_audio=True and is_audio=False)
    channelInfo = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000))
    assert channelInfo is not None, "Failed to retrieve channel information"
    assert len(channelInfo) > 0, "No channels found in the system"

    channelNumbers = [
        ch.channel_number for ch in channelInfo if ch.channel_number]
    channelTitles = [ch.title for ch in channelInfo if ch.title]
    log.info(
        "All Channels (Audio and Non-Audio) - Number of Channels: %d",
        len(channelInfo),
    )
    log.info("All Channels (Audio and Non-Audio) - Numbers: %s",
             channelNumbers[:10])
    log.info("All Channels (Audio and Non-Audio) - Titles: %s",
             channelTitles[:10])

    # Test: Get channels with title length filter and is_audio=True
    channelLengthFilter = channelApiClient.get_channels(
        APIQuery.ChannelDesc(min_length=5, max_length=20,
                             is_audio=True, size=10)
    )
    channelNumbers = [
        ch.channel_number for ch in channelLengthFilter if ch.channel_number
    ]
    channelTitles = [ch.title for ch in channelLengthFilter if ch.title]
    log.info(
        "Channel Length Filter (5-20, Radio, Size=10) - Numbers: %s", channelNumbers
    )
    log.info(
        "Channel Length Filter (5-20, Radio, Size=10) - Titles: %s", channelTitles)

    # Test: Get a single channel (default settings)
    singleChannel = channelApiClient.get_channels(APIQuery.ChannelDesc(size=1))
    singleChannelNumbers = [
        ch.channel_number for ch in singleChannel if ch.channel_number
    ]
    singleChannelTitles = [ch.title for ch in singleChannel if ch.title]
    log.info("Single Channel (Default, Size=1) - Numbers: %s",
             singleChannelNumbers)
    log.info("Single Channel (Default, Size=1) - Titles: %s", singleChannelTitles)

    # Test: Get one random channel with title length 5-10 and alphabetic titles
    randomFilteredChannels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(
            min_length=5,
            max_length=10,
            select_alpha=True,
            select_random=True,
            size=1,
        )
    )
    randomFilteredNumbers = [
        ch.channel_number for ch in randomFilteredChannels if ch.channel_number
    ]
    randomFilteredTitles = [
        ch.title for ch in randomFilteredChannels if ch.title]
    log.info(
        "Random Filtered Channel (Length 5-10, Alphabetic, Size=1) - Numbers: %s",
        randomFilteredNumbers,
    )
    log.info(
        "Random Filtered Channel (Length 5-10, Alphabetic, Size=1) - Titles: %s",
        randomFilteredTitles,
    )

    # Test: Get first three audio channels
    audioChannels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(is_audio=True, size=3, select_random=False)
    )
    audioChannelNumbers = [
        ch.channel_number for ch in audioChannels if ch.channel_number
    ]
    audioChannelTitles = [ch.title for ch in audioChannels if ch.title]
    log.info("First Three Audio Channels (Size=3) - Numbers: %s",
             audioChannelNumbers)
    log.info("First Three Audio Channels (Size=3) - Titles: %s",
             audioChannelTitles)

    # Test: Get subscription channels
    subscriptionChannels = channelApiClient.get_subscribed_channels(
        APIQuery.ChannelDesc(channel_number=True, size=1000)
    )
    subscriptionNumbers = [
        ch.channel_number for ch in subscriptionChannels if ch.channel_number
    ]
    subscriptionTitles = [ch.title for ch in subscriptionChannels if ch.title]
    log.info("Subscription Channel Numbers: %s", subscriptionNumbers)
    log.info("Subscription Channel Titles: %s", subscriptionTitles)

    # Test: Get favorite channels
    favoriteChannels = channelApiClient.get_favorite_channels(
        APIQuery.ChannelDesc(channel_number=True, size=1000)
    )
    favoriteNumbers = [
        ch.channel_number for ch in favoriteChannels if ch.channel_number
    ]
    favoriteTitles = [ch.title for ch in favoriteChannels if ch.title]
    log.info("Favorite Channel Numbers: %s", favoriteNumbers)
    log.info("Favorite Channel Titles: %s", favoriteTitles)

    # Test: Get first channel number
    firstChannelNumber = channelApiClient.get_first_channel_number()
    log.info("First Channel Number: %s", firstChannelNumber)

    # Test: Get an invalid channel number
    invalidChannelNumber = channelApiClient.get_invalid_channel_number()
    log.info("Invalid Channel Number: %s", invalidChannelNumber)

    # Test: Get only adult channels
    adult_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=True)
    )
    adult_channel_numbers = [
        ch.channel_number for ch in adult_channels if ch.channel_number
    ]
    adult_channel_titles = [ch.title for ch in adult_channels if ch.title]
    log.info("Adult Channels Only - Count: %d", len(adult_channels))
    log.info("Adult Channel Numbers: %s", adult_channel_numbers)
    log.info("Adult Channel Titles: %s", adult_channel_titles)

    # Test: Get only non-adult channels
    non_adult_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=False)
    )
    log.info("Non-Adult Channels Only - Count: %d", len(non_adult_channels))

    # Test: Get all channels including adult (no adult filter)
    all_channels_no_filter = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000)  # is_adult=None by default
    )
    log.info("All Channels (no filter) - Count: %d",
             len(all_channels_no_filter))

    # Test: Get all channels including adult (explicit method)
    all_channels_including_adult = channelApiClient.get_all_channels_including_adult(
        APIQuery.ChannelDesc(size=1000)
    )
    all_channel_numbers = [
        ch.channel_number for ch in all_channels_including_adult if ch.channel_number
    ]
    all_channel_titles = [
        ch.title for ch in all_channels_including_adult if ch.title]
    adult_in_all = [ch for ch in all_channels_including_adult if ch.is_adult]
    non_adult_in_all = [
        ch for ch in all_channels_including_adult if not ch.is_adult]

    log.info(
        "All Channels Including Adult - Total Count: %d",
        len(all_channels_including_adult),
    )
    log.info("All Channels Including Adult - Adult Count: %d", len(adult_in_all))
    log.info(
        "All Channels Including Adult - Non-Adult Count: %d", len(
            non_adult_in_all)
    )
    log.info(
        "All Channels Including Adult - Sample Numbers: %s...%s",
        all_channel_numbers[:10],
        all_channel_numbers[-10:],
    )
    log.info(
        "All Channels Including Adult - Sample Titles: %s...%s",
        all_channel_titles[:5],
        all_channel_titles[-5:],
    )

    # Test: Get only adult channels
    adult_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=True)
    )
    adult_channel_numbers = [
        ch.channel_number for ch in adult_channels if ch.channel_number
    ]
    adult_channel_titles = [ch.title for ch in adult_channels if ch.title]
    log.info("Adult Channels Only - Count: %d", len(adult_channels))
    log.info("Adult Channel Numbers: %s", adult_channel_numbers)
    log.info("Adult Channel Titles: %s", adult_channel_titles)

    # Test: Get only non-adult channels
    non_adult_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=False)
    )
    log.info("Non-Adult Channels Only - Count: %d", len(non_adult_channels))
    non_adult_channel_numbers = [
        ch.channel_number for ch in non_adult_channels if ch.channel_number
    ]
    non_adult_channel_titles = [
        ch.title for ch in non_adult_channels if ch.title]
    log.info("Non-Adult Channel Numbers: %s", non_adult_channel_numbers)
    log.info("Non-Adult Channel Titles: %s", non_adult_channel_titles)

    # Test: Get all channels including adult (no adult filter)
    all_channels_no_filter = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000)  # is_adult=None by default
    )
    log.info("All Channels (no filter) - Count: %d",
             len(all_channels_no_filter))

    # Test adult filtering behavior
    non_adult_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=False)
    )
    non_adult_count = len(non_adult_channels)
    log.info("Non-Adult Channels (is_adult=False) - Count: %d", non_adult_count)

    adult_enabled_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=True)
    )
    adult_enabled_count = len(adult_enabled_channels)
    log.info("Adult-Enabled Channels (is_adult=True) - Count: %d",
             adult_enabled_count)

    all_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=None)
    )
    all_channels_count = len(all_channels)
    log.info("All Channels (is_adult=None) - Count: %d", all_channels_count)

    # Verify the counts
    assert (
        adult_enabled_count >= non_adult_count
    ), "Adult-enabled should have more or equal channels than non-adult"
    assert (
        all_channels_count == adult_enabled_count
    ), "All channels should equal adult-enabled channels"

    actual_adult_channels = [
        ch for ch in adult_enabled_channels if ch.is_adult]
    actual_non_adult_channels = [
        ch for ch in adult_enabled_channels if not ch.is_adult]

    log.info(
        "Actual adult channels in adult-enabled result: %d", len(
            actual_adult_channels)
    )
    log.info(
        "Actual non-adult channels in adult-enabled result: %d",
        len(actual_non_adult_channels),
    )

    # Test: Get ONLY adult channels
    adult_only_channels = channelApiClient.get_adult_only_channels(
        APIQuery.ChannelDesc(size=1000)
    )
    adult_only_numbers = [
        ch.channel_number for ch in adult_only_channels if ch.channel_number
    ]
    adult_only_titles = [ch.title for ch in adult_only_channels if ch.title]

    log.info("Adult-Only Channels - Count: %d", len(adult_only_channels))
    log.info("Adult-Only Channel Numbers: %s", adult_only_numbers)
    log.info("Adult-Only Channel Titles: %s", adult_only_titles)

    # Verify all returned channels are actually adult channels
    for ch in adult_only_channels:
        assert (
            ch.is_adult
        ), f"Channel {ch.channel_number} should be adult but is_adult={ch.is_adult}"

    log.info("All returned channels are confirmed to be adult channels")

    # Get all channels first to demonstrate the exclude functionality
    all_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, channel_number=True)
    )
    all_channel_numbers = [
        ch.channel_number for ch in all_channels if ch.channel_number
    ]
    log.info("All Channels - Numbers: %s", all_channel_numbers)
    log.info("Total channels before exclude: %d", len(all_channels))

    # Test: Exclude a specific channel (use the last channel number for demonstration)
    if all_channel_numbers:
        exclude_channel = all_channel_numbers[-1]  # Use the last channel
        filtered_channels = channelApiClient.get_channels(
            APIQuery.ChannelDesc(
                size=1000, channel_number=True, exclude_channel_number=exclude_channel
            )
        )
        filtered_channel_numbers = [
            ch.channel_number for ch in filtered_channels if ch.channel_number
        ]

        log.info("Excluding channel: %s", exclude_channel)
        log.info(
            "Channels after excluding %s: %s",
            exclude_channel,
            filtered_channel_numbers,
        )
        log.info("Total channels after exclude: %d", len(filtered_channels))

        # Verify the excluded channel is not in the results
        assert (
            exclude_channel not in filtered_channel_numbers
        ), f"Channel {exclude_channel} should be excluded but was found in results"
        log.info(
            "Exclude functionality verified: Channel %s successfully excluded",
            exclude_channel,
        )

    # Test: First/Last channel functionality
    if all_channels:
        # Test first channel
        first_channel = channelApiClient.get_channels(
            APIQuery.ChannelDesc(first_channel=True)
        )
        if first_channel:
            log.info("First channel: %s", first_channel[0].channel_number)
            log.info("First channel title: %s", first_channel[0].title)

        # Test last channel
        last_channel = channelApiClient.get_channels(
            APIQuery.ChannelDesc(last_channel=True, is_adult=True)
        )
        if last_channel:
            log.info("Last channel: %s", last_channel[0].channel_number)
            log.info("Last channel title: %s", last_channel[0].title)

    # Test 1: exclude_first_last with regular selection (non-random)
    all_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=False)
    )
    all_numbers = [
        ch.channel_number for ch in all_channels if ch.channel_number]
    log.info("All channels: %s", all_numbers)

    # Get channels excluding first and last
    excluded_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(size=1000, is_adult=False,
                             exclude_first_last=True)
    )
    excluded_numbers = [
        ch.channel_number for ch in excluded_channels if ch.channel_number
    ]
    log.info("Channels excluding first/last: %s", excluded_numbers)

    # Verify first and last are excluded
    if len(all_numbers) > 2:
        first_channel = all_numbers[0]
        last_channel = all_numbers[-1]
        assert (
            first_channel not in excluded_numbers
        ), f"First channel {first_channel} should be excluded"
        assert (
            last_channel not in excluded_numbers
        ), f"Last channel {last_channel} should be excluded"
        log.info(
            "First and last channels successfully excluded from regular selection")

    # Test 2: exclude_first_last with random selection
    random_excluded_channels = channelApiClient.get_channels(
        APIQuery.ChannelDesc(
            size=1, is_adult=False, select_random=True, exclude_first_last=True
        )
    )
    random_excluded_numbers = [
        ch.channel_number for ch in random_excluded_channels if ch.channel_number
    ]
    log.info("Random channels excluding first/last: %s",
             random_excluded_numbers)

    # Verify first and last are excluded from random selection
    if len(all_numbers) > 2:
        assert (
            first_channel not in random_excluded_numbers
        ), f"First channel {first_channel} should be excluded from random selection"
        assert (
            last_channel not in random_excluded_numbers
        ), f"Last channel {last_channel} should be excluded from random selection"
        log.info(
            "First and last channels successfully excluded from random selection")

    log.info("-----------------End of Channel API Results----------------")
    return channelInfo


def test_get_subscribed_channels() -> List[APIQuery.Channel]:
    """
    Retrieve subscribed channels using the channel API.
    This function is used to get the list of channels that the user is subscribed to.
    """
    Utils().collect_and_validate_device_info()
    channelApiClient = Interface().channel_api
    log.info("-----------Subscribed Channels------------------")
    subscribed_channels = channelApiClient.get_subscribed_channels(
        APIQuery.ChannelDesc(
            channel_number=True, size=1000, select_random=True, max_length=20
        )
    )
    channel_names = [ch.title for ch in subscribed_channels]
    log.info("Channel name of the subscribed channels: %s", channel_names)

    # Directly select and print the first random channel name
    random_channel_name = channel_names[0]  # First (and only) channel name
    log.info("Selected random channel name: %s", random_channel_name)
    log.info("Subscribed Channels: %s", len(subscribed_channels))

    return subscribed_channels
