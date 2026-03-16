# base_api_client.py

import requests
from pathlib import Path

from APIs.dtdl.Interface import Interface
from APIs.dtdl.config_manager import Config_Manager


class BaseApiClient:
    def __init__(self, config_manager=None):

        # Resolve config manager
        if config_manager:
            self.config_manager = config_manager
        else:
            config_path = Path(__file__).resolve().parent / "config.json"
            self.config_manager = Config_Manager(config_path, Interface)

        # Runtime values injected via Interface
        self.language = Interface.language
        self.natco_config = Interface.natco_config
        self.major_version = Interface.major_version
        self.user_and_device_data = Interface.user_and_device_details
        self.STBConfig = Interface.STBConfig

        self.session = requests.Session()
        self.access_token = None
        self.adult_token = None

    # ----------------------------------------------------------
    # Adult Token
    # ----------------------------------------------------------

    def _get_adult_token_from_stb_data(self):
        """
        Fetch x-adult-token from device/user data passed via Interface
        """

        try:
            device_details = self.user_and_device_data

            if isinstance(device_details, tuple) and len(device_details) >= 5:
                user_info = device_details[4]

                if isinstance(user_info, dict):
                    return user_info.get("x-adult-token", "")

            return ""

        except Exception as e:
            print(f"Error fetching adult token: {e}")
            return ""

    # ----------------------------------------------------------
    # Generic API Request
    # ----------------------------------------------------------

    def make_request(
        self,
        method,
        url,
        requires_auth=True,
        requires_adult_token=False,
        **kwargs,
    ):

        # Ensure access token exists
        if requires_auth and not self.access_token:
            self._refresh_access_token()

        if "headers" not in kwargs:
            kwargs["headers"] = {}

        # Add auth headers
        if requires_auth:
            kwargs["headers"]["Authorization"] = f"Bearer {self.access_token}"
            kwargs["headers"]["bff_token"] = self.access_token

        # Add adult token if required
        if requires_adult_token:

            if not self.adult_token:
                self.adult_token = self._get_adult_token_from_stb_data()

            if self.adult_token:
                kwargs["headers"]["x-adult-token"] = self.adult_token

        response = self.session.request(method, url, **kwargs)

        response.raise_for_status()

        return response.json()

    # ----------------------------------------------------------
    # Access Token
    # ----------------------------------------------------------

    def _refresh_access_token(self):

        data = self.config_manager.get_data(self.language, "LOGIN")

        # Some natcos already return bff_token
        if data.get("bff_token") and self.STBConfig.fdn_natco in [
            "HU SDMC",
            "HU SEI",
            "MKT",
        ]:
            self.access_token = data["bff_token"]
            return

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        login_endpoint = self.config_manager.get_endpoint(self.language, "LOGIN")

        url = f"{base_url}{login_endpoint}"

        headers = self.config_manager.get_header(self.language, "LOGIN")

        response = self.session.post(url, headers=headers, json=data)

        response.raise_for_status()

        response_json = response.json()

        self.access_token = response_json.get("accessToken", "")