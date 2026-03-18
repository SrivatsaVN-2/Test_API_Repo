import datetime
from typing import List, Dict, Any

from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.Home")


class HomeApiClient(BaseApiClient):
    def __init__(self, interface):
        super().__init__(interface=interface)

        self._page_content = None
        self._rail_titles = None
        self._now_on_tv_info = None
        self._current_programs = None

    # =====================================================
    # 🔹 PAGE CONTENT
    # =====================================================

    def get_page_content(self, page_id=None, content_type="home") -> Dict[str, Any]:
        self._page_content = None
        self._rail_titles = None
        self._now_on_tv_info = None

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        page_url = self.config_manager.get_endpoint(self.language, "PAGE_URL")

        if not page_id:
            page_ids = self.config_manager.get_param(self.language, "PAGE_IDS")
            if page_ids and content_type in page_ids:
                page_id = page_ids[content_type]

        url = f"{base_url}{page_url}".replace("{page_id}", page_id)

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "PAGE_CONTENT_PARAM")

        self._page_content = self.make_request(
            "GET", url, headers=headers, params=params
        )

        return self._page_content

    # =====================================================
    # 🔹 RAIL TITLES
    # =====================================================

    def get_rail_components_titles(self) -> List[str]:
        if self._rail_titles is not None:
            return self._rail_titles

        self._rail_titles = []

        if not self._page_content:
            return self._rail_titles

        for component in self._page_content.get("components", []):
            if (
                component.get("template_id")
                and "RAIL" in component.get("template_id")
                and component.get("template_id") != "HIGHLIGHT"
                and component.get("title")
            ):
                self._rail_titles.append(component.get("title"))

        return self._rail_titles

    # =====================================================
    # 🔹 FIRST RAIL
    # =====================================================

    def get_first_rail_info(self, content_type="home") -> Dict[str, Any]:
        if self._now_on_tv_info is not None:
            return self._now_on_tv_info

        self._now_on_tv_info = {
            "present": False,
            "index": None,
            "title": None,
            "component_id": None,
        }

        if self._page_content is None:
            self.get_page_content(content_type=content_type)

        if not self._page_content:
            return self._now_on_tv_info

        rails = [
            comp
            for comp in self._page_content.get("components", [])
            if comp.get("template_id")
            and "RAIL" in comp.get("template_id")
            and comp.get("template_id") != "HIGHLIGHT"
        ]

        if rails:
            first = rails[0]
            self._now_on_tv_info = {
                "present": True,
                "index": 0,
                "title": first.get("title"),
                "component_id": first.get("id"),
            }

        return self._now_on_tv_info

    # =====================================================
    # 🔹 CURRENT PROGRAMS (EPG INTEGRATION)
    # =====================================================

    def get_all_current_programs(
        self, show_types=None, max_program_length=None
    ) -> List[Dict]:

        try:
            if show_types is None:
                show_types = ["TVShow", "Movie"]

            epg_api = self.interface.epg_api()

            program_desc = APIQuery.ProgramDesc(
                is_adult=False,
                is_subscribed=True,
                is_audio=False,
            )

            programs = epg_api.get_programs(
                program_desc=program_desc,
                current_time_only=True,
            )

            result = []

            for program in programs:

                if not program.description:
                    continue

                if max_program_length and len(program.description) > max_program_length:
                    continue

                channel_number = program.channel_number

                if not channel_number:
                    channel_number = epg_api.get_channel_for_station(
                        program.station_id
                    )
                    if not channel_number:
                        continue

                if program.show_type not in show_types:
                    continue

                result.append(
                    {
                        "title": program.description,
                        "station_id": program.station_id,
                        "program_id": program.program_id,
                        "start_time": program.start_time,
                        "end_time": program.end_time,
                        "show_type": program.show_type,
                        "api_channel_number": channel_number,
                        "stb_channel_number": channel_number,
                        "recording_available": program.is_recording_available_content,
                        "catchup_enabled": program.is_catchup_enabled,
                        "remaining_minutes": self._remaining_minutes(
                            program.end_time
                        ),
                    }
                )

            self._current_programs = result
            return result

        except Exception as e:
            log.error(f"Error getting programs: {e}")
            return []

    # =====================================================
    # 🔹 TIME CALC
    # =====================================================

    def _remaining_minutes(self, end_time_str):
        try:
            now = datetime.datetime.now()
            hour, minute = map(int, end_time_str.split(":"))

            end_time = now.replace(hour=hour, minute=minute, second=0)

            if end_time < now:
                end_time += datetime.timedelta(days=1)

            return int((end_time - now).total_seconds() / 60)

        except Exception:
            return 0

    # =====================================================
    # 🔹 NOW ON TV RAIL
    # =====================================================

    def get_now_on_tv_rail_content(self):

        if self._current_programs is None:
            self.get_all_current_programs()

        if not self._current_programs:
            return []

        rail_info = self.get_first_rail_info()

        if not rail_info["present"]:
            return []

        return [
            {
                "program_name": p["title"],
                "channel_number": p["stb_channel_number"],
                "index": i,
            }
            for i, p in enumerate(self._current_programs)
            if p.get("title") and p.get("stb_channel_number")
        ]

    # =====================================================
    # 🔹 ALL RAILS
    # =====================================================

    def get_all_rail_info(self, content_type="home") -> List[Dict[str, Any]]:

        if self._page_content is None:
            self.get_page_content(content_type=content_type)

        if not self._page_content:
            return []

        rails = [
            comp
            for comp in self._page_content.get("components", [])
            if comp.get("template_id")
            and "RAIL" in comp.get("template_id")
            and comp.get("template_id") != "HIGHLIGHT"
        ]

        return [
            {
                "present": True,
                "index": i,
                "title": rail.get("title"),
                "component_id": rail.get("id"),
            }
            for i, rail in enumerate(rails)
        ]
