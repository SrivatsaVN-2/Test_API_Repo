# mobile_interface.py
#
# Mobile-touchpoint equivalent of Interface.py. The only piece that's
# genuinely touchpoint-specific: how natco/language/credentials get resolved
# (STB reads STBConfig/pytest-stb options; mobile reads the --natco CLI
# option plus Configs/credentials.yaml). Once built, this plugs directly
# into the same shared BaseApiClient/Config_Manager and shared domain classes
# (HomeApiClient, ChannelApiClient, RecordingApiClient, etc. in home_api.py,
# channel_api.py, recording_api.py, ...) that STB uses - there's no separate
# mobile_*_api.py layer any more.
#
# Source mapping (STB -> Mobile):
#   STBConfig.fdn_natco        -> the `natco` pytest fixture (--natco)
#   STBConfig.adb_device_id    -> helpers.device_manager.get_device_info(os_type)["device_id"]
#                                  (fetched live via adb/ideviceinfo, not static)
#   user_and_device_details    -> Configs/credentials.yaml[natco] (username/passcode)
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

from helpers import device_manager


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


def build_mobile_interface(natco, os_type, username, passcode, bff_token=""):
    """
    Build an Interface-shaped object for the mobile touchpoint.

    natco: e.g. "at" - drives config.json's language bucket, same as
        STBConfig.fdn_natco does for STB. Config.json's buckets are natco
        codes (AT, HR, ME, PL, MKT, HU), so this is upper-cased directly
        rather than routed through the --lang (english/native) option.
    os_type: "android" or "ios" - used to fetch the currently connected
        device's real id at runtime (STB used a static adb_device_id).
    username, passcode: from Configs/credentials.yaml for this natco -
        passcode is what actually reaches telekomLogin.password (see the
        module docstring).
    bff_token: optional, from Configs/credentials.yaml. Used as the fail-safe
        access token if dynamic LOGIN fails (see base_api_client.py's
        _refresh_access_token()), and auto-refreshed there on success.
    """
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
