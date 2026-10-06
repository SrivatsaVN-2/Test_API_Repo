# base_api_client.py

import time
import uuid

import requests
import yaml
from pathlib import Path

from Test_API_Repo.APIs.dtdl.config_manager import Config_Manager
from Test_API_Repo.Utilities.Loggers import Logger

log = Logger().setup_logger("API.BaseApiClient")

# Test_API_Repo/APIs/dtdl/base_api_client.py -> repo root is 3 parents up.
_CREDENTIALS_PATH = Path(__file__).resolve().parents[3] / "configs" / "credentials.yaml"


class BaseApiClient:

    _FRESH_ID_HEADERS = ("device-id", "requestid", "x-request-session-id", "x-request-tracking-id")
    _LOGIN_MAX_ATTEMPTS = 4
    _LOGIN_RETRY_BACKOFF_SECONDS = 2

    def __init__(self, interface=None, config_manager=None):

        if not interface:
            raise ValueError("Interface instance is required")

        self.interface = interface

        if config_manager:
            self.config_manager = config_manager
        else:
            config_path = Path(__file__).resolve().parent / "config.json"
            self.config_manager = Config_Manager(config_path, interface)

        # -----------------------------------
        # Interface data
        # -----------------------------------
        self.language = self.interface.language
        self.natco_config = self.interface.natco_config
        self.major_version = self.interface.major_version
        self.user_and_device_data = self.interface.user_and_device_details
        self.stb_config = self.interface.STBConfig

        self.session = requests.Session()
        self.access_token = None
        self.adult_token = None

    # =====================================================
    # 🔹 HEADER BUILDER (NEW - replaces get_headers())
    # =====================================================

    def _build_headers(self, header_type="OTHER", requires_auth=True, requires_adult=False):

        # 1. Base headers from config
        headers = self.config_manager.get_header(
            self.language, header_type, token=self.access_token
        ) or {}

        # 2. Auth headers
        if requires_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            headers["bff_token"] = self.access_token

        # 3. Device info
        device_id = getattr(self.stb_config, "adb_device_id", None)
        if device_id:
            headers["x-device-id"] = device_id

        # 4. Natco + language
        natco = self.natco_config.get("natco")
        if natco:
            headers["x-natco"] = natco

        headers["x-language"] = self.language

        # 5. Adult token
        if requires_adult:
            if not self.adult_token:
                self.adult_token = self._get_adult_token_from_interface()

            if self.adult_token:
                headers["x-adult-token"] = self.adult_token

        return headers

    # =====================================================
    # 🔹 TOKEN HELPERS
    # =====================================================

    def _get_adult_token_from_interface(self):
        try:
            if not self.user_and_device_data:
                return ""

            if isinstance(self.user_and_device_data, dict):
                return self.user_and_device_data.get("x-adult-token", "")

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

        # 1. Ensure token
        if requires_auth and not self.access_token:
            self._refresh_access_token()

        # 2. Build headers (REPLACED LOGIC)
        headers = self._build_headers(
            header_type="OTHER",
            requires_auth=requires_auth,
            requires_adult=requires_adult_token,
        )

        # 3. Merge custom headers if provided.
        # Callers often pass a header dict fetched straight from a static
        # config.json template (e.g. header_type="BFF_OTHER"), which can
        # contain a placeholder empty-string "bff_token"/"Authorization"
        # entry. A plain .update() would let that blank placeholder
        # overwrite the real auth values _build_headers() just computed
        # above - so blank/None values from the caller are dropped instead
        # of applied, while any genuine override the caller supplies still
        # takes effect.
        if "headers" in kwargs:
            custom_headers = {
                k: v for k, v in kwargs["headers"].items() if v not in (None, "")
            }
            headers.update(custom_headers)

        kwargs["headers"] = headers

        # 4. API call
        response = self.session.request(method, url, **kwargs)

        response.raise_for_status()

        try:
            return response.json()
        except Exception:
            return response.text

    # =====================================================
    # 🔹 TOKEN REFRESH
    # =====================================================
    #
    # NATCO shortcut (HU SDMC / HU SEI / MKT) is unchanged: those skip LOGIN
    # entirely and use the stored bff_token immediately, exactly as before.
    #
    # Every other NATCO (e.g. AT) now gets a resilient dynamic LOGIN: the
    # LOGIN gateway load-balances across backend instances, at least one of
    # which has been observed intermittently returning 500/503 (confirmed by
    # differing Set-Cookie srv_N values and a canary:true response header on
    # the failing one). Which instance a given request lands on isn't
    # controlled by the client, so a 5xx is retried a few times on the theory
    # that a later attempt lands on a healthy instance - regenerating
    # config.json's static LOGIN identifiers (device-id, requestid,
    # x-request-session-id, x-request-tracking-id) per attempt, since those
    # are captured-once values every automated login was otherwise replaying
    # unchanged. If dynamic LOGIN still fails after retries (or hits an
    # un-retryable 4xx), the stored bff_token - if one is configured - is
    # used as a fail-safe instead of erroring out. If dynamic LOGIN succeeds
    # and the fresh token differs from the stored one, the stored one is
    # updated automatically (tokens expire ~2 weeks after issue).

    def _refresh_access_token(self):

        data = self.config_manager.get_data(self.language, "LOGIN")

        if not data or not data.get("telekomLogin"):
            raise ValueError("Missing 'telekomLogin' in login payload")

        username = data["telekomLogin"].get("username")
        password = data["telekomLogin"].get("password")

        if not username or not password:
            raise ValueError(
                f"Invalid credentials → username={username}, password={password}"
            )

        fallback_bff_token = data.get("bff_token")

        # NATCO shortcut - unchanged.
        if (
            fallback_bff_token
            and self.stb_config
            and getattr(self.stb_config, "fdn_natco", None)
            in ["HU SDMC", "HU SEI", "MKT"]
        ):
            self.access_token = fallback_bff_token
            return

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        login_endpoint = self.config_manager.get_endpoint(self.language, "LOGIN")

        if login_endpoint.startswith("http"):
            url = login_endpoint
        else:
            url = f"{base_url.rstrip('/')}/{login_endpoint.lstrip('/')}"

        last_response = None
        fresh_token = None

        for attempt in range(1, self._LOGIN_MAX_ATTEMPTS + 1):
            headers = self.config_manager.get_header(self.language, "LOGIN")

            # Fresh identifiers per attempt - see class docstring above.
            for header_name in self._FRESH_ID_HEADERS:
                if header_name in headers:
                    headers[header_name] = str(uuid.uuid4())

            try:
                response = self.session.post(url, headers=headers, json=data)
            except requests.exceptions.RequestException:
                # Per-attempt detail is suppressed - only the single summary
                # line below (on final fallback) is shown.
                last_response = None
                if attempt < self._LOGIN_MAX_ATTEMPTS:
                    time.sleep(self._LOGIN_RETRY_BACKOFF_SECONDS)
                continue

            if response.status_code < 500:
                # 2xx, or an un-retryable 4xx (bad credentials, 401, 403,
                # etc.) - retrying with the same data won't help, so stop
                # trying the dynamic path here either way.
                last_response = response
                if response.status_code < 300:
                    fresh_token = response.json().get("accessToken", "")
                break

            last_response = response
            remaining = self._LOGIN_MAX_ATTEMPTS - attempt
            # Per-attempt detail is suppressed - only the single summary line
            # below (on final fallback) is shown.
            if remaining:
                time.sleep(self._LOGIN_RETRY_BACKOFF_SECONDS)

        if fresh_token:
            self.access_token = fresh_token
            log.info("Dynamically generated a fresh access token via LOGIN.")
            if fallback_bff_token and fallback_bff_token != fresh_token:
                self._persist_bff_token_if_changed(fresh_token)
            return

        # Dynamic LOGIN failed - fall back to the stored bff_token (the
        # "instead of erroring, read the hardcoded bff_token" fail-safe).
        if fallback_bff_token:
            status_desc = str(last_response.status_code) if last_response is not None else "no response"
            log.error(f"Error {status_desc} while logging in - falling back to hardcoded BFF token.")
            self.access_token = fallback_bff_token
            return

        # No fallback available either - fail loudly with whatever detail we have.
        if last_response is not None:
            last_response.raise_for_status()
        raise ValueError("LOGIN failed (no response from server) and no fallback bff_token is configured.")

    def _persist_bff_token_if_changed(self, new_token):
        """
        Updates credentials.yaml's bff_token for the current NATCO if it
        differs from what's stored, so the next run picks up the fresh token
        without needing another dynamic LOGIN. Best-effort: a failure here
        (e.g. file locked) is logged, not raised - self.access_token is
        already set from the live LOGIN response regardless.
        """
        natco_key = self.language.lower()
        try:
            with open(_CREDENTIALS_PATH, "r", encoding="utf-8") as f:
                doc = yaml.safe_load(f)

            natco_creds = doc.get("credentials", {}).get(natco_key)
            if natco_creds is None:
                log.warning(f"No '{natco_key}' entry in credentials.yaml - skipping bff_token persist.")
                return

            if natco_creds.get("bff_token") == new_token:
                return  # unchanged, nothing to write

            natco_creds["bff_token"] = new_token

            with open(_CREDENTIALS_PATH, "w", encoding="utf-8") as f:
                yaml.safe_dump(doc, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

            log.info(f"credentials.yaml's bff_token for '{natco_key}' updated with the freshly generated token.")

        except Exception as e:
            log.warning(f"Could not persist updated bff_token to credentials.yaml: {e!r}")
