# config_manager.py
# Handles reading and providing configuration data from a JSON file

import json


LANGUAGE_MAPPING = {
    ("at", "AT"): "de",
    ("de", "AT"): "de",
    ("eng", "AT"): "en_at",
    ("hr", "HR"): "hr",
    ("eng", "HR"): "en_hr",
    ("pl", "PL"): "pl",
    ("eng", "PL"): "en_pl",
    ("me", "ME"): "me",
    ("eng", "ME"): "en_me",
    ("hu", "HU"): "hu",
    ("eng", "HU"): "en",
    ("mkt", "MKT"): "mk",
    ("mk", "MKT"): "mk",
    ("eng", "MKT"): "en_mk",
}


class Config_Manager:

    def __init__(self, config_file, interface):
        """
        Config manager receives Interface dependency.
        """

        self.interface = interface
        self.language = interface.language
        self.STBConfig = interface.STBConfig

        with open(config_file, "r") as file:
            self.config = json.load(file)

    # ---------------------------------------------------------

    def _map_language(self, lang):
        """
        Map device language + natco to config language key
        """
        natco = self.STBConfig.fdn_natco

        key = (lang, natco)

        mapped_lang = LANGUAGE_MAPPING.get(key, lang)

        return mapped_lang

    # ---------------------------------------------------------

    def get_endpoint(self, lang, endpoint_type):

        mapped_lang = self._map_language(lang)

        endpoint = self.config.get("endpoints", {}).get(mapped_lang, {}).get(endpoint_type, "")

        print(f"Fetched endpoint for lang '{mapped_lang}' and type '{endpoint_type}': {endpoint}")

        return endpoint

    # ---------------------------------------------------------

    def get_header(self, lang, header_type, token=""):

        mapped_lang = self._map_language(lang)

        header = self.config.get("headers", {}).get(mapped_lang, {}).get(header_type, {}).copy()

        if header_type == "OTHER":
            header["Authorization"] = f"Bearer {token}"

        elif header_type == "BFF_OTHER":
            header["bff_token"] = token

            if "x-adult-token" in header:
                del header["x-adult-token"]

        return header

    # ---------------------------------------------------------

    def get_param(self, lang, param_type):

        mapped_lang = self._map_language(lang)

        params = self.config.get("params", {}).get(mapped_lang, {}).get(param_type, {}).copy()

        if "app_language" in params:

            language = self.interface.language
            key = (language, mapped_lang)

            if key in LANGUAGE_MAPPING:
                params["app_language"] = LANGUAGE_MAPPING[key]

        return params

    # ---------------------------------------------------------

    def get_data(self, lang, data_type, username="", password=""):

        mapped_lang = self._map_language(lang)

        data = self.config.get("data", {}).get(mapped_lang, {}).get(data_type, {}).copy()

        device_id = self.STBConfig.adb_device_id

        utils = self.interface.utils
        user_info = utils.get_device_and_user_info(device_id)

        if not user_info or len(user_info) < 5:
            raise Exception("Invalid device/user data received from utils")

        user_id = user_info[3]
        user_details = user_info[4]

        if isinstance(user_details, dict):
            pwd = user_details.get("passcode")
            data["bff_token"] = user_details.get("bff_token")

        else:
            pwd = None
            data["bff_token"] = None
        if self.STBConfig.fdn_natco in ["HU SDMC", "HU SEI", "MKT"]:
            return data

        if data_type == "LOGIN":

            if username:
                data["telekomLogin"]["username"] = username
            else:
                data["telekomLogin"]["username"] = user_id

            if password:
                data["telekomLogin"]["password"] = password
            else:
                data["telekomLogin"]["password"] = pwd

        return data