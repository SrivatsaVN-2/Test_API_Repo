import datetime
import re
from typing import Any, List, Optional
import sys
from pathlib import Path

# add project root directory to python path
ROOT_PATH = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_PATH))
import pytz
#import stbt
from APIs.dtdl.Interface import Interface
from APIs.dtdl.base_api_client import BaseApiClient
from APIs.dtdl.config_manager import Config_Manager
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger
from tests.Test_API_Repo.Utilities.Utils import Utils

"""
from tests.androidtv.api.dtdl.base_api_client import BaseApiClient
from tests.androidtv.api.dtdl.interface import ApiLibrary
from tests.androidtv.libraries.datatype import APIQuery
from tests.androidtv.pages.utility.system_logger import Logger
from tests.androidtv.pages.utility.utils import Utils
"""
log = Logger().setup_logger("EPG.API")


def get_device_timezone():
    """
    Get timezone from stbt configuration for the current device

    Returns:
        str: The timezone string from configuration or default
    
    try:
        default_timezone = "Europe/Lisbon"
        timezone_str = stbt.get_config(
            "device_under_test", "timezone", default_timezone
        )
        return timezone_str
    except Exception as e:
        log.warning("Error getting timezone from config: %s", e)
        return "Europe/Lisbon"
"""

class EpgApiClient(BaseApiClient):
   def __init__(self, interface):
    """
    Initialize the EpgApiClient using the shared Interface object.

    Args:
        interface (Interface): Shared API interface containing runtime configuration.
    """
    try:
        # store interface reference
        self.interface = interface

        # call base client
        super().__init__(interface.config_manager, interface.natco_config)

        self.station_to_channel_map = {}
        self.channels = []

        # access shared values from interface
        self.language = interface.language
        self.device_and_user_details = interface.user_and_device_details
        self.STBConfig = interface.STBConfig

        # initialize utils if needed
        from Utilities.utils import Utils
        self.utils = Utils(interface)

        # initialize channel map
        self._initialize_station_channel_map()

    except Exception as e:
        log.error("Error initializing EpgApiClient: %s", str(e))
    def _initialize_station_channel_map(self) -> List[APIQuery.Channel]:
        """
        Initialize the mapping between station IDs and channel numbers and create a list of APIQuery.Channel objects
        by using the channel_api client instead of making a redundant API call.

        Returns:
            List[APIQuery.Channel]: List of APIQuery.Channel objects created from the Channel API client
        """
        try:
            channel_client = self.interface.channel_api
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
            # log.info("Initialized %d channels", len(self.channels))
            return self.channels
        except Exception as e:
            log.error("Error initializing station to channel mapping: %s", e)
            return []

    def get_channel_for_station(self, station_id: str) -> Optional[int]:
        """
        Get the channel number for a given station ID.

        Args:
            station_id (str): The station ID to look up

        Returns:
            Optional[int]: The channel number if found, None otherwise
        """
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
        """
        Retrieve EPG schedule data for the specified parameters.

        Args:
            date (Optional[str]): Date for which to fetch the schedule in YYYY-MM-DD format.
                                If None, the current date is used.
            hour_offset (int): Starting hour offset (0, 3, 6, 9, 12, 15, 18, or 21).
            station_ids (Optional[List[str]]): List of station IDs to filter.
            channel_numbers (Optional[List[int]]): List of channel numbers to filter.

        Returns:
            dict[str, Any]: The schedule data retrieved from the API.
        """
        try:
            valid_offsets = [0, 3, 6, 9, 12, 15, 18, 21]
            if hour_offset not in valid_offsets:
                log.warning(
                    "Invalid hour_offset %d. Using default value 21.", hour_offset
                )
                hour_offset = 21
            if date is None:
                date = datetime.datetime.now().strftime("%Y-%m-%d")
            base_url = self.config_manager.get_endpoint(self.language, "BASE")
            endpoint = self.config_manager.get_endpoint(self.language, "EPG_SCHEDULE")
            url = f"{base_url}{endpoint}"
            params = self.config_manager.get_param(
                self.language, "EPG_SCHEDULE_PARAM"
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
        except Exception as e:
            log.error("Exception trace:", exc_info=True)
            log.error("Failed to fetch schedule data: %s", str(e))
            raise

    def get_programs(
        self,
        program_desc: Optional[APIQuery.ProgramDesc] = None,
        current_time_only: bool = True,
        day: str = "today",   # "today" | "yesterday" | "tomorrow"
    ) -> List[APIQuery.Program]:
        """
        Retrieve a list of programs based on the provided ProgramDesc criteria, optionally filtered
        to programs airing at the current time in the device's timezone.
        Can also return a single randomly selected program if select_random flag is set in program_desc.

        Args:
            program_desc (Optional[APIQuery.ProgramDesc]): Program description with filtering criteria.
                If None, uses default parameters (is_adult=False, is_subscribed=True,
                is_audio=False, hasTimeshift=False).

            current_time_only (bool): If True, only include programs airing now.
                If False, include all programs.

            day (str): Day for which schedule should be fetched.
                Supported values: "today" (default), "yesterday", "tomorrow".

        Returns:
            List[APIQuery.Program]: List of Program objects containing program details
                or a list with a single randomly selected program if select_random is True.
        """
        try:
            import random

            program_desc = program_desc or APIQuery.ProgramDesc(
                is_adult=False, is_subscribed=True, is_audio=False, hasTimeshift=False
            )

            timezone_str = get_device_timezone()
            try:
                tz = pytz.timezone(timezone_str)
            except pytz.exceptions.UnknownTimeZoneError:
                log.warning("Unknown timezone %s, falling back to UTC", timezone_str)
                tz = pytz.UTC
            current_time = datetime.datetime.now(tz)
            utc_time = current_time.astimezone(pytz.UTC)
            current_hour = utc_time.hour
            valid_offsets = [0, 3, 6, 9, 12, 15, 18, 21]
            hour_offset = max(
                [offset for offset in valid_offsets if offset <= current_hour],
                default=0,
            )
            # date_now = datetime.datetime.now().strftime("%Y-%m-%d")
            
            day_key = (day or "today").strip().lower()
            if day_key == "yesterday":
                schedule_day_offset = -1
            elif day_key == "tomorrow":
                schedule_day_offset = 1
            else:
                schedule_day_offset = 0  # default "today"

            # For non-today days, "live now" filtering doesn't make sense
            if schedule_day_offset != 0 and current_time_only:
                log.info("day=%s so disabling current_time_only", day_key)
                current_time_only = False

            target_utc_date = (datetime.datetime.now() + datetime.timedelta(days=schedule_day_offset)).date()
            date_now = target_utc_date.strftime("%Y-%m-%d")
            schedule_data = self.get_schedule(
                date=date_now, hour_offset=hour_offset, is_adult=program_desc.is_adult
            )

            if not isinstance(schedule_data, dict) or "channels" not in schedule_data:
                log.error("Invalid schedule data format: %s", schedule_data)
                return []

            channel_client = self.api_library.channel_api
            channel_objs = channel_client.get_subscribed_channels(
                APIQuery.ChannelDesc(size=1000), is_adult=program_desc.is_adult
            )
            station_to_channel = {}
            for ch_obj in channel_objs:
                if ch_obj.station_id and ch_obj.channel_number:
                    station_to_channel[ch_obj.station_id] = ch_obj
            result = []
            for station_id, programs in schedule_data["channels"].items():
                if station_id is None:
                    log.warning("Skipping programs with null station_id")
                    continue
                channel_obj = station_to_channel.get(station_id)
                channel_number = channel_obj.channel_number if channel_obj else None

                # Skip this channel if it matches the exclude_channel_number in program_desc
                if (
                    program_desc.exclude_channel_number is not None
                    and channel_number == program_desc.exclude_channel_number
                ):
                    continue

                for program_data in programs:
                    if (
                        program_desc.channel_number
                        and channel_number != program_desc.channel_number
                    ):
                        continue
                    if (
                        program_desc.show_type
                        and program_data.get("show_type", "") != program_desc.show_type
                    ):
                        continue
                    if (
                        program_desc.require_episode_info
                        and program_data.get("show_type") == "TVShow"
                    ):
                        # Check if essential episode information is present and not null
                        series_id = program_data.get("series_id")
                        season_id = program_data.get("season_id")
                        season_number = program_data.get("season_number")
                        episode_number = program_data.get("episode_number")

                        # Skip if any essential episode info is missing or null
                        if (
                            not series_id
                            or not season_id
                            or not season_number
                            or not episode_number
                        ):
                            continue

                    if (
                        program_desc.is_adult is not None
                        and program_data.get("is_adult", False) != program_desc.is_adult
                    ):
                        continue
                    if program_desc.is_audio is not None:
                        is_audio_channel = any(
                            ch.is_audio
                            for ch in channel_objs
                            if ch.station_id == station_id
                        )
                        if is_audio_channel != program_desc.is_audio:
                            continue
                    if (
                        program_desc.recording_available is not None
                        and program_data.get("is_recording_available_content", False)
                        != program_desc.recording_available
                    ):
                        continue
                    if (
                        program_desc.catchup_enabled is not None
                        and program_data.get("is_catchup_enabled", False)
                        != program_desc.catchup_enabled
                    ):
                        continue

                    if program_desc.hasTimeshift is not None:
                        entitlements = program_data.get("entitlements", {})
                        has_timeshift = entitlements.get("hasTimeshift", False)
                        if has_timeshift != program_desc.hasTimeshift:
                            continue

                    if program_desc.is_subscribed is not None:
                        is_subscribed = any(
                            ch.is_subscribed
                            for ch in channel_objs
                            if ch.station_id == station_id
                        )
                        if is_subscribed != program_desc.is_subscribed:
                            continue

                    # NEW: Rating filtering
                    program_rating = program_data.get("ratings")
                    if not program_desc.matches_rating(program_rating):
                        continue

                    description = program_data.get("description", "")
                    if (
                        program_desc.min_length is not None
                        and len(description) < program_desc.min_length
                    ):
                        continue
                    if (
                        program_desc.max_length is not None
                        and len(description) > program_desc.max_length
                    ):
                        continue

                    title = description
                    show_type = program_data.get("show_type", "Unknown")
                    if show_type == "TVShow" and program_data.get("episode_name"):
                        title = f"{description} - {program_data.get('episode_name')}"

                    if (
                        program_desc.max_length is not None
                        and len(title) > program_desc.max_length
                    ):
                        continue

                    if program_desc.select_alpha and title:
                        if not (
                            isinstance(title, str)
                            and all(
                                c.isascii() and (c.isalnum() or c.isspace())
                                for c in title.strip()
                            )
                        ):
                            continue

                    start_time_str = program_data.get("start_time")
                    end_time_str = program_data.get("end_time")
                    if not start_time_str or not end_time_str:
                        continue

                    try:
                        start_time_str = re.sub(r"\.\d+(?=[-+Z])", "", start_time_str)
                        end_time_str = re.sub(r"\.\d+(?=[-+Z])", "", end_time_str)
                        start_time_str = start_time_str.replace("Z", "+00:00")
                        end_time_str = end_time_str.replace("Z", "+00:00")
                        start_time = datetime.datetime.fromisoformat(
                            start_time_str
                        ).astimezone(tz)
                        end_time = datetime.datetime.fromisoformat(
                            end_time_str
                        ).astimezone(tz)
                    except ValueError as e:
                        log.warning(
                            "Error parsing time for program %s: %s (start=%s, end=%s)",
                            title,
                            e,
                            start_time_str,
                            end_time_str,
                        )
                        continue

                    # remaining_minutes = (end_time - current_time).total_seconds() / 60
                    # program_remaining_mins = max(0, remaining_minutes)
                    # if not program_desc.matches_remaining_time(remaining_minutes):
                    #     continue

                    # if current_time_only and not (
                    #     start_time <= current_time <= end_time
                    # ):
                    #     continue
                    
                    is_live = start_time <= current_time <= end_time

                    # Compute remaining time once
                    remaining_minutes = (end_time - current_time).total_seconds() / 60
                    program_remaining_mins = max(0, remaining_minutes)

                    # Apply remaining-time filter ONLY for "today"
                    if schedule_day_offset == 0:
                        if not program_desc.matches_remaining_time(remaining_minutes):
                            continue

                    if current_time_only and not is_live:
                        continue
                    
                    entitlements = program_data.get("entitlements", {})
                    has_timeshift = entitlements.get("hasTimeshift", False)

                    program = APIQuery.Program(
                        station_id=station_id,
                        channel=channel_obj,
                        channel_number=channel_number,
                        program_id=program_data.get("program_id"),
                        description=title,
                        show_type=show_type,
                        start_time=start_time.strftime("%H:%M"),
                        end_time=end_time.strftime("%H:%M"),
                        is_recording_available_content=program_data.get(
                            "is_recording_available_content", False
                        ),
                        is_catchup_enabled=program_data.get(
                            "is_catchup_enabled", False
                        ),
                        full_description=description,
                        episode_name=program_data.get("episode_name"),
                        series_id=program_data.get("series_id"),
                        season_id=program_data.get("season_id"),
                        season_number=program_data.get("season_number"),
                        episode_number=program_data.get("episode_number"),
                        genres=program_data.get("genres", []),
                        release_year=program_data.get("release_year"),
                        is_adult=program_data.get("is_adult", False),
                        entitlements=entitlements,
                        hasTimeshift=has_timeshift,
                        ratings=program_rating,
                        remaining_minutes=program_remaining_mins,
                    )
                    result.append(program)

            station_to_display_number = {}
            for program in result:
                if program.station_id in station_to_channel:
                    station_to_display_number[program.station_id] = station_to_channel[
                        program.station_id
                    ].channel_number
            result.sort(
                key=lambda prog: station_to_display_number.get(
                    prog.station_id, float("inf")
                )
            )

            # If select_random is True and we have results, return a random program
            if program_desc.select_random and result:
                random_program = random.choice(result)
                # log.info("Randomly selected channel: %s", random_program.channel_number)
                return [random_program]  # Return as a list with a single program

            # log.info("Returning %d programs", len(result))
            for prog in result:
                channel_number = station_to_channel.get(prog.station_id, "Unknown")
                # log.info(
                #     "Channel %s (Station %s): %s (%s) | %s-%s, Remaining: %.1f mins, Timeshift: %s",
                #     prog.channel_number,
                #     prog.station_id,
                #     prog.description,
                #     prog.show_type,
                #     prog.start_time,
                #     prog.end_time,
                #     program_remaining_mins,
                #     prog.hasTimeshift,
                # )
            return result
        except Exception as e:
            log.error("Error retrieving programs: %s", str(e))
            return []

