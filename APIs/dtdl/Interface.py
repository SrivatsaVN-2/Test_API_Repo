from APIs.dtdl.config_manager import Config_Manager
class Interface:
  def __init__(self,language, user_and_device_details, major_version, natco_config, STBConfig):
    #fields will be updated
    self.language = language
    self.user_and_device_details = user_and_device_details
    self.major_version = major_version
    self.natco_config = natco_config
    self.STBConfig = STBConfig
    self.config_manager = Config_Manager()
    self._channel_api_client = None
    self._home_api_client = None
    self._epg_api_client = None
  @property
  def channel_api(self):
    if self._channel_api_client is None:
      from APIs.dtdl.channel_api import ChannelApiClient

      self._channel_api_client = ChannelApiClient(config_manager, self.natco_config)
    return self._channel_api_client
  
  @property
  def home_api(self):
    if self._home_api_client is None:
      from APIs.dtdl.home_api import HomeApiClient

      self._home_api_client = HomeApiClient(config_manager, self.natco_config)
    return self._home_api_client

  
  def epg_api(self):
    if self._epg_api_client is None:
      from tests.Test_API_Repo.APIs.dtdl.epg_api import EpgApiClient
      self._epg_api_client = EpgApiClient(self)
    return self._epg_api_client
  
