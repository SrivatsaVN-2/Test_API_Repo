# config_manager.py
# Handles reading and providing configuration data from a JSON file

import json
import os

from APIs.dtdl.Interface import Interface

"""
from tests.androidtv.pages.helper import get_language
from tests.androidtv.pages.utility.stbconfig import STBConfig
from tests.androidtv.pages.utility.utils import Utils
"""

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


class ConfigManager:
    def __init__(self, config_file):
        self.interface = Interface()
        self.language = Interface.language
        # print(os.getcwd())
        with open(config_file, "r") as file:
            self.config = json.load(file)


    def get_endpoint(self, lang, endpoint_type):
        return self.config["endpoints"].get(lang, {}).get(endpoint_type, "")

    def get_header(self, lang, header_type, token=""):
        header = self.config["headers"].get(lang, {}).get(header_type, {})
        # if header_type in ["OTHER", "BFF_OTHER"]:
        #     header['Authorization'] = f'Bearer {token}'
        # return header
        # Check if token needs to be added to the header
        if header_type == "OTHER":
            header["Authorization"] = f"Bearer {token}"
            # print("Authorisation Token", token)
        elif header_type == "BFF_OTHER":
            header["bff_token"] = token

            # Remove x-adult-token from config headers as it should come from stb_data.json
            if "x-adult-token" in header:
                del header["x-adult-token"]

        return header

    def get_param(self, lang, param_type):
        params = self.config["params"].get(lang, {}).get(param_type, {}).copy()
        if "app_language" in params:

            language = get_language()
            key = (language, lang)
            if key in LANGUAGE_MAPPING:
                params["app_language"] = LANGUAGE_MAPPING[key]
        return params

    def get_data(self, lang, data_type, username="", password=""):
        user_infor = []
        data = self.config["data"].get(lang, {}).get(data_type, {}).copy()
        device_id = STBConfig.adb_device_id
        user_info = Utils().get_device_and_user_info(device_id)
        user_id, user_infor = user_info[3], user_info[4]
        # print("User info", user_infor)
        # print("User id", user_id)
        pwd = user_infor.get("passcode")
        data["bff_token"] = user_infor.get("bff_token")
        # print("STBConfig.fdn_natco ", STBConfig.fdn_natco)
        if STBConfig.fdn_natco in ["HU SDMC", "HU SEI", "MKT"]:
            # print("data", data)
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
        # print("Data", data)
        return data

