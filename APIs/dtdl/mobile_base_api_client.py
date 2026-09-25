# mobile_base_api_client.py
#
# The LOGIN endpoint (gateway-at-proxy.tv.yo-digital.com) load-balances
# across at least two backend instances - one healthy, one intermittently
# returning 500/503 (confirmed by different Set-Cookie srv_N values and a
# canary:true response header on the failing one). Which instance a given
# request lands on isn't controlled by the client, so this retries the LOGIN
# POST a few times on a 5xx before giving up, on the theory that a later
# attempt is likely to land on the healthy instance. This does not touch
# base_api_client.py (STB's shared login flow).
#
# Also regenerates config.json's static LOGIN identifiers (device-id,
# requestid, x-request-session-id, x-request-tracking-id) per attempt, since
# those are captured-once values every automated login was replaying
# unchanged, unlike a real UI login which mints fresh ones each time.
#
# bff_token shortcut: STB's base_api_client.py only honors a pre-supplied
# bff_token (skipping the LOGIN POST entirely) for a hardcoded natco list
# (HU SDMC/HU SEI/MKT). Mobile isn't bound by that STB-specific list - if a
# bff_token is supplied for ANY natco (e.g. captured from a real logged-in
# browser session for test777), use it directly.

import time
import uuid

from Test_API_Repo.APIs.dtdl.base_api_client import BaseApiClient


class MobileBaseApiClient(BaseApiClient):

    _FRESH_ID_HEADERS = ("device-id", "requestid", "x-request-session-id", "x-request-tracking-id")
    _LOGIN_MAX_ATTEMPTS = 4
    _LOGIN_RETRY_BACKOFF_SECONDS = 2

    def _refresh_access_token(self):
        data = self.config_manager.get_data(self.language, "LOGIN")

        if not data or not data.get("telekomLogin"):
            raise ValueError("Missing 'telekomLogin' in login payload")

        username = data["telekomLogin"].get("username")
        password = data["telekomLogin"].get("password")

        if not username or not password:
            raise ValueError(
                f"Invalid credentials -> username={username}, password={'set' if password else 'missing'}"
            )

        if data.get("bff_token"):
            self.access_token = data["bff_token"]
            return

        base_url = self.config_manager.get_endpoint(self.language, "BASE")
        login_endpoint = self.config_manager.get_endpoint(self.language, "LOGIN")

        if login_endpoint.startswith("http"):
            url = login_endpoint
        else:
            url = f"{base_url.rstrip('/')}/{login_endpoint.lstrip('/')}"

        last_response = None

        for attempt in range(1, self._LOGIN_MAX_ATTEMPTS + 1):
            headers = self.config_manager.get_header(self.language, "LOGIN")

            # Fresh identifiers per attempt - see module docstring.
            for header_name in self._FRESH_ID_HEADERS:
                if header_name in headers:
                    headers[header_name] = str(uuid.uuid4())

            response = self.session.post(url, headers=headers, json=data)

            if response.status_code < 500:
                # 2xx or 4xx - retrying a 4xx (bad credentials, etc.) won't
                # help, so resolve here either way.
                response.raise_for_status()
                self.access_token = response.json().get("accessToken", "")
                if not self.access_token:
                    raise ValueError("Access token missing in response")
                return

            last_response = response
            remaining = self._LOGIN_MAX_ATTEMPTS - attempt
            if remaining:
                time.sleep(self._LOGIN_RETRY_BACKOFF_SECONDS)

        last_response.raise_for_status()
