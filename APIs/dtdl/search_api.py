import random

from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.Search")


class SearchApiClient(BaseApiClient):

    def __init__(self, interface):
        super().__init__(interface=interface)

    # =====================================================
    # 🔹 SEARCH MOVIE
    # =====================================================

    def search_movie(self, movie_title):
        """
        Search for a specific movie using the search API
        """

        try:
            base_url = self.config_manager.get_endpoint(self.language, "BASE")
            endpoint = self.config_manager.get_endpoint(self.language, "SEARCH_URL")

            url = f"{base_url}{endpoint}"

            params = self.config_manager.get_param(
                self.language, "CHANNEL_INFO"
            ).copy()

            params["text_search"] = movie_title

            headers = self.config_manager.get_header(self.language, "OTHER")

            # Inject auth from interface (important change)
            if getattr(self.interface, "user_and_device_details", None):
                access_token = self.interface.user_and_device_details.get(
                    "access_token"
                )

                if access_token:
                    headers.update(
                        {
                            "bff_token": access_token,
                            "Authorization": f"Bearer {access_token}",
                        }
                    )

            log.info("Searching for movie: %s", movie_title)

            return self.make_request("GET", url, headers=headers, params=params)

        except Exception as e:
            log.error("Error searching for movie: %s", e)
            return {"error": str(e)}

    # =====================================================
    # 🔹 RANDOM CURRENT MOVIE SEARCH (EPG INTEGRATION)
    # =====================================================

    def search_random_current_movie(self):
        """
        Get a random current movie and search for it
        """

        try:
            # 🔥 Replace ApiLibrary with interface
            epg_api = self.interface.epg_api()

            program_desc = APIQuery.ProgramDesc(
                show_type="Movie",
                is_adult=False,
                is_subscribed=True,
                is_audio=False,
            )

            current_movies = epg_api.get_programs(
                program_desc=program_desc,
                current_time_only=True,
            )

            if not current_movies:
                log.warning("No current movies found")
                return None, {"error": "No current movies found"}, []

            movie_dicts = []

            for movie in current_movies:

                if not movie.description:
                    continue

                channel_number = epg_api.get_channel_for_station(
                    movie.station_id
                )

                if not channel_number:
                    continue

                title = movie.description

                has_diacritics = any(ord(c) > 127 for c in title)
                has_numbers = any(c.isdigit() for c in title)

                if not has_diacritics and not has_numbers and len(title) <= 15:

                    movie_dicts.append(
                        {
                            "title": title,
                            "start_time": movie.start_time,
                            "end_time": movie.end_time,
                            "station_id": movie.station_id,
                            "program_id": movie.program_id,
                            "show_type": movie.show_type,
                            "channel_number": channel_number,
                        }
                    )

            # 🔥 Fallback logic (unchanged)
            if not movie_dicts:
                log.warning("No suitable movies found after filtering")

                if current_movies:
                    random_movie = current_movies[0]
                    random_movie = {
                        "title": random_movie.description,
                        "start_time": random_movie.start_time,
                        "end_time": random_movie.end_time,
                    }
                else:
                    return None, {"error": "No suitable movies found"}, []
            else:
                random_movie = random.choice(movie_dicts)

            movie_title = random_movie.get("title", "")

            log.info("Selected random movie: %s", movie_title)

            search_result = self.search_movie(movie_title)

            all_movies_array = search_result.get("movies", [])

            exact_match_movies = []

            for index, movie in enumerate(all_movies_array):

                if movie.get("name", "").lower() == movie_title.lower():

                    movie["original_index"] = index + 1
                    exact_match_movies.append(movie)

            return random_movie, search_result, exact_match_movies

        except Exception as e:
            log.error("Error in search_random_current_movie: %s", e)
            return None, {"error": str(e)}, []

    # =====================================================
    # 🔹 HELPERS
    # =====================================================

    def get_movies_array(self, search_result):
        return search_result.get("movies", [])

    def get_exact_match_movies_array(self, search_result, movie_title):

        movies_array = search_result.get("movies", [])

        exact_matches = []

        for index, movie in enumerate(movies_array):

            if movie.get("name", "").lower() == movie_title.lower():

                movie["original_index"] = index + 1
                exact_matches.append(movie)

        return exact_matches
