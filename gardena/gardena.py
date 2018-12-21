import logging
import requests

_LOGGER = logging.getLogger(__name__)

def as_type(type, object):
    if isinstance(object, type):
        return object
    return type(**object)

def as_listof(type, value):
    return [as_type(Property, v) for v in value or []]

def lenient(type_converter=None):
    
    def matching_type(value, key):
        converter = type_converter.get(key, None) if type_converter else None
        if not converter:
            return value
        return converter(value)
    
    def decorator(func):
        import inspect
        from functools import wraps
        sig = inspect.signature(func)
        keys = [param.name for param in sig.parameters.values() if param.kind == param.POSITIONAL_OR_KEYWORD]
    
        @wraps(func)
        def lenient_function(*args, **kw):
            a = [matching_type(value, name) for name, value in zip(keys, args)]
            filtered = { key: matching_type(kw.get(key, None), key) for key in keys[len(args):] }
            return func(*args, **filtered)
    
        return lenient_function
    return decorator

def defaults_namedtuple(name, fields, type_converter=None):
    from collections import namedtuple

    result = namedtuple(name, fields)
    result.__new__ = lenient(type_converter)(result.__new__)
    return result

Session = defaults_namedtuple("Session", "token user_id refresh_token")
Location = defaults_namedtuple("Location", "id name devices")
Property = defaults_namedtuple("Property", "id name value unit timestamp writeable supported_values")
Ability = defaults_namedtuple("Ability", "id name type properties", {
    "properties": lambda value: as_listof(Property, value)
})
Device = defaults_namedtuple("Device", "id name description category device_state, abilities", {
    "abilities": lambda value: as_listof(Ability, value)
})

class Hub:
    BASE_URL = "https://smart.gardena.com/sg-1"

    session = Session()
    requestSession = None
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.requestSession = requests.Session()
    
    def execute(self, path, params=None, data=None, method=None):
        headers = {
            "Accept": "application/json",
        }
        
        if not method:
            method = "get" if data is None else "post"
        response = self.requestSession.request(
            method,
            url=self.BASE_URL + path,
            params=params,
            headers=headers,
            json=data,
            allow_redirects=True,
        )
        print(response.content)
        return response
    
    def login(self):
        _LOGGER.info("Logging in with user name %s", self.username)
        self.requestSession = requests.Session()
        data = {
            "sessions": {
                "email": self.username,
                "password": self.password,
            }
        }
        response = self.execute("/sessions", data=data)
        json = response.json()
        self.session = Session(**json.get("sessions", {}))
        _LOGGER.info("Got a session %s", self.session)
        self.requestSession.headers["X-Session"] = self.session.token
    
    def retrieve_locations(self):
        _LOGGER.info("Retrieving locations for user id %s", self.session.user_id)
        response = self.execute("/locations", {"user_id": self.session.user_id})
        data = response.json()
        _LOGGER.info("Got locations %s", data)
        return [as_type(Location, location) for location in data.get("locations", [])]
    
    def retrieve_devices(self, location):
        _LOGGER.info("Retrieving devices for location id %s", location.id)
        response = self.execute("/devices", {"locationId": location.id})
        data = response.json()
        _LOGGER.info("Got devices %s", data)
        return [as_type(Device, location) for location in data.get("devices", [])]
        
