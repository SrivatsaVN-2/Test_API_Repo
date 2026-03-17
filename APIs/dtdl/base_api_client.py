# base_api_client.py

import requests
from pathlib import Path

from tests.Test_API_Repo.APIs.dtdl.config_manager import Config_Manager


class BaseApiClient:
    def __init__(self, interface=None, config_manager=None):
        """
        Base API Client that relies on Interface as the central data provider
        """

        # -----------------------------------
        # 1. Store Interface (CORE OBJECT)
        # -----------------------------------
        if not interface:
            raise ValueError("Interface instance is required")

        self.interface = interface

        # -----------------------------------
        # 2. Config Manager
        # -----------------------------------
        if config_manager:
            self.config_manager = config_manager
        else:
            config_path = Path(__file__).resolve().parent / "config.json"
            self.config_manager = Config_Manager(config_path, interface)

        # -----------------------------------
        # 3. Pull data from Interface (clean way)
        # -----------------------------------
        self.language = self.interface.language
        self.natco_config = self.interface.natco_config
        self.major_version = self.interface.major_version
        self.user_and_device_data = self.interface.user_and_device_details
        self.stb_config = self.interface.STBConfig

        # -----------------------------------
        # 4. Session setup
        # -----------------------------------
        self.session = requests.Session()
        self.access_token = None
        self.adult_token = None

    # =====================================================
    # 🔹 TOKEN HELPERS
    # =====================================================

    def _get_adult_token_from_interface(self):
        """
        Fetch x-adult-token safely from interface data
        """
        try:
            if not self.user_and_device_data:
                return ""

            # ✅ Handle dict (preferred structure)
            if isinstance(self.user_and_device_data, dict):
                return self.user_and_device_data.get("x-adult-token", "")

            # ⚠️ Fallback (legacy tuple support)
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
        """
        Centralized API request handler
        """

        # -----------------------------------
        # 1. Ensure access token
        # -----------------------------------
        if requires_auth and not self.access_token:
            self._refresh_access_token()

        # -----------------------------------
        # 2. Merge headers
        # -----------------------------------
        headers = self.interface.get_headers() or {}

        if "headers" in kwargs:
            headers.update(kwargs["headers"])

        # -----------------------------------
        # 3. Auth headers
        # -----------------------------------
        if requires_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            headers["bff_token"] = self.access_token

        # -----------------------------------
        # 4. Adult token (if needed)
        # -----------------------------------
        if requires_adult_token:
            if not self.adult_token:
                self.adult_token = self._get_adult_token_from_interface()

            if self.adult_token:
                headers["x-adult-token"] = self.adult_token

        kwargs["headers"] = headers

        # -----------------------------------
        # 5. Make request
        # -----------------------------------
        response = self.session.request(method, url, **kwargs)

        # Debug (optional)
        print(f"[API] {method} {url}")
        print(f"[HEADERS] {headers}")

        response.raise_for_status()

        # -----------------------------------
        # 6. Return JSON safely
        # -----------------------------------
        try:
            return response.json()
        except Exception:
            return response.text

    # =====================================================
    # 🔹 TOKEN REFRESH
    # =====================================================

    def _refresh_access_token(self):
        """
        Fetch access token using login API
        """

        data = self.config_manager.get_data(self.language, "LOGIN")

        # -----------------------------------
        # SAFETY CHECKS
        # -----------------------------------
        if not data or not data.get("telekomLogin"):
            raise ValueError("Missing 'telekomLogin' in login payload")

        username = data["telekomLogin"].get("username")
        password = data["telekomLogin"].get("password")

        if not username or not password:
            raise ValueError(
                f"Invalid credentials → username={username}, password={password}"
            )

        # -----------------------------------
        # NATCO Shortcut (NO LOGIN CALL)
        # -----------------------------------
        if (
            data.get("bff_token")
            and self.stb_config
            and getattr(self.stb_config, "fdn_natco", None)
            in ["HU SDMC", "HU SEI", "MKT"]
        ):
            self.access_token = data["bff_token"]
            return

        # -----------------------------------
        # Build URL
        # -----------------------------------
        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        login_endpoint = self.config_manager.get_endpoint(self.language, "LOGIN")

        if not login_endpoint:
            raise ValueError("LOGIN endpoint is empty")

        if login_endpoint.startswith("http"):
            url = login_endpoint
        else:
            if not base_url:
                raise ValueError("BASE endpoint is empty")
            url = f"{base_url.rstrip('/')}/{login_endpoint.lstrip('/')}"

        # -----------------------------------
        # Headers
        # -----------------------------------
        headers = self.config_manager.get_header(self.language, "LOGIN")

        print("🔐 LOGIN REQUEST")
        print("URL:", url)
        print("Headers:", headers)

        # -----------------------------------
        # API Call
        # -----------------------------------
        response = self.session.post(url, headers=headers, json=data)
        response.raise_for_status()

        response_json = response.json()

        self.access_token = response_json.get("accessToken", "")

        if not self.access_token:
            raise ValueError("Access token missing in response")

        print("✅ Access token fetched successfully")
