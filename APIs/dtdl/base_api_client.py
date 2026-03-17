# base_api_client.py

import requests
from pathlib import Path

from tests.Test_API_Repo.APIs.dtdl.config_manager import Config_Manager


class BaseApiClient:
    def __init__(self, interface=None, config_manager=None):

        if not interface:
            raise ValueError("Interface instance is required")

        self.interface = interface

        if config_manager:
            self.config_manager = config_manager
        else:
            config_path = Path(__file__).resolve().parent / "config.json"
            self.config_manager = Config_Manager(config_path, interface)

        # -----------------------------------
        # Interface data
        # -----------------------------------
        self.language = self.interface.language
        self.natco_config = self.interface.natco_config
        self.major_version = self.interface.major_version
        self.user_and_device_data = self.interface.user_and_device_details
        self.stb_config = self.interface.STBConfig

        self.session = requests.Session()
        self.access_token = None
        self.adult_token = None

    # =====================================================
    # 🔹 HEADER BUILDER (NEW - replaces get_headers())
    # =====================================================

    def _build_headers(self, header_type="OTHER", requires_auth=True, requires_adult=False):

        # 1. Base headers from config
        headers = self.config_manager.get_header(
            self.language, header_type, token=self.access_token
        ) or {}

        # 2. Auth headers
        if requires_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            headers["bff_token"] = self.access_token

        # 3. Device info
        device_id = getattr(self.stb_config, "adb_device_id", None)
        if device_id:
            headers["x-device-id"] = device_id

        # 4. Natco + language
        natco = self.natco_config.get("natco")
        if natco:
            headers["x-natco"] = natco

        headers["x-language"] = self.language

        # 5. Adult token
        if requires_adult:
            if not self.adult_token:
                self.adult_token = self._get_adult_token_from_interface()

            if self.adult_token:
                headers["x-adult-token"] = self.adult_token

        return headers

    # =====================================================
    # 🔹 TOKEN HELPERS
    # =====================================================

    def _get_adult_token_from_interface(self):
        try:
            if not self.user_and_device_data:
                return ""

            if isinstance(self.user_and_device_data, dict):
                return self.user_and_device_data.get("x-adult-token", "")

            if isinstance(self.user_and_device_data, tuple):
                if len(self.user_and_device_data) >= 5:
                    user_info = self.user_and_device_data[4]
                    if isinstance(user_info, dict):
                        return user_info.get("x-adult-token", "")

            return ""

        except Exception as e:
            print(f"Error fetching adult token: {e}")
            return ""

    # =====================================================
    # 🔹 REQUEST HANDLER
    # =====================================================

    def make_request(
        self,
        method,
        url,
        requires_auth=True,
        requires_adult_token=False,
        **kwargs,
    ):

        # 1. Ensure token
        if requires_auth and not self.access_token:
            self._refresh_access_token()

        # 2. Build headers (REPLACED LOGIC)
        headers = self._build_headers(
            header_type="OTHER",
            requires_auth=requires_auth,
            requires_adult=requires_adult_token,
        )

        # 3. Merge custom headers if provided
        if "headers" in kwargs:
            headers.update(kwargs["headers"])

        kwargs["headers"] = headers

        # 4. API call
        response = self.session.request(method, url, **kwargs)

        print(f"[API] {method} {url}")
        print(f"[HEADERS] {headers}")

        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            return response.text

    # =====================================================
    # 🔹 TOKEN REFRESH (UNCHANGED)
    # =====================================================

    def _refresh_access_token(self):

        data = self.config_manager.get_data(self.language, "LOGIN")

        if not data or not data.get("telekomLogin"):
            raise ValueError("Missing 'telekomLogin' in login payload")

        username = data["telekomLogin"].get("username")
        password = data["telekomLogin"].get("password")

        if not username or not password:
            raise ValueError(
                f"Invalid credentials → username={username}, password={password}"
            )

        # NATCO shortcut
        if (
            data.get("bff_token")
            and self.stb_config
            and getattr(self.stb_config, "fdn_natco", None)
            in ["HU SDMC", "HU SEI", "MKT"]
        ):
            self.access_token = data["bff_token"]
            return

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        login_endpoint = self.config_manager.get_endpoint(self.language, "LOGIN")

        if login_endpoint.startswith("http"):
            url = login_endpoint
        else:
            url = f"{base_url.rstrip('/')}/{login_endpoint.lstrip('/')}"

        headers = self.config_manager.get_header(self.language, "LOGIN")

        print("🔐 LOGIN REQUEST")
        print("URL:", url)
        print("Headers:", headers)

        response = self.session.post(url, headers=headers, json=data)
        response.raise_for_status()

        self.access_token = response.json().get("accessToken", "")

        if not self.access_token:
            raise ValueError("Access token missing in response")

        print("✅ Access token fetched successfully")
