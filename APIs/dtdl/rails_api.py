from .const.rail_constant import Category, CATEGORY_TITLES

from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.Rails")


class RailsApiClient(BaseApiClient):

    device_type = "ANDROIDTV"

    def __init__(self, interface):
        super().__init__(interface=interface)

    # =====================================================
    # 🔹 ROOT CATEGORY → PAGE ID
    # =====================================================

    def get_root_category_page_id(
        self, category: str, app_language: str | None = None
    ) -> str:

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        root_category_url = self.config_manager.get_endpoint(
            self.language, "ROOT_CATEGORY"
        )

        url = f"{base_url}{root_category_url}"

        headers = self.config_manager.get_header(self.language, "OTHER")

        params = self.config_manager.get_param(self.language, "CHANNEL_INFO").copy()
        params["device_type"] = self.device_type

        if app_language is not None:
            params["app_language"] = app_language

        effective_app_language = params.get("app_language")

        resolved_title = self._resolve_category_title(
            category, effective_app_language
        )

        root_category_data = self.make_request(
            "GET", url, headers=headers, params=params
        )

        categories = root_category_data.get("categories", [])

        for cat in categories:
            if cat.get("title") == resolved_title:
                page_id = cat.get("page_id")
                if page_id is None:
                    raise ValueError(
                        f"Category '{resolved_title}' found but missing 'page_id'"
                    )
                return page_id

        raise ValueError(f"No category found with title '{resolved_title}'")

    # =====================================================
    # 🔹 CATEGORY TITLE RESOLUTION
    # =====================================================

    def _resolve_category_title(
        self,
        category_or_title: str,
        app_language: str | None,
    ) -> str:

        if category_or_title in CATEGORY_TITLES:

            if not app_language:
                raise ValueError(
                    f"Cannot resolve category '{category_or_title}' because app_language is missing."
                )

            lang_map = CATEGORY_TITLES.get(category_or_title, {})
            resolved_title = lang_map.get(app_language)

            if not resolved_title:
                raise ValueError(
                    f"Category '{category_or_title}' not configured for app_language '{app_language}'."
                )

            return resolved_title

        return category_or_title.strip()

    # =====================================================
    # 🔹 FETCH PAGE CONTENT
    # =====================================================

    def get_page_content_by_page_id(
        self,
        page_id: str,
        app_language: str | None = None,
        offset: int = 0,
        extra_params: dict | None = None,
    ):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        page_url = self.config_manager.get_endpoint(self.language, "PAGE_URL")

        url = f"{base_url}{page_url}".replace("{page_id}", page_id)

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")

        params = self.config_manager.get_param(
            self.language, "PAGE_CONTENT_PARAM"
        ).copy()

        params["offset"] = str(offset)

        if app_language is not None:
            params["app_language"] = app_language

        if extra_params:
            params.update(extra_params)

        return self.make_request("GET", url, headers=headers, params=params)

    # =====================================================
    # 🔹 PAGINATED FETCH (ALL RAILS)
    # =====================================================

    def get_all_page_content(
        self,
        page_id: str,
        app_language: str,
        start_offset: int = 0,
        extra_params: dict | None = None,
        exclude_templates: set[str] | None = None,
    ):

        exclude_templates = exclude_templates or set()

        all_components = []
        seen_ids = set()

        offset = int(start_offset)

        while True:

            data = self.get_page_content_by_page_id(
                page_id=page_id,
                app_language=app_language,
                offset=offset,
                extra_params=extra_params,
            )

            if not data:
                break

            raw_components = data.get("components") or []

            components = [
                c for c in raw_components
                if c.get("template_id") not in exclude_templates
            ]

            for c in components:
                cid = c.get("id")

                if cid and cid in seen_ids:
                    continue

                if cid:
                    seen_ids.add(cid)

                all_components.append(c)

            next_offset = data.get("next_offset", -1)

            if next_offset in (-1, None):
                break

            if int(next_offset) == offset:
                raise RuntimeError(
                    f"Pagination stuck: next_offset={next_offset}, offset={offset}"
                )

            offset = int(next_offset)

        return {"page_id": page_id, "components": all_components}

    # =====================================================
    # 🔹 FORMAT RAILS
    # =====================================================

    def format_rails_data(self, page_data: dict):

        components = (page_data or {}).get("components") or []

        formatted = []

        for index, c in enumerate(components):

            cta = c.get("cta") or {}

            formatted.append(
                {
                    "index": index,
                    "id": c.get("id", ""),
                    "template_id": c.get("template_id", ""),
                    "title": c.get("title", ""),
                    "deeplink": cta.get("deeplink", "")
                    if isinstance(cta, dict)
                    else "",
                    "is_adult": bool(c.get("is_adult", False)),
                }
            )

        return formatted

    # =====================================================
    # 🔹 MAIN API
    # =====================================================

    def get_rail_data(
        self,
        category: Category | str,
        app_language: str | None = None,
        start_offset: int = 0,
        extra_params: dict | None = None,
    ):

        page_id = self.get_root_category_page_id(
            category=category,
            app_language=app_language,
        )

        page_data = self.get_all_page_content(
            page_id=page_id,
            app_language=app_language,
            start_offset=start_offset,
            extra_params=extra_params,
            exclude_templates={"HIGHLIGHT"},
        )

        return self.format_rails_data(page_data)
