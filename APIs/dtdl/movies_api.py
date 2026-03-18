import random
from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger

log = Logger().setup_logger("moviesAPI")


class MoviesApiClient(BaseApiClient):
    """
    Client for interacting with movie-related API endpoints.
    """

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
            params = self.config_manager.get_param(
                self.language, "MOVIES_CONTENT_PARAM"
            ).copy()
        else:
            params = self.config_manager.get_param(
                self.language, "PAGE_CONTENT_PARAM"
            ).copy()

        params["offset"] = offset

        return self.make_request("GET", url, headers=headers, params=params)

    def get_all_page_content(self, content_type="movies"):
        movies_params = self.config_manager.get_param(
            self.language, "MOVIES_CONTENT_PARAM"
        )
        offsets = movies_params.get("offset", ["0"])

        all_components = []
        seen_rail_ids = set()

        for offset in offsets:
            content = self.get_page_content(
                content_type=content_type, offset=str(offset)
            )

            if content and "components" in content:
                for component in content["components"]:
                    if component.get("template_id") == "RAIL":
                        rail_id = component["id"]
                        if rail_id not in seen_rail_ids:
                            all_components.append(component)
                            seen_rail_ids.add(rail_id)

        return {"components": all_components}

    def get_items_from_rails(self, content_type="movies", limit=10):
        content = self.get_all_page_content(content_type=content_type)
        items_by_rail = {}

        if content:
            for component in content.get("components", []):
                if component.get("template_id") == "RAIL":

                    rail_id = component["id"]
                    rail_title = component["title"]

                    content_details = component.get("content_details", {})
                    end_point = content_details.get("end_point", "")

                    base_url = self.config_manager.get_endpoint(self.language, "BASE")

                    if not end_point:
                        log.warning(
                            "No end_point found for rail: %s", rail_title
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

                        if content_type == "movies":
                            params = self.config_manager.get_param(
                                self.language, "MOVIES_ITEMS_PARAM"
                            )
                        else:
                            params = self.config_manager.get_param(
                                self.language, "PAGE_CONTENT_PARAM"
                            )

                    headers = self.config_manager.get_header(self.language, "BFF_OTHER")

                    rail_data = self.make_request(
                        "GET", url, headers=headers, params=params
                    )

                    if rail_data:

                        assets = (
                            rail_data.get("assets")
                            or rail_data.get("items")
                            or rail_data.get("data")
                            or []
                        )

                        limited_assets = (
                            assets[:limit] if limit and limit > 0 else assets
                        )

                        items_by_rail[rail_title] = [
                            {**item, "index": i}
                            for i, item in enumerate(limited_assets, 1)
                        ]

                    else:
                        log.warning("No data returned for rail: %s", rail_title)
                        items_by_rail[rail_title] = []

        return items_by_rail

    def get_asset_actions(self, asset_id):
        base_url = self.config_manager.get_endpoint(self.language, "BASE")

        asset_action_url = self.config_manager.get_endpoint(
            self.language, "ASSET_ACTION_URL"
        )

        url = f"{base_url}{asset_action_url.replace('{asset_id}', asset_id)}"

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "CHANNEL_INFO")

        try:
            return self.make_request("GET", url, headers=headers, params=params)

        except Exception as e:
            log.error("Error fetching asset actions for %s: %s", asset_id, str(e))
            return None

    def _create_movie_object_from_asset_action(
        self, item_data, asset_actions_data, rail_title=None, rail_index=None):
    """
    Create a Movie object from item data and asset actions data.
    """

        actions = asset_actions_data.get("actions", {})

    # Extract action options
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

    # Calculate derived fields
        has_trailer = len(trailer_options) > 0
        has_rent_options = len(rent_options) > 0
        has_purchase_options = len(purchase_options) > 0
        has_watch_options = len(watch_options) > 0
        has_catchup_schedules = len(catchup_schedules) > 0
        has_channels = len(channels) > 0

    # Check if rentable only
        is_rentable_only = (
            has_rent_options
            and not has_watch_options
            and not has_catchup_schedules
            and not has_channels
        )

    # Extract pricing information
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

    # Extract currencies and qualities
        currencies = list(
            set(
                [
                    opt.get("currency")
                    for opt in rent_options + purchase_options
                    if opt.get("currency")
                ]
            )
        )

        qualities = list(
            set(
                [
                    opt.get("quality")
                    for opt in rent_options + purchase_options
                    if opt.get("quality")
                ]
            )
        )

    # Accessibility features
        has_sign_language = any(
            opt.get("has_sign_language", False)
            for action_list in [
                rent_options,
                purchase_options,
                watch_options,
                catchup_schedules,
            ]
            for opt in action_list
        )

        has_audio_description = any(
            opt.get("has_audio_description", False)
            for action_list in [
                rent_options,
                purchase_options,
                watch_options,
                catchup_schedules,
            ]
            for opt in action_list
        )

        has_closed_captions = any(
            opt.get("has_closed_captions", False)
            for action_list in [
                rent_options,
                purchase_options,
                watch_options,
                catchup_schedules,
            ]
            for opt in action_list
        )    

    # Position info
        position_info = {
            "rail": rail_index,
            "item": item_data.get("index", 1) - 1,
            "rail_title": rail_title,
        }

        return APIQuery.Movie(
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

        # Actions
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

        # Derived
            has_trailer=has_trailer,
            has_rent_options=has_rent_options,
            has_purchase_options=has_purchase_options,
            has_watch_options=has_watch_options,
            has_catchup_schedules=has_catchup_schedules,
            has_channels=has_channels,
            is_rentable_only=is_rentable_only,
            min_rent_price=min_rent_price,
            max_rent_price=max_rent_price,
            min_purchase_price=min_purchase_price,
            max_purchase_price=max_purchase_price,
            currencies=currencies,
            qualities=qualities,
            has_sign_language=has_sign_language,
            has_audio_description=has_audio_description,
            has_closed_captions=has_closed_captions,

        # Metadata
            title=item_data.get("title", asset_actions_data.get("episode_name")),
            description=item_data.get("description", ""),
            thumbnail=item_data.get("thumbnail", ""),
            poster_image_url=item_data.get("poster_image_url", ""),
            release_year=item_data.get("release_year"),
            deeplink=item_data.get("cta", {}).get("deeplink", ""),
            cta_title=item_data.get("cta", {}).get("title", ""),
            runtime_seconds=item_data.get("runtime_seconds"),
            index=item_data.get("index"),

        # Position
            rail_title=rail_title,
            rail_index=rail_index,
            position=position_info,
        )
    def _filter_movies_by_description(self, movies_list, movie_desc):
    """
    Filter movies based on MovieDesc criteria.
    """

        filtered_movies = []

        for movie in movies_list:

        # =====================================================
        # 🔹 BASIC FILTERS
        # =====================================================

            if getattr(movie_desc, "show_type", None) and movie.show_type != movie_desc.show_type:
                continue

            if getattr(movie_desc, "episode_name", None) and movie.episode_name != movie_desc.episode_name:
                continue

            if getattr(movie_desc, "original_asset_id", None) and movie.original_asset_id != movie_desc.original_asset_id:
                continue

        # =====================================================
        # 🔹 EXCLUSION FILTERS
        # =====================================================

            if getattr(movie_desc, "exclude_asset_id", None) and movie.id == movie_desc.exclude_asset_id:
                continue

            if getattr(movie_desc, "exclude_asset_ids", None) and movie.id in movie_desc.exclude_asset_ids:
                continue

        # =====================================================
        # 🔹 RAIL FILTERS
        # =====================================================

            if getattr(movie_desc, "rail_title", None) and movie.rail_title != movie_desc.rail_title:
                continue

            if getattr(movie_desc, "rail_index", None) is not None and movie.rail_index != movie_desc.rail_index:
                continue

        # =====================================================
        # 🔹 BOOLEAN FILTERS
        # =====================================================

            if getattr(movie_desc, "is_adult", None) is not None and getattr(movie, "is_adult", None) != movie_desc.is_adult:
                continue

            if getattr(movie_desc, "is_geo_blocked", None) is not None and movie.is_geo_blocked != movie_desc.is_geo_blocked:
                continue

            if getattr(movie_desc, "is_device_not_compatible", None) is not None and movie.is_device_not_compatible != movie_desc.is_device_not_compatible:
                continue

            if getattr(movie_desc, "has_trailer", None) is not None and getattr(movie, "has_trailer", None) != movie_desc.has_trailer:
                continue

            if getattr(movie_desc, "has_rent_options", None) is not None and getattr(movie, "has_rent_options", None) != movie_desc.has_rent_options:
                continue

            if getattr(movie_desc, "has_purchase_options", None) is not None and getattr(movie, "has_purchase_options", None) != movie_desc.has_purchase_options:
                continue

            if getattr(movie_desc, "has_watch_options", None) is not None and getattr(movie, "has_watch_options", None) != movie_desc.has_watch_options:
                continue

            if getattr(movie_desc, "has_catchup_schedules", None) is not None and getattr(movie, "has_catchup_schedules", None) != movie_desc.has_catchup_schedules:
                continue

            if getattr(movie_desc, "has_channels", None) is not None and getattr(movie, "has_channels", None) != movie_desc.has_channels:
                continue

            if getattr(movie_desc, "is_rentable_only", None) is not None and getattr(movie, "is_rentable_only", None) != movie_desc.is_rentable_only:
                continue

            if getattr(movie_desc, "has_sign_language", None) is not None and getattr(movie, "has_sign_language", None) != movie_desc.has_sign_language:
                continue

            if getattr(movie_desc, "has_audio_description", None) is not None and getattr(movie, "has_audio_description", None) != movie_desc.has_audio_description:
                continue

            if getattr(movie_desc, "has_closed_captions", None) is not None and getattr(movie, "has_closed_captions", None) != movie_desc.has_closed_captions:
                continue

        # =====================================================
        # 🔹 PRICE FILTERS
        # =====================================================

            if getattr(movie_desc, "min_price", None) is not None:
                movie_min_price = getattr(movie, "min_rent_price", None)
                if movie_min_price is None or movie_min_price < movie_desc.min_price:
                    continue

            if getattr(movie_desc, "max_price", None) is not None:
                movie_max_price = getattr(movie, "max_rent_price", None)
                if movie_max_price is None or movie_max_price > movie_desc.max_price:
                    continue

        # =====================================================
        # 🔹 CURRENCY / QUALITY
        # =====================================================

            if getattr(movie_desc, "currency", None):
                if movie_desc.currency not in getattr(movie, "currencies", []):
                    continue

            if getattr(movie_desc, "quality", None):
                if movie_desc.quality not in getattr(movie, "qualities", []):
                    continue

        # =====================================================
        # 🔹 CONTENT TYPE
        # =====================================================

            if getattr(movie_desc, "content_type", None):
                rent_opts = getattr(movie, "rent_options", [])
                purchase_opts = getattr(movie, "purchase_options", [])
                watch_opts = getattr(movie, "watch_options", [])

                if not any(
                    opt.get("content_type") == movie_desc.content_type
                    for opt in rent_opts + purchase_opts + watch_opts
                ):
                    continue

        # =====================================================
        # 🔹 RENTAL WINDOW
        # =====================================================

            if getattr(movie_desc, "rental_window_hours", None) is not None:
                rental_window_match = False

                for rent_opt in getattr(movie, "rent_options", []):
                    rental_window = rent_opt.get("rental_window", "")

                    if rental_window:
                        try:
                            parts = rental_window.split(".")
                            if len(parts) == 2:
                                days = int(parts[0])
                                hours = int(parts[1].split(":")[0])
                                total_hours = days * 24 + hours

                                if total_hours >= movie_desc.rental_window_hours:
                                    rental_window_match = True
                                    break
                        except (ValueError, IndexError):
                            continue

                    if not rental_window_match:
                        continue

        # =====================================================
        # 🔹 TITLE LENGTH
        # =====================================================

            title = movie.episode_name or getattr(movie, "title", "")

            if title:
                length = len(title)

                if getattr(movie_desc, "min_length", None) is not None and length < movie_desc.min_length:
                    continue

                if getattr(movie_desc, "max_length", None) is not None and length > movie_desc.max_length:
                    continue

        # =====================================================
        # ✅ PASSED ALL FILTERS
        # =====================================================

            filtered_movies.append(movie)

        return filtered_movies
    
    import random

    def get_crew_details(self, person_id):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        crew_url = self.config_manager.get_endpoint(self.language, "CAST_DETAIL_URL")

        url = f"{base_url}{crew_url.replace('{person_id}', person_id)}"

        headers = self.config_manager.get_header(self.language, "CREW_HEADERS")
        params = self.config_manager.get_param(self.language, "CREW_DETAIL_PARAM")

        try:
            response = self.make_request("GET", url, headers=headers, params=params)
            return {
                "name": response.get("person", {}).get("person_name", ""),
                "role_name": response.get("person", {}).get("role_name", ""),
            }
        except Exception as e:
            log.error("Error fetching crew details for %s: %s", person_id, str(e))
            return None


    def get_movies_crew(self, asset_id):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        crew_url = self.config_manager.get_endpoint(self.language, "ASSET_DETAIL_URL")

        url = f"{base_url}{crew_url.replace('{asset_id}', asset_id)}"

        headers = self.config_manager.get_header(self.language, "CREW_HEADERS")
        params = self.config_manager.get_param(self.language, "CREW_CONTENT_PARAM")

        try:
            response = self.make_request("GET", url, headers=headers, params=params)

            return {
                "cast_count": len(response.get("roles", [])),
                "cast": [
                    self.get_crew_details(role["person_id"])
                    for role in response.get("roles", [])
                ],
            }

        except Exception as e:
            log.error("Error fetching crew for %s: %s", asset_id, str(e))
            return None


    def get_movie_details(
        self,
        movie_desc=None,
        content_type="movies",
        stop_at_first_rentable=False,
        include_asset_actions=True,
        analysis_mode=False,
    ):

        try:
            if movie_desc is None:
                movie_desc = APIQuery.MovieDesc()

            items_by_rail = self.get_items_from_rails(content_type=content_type)

            all_movies = []
            processed_count = 0
            rail_summary = {}
            found_rentable = False
            rentable_movie_info = None

            for rail_index, (rail_title, items) in enumerate(items_by_rail.items()):

                if not items:
                    continue

                if analysis_mode:
                    rail_summary[rail_title] = {
                        "rail_index": rail_index,
                        "total_movies": 0,
                        "rentable_only": 0,
                        "free_movies": 0,
                        "with_trailers": 0,
                        "sample_movies": [],
                    }

                for item in items:

                    if stop_at_first_rentable and found_rentable:
                        break

                    asset_id = item.get("id")
                    if not asset_id:
                        continue

                    try:
                        movie_obj = None

                        if include_asset_actions:
                            asset_actions = self.get_asset_actions(asset_id)

                            if asset_actions:
                                movie_obj = self._create_movie_object_from_asset_action(
                                    item, asset_actions, rail_title, rail_index
                                )

                                if stop_at_first_rentable and movie_obj.is_rentable_only:
                                    rentable_movie_info = {
                                        "rail": rail_title,
                                        "rail_index": rail_index,
                                        "title": movie_obj.episode_name,
                                        "asset_id": asset_id,
                                        "index": movie_obj.index,
                                        "deeplink": movie_obj.deeplink,
                                        "cta_title": movie_obj.cta_title,
                                        "thumbnail": movie_obj.thumbnail,
                                        "poster_image_url": movie_obj.poster_image_url,
                                        "description": movie_obj.description,
                                        "release_year": movie_obj.release_year,
                                        "min_rent_price": movie_obj.min_rent_price,
                                        "currencies": movie_obj.currencies,
                                        "position": movie_obj.position,
                                    }
                                    found_rentable = True

                        else:
                            movie_obj = APIQuery.Movie(
                                id=asset_id,
                                title=item.get("title", "Unknown"),
                                description=item.get("description", ""),
                                thumbnail=item.get("thumbnail", ""),
                                poster_image_url=item.get("poster_image_url", ""),
                                release_year=item.get("release_year"),
                                deeplink=item.get("cta", {}).get("deeplink", ""),
                                cta_title=item.get("cta", {}).get("title", ""),
                                runtime_seconds=item.get("runtime_seconds"),
                                index=item.get("index"),
                                rail_title=rail_title,
                                rail_index=rail_index,
                                position={
                                    "rail": rail_index,
                                    "item": item.get("index", 1) - 1,
                                    "rail_title": rail_title,
                                },
                            )

                        if movie_obj:
                            all_movies.append(movie_obj)
                            processed_count += 1

                            if analysis_mode:
                                rail_info = rail_summary[rail_title]
                                rail_info["total_movies"] += 1

                                if getattr(movie_obj, "is_rentable_only", False):
                                    rail_info["rentable_only"] += 1

                                if (
                                    getattr(movie_obj, "has_watch_options", False)
                                    or getattr(movie_obj, "has_catchup_schedules", False)
                                    or getattr(movie_obj, "has_channels", False)
                                ):
                                    rail_info["free_movies"] += 1

                                if getattr(movie_obj, "has_trailer", False):
                                    rail_info["with_trailers"] += 1

                                if len(rail_info["sample_movies"]) < 3:
                                    rail_info["sample_movies"].append(
                                        {
                                            "title": movie_obj.episode_name or movie_obj.title,
                                            "index": movie_obj.index,
                                            "position": movie_obj.position,
                                        }
                                    )

                    except Exception as e:
                        log.error("Error processing asset %s: %s", asset_id, str(e))
                        continue

                if stop_at_first_rentable and found_rentable:
                    break

            filtered_movies = self._filter_movies_by_description(all_movies, movie_desc)

        # 🔥 FIXED: removed Utils
            if getattr(movie_desc, "select_random", False) and len(filtered_movies) > movie_desc.size:

                selected = []
                pool = filtered_movies.copy()

                for _ in range(min(movie_desc.size, len(pool))):
                    if not pool:
                        break
                    idx = random.randint(0, len(pool) - 1)
                    selected.append(pool.pop(idx))

                final_movies = selected
            else:
                final_movies = filtered_movies[: movie_desc.size]

            navigation = None
            if final_movies and getattr(final_movies[0], "position", None):
                navigation = self._generate_navigation_instructions(final_movies[0])

            result = {
                "movies": final_movies,
                "total_processed": processed_count,
                "total_filtered": len(filtered_movies),
                "final_count": len(final_movies),
            }

            if analysis_mode:
                result["rail_summary"] = rail_summary

            if stop_at_first_rentable:
                result["found_rentable"] = found_rentable
                result["rentable_movie_info"] = rentable_movie_info

            if navigation:
                result["navigation_instructions"] = navigation

            return result

        except Exception as e:
            log.error("Error retrieving movie details: %s", str(e))
            raise AssertionError(f"Failed to get movie details: {str(e)}")

    import random

    def _generate_navigation_instructions(self, movie):

        try:
            if not movie or not movie.position:
                return None

            rail_steps = movie.position.get("rail", 0)
            item_steps = movie.position.get("item", 0)

            instructions = {
                "movie_title": movie.episode_name or movie.title,
                "rail_title": movie.rail_title,
                "steps": [
                    "Navigate to Movies section",
                    f"Press DOWN {rail_steps} times to reach rail '{movie.rail_title}'",
                    f"Press RIGHT {item_steps} times to reach movie '{movie.episode_name or movie.title}'",
                    "Press OK to select movie",
                ],
                "total_down_presses": rail_steps,
                "total_right_presses": item_steps,
                "expected_result": f"Movie details page for '{movie.episode_name or movie.title}'",
            }

            if getattr(movie, "is_rentable_only", False):
                price = getattr(movie, "min_rent_price", None)
                currency = movie.currencies[0] if getattr(movie, "currencies", []) else "EUR"

                instructions["additional_info"] = (
                    f"This movie is rentable for {price} {currency}"
                    if price else "This movie is rentable"
                )

            return instructions

        except Exception as e:
            log.error("Error generating navigation instructions: %s", str(e))
            return None


    def get_rentable_movies(self, movie_desc=None, content_type="movies"):

        if movie_desc is None:
            movie_desc = APIQuery.MovieDesc()

        movie_desc.is_rentable_only = True
        movie_desc.has_rent_options = True

        result = self.get_movie_details(movie_desc, content_type, True)
        return result["movies"]


    def get_free_movies(self, movie_desc=None, content_type="movies"):
    
        if movie_desc is None:
            movie_desc = APIQuery.MovieDesc()

        movie_desc.is_rentable_only = False

        result = self.get_movie_details(movie_desc, content_type, True)

        return [
            m for m in result["movies"]
            if getattr(m, "has_watch_options", False)
            or getattr(m, "has_catchup_schedules", False)
            or getattr(m, "has_channels", False)
        ][: movie_desc.size]


    def get_movies_by_rail(self, rail_title=None, rail_index=None, movie_desc=None, content_type="movies"):

    if movie_desc is None:
        movie_desc = APIQuery.MovieDesc()

    if rail_title:
        movie_desc.rail_title = rail_title
    if rail_index is not None:
        movie_desc.rail_index = rail_index

    return self.get_movie_details(movie_desc, content_type, True)["movies"]


    def get_cast_and_crew(self, content_type="movies"):

        try:
            rail_info = self.get_items_from_rails(content_type, limit=10)

            for _, items in rail_info.items():
                for item in items:
                    crew = self.get_movies_crew(item.get("id"))
                    if crew and crew.get("cast"):
                        return crew

        except Exception as e:
            log.debug("Exception: %s", str(e))

        return []


    def get_cast_and_crew_from_rail(self, rail_id, content_type="movies", end_point=None):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
    
        if end_point:
            url = f"{base_url}/{end_point.lstrip('/')}"
            params = self.config_manager.get_param(
                self.language,
                "MOVIES_ITEMS_PARAM" if content_type == "movies" else "PAGE_CONTENT_PARAM"
            )
        else:
            items_url = self.config_manager.get_endpoint(self.language, "COMPONENT_URL")
            url = f"{base_url}{items_url.replace('{component_id}', rail_id)}"
            params = self.config_manager.get_param(self.language, "PAGE_CONTENT_PARAM")

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")

        rail_data = self.make_request("GET", url, headers=headers, params=params)
        if not rail_data:
            return {}

        assets = (
            rail_data.get("assets")
            or rail_data.get("items")
            or rail_data.get("data")
            or []
        )

        for asset in assets:
            asset_id = asset.get("id")
            if not asset_id:
                continue

            cast = self.get_movies_crew(asset_id)
            if cast:
                return cast

        return {}


    def get_first_available_cast_and_crew(self, content_type="movies"):

        content = self.get_all_page_content(content_type)

        if not content:
            return {}

        for comp in content.get("components", []):
            if comp.get("template_id") != "RAIL":
                continue

            result = self.get_cast_and_crew_from_rail(
                comp.get("id"),
                content_type,
                comp.get("content_details", {}).get("end_point")
            )

            if result:
                return result

        return {}


    def get_first_rentable_movie(self, content_type="movies"):

        return self.get_movie_details(
            APIQuery.MovieDesc(size=1),
            content_type,
            stop_at_first_rentable=True,
            include_asset_actions=True,
        )

    def navigate_to_movie(self, movie):
        return self._generate_navigation_instructions(movie)


    def get_asset_actions_until_first_rentable(self, content_type="movies"):

        log.warning("Deprecated → use get_first_rentable_movie")
        return self.get_first_rentable_movie(content_type)


    def get_rentable_items(self, content_type="movies"):

        log.warning("Deprecated → use get_rentable_movies")

        movies = self.get_rentable_movies(APIQuery.MovieDesc(size=100), content_type)

        result = {}
        for m in movies:
            rail = m.rail_title or "Unknown"

            result.setdefault(rail, []).append({
                "index": m.index,
                "title": m.episode_name or m.title,
                "id": m.id,
                "position": m.position,
            })

        return result


    def get_movies_content(self, movies_desc=None, content_type="movies", include_asset_actions=True):

        try:
            if movies_desc is None:
                movies_desc = APIQuery.MovieDesc()
    
            items_by_rail = self.get_items_from_rails(content_type)
            all_movies = []

            for rail_index, (rail_title, items) in enumerate(items_by_rail.items()):

                if movies_desc.rail_title and rail_title != movies_desc.rail_title:
                    continue

                if movies_desc.rail_index is not None and rail_index != movies_desc.rail_index:
                    continue

                for item in items:

                    asset_id = item.get("id")
                    if not asset_id:
                        continue

                    try:
                        movie_obj = None

                        if include_asset_actions and item.get("type") == "Movie":
                            actions = self.get_asset_actions(asset_id)
                            if actions:
                                movie_obj = self._create_movie_object_from_asset_action(
                                    item, actions, rail_title, rail_index
                                )
                        else:
                            movie_obj = APIQuery.Movie(
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

                        if movie_obj:
                            all_movies.append(movie_obj)

                    except Exception as e:
                        log.error("Error processing %s: %s", asset_id, str(e))

            filtered = self._filter_movies_by_description(all_movies, movies_desc)

        # 🔥 FIXED Utils
            if getattr(movies_desc, "select_random", False) and len(filtered) > movies_desc.size:
                result = []
                pool = filtered.copy()

                for _ in range(min(movies_desc.size, len(pool))):
                    idx = random.randint(0, len(pool) - 1)
                    result.append(pool.pop(idx))
            else:
                result = filtered[: movies_desc.size]

            return [m.episode_name for m in result] if result else []

        except Exception as e:
            log.error("Error retrieving movies content: %s", str(e))
            return []
