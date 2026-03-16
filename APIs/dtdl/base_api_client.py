# base_api_client.py

import requests

from APIs.dtdl.Interface import Interface
from APIs.dtdl.config_manager import Config_Manager

"""
#We can create convert config.json to python dict/class.
from tests.androidtv.api.dtdl.config_manager import ConfigManager #get endpoints, headers, data and params
from tests.androidtv.pages.helper import get_natco_config #get natco config for language
from tests.androidtv.pages.utility.stbconfig import STBConfig #get stb config fields
from tests.androidtv.pages.utility.utils import Utils #get device details and user info to fetch x-adult-token from stb_data.json
"""


class BaseApiClient:
    def __init__(self, config_manager):

        if config_manager:
            self.config_manager = config_manager
        else:
            config_path = "APIs/dtdl/config.json"
            self.config_manager = ConfigManager(config_path)

        self.language = None
        self.natco_config = None
        self.major_version = None
        self.user_and_device_data = None
        self.STBConfig = None

        self.session = requests.Session()
        self.access_token = None
        self.adult_token = None

    def _get_adult_token_from_stb_data(self):
        """
        Fetch the x-adult-token from stb_data.json based on the device ID
        """
        try:
            #device_id = STBConfig.adb_device_id
            #device_details = Utils().get_device_and_user_info(device_id)
            if isinstance(device_details, tuple) and len(device_details) >= 5:
                user_info = device_details[4]
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

        # Add x-adult-token if required
        if requires_adult_token:
            if not self.adult_token:
                self.adult_token = self._get_adult_token_from_stb_data()
            if self.adult_token:
                kwargs["headers"]["x-adult-token"] = self.adult_token

        response = self.session.request(method, url, **kwargs)
        # print("Response : ", response)
        response.raise_for_status()
        return response.json()

    def _refresh_access_token(self):

        data = self.config_manager.get_data(self.language, "LOGIN")

        if data.get("bff_token") and STBConfig().fdn_natco in [
            "HU SDMC",
            "HU SEI",
            "MKT",
        ]:
            self.access_token = data["bff_token"]
            return

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        login_endpoint = self.config_manager.get_endpoint(self.language, "LOGIN")

        if login_endpoint.startswith("http"):
            url = login_endpoint
        else:
            url = f"{base_url}{login_endpoint}"

        headers = self.config_manager.get_header(self.language, "LOGIN")

        response = self.session.post(url, headers=headers, json=data)

        response.raise_for_status()

        self.access_token = response.json().get("accessToken", "")