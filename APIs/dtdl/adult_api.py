from typing import List, Dict
import random

from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger

log = Logger().setup_logger("API.Adult")


class AdultApiClient(BaseApiClient):
    def __init__(self, interface):
        super().__init__(interface=interface)

    # =====================================================
    # 🔹 PAGE CONTENT (ADULT)
    # =====================================================

    def get_page_content(self, page_id=None, content_type="adult"):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        page_url = self.config_manager.get_endpoint(self.language, "PAGE_URL")

        has_rentals = bool(self.get_rental_watchlist_content(check_rental=True))
        has_watchlist = bool(self.get_rental_watchlist_content(check_watchlist=True))

        if not page_id:
            page_ids = self.config_manager.get_param(self.language, "PAGE_IDS")
            if page_ids and content_type in page_ids:
                page_id = page_ids[content_type]

        url = f"{base_url}{page_url}".replace("{page_id}", page_id)

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "ADULT_CONTENT_PARAM")

        unique_rails = []
        seen_titles = set()
        has_highlight = False

        offsets = params.get("offset", ["0"])
        if not isinstance(offsets, list):
            offsets = [offsets]

        for offset in offsets:
            params["offset"] = offset

            response = self.make_request(
                "GET",
                url,
                headers=headers,
                params=params,
                requires_adult_token=True,
            )

            if not response:
                continue

            for comp in response.get("components", []):

                if comp.get("template_id") == "HIGHLIGHT":
                    has_highlight = True

                if comp.get("is_adult") and comp.get("template_id") == "RAIL":

                    details = comp.get("content_details", {})
                    rail_title = comp.get("title")

                    is_rental = details.get("tag") == "rentals"
                    is_watchlist = details.get("tag") == "watchlist"

                    if (
                        (is_rental and has_rentals)
                        or is_watchlist
                        or has_watchlist
                        or (
                            comp.get("type", "") == ""
                            and details.get("type") != "subscriber"
                        )
                    ):
                        if rail_title and rail_title not in seen_titles:
                            seen_titles.add(rail_title)
                            unique_rails.append(comp)

        return {"rails": unique_rails, "has_highlight": has_highlight}

    # =====================================================
    # 🔹 FETCH RAIL ITEMS
    # =====================================================

    def get_single_rail_items(self, rail):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "ADULT_CONTENT_PARAM")

        endpoint = rail.get("content_details", {}).get("end_point")

        if not endpoint:
            return None

        url = f"{base_url}/{endpoint}"

        try:
            return self.make_request(
                "GET",
                url,
                headers=headers,
                params=params,
                requires_adult_token=True,
            )
        except Exception as e:
            log.error(f"Rail fetch failed: {e}")
            return None

    def get_items_from_rails(self, rails):
        return {r.get("id"): self.get_single_rail_items(r) for r in rails}

    # =====================================================
    # 🔹 ASSET ACTIONS
    # =====================================================

    def get_asset_actions(self, asset_id):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        endpoint = self.config_manager.get_endpoint(
            self.language, "ASSET_ACTION_URL"
        )

        url = f"{base_url}{endpoint.replace('{asset_id}', asset_id)}"

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "ADULT_INFO")

        try:
            return self.make_request(
                "GET",
                url,
                headers=headers,
                params=params,
                requires_adult_token=True,
            )
        except Exception as e:
            log.error(f"Asset action failed: {e}")
            return None

    # =====================================================
    # 🔹 RENTAL / WATCHLIST
    # =====================================================

    def get_rental_watchlist_content(self, check_rental=False, check_watchlist=False):

        if not any([check_rental, check_watchlist]):
            return []

        endpoint_map = {
            "rental": "RENTAL_ADULT",
            "watchlist": "ADULT_WATCHLIST",
        }

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "ADULT_CONTENT_PARAM")

        results = []

        for key, flag in [
            ("rental", check_rental),
            ("watchlist", check_watchlist),
        ]:
            if not flag:
                continue

            endpoint = self.config_manager.get_endpoint(
                self.language, endpoint_map[key]
            )

            url = f"{base_url}{endpoint}"

            response = self.make_request(
                "GET",
                url,
                headers=headers,
                params=params,
                requires_adult_token=True,
            )

            if response and "assets" in response:
                results.extend([a.get("title") for a in response["assets"]])

        return results

    # =====================================================
    # 🔹 MAIN ADULT CONTENT
    # =====================================================

    def get_adult_content(self, adult_desc=None) -> List[APIQuery.Adult]:

        adult_desc = adult_desc or APIQuery.AdultDesc()

        page = self.get_page_content()
        rails = page.get("rails", [])

        result = []

        for rail_index, rail in enumerate(rails):

            if adult_desc.rail_index is not None and rail_index != adult_desc.rail_index:
                continue

            rail_title = rail.get("title")

            if adult_desc.rail_title and rail_title != adult_desc.rail_title:
                continue

            data = self.get_single_rail_items(rail)

            if not data or "assets" not in data:
                continue

            for asset_index, asset in enumerate(data["assets"]):

                asset_id = asset.get("id")
                if not asset_id:
                    continue

                actions = self.get_asset_actions(asset_id)
                if not actions:
                    continue

                # 🔥 minimal filtering retained (core logic)
                episode_name = asset.get("title", "")

                content = APIQuery.Adult(
                    id=asset_id,
                    episode_name=episode_name,
                    rail_title=rail_title,
                    rail_index=rail_index,
                    position={"rail_index": rail_index, "asset_index": asset_index},
                )

                result.append(content)

                if len(result) >= adult_desc.size:
                    break

            if len(result) >= adult_desc.size:
                break

        # 🔹 Random selection
        if adult_desc.select_random and result:
            return [random.choice(result)]

        return result[: adult_desc.size]

    # =====================================================
    # 🔹 UTILS
    # =====================================================

    def get_program_names_only_alphabets(self, names):
        return [n for n in names if all(c.isalpha() or c.isspace() for c in n)]
