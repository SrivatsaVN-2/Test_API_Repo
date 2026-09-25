# mobile_movies_api.py
#
# Movies API client for the mobile touchpoint. Mirrors the parts of
# movies_api.py (STB) needed to fetch real movie titles from an account's
# actual movie rails - not just rail/category names (that's all
# mobile_home_api.py's get_all_rail_info() returns).

from Test_API_Repo.APIs.dtdl.mobile_base_api_client import MobileBaseApiClient
from Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.MobileMovies")


class MobileMoviesApiClient(MobileBaseApiClient):

    # =====================================================
    # 🔹 PAGE CONTENT
    # =====================================================

    def get_page_content(self, page_id=None, content_type=None, offset="0"):
        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        page_url = self.config_manager.get_endpoint(self.language, "PAGE_URL")

        if not content_type:
            content_type = "movies"

        if not page_id:
            page_ids = self.config_manager.get_param(self.language, "PAGE_IDS")
            if page_ids and content_type in page_ids:
                page_id = page_ids[content_type]

        url = f"{base_url}{page_url}".replace("{page_id}", page_id)
        headers = self.config_manager.get_header(self.language, "BFF_OTHER")

        if content_type == "movies":
            params = self.config_manager.get_param(self.language, "MOVIES_CONTENT_PARAM").copy()
        else:
            params = self.config_manager.get_param(self.language, "PAGE_CONTENT_PARAM").copy()

        params["offset"] = offset

        return self.make_request("GET", url, headers=headers, params=params)

    # =====================================================
    # 🔹 ALL PAGE CONTENT (PAGINATED RAILS)
    # =====================================================

    def get_all_page_content(self, content_type="movies"):
        movies_params = self.config_manager.get_param(self.language, "MOVIES_CONTENT_PARAM")
        offsets = movies_params.get("offset", ["0"])

        all_components = []
        seen_rail_ids = set()

        for offset in offsets:
            content = self.get_page_content(content_type=content_type, offset=str(offset))

            if content and "components" in content:
                for component in content["components"]:
                    template_id = component.get("template_id") or ""
                    # Real rail template_ids are e.g. "RAIL_AUTOMATIC"/"RAIL_LIVE",
                    # never the exact literal "RAIL" - substring check, matching
                    # mobile_home_api.py's convention (STB's movies_api.py used an
                    # exact match here, which never matches anything real).
                    if "RAIL" in template_id and template_id != "HIGHLIGHT":
                        rail_id = component["id"]
                        if rail_id not in seen_rail_ids:
                            all_components.append(component)
                            seen_rail_ids.add(rail_id)

        return {"components": all_components}

    # =====================================================
    # 🔹 ACTUAL MOVIE ITEMS PER RAIL
    # =====================================================

    def get_items_from_rails(self, content_type="movies", limit=10):
        content = self.get_all_page_content(content_type=content_type)
        items_by_rail = {}

        if not content:
            return items_by_rail

        # get_all_page_content() already filtered to real rail components.
        for component in content.get("components", []):
            rail_id = component["id"]
            rail_title = component["title"]

            content_details = component.get("content_details", {})
            end_point = content_details.get("end_point", "")

            base_url = self.config_manager.get_endpoint(self.language, "BASE")

            if not end_point:
                items_url = self.config_manager.get_endpoint(self.language, "COMPONENT_URL")
                url = f"{base_url}{items_url.replace('{component_id}', rail_id)}"
                params = self.config_manager.get_param(self.language, "PAGE_CONTENT_PARAM")
            else:
                url = f"{base_url}/{end_point}"
                if content_type == "movies":
                    params = self.config_manager.get_param(self.language, "MOVIES_ITEMS_PARAM")
                else:
                    params = self.config_manager.get_param(self.language, "PAGE_CONTENT_PARAM")

            headers = self.config_manager.get_header(self.language, "BFF_OTHER")

            rail_data = self.make_request("GET", url, headers=headers, params=params)

            if not rail_data:
                log.warning("No data returned for rail: %s", rail_title)
                items_by_rail[rail_title] = []
                continue

            assets = rail_data.get("assets") or rail_data.get("items") or rail_data.get("data") or []
            limited_assets = assets[:limit] if limit and limit > 0 else assets

            items_by_rail[rail_title] = [
                {**item, "index": i} for i, item in enumerate(limited_assets, 1)
            ]

        return items_by_rail
