from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.androidtv.pages.utility.system_logger import Logger


log = Logger().setup_logger("API.Recording")


class RecordingApiClient(BaseApiClient):

    def __init__(self, interface):
        super().__init__(interface=interface)

    # =====================================================
    # 🔹 FETCH RECORDINGS PAGE
    # =====================================================

    def get_page_content(self, page_id=None, content_type=None):
        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        page_url = self.config_manager.get_endpoint(self.language, "RECORDINGS_URL")

        if not content_type:
            content_type = "recordings"

        url = f"{base_url}{page_url}"

        log.info(f"Fetching {content_type} from URL: {url}")

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "RECORDING_PARAM")

        log.info(
            f"Fetching {content_type} from URL: {url} with params: {params} and headers: {headers}"
        )

        return self.make_request("GET", url, headers=headers, params=params)

    # =====================================================
    # 🔹 OBJECT CREATION
    # =====================================================

    def _create_recording_object(self, recording_data):

        series_detail = recording_data.get("series_detail")

        if series_detail:
            get_series_status = [
                {
                    series_detail.get("title", "Unknown"): series_detail.get(
                        "item_state", "unknown"
                    )
                }
            ]
        else:
            get_series_status = []

        title = None

        if recording_data.get("type") == "Series":
            title = recording_data.get("series_detail", {}).get("title")

        elif recording_data.get("type") == "SingleProgram":
            program_details = recording_data.get("program_details", {})
            for programs in program_details.values():
                if programs:
                    title = programs[0].get("name")
                    break

        program_id = recording_data.get("program_details", {})

        item_state = None
        if recording_data.get("type") == "Series":
            item_state = recording_data["series_detail"]["item_state"]

        program_status_dict = {}

        for episode_list in program_id.values():

            if recording_data.get("type") != "Series":
                item_state = episode_list[0].get("item_state")

            for episode in episode_list:
                program_status_dict[episode["name"]] = episode["item_state"]

        program_status_list = [program_status_dict]

        return APIQuery.Recordings(
            title=title,
            id=recording_data.get("id"),
            type=recording_data.get("type"),
            is_recording_complete_series=recording_data.get(
                "is_recording_complete_series"
            ),
            item_state=item_state,
            is_series=True if get_series_status else False,
            is_singleprogram=True
            if recording_data["type"] != "Series"
            else False,
            series_detail=get_series_status,
            program_detail=program_status_list,
        )

    # =====================================================
    # 🔹 FILTERING
    # =====================================================

    def _filter_recordings(self, recordings, filter_criteria):

        filtered_recordings = []

        for recording in recordings:

            if (
                getattr(filter_criteria, "type", None)
                and recording.type != filter_criteria.type
            ):
                continue

            if (
                getattr(filter_criteria, "item_state", None)
                and recording.item_state != filter_criteria.item_state
            ):
                continue

            filtered_recordings.append(recording)

        log.info(f"Filtered recordings count: {len(filtered_recordings)}")

        return filtered_recordings

    # =====================================================
    # 🔹 MAIN API
    # =====================================================

    def get_recordings(
        self,
        filter_criteria=APIQuery.RecordingsDesc(
            type="SingleProgram",
            item_state="recorded",
        ),
    ):
        """
        Fetch recordings and apply optional filtering
        """

        response = self.get_page_content(content_type="recordings")

        if not response or "recordings" not in response:
            log.warning("RecordingApi: No response or missing recordings list.")
            return []

        data = response["recordings"]

        recordings = [self._create_recording_object(r) for r in data]

        log.info("RecordingApi: Total recordings fetched: %s", len(recordings))

        if filter_criteria is None:
            return recordings

        filtered = self._filter_recordings(recordings, filter_criteria)

        log.info("RecordingApi: Filtered recordings count: %s", len(filtered))

        if len(filtered) == 0:
            log.warning(
                "RecordingApi: No recordings matched the filter (%s). Dumping mismatches...",
                filter_criteria,
            )

            for r in recordings:
                log.info(
                    "Mismatch → title=%s type=%s state=%s",
                    getattr(r, "title", None),
                    getattr(r, "type", None),
                    getattr(r, "item_state", None),
                )

        return filtered

    # =====================================================
    # 🔹 INTERNAL PARSER
    # =====================================================

    def __parse_tv_recordings(self, data):

        result = {"recordings": {}, "scheduled_recordings": {}}

        for recording in data.get("recordings", []):

            recording_type = recording.get("type")

            if recording_type == "Series":

                series_title = recording.get("series_detail", {}).get(
                    "title", "Unknown Series"
                )

                program_details = recording.get("program_details", {})

                for _, episodes in program_details.items():

                    for episode in episodes:

                        item_state = episode.get("item_state")
                        season_number = episode.get(
                            "season_number", "Unknown Season"
                        )

                        if series_title not in result["recordings"]:
                            result["recordings"][series_title] = {}

                        if series_title not in result["scheduled_recordings"]:
                            result["scheduled_recordings"][series_title] = {}

                        season_key = f"season {season_number}"

                        if item_state == "recorded":

                            result["recordings"][series_title].setdefault(
                                season_key, {"recording": 0}
                            )
                            result["recordings"][series_title][season_key][
                                "recording"
                            ] += 1

                        elif item_state == "scheduled":

                            result["scheduled_recordings"][series_title].setdefault(
                                season_key, {"scheduled_recording": 0}
                            )
                            result["scheduled_recordings"][series_title][season_key][
                                "scheduled_recording"
                            ] += 1

            elif recording_type == "SingleProgram":

                program_details = recording.get("program_details", {})

                for _, episodes in program_details.items():

                    for episode in episodes:

                        program_name = episode.get("name", "Unknown Program")
                        item_state = episode.get("item_state")

                        if item_state == "recorded":

                            result["recordings"].setdefault(
                                program_name, {"recording": 0}
                            )
                            result["recordings"][program_name]["recording"] += 1

                        elif item_state == "scheduled":

                            result["scheduled_recordings"].setdefault(
                                program_name, {"scheduled_recording": 0}
                            )
                            result["scheduled_recordings"][program_name][
                                "scheduled_recording"
                            ] += 1

        result["recordings"] = {k: v for k, v in result["recordings"].items() if v}
        result["scheduled_recordings"] = {
            k: v for k, v in result["scheduled_recordings"].items() if v
        }

        return result

    # =====================================================
    # 🔹 SUMMARY APIs
    # =====================================================

    def get_recording_overview(self):
        response = self.get_page_content(content_type="recordings")
        return self.__parse_tv_recordings(response)

    def get_recording_program_names(self):

        recordings = self.get_recordings(filter_criteria=None)

        scheduled_programs = []

        for recording in recordings:

            if getattr(recording, "item_state", None) == "recording":

                title = getattr(recording, "title", None)

                if title:
                    scheduled_programs.append(title)

        log.info("Scheduled programs count: %s", len(scheduled_programs))

        return scheduled_programs
