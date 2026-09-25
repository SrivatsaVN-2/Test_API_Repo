# mobile_search_api.py
#
# Search API client for the mobile touchpoint. Used here not to validate
# search itself, but as a source of real, catalog-wide movie/series titles -
# unlike home/movies rails, SEARCH isn't limited to the account's own
# entitlements/viewing history, so it still returns real titles even for an
# account with no personalized content (e.g. test777, which has none - see
# conversation history). One call returns movies (`movies`), series
# (`tv_shows`), and people (`persons`) in the same response.

from Test_API_Repo.APIs.dtdl.mobile_base_api_client import MobileBaseApiClient
from Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.MobileSearch")


class MobileSearchApiClient(MobileBaseApiClient):

    def search_movie(self, query, size=None):
        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        endpoint = self.config_manager.get_endpoint(self.language, "SEARCH_URL")
        url = f"{base_url}{endpoint}"

        params = self.config_manager.get_param(self.language, "CHANNEL_INFO").copy()
        params["text_search"] = query
        if size is not None:
            # API default is 25 if omitted; 100 is the confirmed max (size>100
            # returns 400 Bad Request) - see conversation history.
            params["size"] = str(size)

        headers = self.config_manager.get_header(self.language, "OTHER")

        log.info("Searching catalog for: %s (size=%s)", query, size)
        return self.make_request("GET", url, headers=headers, params=params)

    def get_movies_array(self, search_result):
        return (search_result or {}).get("movies", [])

    def get_tv_shows_array(self, search_result):
        return (search_result or {}).get("tv_shows", [])

    def get_persons_array(self, search_result):
        return (search_result or {}).get("persons", [])
