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
        Config manager should not create Interface.
        It receives Interface as a dependency.
        """

        self.interface = interface
        self.language = interface.language
        self.STBConfig = interface.STBConfig

        with open(config_file, "r") as file:
            self.config = json.load(file)

    def get_endpoint(self, lang, endpoint_type):
        return self.config["endpoints"].get(lang, {}).get(endpoint_type, "")

    def get_header(self, lang, header_type, token=""):
        header = self.config["headers"].get(lang, {}).get(header_type, {}).copy()

        if header_type == "OTHER":
            header["Authorization"] = f"Bearer {token}"

        elif header_type == "BFF_OTHER":
            header["bff_token"] = token

            if "x-adult-token" in header:
                del header["x-adult-token"]

        return header

    def get_param(self, lang, param_type):

        params = self.config["params"].get(lang, {}).get(param_type, {}).copy()

        if "app_language" in params:

            language = self.interface.language
            key = (language, lang)

            if key in LANGUAGE_MAPPING:
                params["app_language"] = LANGUAGE_MAPPING[key]

        return params

    def get_data(self, lang, data_type, username="", password=""):

        data = self.config["data"].get(lang, {}).get(data_type, {}).copy()

        device_id = self.STBConfig.adb_device_id

        utils = self.interface.utils
        user_info = utils.get_device_and_user_info(device_id)

        user_id = user_info[3]
        user_details = user_info[4]

        pwd = user_details.get("passcode")

        data["bff_token"] = user_details.get("bff_token")

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