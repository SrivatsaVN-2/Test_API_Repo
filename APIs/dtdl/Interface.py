from pathlib import Path
from Test_API_Repo.APIs.dtdl.config_manager import Config_Manager
class Interface:
  def __init__(self,language, user_and_device_details, major_version, natco_config, STBConfig):
    #fields will be updated
    self.language = language
    self.user_and_device_details = user_and_device_details
    self.major_version = major_version
    self.natco_config = natco_config
    self.STBConfig = STBConfig
    
    config_path = Path(__file__).resolve().parent / "config.json"
    self.config_manager = Config_Manager(config_path, self)

    self._channel_api_client = None
    self._home_api_client = None
    self._epg_api_client = None
    self._movies_api_client = None
    self._recording_api_client = None
    self._rentedcontent_api_client = None
    self._search_api_client = None


    from Test_API_Repo.Utilities.Utils import Utils
    self.utils = Utils(self)

  def movies_api(self):
    if self._movies_api_client == None:
      from Test_API_Repo.APIs.dtdl.movies_api import MoviesApiClient
      self._movies_api_client = MoviesApiClient(interface = self)
    return self._movies_api_client

  def epg_api(self):
    if self._epg_api_client == None:
      from Test_API_Repo.APIs.dtdl.epg_api import EpgApiClient
      self._epg_api_client = EpgApiClient(interface = self)
    return self._epg_api_client

  def channel_api(self):
    if self._channel_api_client == None:
      from Test_API_Repo.APIs.dtdl.channel_api import ChannelApiClient
      self._channel_api_client = ChannelApiClient(interface = self)
    return self._channel_api_client

  def home_api(self):
    if self._home_api_client == None:
      from Test_API_Repo.APIs.dtdl.home_api import HomeApiClient
      self._home_api_client = HomeApiClient(interface = self)
    return self._home_api_client

  def recording_api(self):
    if self._recording_api_client == None:
      from Test_API_Repo.APIs.dtdl.recording_api import RecordingApiClient
      self._recording_api_client = RecordingApiClient(interface = self)
    return self._recording_api_client

  def rentedcontent_api(self):
    if self._rentedcontent_api_client == None:
      from Test_API_Repo.APIs.dtdl.rentedcontent_api import RentedContentApiClient
      self._rentedcontent_api_client = RentedContentApiClient(interface = self)
    return self._rentedcontent_api_client

  def search_api(self):
    if self._search_api_client == None:
      from Test_API_Repo.APIs.dtdl.search_api import SearchApiClient
      self._search_api_client = SearchApiClient(interface = self)
    return self._search_api_client


