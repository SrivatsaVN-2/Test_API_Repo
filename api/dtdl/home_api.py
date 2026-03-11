import datetime
from typing import List, Dict, Any

from .base_api_client import BaseApiClient
from .models.api_query import APIQuery


class HomeApiClient(BaseApiClient):

    def __init__(self, config_manager, natco):

        super().__init__(config_manager, natco)

        self._page_content = None
        self._rail_titles = None
        self._now_on_tv_info = None
        self._current_programs = None

    def get_page_content(self, page_id=None, content_type=None) -> Dict[str, Any]:

        self._page_content = None
        self._rail_titles = None
        self._now_on_tv_info = None

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        page_url = self.config_manager.get_endpoint(self.language, "PAGE_URL")

        if not content_type:
            content_type = "home"

        if not page_id:

            page_ids = self.config_manager.get_param(
                self.language,
                "PAGE_IDS"
            )

            if page_ids and content_type in page_ids:
                page_id = page_ids[content_type]

        url = f"{base_url}{page_url}".replace("{page_id}", page_id)

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")

        params = self.config_manager.get_param(
            self.language,
            "PAGE_CONTENT_PARAM"
        )

        self._page_content = self.make_request(
            "GET",
            url,
            headers=headers,
            params=params,
        )

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
