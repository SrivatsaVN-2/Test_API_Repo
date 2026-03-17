# config_manager.py

import json
from pathlib import Path


LANGUAGE_MAPPING = {
    ("at", "AT"): "at",
    ("de", "AT"): "at",
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
        Config manager uses Interface as the single data source
        """

        if not interface:
            raise ValueError("Interface instance is required")

        # -----------------------------------
        # 1. Store Interface
        # -----------------------------------
        self.interface = interface
        self.language = interface.language.upper()
        self.stb_config = interface.STBConfig
        self.user_data = interface.user_and_device_details

        # -----------------------------------
        # 2. Load config.json safely
        # -----------------------------------
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as file:
            self.config = json.load(file)

    # =====================================================
    # 🔹 LANGUAGE MAPPING
    # =====================================================

    def _map_language(self, lang):
        """
        Map device language + natco to config language key
        """
        natco = getattr(self.stb_config, "fdn_natco", None)

        key = (lang.lower(), natco)
        mapped_lang = LANGUAGE_MAPPING.get(key, lang)

        return mapped_lang.upper()

    # =====================================================
    # 🔹 ENDPOINTS
    # =====================================================

    def get_endpoint(self, lang, endpoint_type):
        mapped_lang = self._map_language(lang)

        endpoint = (
            self.config.get("endpoints", {})
            .get(mapped_lang, {})
            .get(endpoint_type, "")
        )

        print(f"[CONFIG] Endpoint → {mapped_lang} | {endpoint_type} = {endpoint}")

        return endpoint

    # =====================================================
    # 🔹 HEADERS
    # =====================================================

    def get_header(self, lang, header_type, token=""):
        mapped_lang = self._map_language(lang)

        header = (
            self.config.get("headers", {})
            .get(mapped_lang, {})
            .get(header_type, {})
            .copy()
        )

        # -----------------------------------
        # Dynamic injection
        # -----------------------------------
        if header_type == "OTHER" and token:
            header["Authorization"] = f"Bearer {token}"

        elif header_type == "BFF_OTHER" and token:
            header["bff_token"] = token
            header.pop("x-adult-token", None)

        return header

    # =====================================================
    # 🔹 PARAMS
    # =====================================================

    def get_param(self, lang, param_type):
        mapped_lang = self._map_language(lang)

        params = (
            self.config.get("params", {})
            .get(mapped_lang, {})
            .get(param_type, {})
            .copy()
        )

        # -----------------------------------
        # Dynamic language override
        # -----------------------------------
        if "app_language" in params:
            device_lang = self.interface.get_language()
            key = (device_lang.lower(), mapped_lang.lower())

            if key in LANGUAGE_MAPPING:
                params["app_language"] = LANGUAGE_MAPPING[key]

        return params

    # =====================================================
    # 🔹 DATA (IMPORTANT FIXED PART)
    # =====================================================

    def get_data(self, lang, data_type, username="", password=""):
        """
        Fetch request payloads using Interface data (NO re-fetching)
        """

        mapped_lang = self._map_language(lang)

        data = (
            self.config.get("data", {})
            .get(mapped_lang, {})
            .get(data_type, {})
            .copy()
        )

        if not data:
            raise ValueError(f"No data found for {mapped_lang} → {data_type}")

        # -----------------------------------
        # Extract from Interface (clean way)
        # -----------------------------------
        user_id = self.interface.get_user_id()
        device_id = self.interface.get_device_id()
        user_details = self.user_data or {}

        # -----------------------------------
        # Extract tokens safely
        # -----------------------------------
        bff_token = ""
        passcode = ""

        if isinstance(user_details, dict):
            bff_token = user_details.get("bff_token", "")
            passcode = user_details.get("passcode", "")

        # Inject into payload
        data["bff_token"] = bff_token

        # -----------------------------------
        # NATCO shortcut (no login needed)
        # -----------------------------------
        if getattr(self.stb_config, "fdn_natco", None) in [
            "HU SDMC",
            "HU SEI",
            "MKT",
        ]:
            return data

        # -----------------------------------
        # LOGIN handling
        # -----------------------------------
        if data_type == "LOGIN":

            data.setdefault("telekomLogin", {})

            data["telekomLogin"]["username"] = username or user_id
            data["telekomLogin"]["password"] = password or passcode

            # Safety check
            if not data["telekomLogin"]["username"]:
                raise ValueError("Username missing in LOGIN payload")

            if not data["telekomLogin"]["password"]:
                raise ValueError("Password missing in LOGIN payload")

        return data
