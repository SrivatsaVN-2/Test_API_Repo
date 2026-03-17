# base_api_client.py

import requests

from tests.Test_API_Repo.APIs.dtdl.config_manager import Config_Manager


class BaseApiClient:
    def __init__(self, config_manager=None, interface=None):

        # Store interface (VERY IMPORTANT)
        self.interface = interface

        if config_manager:
            self.config_manager = config_manager
        else:
            config_path = "APIs/dtdl/config.json"
            self.config_manager = Config_Manager(config_path, interface)

        # Pull values from interface if available
        self.language = getattr(interface, "language", None)
        self.natco_config = getattr(interface, "natco_config", None)
        self.major_version = getattr(interface, "major_version", None)
        self.user_and_device_data = getattr(interface, "user_and_device_details", None)
        self.STBConfig = getattr(interface, "STBConfig", None)

        self.session = requests.Session()
        self.access_token = None
        self.adult_token = None

    def _get_adult_token_from_stb_data(self):
        """
        Fetch x-adult-token from injected interface data (NOT from file)
        """
        try:
            if (
                self.user_and_device_data
                and isinstance(self.user_and_device_data, tuple)
                and len(self.user_and_device_data) >= 5
            ):
                user_info = self.user_and_device_data[4]
                return user_info.get("x-adult-token", "")

            return ""

        except Exception as e:
            print(f"Error fetching adult token: {e}")
            return ""

    def make_request(
        self, method, url, requires_auth=True, requires_adult_token=False, **kwargs
    ):
        if requires_auth and not self.access_token:
            self._refresh_access_token()

        if "headers" not in kwargs:
            kwargs["headers"] = {}

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

    def _refresh_access_token(self):

        data = self.config_manager.get_data(self.language, "LOGIN")

        # 🔥 SAFETY CHECK (prevents useless API calls)
        if not data.get("telekomLogin"):
            raise ValueError("Missing 'telekomLogin' in login payload")

        username = data["telekomLogin"].get("username")
        password = data["telekomLogin"].get("password")

        if not username or not password:
            raise ValueError(
                f"Invalid credentials → username={username}, password={password}"
            )

        # Handle special NATCO case
        if data.get("bff_token") and self.STBConfig and self.STBConfig.fdn_natco in [
            "HU SDMC",
            "HU SEI",
            "MKT",
        ]:
            self.access_token = data["bff_token"]
            return

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        login_endpoint = self.config_manager.get_endpoint(self.language, "LOGIN")

        if not login_endpoint:
            raise ValueError("LOGIN endpoint is empty")

        # Fix URL construction
        if login_endpoint.startswith("http"):
            url = login_endpoint
        else:
            if not base_url:
                raise ValueError("BASE endpoint is empty")
            url = f"{base_url.rstrip('/')}/{login_endpoint.lstrip('/')}"

        headers = self.config_manager.get_header(self.language, "LOGIN")

        print("Login data:", url, headers, data)

        response = self.session.post(url, headers=headers, json=data)

        response.raise_for_status()

        self.access_token = response.json().get("accessToken", "")