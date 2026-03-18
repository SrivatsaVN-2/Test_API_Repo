from tests.Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient
from tests.Test_API_Repo.Utilities.Queries import APIQuery
from tests.Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("API.RentedContent")


class RentedContentApiClient(BaseApiClient):

    def __init__(self, interface):
        super().__init__(interface=interface)

    # =====================================================
    # 🔹 FETCH RENTED CONTENT
    # =====================================================

    def get_page_content(self, content_type=None):

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        rented_url = self.config_manager.get_endpoint(self.language, "RENTAL")

        if not content_type:
            content_type = "rentedContent"

        url = f"{base_url}/{rented_url}"

        headers = self.config_manager.get_header(self.language, "BFF_OTHER")
        params = self.config_manager.get_param(self.language, "RENTAL_PARAM")

        return self.make_request("GET", url, headers=headers, params=params)

    # =====================================================
    # 🔹 OBJECT CREATION
    # =====================================================

    def _create_rented_object(self, rented_data):

        return APIQuery.RentalContent(
            id=rented_data.get("id"),
            type=rented_data.get("type"),
            title=rented_data.get("title"),
            rating=rented_data.get("ratings") or rented_data.get("rating"),
            deeplink=rented_data.get("cta", {}).get("deeplink", ""),
            quality=rented_data.get("quality"),
        )

    # =====================================================
    # 🔹 FILTERING
    # =====================================================

    def _filter_rented_content(self, rented_contents, rented_desc=None):

        rented_list = []

        for rentable in rented_contents:

            if (
                getattr(rented_desc, "type", None)
                and rentable.type != rented_desc.type
            ):
                continue

            if (
                getattr(rented_desc, "title", None)
                and rentable.title != rented_desc.title
            ):
                continue

            if (
                getattr(rented_desc, "rating", None)
                and str(rentable.rating) != str(rented_desc.rating)
            ):
                continue

            if (
                getattr(rented_desc, "quality", None)
                and rentable.quality != rented_desc.quality
            ):
                continue

            rented_list.append(rentable)

        return rented_list

    # =====================================================
    # 🔹 MAIN API
    # =====================================================

    def get_rented_content(self, rented_desc=None):
        """
        Get rented content
        """

        try:
            response = self.get_page_content(content_type="rentedContent")

            assets = response.get("assets", [])

            if not assets:
                log.info("No rented movies found")
                return []

            rented_list = [
                self._create_rented_object(item) for item in assets
            ]

            log.info("Total rented content fetched: %s", len(rented_list))

            return self._filter_rented_content(rented_list, rented_desc)

        except Exception as e:
            log.error("Error fetching rented data: %s", str(e))
            return None
