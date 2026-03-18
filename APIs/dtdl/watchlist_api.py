from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.WatchList")


class WatchListApiClient(BaseApiClient):

    def __init__(self, interface):
        super().__init__(interface=interface)

    # =====================================================
    # 🔹 FETCH WATCHLIST
    # =====================================================

    def get_page_content(self, content_type=None, isAdult=False):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")

        if isAdult:
            end_point_url = self.config_manager.get_endpoint(
                self.language, "ADULT_WATCHLIST"
            )
            headers = self.config_manager.get_header(self.language, "BFF_OTHER")
            params = self.config_manager.get_param(
                self.language, "ADULT_CONTENT_PARAM"
            ).copy()
            params["offset"] = 0
            requires_adult_token = True

        else:
            end_point_url = self.config_manager.get_endpoint(
                self.language, "MY_WATCHLIST"
            )
            headers = self.config_manager.get_header(self.language, "BFF_OTHER")
            params = self.config_manager.get_param(
                self.language, "SUBSCRIPTION_INFO"
            )
            requires_adult_token = False

        content_type = content_type or "watchlist"

        url = f"{base_url}{end_point_url}"

        return self.make_request(
            "GET",
            url,
            headers=headers,
            params=params,
            requires_adult_token=requires_adult_token,
        )

    # =====================================================
    # 🔹 OBJECT CREATION
    # =====================================================

    def _create_watchlist_object(self, watchlist_data):

        return APIQuery.WatchList(
            id=watchlist_data.get("id"),
            type=watchlist_data.get("type"),
            title=watchlist_data.get("name") or watchlist_data.get("title"),
            rating=watchlist_data.get("ratings")
            or watchlist_data.get("rating"),
        )

    # =====================================================
    # 🔹 FILTERING
    # =====================================================

    def _filter_watchlist_content(self, watchlists, watchlist_desc=None):

        filtered = []

        for watchlist in watchlists:

            if (
                getattr(watchlist_desc, "type", None)
                and watchlist.type != watchlist_desc.type
            ):
                continue

            if (
                getattr(watchlist_desc, "title", None)
                and watchlist.title != watchlist_desc.title
            ):
                continue

            if (
                getattr(watchlist_desc, "rating", None)
                and str(watchlist.rating) != str(watchlist_desc.rating)
            ):
                continue

            filtered.append(watchlist)

        return filtered

    # =====================================================
    # 🔹 MAIN API
    # =====================================================

    def get_watchlist_content(self, watchlist_desc=None, isAdult=False):
        """
        Get watchlist content
        """

        try:
            response = self.get_page_content(
                content_type="watchlist",
                isAdult=isAdult,
            )

            if isAdult:
                items = response.get("assets", [])
            else:
                items = response.get("items", [])

            if not items:
                log.info("No watchList content found")
                return []

            watchlist_items = [
                self._create_watchlist_object(item) for item in items
            ]

            log.info(
                "Total watchList content fetched: %s", len(watchlist_items)
            )

            return self._filter_watchlist_content(
                watchlist_items, watchlist_desc
            )

        except Exception as e:
            log.error("Error fetching watchList data: %s", str(e))
            return None
