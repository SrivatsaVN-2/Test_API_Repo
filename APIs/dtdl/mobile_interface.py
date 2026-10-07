# mobile_interface.py
#
# Mobile-touchpoint equivalent of Interface.py. The only piece that's
# genuinely touchpoint-specific: how natco/language/credentials get resolved
# (STB reads STBConfig/pytest-stb options; mobile reads the --natco CLI
# option plus configs/credentials.yaml). Once built, this plugs directly
# into the same shared BaseApiClient/Config_Manager and shared domain classes
# (HomeApiClient, ChannelApiClient, RecordingApiClient, etc. in home_api.py,
# channel_api.py, recording_api.py, ...) that STB uses - there's no separate
# mobile_*_api.py layer any more.
#
# build_mobile_interface(natco, os_type) is the one call a test case needs -
# it reads configs/credentials.yaml itself, so test cases don't each repeat
# the credential-fetching boilerplate (that used to be
# imports.base.get_credentials() plus an assert, in every test file).
#
# Source mapping (STB -> Mobile):
#   STBConfig.fdn_natco        -> the `natco` pytest fixture (--natco)
#   STBConfig.adb_device_id    -> helpers.device_manager.get_device_info(os_type)["device_id"]
#                                  (fetched live via adb/ideviceinfo, not static)
#   user_and_device_details    -> configs/credentials.yaml[natco] (username/passcode)
#   ...[4]["passcode"]         -> credentials.yaml's "passcode" field - this is what
#                                  Config_Manager.get_data() actually sends as
#                                  telekomLogin.password (`password or passcode`,
#                                  and the `password` arg passed in is always "").
#                                  credentials.yaml's separate "password" field is
#                                  kept for reference but not used in this LOGIN flow.
#   ...[4]["bff_token"]        -> credentials.yaml's "bff_token" field (optional). Used
#                                  by BaseApiClient._refresh_access_token() as the
#                                  fail-safe if dynamic LOGIN fails - for any natco, not
#                                  just STB's HU SDMC/HU SEI/MKT shortcut list (see
#                                  base_api_client.py).
#   ...[4]["x-adult-token"] -> no mobile equivalent yet; left empty.

from pathlib import Path

import yaml

from helpers import device_manager

# Test_API_Repo/APIs/dtdl/mobile_interface.py -> repo root is 3 parents up.
_CREDENTIALS_PATH = Path(__file__).resolve().parents[3] / "configs" / "credentials.yaml"


class MobileUserAndDeviceDetails:
    """
    Adapter for interface.user_and_device_details.

    Test_API_Repo's own code reads this two incompatible ways:
    Config_Manager.get_data() indexes it like a tuple ([0]=device_id,
    [3]=username, [4]=dict with passcode/bff_token), while
    SearchApiClient.search_movie() calls .get("access_token") on it like a
    dict. This satisfies both without changing either STB file.
    """

    def __init__(self, device_id, username, passcode, bff_token="", access_token=""):
        self._by_index = {
            0: device_id,
            3: username,
            4: {"passcode": passcode, "bff_token": bff_token, "access_token": access_token},
        }

    def __getitem__(self, index):
        return self._by_index[index]

    def get(self, key, default=None):
        return self._by_index[4].get(key, default)

    def __bool__(self):
        return True


class _MobileStbConfig:
    """Minimal stand-in for the STBConfig fields base_api_client.py actually reads."""

    def __init__(self, fdn_natco, adb_device_id):
        self.fdn_natco = fdn_natco
        self.adb_device_id = adb_device_id


class MobileInterface:
    """Mobile-touchpoint stand-in for Test_API_Repo's Interface class."""

    def __init__(self, language, natco_config, user_and_device_details, stb_config):
        self.language = language
        self.natco_config = natco_config
        self.major_version = "1.0"
        self.user_and_device_details = user_and_device_details
        self.STBConfig = stb_config


def _load_credentials(natco):
    """
    Read username/passcode/bff_token for `natco` from configs/credentials.yaml.
    passcode is what actually reaches telekomLogin.password (see the module
    docstring); bff_token is optional, used only as the dynamic-LOGIN
    fail-safe.
    """
    if not _CREDENTIALS_PATH.exists():
        raise FileNotFoundError(f"Credentials file not found at: {_CREDENTIALS_PATH}")

    with open(_CREDENTIALS_PATH, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}

    natco_creds = (doc.get("credentials") or {}).get(natco.lower(), {})
    username = natco_creds.get("username")

    if not username:
        raise ValueError(f"No credentials configured for NATCO '{natco}' in {_CREDENTIALS_PATH}")

    return username, natco_creds.get("passcode", ""), natco_creds.get("bff_token", "")


def build_mobile_interface(natco, os_type):
    """
    Build an Interface-shaped object for the mobile touchpoint, reading its
    credentials from configs/credentials.yaml itself.

    natco: e.g. "at" - drives config.json's language bucket, same as
        STBConfig.fdn_natco does for STB. Config.json's buckets are natco
        codes (AT, HR, ME, PL, MKT, HU), so this is upper-cased directly
        rather than routed through the --lang (english/native) option. Also
        the key used to look up this natco's credentials.
    os_type: "android" or "ios" - used to fetch the currently connected
        device's real id at runtime (STB used a static adb_device_id).
    """
    username, passcode, bff_token = _load_credentials(natco)

    device_info = device_manager.get_device_info(os_type)
    device_id = device_info.get("device_id") or "Unknown"

    stb_config = _MobileStbConfig(fdn_natco=natco.upper(), adb_device_id=device_id)

    user_and_device_details = MobileUserAndDeviceDetails(
        device_id=device_id,
        username=username,
        passcode=passcode,
        bff_token=bff_token,
    )

    return MobileInterface(
        language=natco.upper(),
        natco_config={"natco": natco.lower()},
        user_and_device_details=user_and_device_details,
        stb_config=stb_config,
    )
