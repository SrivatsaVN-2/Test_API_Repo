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

    def _create_series_object_from_asset_action(
        self, item_data, asset_actions_data, rail_title=None, rail_index=None
    ):
        """
        Create a Series object from item data and asset actions data.
        """

        actions = asset_actions_data.get("actions", {})

        # =====================================================
        # 🔹 ACTION OPTIONS
        # =====================================================

        watch_options = actions.get("watch", [])
        subscribe_options = actions.get("subscribe", [])
        schedules = actions.get("schedules", [])
        channels = actions.get("channels", {})
        catchup_schedules = actions.get("catchup_schedules", [])
        channel_subscribe_options = actions.get("channel_subscribe", [])
        trailer_options = actions.get("trailer", [])
        rent_options = actions.get("rent", [])
        purchase_options = actions.get("purchase", [])
        is_pinned = actions.get("pinned", False)

        # =====================================================
        # 🔹 DERIVED FLAGS
        # =====================================================

        has_trailer = bool(trailer_options)
        has_rent_options = bool(rent_options)
        has_purchase_options = bool(purchase_options)
        has_watch_options = bool(watch_options)
        has_catchup_schedules = bool(catchup_schedules)
        has_channels = bool(channels)
        has_schedules = bool(schedules)

        # =====================================================
        # 🔹 CHANNEL / STATION INFO
        # =====================================================

        content_channel_number = None
        content_station_id = None
        is_restricted = False

        for schedule in schedules + catchup_schedules:

            if schedule.get("channel_number"):
                content_channel_number = int(schedule.get("channel_number"))

            if schedule.get("station_id"):
                content_station_id = schedule.get("station_id")

            if schedule.get("is_restricted", False):
                is_restricted = True

        # =====================================================
        # 🔹 PRICING
        # =====================================================

        rent_prices = [
            opt.get("price_double", opt.get("price", 0))
            for opt in rent_options
            if opt.get("price_double") or opt.get("price")
        ]

        purchase_prices = [
            opt.get("price_double", opt.get("price", 0))
            for opt in purchase_options
            if opt.get("price_double") or opt.get("price")
        ]

        min_rent_price = min(rent_prices) if rent_prices else None
        max_rent_price = max(rent_prices) if rent_prices else None
        min_purchase_price = min(purchase_prices) if purchase_prices else None
        max_purchase_price = max(purchase_prices) if purchase_prices else None

        # =====================================================
        # 🔹 CURRENCY & QUALITY
        # =====================================================

        currencies = list(
            {
                opt.get("currency")
                for opt in rent_options + purchase_options
                if opt.get("currency")
            }
        )

        qualities = list(
            {
                opt.get("quality")
                for opt in rent_options + purchase_options
                if opt.get("quality")
            }
        )

        # =====================================================
        # 🔹 ACCESSIBILITY
        # =====================================================

        has_sign_language = any(
            opt.get("has_sign_language", False)
            for group in [rent_options, purchase_options, watch_options, catchup_schedules]
            for opt in group
        )

        has_audio_description = any(
            opt.get("has_audio_description", False)
            for group in [rent_options, purchase_options, watch_options, catchup_schedules]
            for opt in group
        )

        has_closed_captions = any(
            opt.get("has_closed_captions", False)
            for group in [rent_options, purchase_options, watch_options, catchup_schedules]
            for opt in group
        )

        # =====================================================
        # 🔹 RUNTIME
        # =====================================================

        runtime_seconds = None

        for opt in rent_options + purchase_options:
            if opt.get("runtime_seconds"):
                runtime_seconds = opt.get("runtime_seconds")
                break

        # =====================================================
        # 🔹 POSITION
        # =====================================================

        position_info = {
            "rail": rail_index,
            "item": item_data.get("index", 1) - 1,
            "rail_title": rail_title,
        }

        # =====================================================
        # 🔹 FINAL OBJECT
        # =====================================================

        return APIQuery.Series(
            id=asset_actions_data.get("id"),
            episode_name=asset_actions_data.get("episode_name"),
            original_asset_id=asset_actions_data.get("original_asset_id"),
            show_type=asset_actions_data.get("show_type"),
            is_geo_blocked=asset_actions_data.get("is_geo_blocked", False),
            is_device_not_compatible=asset_actions_data.get(
                "is_device_not_compatible", False
            ),
            blocked_channels=asset_actions_data.get("blocked_channels", []),
            is_any_schedule_exist=asset_actions_data.get(
                "is_any_schedule_exist", False
            ),
            provider_id=asset_actions_data.get("provider_id"),

            # 🔹 actions
            watch_options=watch_options,
            subscribe_options=subscribe_options,
            schedules=schedules,
            channels=channels,
            catchup_schedules=catchup_schedules,
            channel_subscribe_options=channel_subscribe_options,
            trailer_options=trailer_options,
            rent_options=rent_options,
            purchase_options=purchase_options,
            is_pinned=is_pinned,

            # 🔹 derived
            has_trailer=has_trailer,
            has_rent_options=has_rent_options,
            has_purchase_options=has_purchase_options,
            has_watch_options=has_watch_options,
            has_catchup_schedules=has_catchup_schedules,
            has_channels=has_channels,
            has_schedules=has_schedules,
            is_restricted=is_restricted,
            channel_number=content_channel_number,
            station_id=content_station_id,

            min_rent_price=min_rent_price,
            max_rent_price=max_rent_price,
            min_purchase_price=min_purchase_price,
            max_purchase_price=max_purchase_price,

            currencies=currencies,
            qualities=qualities,

            has_sign_language=has_sign_language,
            has_audio_description=has_audio_description,
            has_closed_captions=has_closed_captions,

            content_type=None,
            runtime_seconds=runtime_seconds,
            release_year=item_data.get("release_year"),

            # 🔹 metadata
            title=item_data.get("title", asset_actions_data.get("episode_name")),
            description=item_data.get("description", ""),

            # 🔹 rail info
            rail_title=rail_title,
            rail_index=rail_index,
            position=position_info,
        )

    def _create_series_object_from_asset_action(
        self, item_data, asset_actions_data, rail_title=None, rail_index=None
    ):
        """
        Create a Series object from item data and asset actions data.
        """

        actions = asset_actions_data.get("actions", {})

        # =====================================================
        # 🔹 ACTION OPTIONS
        # =====================================================

        watch_options = actions.get("watch", [])
        subscribe_options = actions.get("subscribe", [])
        schedules = actions.get("schedules", [])
        channels = actions.get("channels", {})
        catchup_schedules = actions.get("catchup_schedules", [])
        channel_subscribe_options = actions.get("channel_subscribe", [])
        trailer_options = actions.get("trailer", [])
        rent_options = actions.get("rent", [])
        purchase_options = actions.get("purchase", [])
        is_pinned = actions.get("pinned", False)

        # =====================================================
        # 🔹 DERIVED FLAGS
        # =====================================================

        has_trailer = bool(trailer_options)
        has_rent_options = bool(rent_options)
        has_purchase_options = bool(purchase_options)
        has_watch_options = bool(watch_options)
        has_catchup_schedules = bool(catchup_schedules)
        has_channels = bool(channels)
        has_schedules = bool(schedules)

        # =====================================================
        # 🔹 CHANNEL / STATION INFO
        # =====================================================

        content_channel_number = None
        content_station_id = None
        is_restricted = False

        for schedule in schedules + catchup_schedules:

            if schedule.get("channel_number"):
                content_channel_number = int(schedule.get("channel_number"))

            if schedule.get("station_id"):
                content_station_id = schedule.get("station_id")

            if schedule.get("is_restricted", False):
                is_restricted = True

        # =====================================================
        # 🔹 PRICING
        # =====================================================

        rent_prices = [
            opt.get("price_double", opt.get("price", 0))
            for opt in rent_options
            if opt.get("price_double") or opt.get("price")
        ]

        purchase_prices = [
            opt.get("price_double", opt.get("price", 0))
            for opt in purchase_options
            if opt.get("price_double") or opt.get("price")
        ]

        min_rent_price = min(rent_prices) if rent_prices else None
        max_rent_price = max(rent_prices) if rent_prices else None
        min_purchase_price = min(purchase_prices) if purchase_prices else None
        max_purchase_price = max(purchase_prices) if purchase_prices else None

        # =====================================================
        # 🔹 CURRENCY & QUALITY
        # =====================================================

        currencies = list(
            {
                opt.get("currency")
                for opt in rent_options + purchase_options
                if opt.get("currency")
            }
        )

        qualities = list(
            {
                opt.get("quality")
                for opt in rent_options + purchase_options
                if opt.get("quality")
            }
        )

        # =====================================================
        # 🔹 ACCESSIBILITY
        # =====================================================

        has_sign_language = any(
            opt.get("has_sign_language", False)
            for group in [rent_options, purchase_options, watch_options, catchup_schedules]
            for opt in group
        )

        has_audio_description = any(
            opt.get("has_audio_description", False)
            for group in [rent_options, purchase_options, watch_options, catchup_schedules]
            for opt in group
        )

        has_closed_captions = any(
            opt.get("has_closed_captions", False)
            for group in [rent_options, purchase_options, watch_options, catchup_schedules]
            for opt in group
        )

        # =====================================================
        # 🔹 RUNTIME
        # =====================================================

        runtime_seconds = None

        for opt in rent_options + purchase_options:
            if opt.get("runtime_seconds"):
                runtime_seconds = opt.get("runtime_seconds")
                break

        # =====================================================
        # 🔹 POSITION
        # =====================================================

        position_info = {
            "rail": rail_index,
            "item": item_data.get("index", 1) - 1,
            "rail_title": rail_title,
        }

        # =====================================================
        # 🔹 FINAL OBJECT
        # =====================================================

        return APIQuery.Series(
            id=asset_actions_data.get("id"),
            episode_name=asset_actions_data.get("episode_name"),
            original_asset_id=asset_actions_data.get("original_asset_id"),
            show_type=asset_actions_data.get("show_type"),
            is_geo_blocked=asset_actions_data.get("is_geo_blocked", False),
            is_device_not_compatible=asset_actions_data.get(
                "is_device_not_compatible", False
            ),
            blocked_channels=asset_actions_data.get("blocked_channels", []),
            is_any_schedule_exist=asset_actions_data.get(
                "is_any_schedule_exist", False
            ),
            provider_id=asset_actions_data.get("provider_id"),

            # 🔹 actions
            watch_options=watch_options,
            subscribe_options=subscribe_options,
            schedules=schedules,
            channels=channels,
            catchup_schedules=catchup_schedules,
            channel_subscribe_options=channel_subscribe_options,
            trailer_options=trailer_options,
            rent_options=rent_options,
            purchase_options=purchase_options,
            is_pinned=is_pinned,

            # 🔹 derived
            has_trailer=has_trailer,
            has_rent_options=has_rent_options,
            has_purchase_options=has_purchase_options,
            has_watch_options=has_watch_options,
            has_catchup_schedules=has_catchup_schedules,
            has_channels=has_channels,
            has_schedules=has_schedules,
            is_restricted=is_restricted,
            channel_number=content_channel_number,
            station_id=content_station_id,

            min_rent_price=min_rent_price,
            max_rent_price=max_rent_price,
            min_purchase_price=min_purchase_price,
            max_purchase_price=max_purchase_price,

            currencies=currencies,
            qualities=qualities,

            has_sign_language=has_sign_language,
            has_audio_description=has_audio_description,
            has_closed_captions=has_closed_captions,

            content_type=None,
            runtime_seconds=runtime_seconds,
            release_year=item_data.get("release_year"),

            # 🔹 metadata
            title=item_data.get("title", asset_actions_data.get("episode_name")),
            description=item_data.get("description", ""),

            # 🔹 rail info
            rail_title=rail_title,
            rail_index=rail_index,
            position=position_info,
        )

    import random

    def get_series_content(
        self, series_desc=None, content_type="series", include_asset_actions=True    
    ):
    """
    Comprehensive series retrieval function.
    """

        try:
            if series_desc is None:
                series_desc = APIQuery.SeriesDesc()

        # =====================================================
        # 🔹 FETCH DATA FROM RAILS
        # =====================================================

            items_by_rail = self.get_items_from_rails(content_type=content_type)

            all_series = []
            processed_count = 0

            for rail_index, (rail_title, items) in enumerate(items_by_rail.items()):

                if not items:
                    continue

            # Rail filters (unchanged logic)
                if getattr(series_desc, "rail_title", None) and rail_title != series_desc.rail_title:
                    continue

                if getattr(series_desc, "rail_index", None) is not None and rail_index != series_desc.rail_index:
                    continue

                for item in items:
                    asset_id = item.get("id")
                    if not asset_id:
                        continue

                    try:
                        series_obj = None

                    # =====================================================
                    # 🔹 WITH ASSET ACTIONS
                    # =====================================================

                        if include_asset_actions:
                            asset_actions = self.get_asset_actions(asset_id)

                            if asset_actions:
                                series_obj = self._create_series_object_from_asset_action(
                                    item, asset_actions, rail_title, rail_index
                                )

                    # =====================================================
                    # 🔹 BASIC OBJECT (NO ACTIONS)
                    # =====================================================

                        else:
                            series_obj = APIQuery.Series(
                                id=asset_id,
                                title=item.get("title", "Unknown"),
                                description=item.get("description", ""),
                                release_year=item.get("release_year"),
                                rail_title=rail_title,
                                rail_index=rail_index,
                                position={
                                    "rail": rail_index,
                                    "item": item.get("index", 1) - 1,
                                    "rail_title": rail_title,
                                },
                            )

                        if series_obj:
                            all_series.append(series_obj)
                            processed_count += 1

                    except Exception as e:
                        log.error(
                            "Error processing asset %s in rail %s: %s",
                            asset_id,
                            rail_title,
                            str(e),
                        )
                        continue

        # =====================================================
        # 🔹 APPLY FILTERS
        # =====================================================

            filtered_series = self._filter_series_by_description(
                all_series, series_desc
            )

        # =====================================================
        # 🔹 RANDOM SELECTION (FIXED: removed Utils)
        # =====================================================

            final_series = filtered_series

            if getattr(series_desc, "select_random", False) and len(filtered_series) > series_desc.size:

                selected_series = []
                available_series = filtered_series.copy()

                for _ in range(min(series_desc.size, len(available_series))):
                    if not available_series:
                        break

                # 🔥 REPLACED Utils().generate_random_index
                    random_index = random.randint(0, len(available_series) - 1)

                    selected_series.append(available_series.pop(random_index))

                final_series = selected_series

            else:
                final_series = filtered_series[: series_desc.size]

            return final_series

        except Exception as e:
            log.error("Error retrieving series content: %s", str(e))
            return []
        
