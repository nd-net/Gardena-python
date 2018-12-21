import logging
import requests

_LOGGER = logging.getLogger(__name__)

def defaults_namedtuple(name, fields):
    from collections import namedtuple
    result = namedtuple(name, fields)
    result.__new__.__defaults__ = (None,) * len(result._fields)
    return result

Session = defaults_namedtuple("Session", "token user_id refresh_token")

class Location:
    
    def __init__(self, id, name=None, devices=None, **kw):
        self.id = id
        self.name = name
        self.devices = devices or []
    
    def __repr__(self):
        return "Location({})".format(", ".join(repr(i) for i in (self.id, self.name, self.devices)))

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
        return [Location(**location) for location in data.get("locations", [])]
