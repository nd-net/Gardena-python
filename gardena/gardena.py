import logging
import requests
from urllib.parse import urljoin

_LOGGER = logging.getLogger(__name__)

class JsonObject:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
    
    def __repr__(self):
        items = ("{}={!r}".format(k, v) for k, v in self.__dict__.items())
        return "{}({})".format(self.__class__.__name__, ", ".join(items))
    
    @classmethod
    def wrap(cls, val):
        if isinstance(val, cls):
            return val
        if isinstance(val, dict):
            return cls(**val)
        return cls(**val.__dict__)
    
    @classmethod
    def wrap_list(cls, val):
        return [cls.wrap(i) for i in val]

class Session(JsonObject):
    token = None
    user_id = None
    refresh_token = None

class Location(JsonObject):
    id = None
    name = None
    devices = None

class Property(JsonObject):
    id = None
    name = None
    value = None
    unit = None
    timestamp = None
    writeable = None
    supported_values = None

class Location(JsonObject):
    id = None
    name = None
    devices= None

class Property(JsonObject):
    id = None
    name = None
    value = None
    unit = None
    timestamp = None
    writeable = None
    supported_values = None

class Ability(JsonObject):
    id = None
    name = None
    type = None
    _properties = {}
    
    @property
    def properties(self):
        return self._properties
    @properties.setter
    def properties(self, value):
        self._properties = Property.wrap_list(value)

class Device(JsonObject):
    id = None
    name = None
    description = None
    category = None
    device_state = None
    _abilities = None
    
    @property
    def abilities(self):
        return self._abilities
    @abilities.setter
    def abilities(self, value):
        self._abilities = Ability.wrap_list(value)

class BaseURLSession(requests.Session):
    
    base_url = None
    
    def __init__(self, base_url=None, *args, **kw):
        super().__init__(*args, **kw)
        self.base_url = base_url
    
    def request(self, method, url, *args, **kw):
        return super().request(method, urljoin(self.base_url, url), *args, **kw)

class Hub:
    base_url = "https://smart.gardena.com/sg-1/"

    session = Session()
    requestSession = None
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.requestSession = BaseURLSession(self.base_url)
    
    def login(self):
        _LOGGER.info("Logging in with user name %s", self.username)
        self.requestSession = BaseURLSession(self.base_url)
        self.requestSession.headers["Accept"] = "application/json"
        data = {
            "sessions": {
                "email": self.username,
                "password": self.password,
            }
        }
        response = self.requestSession.post("sessions", json=data)
        json = response.json()
        self.session = Session(**json.get("sessions", {}))
        _LOGGER.debug("Got a session %s", self.session)
        self.requestSession.headers["X-Session"] = self.session.token
    
    def retrieve_locations(self):
        _LOGGER.info("Retrieving locations for user id %s", self.session.user_id)
        response = self.requestSession.get("locations", params={
            "user_id": self.session.user_id
        })
        data = response.json()
        _LOGGER.debug("Got locations %s", data)
        return Location.wrap_list(data.get("locations", []))
    
    def retrieve_devices(self, location):
        _LOGGER.info("Retrieving devices for location id %s", location.id)
        response = self.requestSession.get("devices", params={
            "locationId": location.id
        })
        data = response.json()
        _LOGGER.debug("Got devices %s", data)
        return Device.wrap_list(data.get("devices", []))
    
