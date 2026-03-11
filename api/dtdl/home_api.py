import datetime
from typing import List, Dict, Any



class HomeApiClient:

    def __init__(self, data_interface):

        self.data_interface = data_interface
        self.APIQuery = data_interface.APIQuery
        self.language = data_interface.language

        self._page_content = None
        self._rail_titles = None
        self._now_on_tv_info = None
        self._current_programs = None

    def get_page_content(self, page_id=None, content_type=None) -> Dict[str, Any]:

        self._page_content = None
        self._rail_titles = None
        self._now_on_tv_info = None

        if not content_type:
            content_type = "home"

        if not page_id:

            page_ids = self.data_interface.get_params("PAGE_IDS")

            if page_ids and content_type in page_ids:
                page_id = page_ids[content_type]

        params = self.data_interface.get_params("PAGE_CONTENT_PARAM")

        response = self.data_interface.request(
            method="GET",
            endpoint="PAGE_URL",
            params=params,
            headers_type="BFF_OTHER",
        )

        self._page_content = response

        return self._page_content

    def get_rail_components_titles(self) -> List[str]:

        if self._rail_titles is not None:
            return self._rail_titles

        self._rail_titles = []

        if not self._page_content or "components" not in self._page_content:
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
