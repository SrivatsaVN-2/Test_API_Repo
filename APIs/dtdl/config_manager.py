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
        Config manager receives Interface from the framework.
        It should NOT fetch STB data itself.
        """

        self.interface = interface
        self.language = interface.language
        self.STBConfig = interface.STBConfig

        # device + user data already provided by STBT repo
        self.device_user_data = interface.user_and_device_details

        with open(config_file, "r") as file:
            self.config = json.load(file)

    # ----------------------------------------------------
    # LANGUAGE RESOLUTION
    # ----------------------------------------------------

    def _resolve_language(self, lang):
        """
        Resolve the correct language key using LANGUAGE_MAPPING.
        """

        natco = self.STBConfig.fdn_natco

        key = (lang, natco)

        if key in LANGUAGE_MAPPING:
            return LANGUAGE_MAPPING[key]

        # fallback to natco if mapping does not exist
        return natco

    # ----------------------------------------------------
    # CONFIG ACCESSORS
    # ----------------------------------------------------

    def get_endpoint(self, lang, endpoint_type):

        lang_key = self._resolve_language(lang)

        endpoint = self.config["endpoints"].get(lang_key, {}).get(endpoint_type, "")

        print(f"Fetched endpoint for lang '{lang_key}' and type '{endpoint_type}': {endpoint}")

        return endpoint

    def get_header(self, lang, header_type, token=""):

        lang_key = self._resolve_language(lang)

        header = self.config["headers"].get(lang_key, {}).get(header_type, {}).copy()

        if header_type == "OTHER":
            header["Authorization"] = f"Bearer {token}"

        elif header_type == "BFF_OTHER":
            header["bff_token"] = token

            if "x-adult-token" in header:
                del header["x-adult-token"]

        return header

    def get_param(self, lang, param_type):

        lang_key = self._resolve_language(lang)

        params = self.config["params"].get(lang_key, {}).get(param_type, {}).copy()

        if "app_language" in params:

            language = self.interface.language
            key = (language, lang)

            if key in LANGUAGE_MAPPING:
                params["app_language"] = LANGUAGE_MAPPING[key]

        return params

    def get_data(self, lang, data_type, username="", password=""):

        lang_key = self._resolve_language(lang)

        data = self.config["data"].get(lang_key, {}).get(data_type, {}).copy()

        # device info already provided by STBT repo
        device_info = self.device_user_data

        device_id = device_info[0]
        natco = device_info[1]
        model = device_info[2]
        user_id = device_info[3]
        user_details = device_info[4]

        # handle both string and dict formats safely
        if isinstance(user_details, str):
            pwd = user_details
            bff_token = ""
        else:
            pwd = user_details.get("passcode")
            bff_token = user_details.get("bff_token")

        data["bff_token"] = bff_token

        if self.STBConfig.fdn_natco in ["HU SDMC", "HU SEI", "MKT"]:
            return data

        if data_type == "LOGIN":

            login_block = data.setdefault("telekomLogin", {})

            login_block["username"] = username if username else user_id
            login_block["password"] = password if password else pwd

        return data