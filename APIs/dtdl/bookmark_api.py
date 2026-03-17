from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.androidtv.pages.utility.system_logger import Logger


log = Logger().setup_logger("API.Bookmark")


class BookMarkApiClient(BaseApiClient):

    def __init__(self, interface):
        super().__init__(interface=interface)

    # =====================================================
    # 🔹 FETCH BOOKMARK PAGE
    # =====================================================

    def get_page_content(self, content_type="bookMark"):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        bookmark_url = self.config_manager.get_endpoint(self.language, "BOOKMARK")

        url = f"{base_url}{bookmark_url}"

        log.info(f"Fetching {content_type} from URL: {url}")

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")

        return self.make_request("GET", url, headers=headers)

    # =====================================================
    # 🔹 OBJECT CREATION
    # =====================================================

    def _create_bookmark_object(self, data):

        return APIQuery.BookMark(
            id=data.get("id"),
            type=data.get("type"),
            title=data.get("title"),
            deeplink=data.get("cta", {}).get("deeplink", ""),
        )

    # =====================================================
    # 🔹 FILTERING
    # =====================================================

    def _filter_bookmark_content(self, bookmarks, desc=None):

        if not desc:
            return bookmarks

        result = []

        for bm in bookmarks:

            if getattr(desc, "type", None) and bm.type != desc.type:
                continue

            if getattr(desc, "title", None) and bm.title != desc.title:
                continue

            result.append(bm)

        return result

    # =====================================================
    # 🔹 MAIN API
    # =====================================================

    def get_bookmark_content(self, bookMarkDesc=None):

        try:
            response = self.get_page_content()

            assets = response.get("bookmarks", [])

            if not assets:
                log.info("No bookmarks found")
                return {"count": 0, "bookmarks": []}

            bookmarks = [
                self._create_bookmark_object(item) for item in assets
            ]

            filtered = self._filter_bookmark_content(bookmarks, bookMarkDesc)

            log.info(f"Total bookmarks fetched: {len(filtered)}")

            return {
                "count": len(filtered),
                "bookmarks": filtered,
            }

        except Exception as e:
            log.error(f"Error fetching bookmarks: {e}")
            return {"count": 0, "bookmarks": []}
