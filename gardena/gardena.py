class NotLoggedInException(Exception):
    """Not logged to Gardena Web Services Exception."""

    def __init__(self):
        super(NotLoggedInException, self).__init__()


def defaults_namedtuple(name, fields):
    from collections import namedtuple
    result = namedtuple(name, fields)
    result.__new__.__defaults__ = (None,) * len(result._fields)
    return result

Session = defaults_namedtuple("Session", "token user_id refresh_token")

class Hub:
    BASE_URL = "https://smart.gardena.com/sg-1"

    session = Session()
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def execute(self, path, data, useSession=True):
        import requests
        import json
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if useSession:
            if not self.session.token:
                raise NotLoggedInException()
            headers["X-Session"] = self.session.token
        return requests.post(
            url=self.BASE_URL + path,
            headers=headers,
            data=json.dumps(data) if data is not None else None
        )
    
    def login(self):
        data = {
            "sessions": {
                "email": self.username,
                "password": self.password,
            }
        }
        response = self.execute("/sessions", data, useSession=False)
        json = response.json()
        self.session = Session(**json.get("sessions", {}))
        if not self.session.token:
            raise NotLoggedInException()
