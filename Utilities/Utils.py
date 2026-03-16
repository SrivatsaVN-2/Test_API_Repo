# External libraries
import json
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Union

# Internal libraries
from tests.Test_API_Repo.Utilities.Loggers import Logger


log = Logger().setup_logger("api.Utils")


class Utils:
    def __init__(self, interface):
        """
        Interface object contains shared runtime data and STBConfig reference.
        """
        self.interface = interface
        self.STBConfig = interface.STBConfig

    def load_data_from_file(self, filename: str) -> Union[Dict[str, Any], None]:
        """
        Load JSON data from a file.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            log.error("File %s not found", filename)
            return None

        except json.JSONDecodeError:
            log.error("Invalid JSON file: %s", filename)
            return None

    def get_device_and_user_info(self, device_id: str) -> Union[Tuple, str]:
        """
        Fetch device information from local JSON file.
        """

        # locate file relative to this module
        filename = Path(__file__).resolve().parent / "stb_data.json"

        data = self.load_data_from_file(filename)

        if not data:
            return "Device data not available"

        device_id = str(device_id).strip()

        devices = data.get("devices", {})
        users = data.get("users", {})

        if device_id not in devices:
            return f"Device with ID {device_id} not found."

        device_info = devices.get(device_id)

        natco = device_info.get("natco")
        model = device_info.get("model")
        user_id = device_info.get("user_id")
        user_info = users.get(user_id, {})
        total_ram = device_info.get("total_ram", "N/A")

        return (device_id, natco, model, user_id, user_info, total_ram)

    def parse_entry(self, entry: str) -> Dict[str, str]:
        """
        Parse friendly device entry string to extract metadata.
        """

        pattern = (
            r"(?P<natco>AT|PL|ME|HU SDMC|HU SEI|HR|MKT)"
            r"(\s+(?P<location>ONSITE|IN))?"
            r"\s+(?P<mr_version>MR\d+(\.\d+)?)"
            r"(\s+(?P<build>eng|debug))?"
        )

        match = re.search(pattern, entry, re.IGNORECASE)

        if not match:
            return {"error": "Could not parse entry"}

        natco = match.group("natco")
        location = match.group("location") or "LISBON"
        mr_version = match.group("mr_version")
        build_type = match.group("build")

        if build_type == "eng":
            build = "engprod"
        elif build_type == "debug":
            build = "debug"
        else:
            build = "prod"

        return {
            "natco": natco,
            "location": location,
            "mr_version": mr_version,
            "build": build,
        }

    def update_stb_config(self, device_info: Tuple, parsed_entry: Dict[str, str]):
        """
        Update shared STBConfig reference with collected values.
        """

        device_id, natco, model, user_id, user_info, total_ram = device_info

        # Modify attributes on shared STBConfig reference
        self.STBConfig.invntry_device_id = device_id
        self.STBConfig.invntry_natco = natco
        self.STBConfig.invntry_model_name = model
        self.STBConfig.user_id = user_id
        self.STBConfig.user_info = user_info
        self.STBConfig.total_ram = total_ram

        self.STBConfig.fdn_natco = parsed_entry.get("natco")
        self.STBConfig.fdn_mr_version = parsed_entry.get("mr_version")
        self.STBConfig.fnd_build = parsed_entry.get("build")

        log.info("STBConfig updated through API repo utils")
