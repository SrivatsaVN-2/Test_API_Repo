from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.androidtv.pages.utility.system_logger import Logger

log = Logger().setup_logger("API.Series")


class SeriesApiClient(BaseApiClient):
    """
    Client for interacting with series/TV shows related API endpoints.
    """

    def __init__(self, interface):
        super().__init__(interface=interface)

    # =====================================================
    # 🔹 PAGE CONTENT
    # =====================================================

    def get_page_content(self, page_id=None, content_type="series", offset="0"):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        page_url = self.config_manager.get_endpoint(self.language, "PAGE_URL")

        if not page_id:
            page_ids = self.config_manager.get_param(self.language, "PAGE_IDS")
            if page_ids and content_type in page_ids:
                page_id = page_ids[content_type]

        url = f"{base_url}{page_url}".replace("{page_id}", page_id)

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")

        params = self.config_manager.get_param(
            self.language, "PAGE_CONTENT_PARAM"
        ).copy()

        params["offset"] = offset

        return self.make_request("GET", url, headers=headers, params=params)

    # =====================================================
    # 🔹 ALL PAGE CONTENT (MULTI OFFSET)
    # =====================================================

    def get_all_page_content(self, content_type="series"):

        page_params = self.config_manager.get_param(
            self.language, "PAGE_CONTENT_PARAM"
        )

        offsets = page_params.get("offset", ["0"])

        if not isinstance(offsets, list):
            offsets = [offsets]

        all_components = []
        seen_rail_ids = set()

        for offset in offsets:

            content = self.get_page_content(
                content_type=content_type,
                offset=str(offset),
            )

            if content and "components" in content:

                for component in content["components"]:

                    if component.get("template_id") == "RAIL":

                        rail_id = component["id"]

                        if rail_id not in seen_rail_ids:
                            all_components.append(component)
                            seen_rail_ids.add(rail_id)

        return {"components": all_components}

    # =====================================================
    # 🔹 ITEMS FROM RAILS
    # =====================================================

    def get_items_from_rails(self, content_type="series", limit=10):

        content = self.get_all_page_content(content_type=content_type)

        items_by_rail = {}

        if content:

            for component in content.get("components", []):

                if component.get("template_id") == "RAIL":

                    rail_id = component["id"]
                    rail_title = component["title"]

                    content_details = component.get("content_details", {})
                    end_point = content_details.get("end_point", "")

                    base_url = self.config_manager.get_endpoint(
                        self.language, "BASE"
                    )

                    if not end_point:

                        log.warning(
                            "No end_point found for rail: %s, falling back",
                            rail_title,
                        )

                        items_url = self.config_manager.get_endpoint(
                            self.language, "COMPONENT_URL"
                        )

                        url = f"{base_url}{items_url.replace('{component_id}', rail_id)}"

                        params = self.config_manager.get_param(
                            self.language, "PAGE_CONTENT_PARAM"
                        )

                    else:

                        url = f"{base_url}/{end_point}"

                        params = self.config_manager.get_param(
                            self.language, "PAGE_CONTENT_PARAM"
                        )

                    headers = self.config_manager.get_header(
                        self.language, "BFF_OTHER"
                    )

                    rail_data = self.make_request(
                        "GET",
                        url,
                        headers=headers,
                        params=params,
                    )

                    if rail_data:

                        assets = (
                            rail_data.get("assets", [])
                            or rail_data.get("items", [])
                            or rail_data.get("data", [])
                        )

                        limited_assets = (
                            assets[:limit] if limit and limit > 0 else assets
                        )

                        items_with_index = [
                            {**item, "index": index}
                            for index, item in enumerate(limited_assets, 1)
                        ]

                        items_by_rail[rail_title] = items_with_index

                    else:
                        log.warning("No data returned for rail: %s", rail_title)
                        items_by_rail[rail_title] = []

        return items_by_rail

    # =====================================================
    # 🔹 ASSET ACTIONS
    # =====================================================

    def get_asset_actions(self, asset_id):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")

        asset_action_url = self.config_manager.get_endpoint(
            self.language, "ASSET_ACTION_URL"
        )

        url = f"{base_url}{asset_action_url.replace('{asset_id}', asset_id)}"

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")

        params = self.config_manager.get_param(self.language, "CHANNEL_INFO")

        try:
            return self.make_request(
                "GET",
                url,
                headers=headers,
                params=params,
            )

        except Exception as e:
            log.error("Failed to fetch asset actions for %s: %s", asset_id, str(e))
            return None
