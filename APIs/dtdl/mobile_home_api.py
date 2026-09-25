# mobile_home_api.py

from typing import List, Dict, Any

from Test_API_Repo.APIs.dtdl.mobile_base_api_client import MobileBaseApiClient
from Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.MobileHome")


class MobileHomeApiClient(MobileBaseApiClient):
    """
    Home page API client for the mobile touchpoint.

    Reuses BaseApiClient for auth/session/header plumbing only. Does not
    touch HomeApiClient (STB) - kept as a separate class so touchpoints can
    diverge (e.g. mobile has no adult content, no linear channel widgets).
    """

    def __init__(self, interface):
        super().__init__(interface=interface)

        self._page_content = None
        self._rail_titles = None

    # =====================================================
    # 🔹 PAGE CONTENT
    # =====================================================

    def get_page_content(self, page_id=None, content_type="mobile_home", requires_auth=True) -> Dict[str, Any]:
        self._page_content = None
        self._rail_titles = None

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        page_url = self.config_manager.get_endpoint(self.language, "PAGE_URL")

        if not page_id:
            page_ids = self.config_manager.get_param(self.language, "PAGE_IDS")
            if page_ids and content_type in page_ids:
                page_id = page_ids[content_type]

        if not page_id:
            raise ValueError(
                f"No page_id configured for content_type='{content_type}' "
                f"(expected under params.PAGE_IDS in config.json)"
            )

        url = f"{base_url}{page_url}".replace("{page_id}", page_id)

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "PAGE_CONTENT_PARAM")

        # requires_auth defaults to True: this should reflect the calling
        # account's actual data (same as STB would see for that account), not
        # generic/anonymous content. Home content happens to also work
        # anonymously (confirmed empirically), so a caller that genuinely
        # doesn't need account-specific data may pass requires_auth=False
        # explicitly - but that's a deliberate choice at the call site, not
        # this class's default behavior.
        self._page_content = self.make_request(
            "GET", url, headers=headers, params=params, requires_auth=requires_auth
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
    # 🔹 ALL RAILS
    # =====================================================

    def get_all_rail_info(self, content_type="mobile_home", requires_auth=True) -> List[Dict[str, Any]]:
        if self._page_content is None:
            self.get_page_content(content_type=content_type, requires_auth=requires_auth)

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
