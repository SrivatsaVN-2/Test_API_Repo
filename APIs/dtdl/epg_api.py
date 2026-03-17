import datetime
import re
from typing import Any, List, Optional

import pytz

from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger

log = Logger().setup_logger("EPG.API")


def get_device_timezone():
    """
    Default fallback timezone (STBT removed → no circular dep)
    """
    return "Europe/Lisbon"


class EpgApiClient(BaseApiClient):

    def __init__(self, interface):
        try:
            # ✅ Correct initialization (fixes broken super call)
            super().__init__(interface=interface)

            # -----------------------------------
            # Store interface (already in base, but explicit for clarity)
            # -----------------------------------
            self.interface = interface

            # -----------------------------------
            # Local caches
            # -----------------------------------
            self.station_to_channel_map = {}
            self.channels = []

            # -----------------------------------
            # Direct references (NO getattr hacks)
            # -----------------------------------
            self.utils = interface.utils

            # -----------------------------------
            # Initialize channel mapping
            # -----------------------------------
            self._initialize_station_channel_map()

        except Exception as e:
            log.error("Error initializing EpgApiClient: %s", str(e))
            raise

    # =====================================================
    # 🔹 CHANNEL MAPPING (unchanged logic)
    # =====================================================

    def _initialize_station_channel_map(self) -> List[APIQuery.Channel]:
        try:
            channel_client = self.interface.channel_api()

            channels = channel_client.get_subscribed_channels(
                APIQuery.ChannelDesc(size=1000)
            )

            self.channels = []
            self.station_to_channel_map = {}

            for channel in channels:
                if channel.station_id and channel.channel_number:
                    self.station_to_channel_map[channel.station_id] = (
                        channel.channel_number
                    )
                    self.channels.append(channel)

            return self.channels

        except Exception as e:
            log.error("Error initializing station to channel mapping: %s", e)
            return []

    def get_channel_for_station(self, station_id: str) -> Optional[int]:
        if not self.station_to_channel_map:
            self._initialize_station_channel_map()
        return self.station_to_channel_map.get(station_id)

    # =====================================================
    # 🔹 SCHEDULE API (cleaned but SAME behavior)
    # =====================================================

    def get_schedule(
        self,
        date: Optional[str] = None,
        hour_offset: int = 21,
        station_ids: Optional[List[str]] = None,
        channel_numbers: Optional[List[int]] = None,
        is_adult: Optional[bool] = None,
    ) -> dict[str, Any]:

        try:
            valid_offsets = [0, 3, 6, 9, 12, 15, 18, 21]

            if hour_offset not in valid_offsets:
                log.warning("Invalid hour_offset %d. Using default 21.", hour_offset)
                hour_offset = 21

            if date is None:
                date = datetime.datetime.now().strftime("%Y-%m-%d")

            base_url = self.config_manager.get_endpoint(self.language, "BASE")
            endpoint = self.config_manager.get_endpoint(
                self.language, "EPG_SCHEDULE"
            )

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

            # ✅ Let BaseApiClient handle headers + tokens
            response_data = self.make_request(
                "GET",
                url,
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

    # =====================================================
    # 🔹 PROGRAM FETCH (LOGIC PRESERVED)
    # =====================================================

    def get_programs(
        self,
        program_desc: Optional[APIQuery.ProgramDesc] = None,
        current_time_only: bool = True,
        day: str = "today",
    ) -> List[APIQuery.Program]:

        try:
            import random

            program_desc = program_desc or APIQuery.ProgramDesc(
                is_adult=False,
                is_subscribed=True,
                is_audio=False,
                hasTimeshift=False,
            )

            timezone_str = get_device_timezone()

            try:
                tz = pytz.timezone(timezone_str)
            except pytz.exceptions.UnknownTimeZoneError:
                log.warning("Unknown timezone %s, using UTC", timezone_str)
                tz = pytz.UTC

            current_time = datetime.datetime.now(tz)
            utc_time = current_time.astimezone(pytz.UTC)

            current_hour = utc_time.hour
            valid_offsets = [0, 3, 6, 9, 12, 15, 18, 21]

            hour_offset = max(
                [offset for offset in valid_offsets if offset <= current_hour],
                default=0,
            )

            # -----------------------------------
            # Day handling
            # -----------------------------------
            day_key = (day or "today").strip().lower()

            if day_key == "yesterday":
                schedule_day_offset = -1
            elif day_key == "tomorrow":
                schedule_day_offset = 1
            else:
                schedule_day_offset = 0

            if schedule_day_offset != 0 and current_time_only:
                log.info("day=%s → disabling current_time_only", day_key)
                current_time_only = False

            target_date = (
                datetime.datetime.now()
                + datetime.timedelta(days=schedule_day_offset)
            ).date()

            date_now = target_date.strftime("%Y-%m-%d")

            schedule_data = self.get_schedule(
                date=date_now,
                hour_offset=hour_offset,
                is_adult=program_desc.is_adult,
            )

            if not isinstance(schedule_data, dict) or "channels" not in schedule_data:
                log.error("Invalid schedule format: %s", schedule_data)
                return []

            # -----------------------------------
            # Channel data (no duplicate API calls)
            # -----------------------------------
            channel_objs = self.channels or self._initialize_station_channel_map()

            station_to_channel = {
                ch.station_id: ch
                for ch in channel_objs
                if ch.station_id and ch.channel_number
            }

            result = []

            # =====================================================
            # 🔥 CORE LOOP (UNCHANGED LOGIC)
            # =====================================================

            for station_id, programs in schedule_data["channels"].items():

                if not station_id:
                    continue

                channel_obj = station_to_channel.get(station_id)
                channel_number = (
                    channel_obj.channel_number if channel_obj else None
                )

                if (
                    program_desc.exclude_channel_number is not None
                    and channel_number == program_desc.exclude_channel_number
                ):
                    continue

                for program_data in programs:

                    # ---- (ALL FILTERS KEPT EXACTLY SAME) ----

                    if (
                        program_desc.channel_number
                        and channel_number != program_desc.channel_number
                    ):
                        continue

                    if (
                        program_desc.show_type
                        and program_data.get("show_type") != program_desc.show_type
                    ):
                        continue

                    if (
                        program_desc.is_adult is not None
                        and program_data.get("is_adult", False)
                        != program_desc.is_adult
                    ):
                        continue

                    start_time_str = program_data.get("start_time")
                    end_time_str = program_data.get("end_time")

                    if not start_time_str or not end_time_str:
                        continue

                    try:
                        start_time_str = re.sub(
                            r"\.\d+(?=[-+Z])", "", start_time_str
                        ).replace("Z", "+00:00")

                        end_time_str = re.sub(
                            r"\.\d+(?=[-+Z])", "", end_time_str
                        ).replace("Z", "+00:00")

                        start_time = datetime.datetime.fromisoformat(
                            start_time_str
                        ).astimezone(tz)

                        end_time = datetime.datetime.fromisoformat(
                            end_time_str
                        ).astimezone(tz)

                    except Exception:
                        continue

                    is_live = start_time <= current_time <= end_time

                    remaining_minutes = (
                        end_time - current_time
                    ).total_seconds() / 60

                    if schedule_day_offset == 0:
                        if not program_desc.matches_remaining_time(
                            remaining_minutes
                        ):
                            continue

                    if current_time_only and not is_live:
                        continue

                    program = APIQuery.Program(
                        station_id=station_id,
                        channel=channel_obj,
                        channel_number=channel_number,
                        program_id=program_data.get("program_id"),
                        description=program_data.get("description", ""),
                        show_type=program_data.get("show_type", "Unknown"),
                        start_time=start_time.strftime("%H:%M"),
                        end_time=end_time.strftime("%H:%M"),
                        is_adult=program_data.get("is_adult", False),
                        remaining_minutes=max(0, remaining_minutes),
                    )

                    result.append(program)

            # -----------------------------------
            # Sorting (unchanged)
            # -----------------------------------
            result.sort(
                key=lambda prog: (
                    prog.channel_number if prog.channel_number else float("inf")
                )
            )

            if program_desc.select_random and result:
                return [random.choice(result)]

            return result

        except Exception as e:
            log.error("Error retrieving programs: %s", str(e))
            return []
