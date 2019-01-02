import logging
import requests
from urllib.parse import urljoin
from typing import List
from inspect import isclass
from enum import Enum

__all__ = [
    "Abilities",
    "Ability",
    "Command",
    "Device",
    "Error",
    "Hub",
    "Location",
    "MowerCommands",
    "OutletCommands",
    "Properties",
    "Property",
    "Recurrence",
    "ScheduledEvent",
    "SensorCommands",
    "Session",
    "StatusReportHistory",
]

_LOGGER = logging.getLogger(__name__)

def convert(cls, value):
    # special handling for typing.List
    if getattr(cls, "__origin__", None) in (list, List):
        try:
            list_type = cls.__args__[0]
            return [convert(list_type, i) for i in value]
        except:
            pass
    if isinstance(value, cls):
        return value
    if isinstance(value, dict):
        return cls(**value)
    return value

class JsonObject:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
    
    def __setattr__(self, name, value):
        attributes = getattr(self, "__attributes__", {})
        cls = attributes.get(name, None)
        if cls:
            value = convert(cls, value)
        super().__setattr__(name, value)
    
    def __repr__(self):
        items = ("{}={!r}".format(k, v) for k, v in self.__dict__.items())
        return "gardena.{}({})".format(self.__class__.__name__, ", ".join(items))

class Error(JsonObject):
    id = None
    status = None
    title = None
    detail = None

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
    supported_values = []

class Ability(JsonObject):
    id = None
    name = None
    type = None
    properties = []
    __attributes__ = {
        "properties": List[Property],
    }

class Recurrence(JsonObject):
    type = None
    weekdays = []

class ScheduledEvent(JsonObject):
    id = None
    type = None
    start_at = None
    end_at = None
    weekday = None
    recurrence = None
    __attributes__ = {
        "recurrence": Recurrence,
    }

class StatusReportHistory(JsonObject):
    level = None
    message = None
    raw_message = None
    source = None
    timestamp = None

class Device(JsonObject):
    id = None
    name = None
    abilities = []
    category = None
    configuration_synchronized = None
    configuration_synchronized_v2 = None
    configuration_update = None
    configuration_update = None
    constraints = []
    description = None
    device_state = None
    property_constraints = []
    scheduled_events = []
    settings = []
    status_report_history = []
    zones = []
    __attributes__ = {
        "abilities": List[Ability],
        "scheduled_events": List[ScheduledEvent],
        "status_report_history": List[StatusReportHistory]
    }
    

class Abilities:
    ambient_temperature = "ambient_temperature"
    battery = "battery"
    device_info = "device_info"
    firmware = "firmware"
    gateway = "gateway"
    humidity = "humidity"
    light = "light"
    manual_watering = "manual_watering"
    mower = "mower"
    mower_stats = "mower_stats"
    mower_type = "mower_type"
    outlet = "outlet"
    power = "power"
    radio = "radio"
    soil_temperature = "soil_temperature"
    watering = "watering"

class Properties:
    # Properties for the "device_info" ability
    connection_status = "connection_status"
    product = "product"
    category = "category"
    wifi_status = "wifi_status"
    version = "version"
    last_time_online = "last_time_online"
    manufacturer = "manufacturer"
    serial_number = "serial_number"
    sgtin = "sgtin"
    ethernet_status = "ethernet_status"

    # Properties for the "gateway" ability
    homekit_setup_payload = "homekit_setup_payload"
    ip_address = "ip_address"
    time_zone = "time_zone"

    # Properties for the "battery" ability
    level = "level"
    charging = "charging"

    # Properties for the "radio" ability
    state = "state"
    # connection_status = "connection_status"
    quality = "quality"

    # Properties for the "firmware" ability
    firmware_upload_progress = "firmware_upload_progress"
    firmware_status = "firmware_status"
    firmware_available_version = "firmware_available_version"
    firmware_command = "firmware_command"
    firmware_update_start = "firmware_update_start"
    inclusion_status = "inclusion_status"

    # Properties for the "mower" ability
    manual_operation = "manual_operation"
    status = "status"
    source_for_next_start = "source_for_next_start"
    override_end_time = "override_end_time"
    error = "error"
    last_error_code = "last_error_code"
    timestamp_last_error_code = "timestamp_last_error_code"
    timestamp_next_start = "timestamp_next_start"

    # Properties for the "mower_stats" ability
    cutting_time = "cutting_time"
    collisions = "collisions"
    running_time = "running_time"
    charging_cycles = "charging_cycles"

    # Properties for the "mower_type" ability
    mmi_version = "mmi_version"
    mainboard_version = "mainboard_version"
    device_variant = "device_variant"
    comboard_version = "comboard_version"
    # serial_number = "serial_number"
    device_type = "device_type"
    base_software_up_to_date = "base_software_up_to_date"

class Command:
    
    def __init__(self, name, ability, parameters=None):
        self.name = name
        self.ability = ability 
        self.parameters = parameters
    
    def __repr__(self):
        args = [self.name, self.ability]
        if self.parameters:
            args.append(self.parameters)
        return "gardena.Command({})".format(", ".join(repr(i) for i in args))

def command(ability):
    def decorator(func):
        import inspect
        from functools import wraps
        signature = inspect.signature(func)
    
        @wraps(func)
        def createCommand(*args, **kw):
            bound = signature.bind(*args, **kw)
            return Command(func.__name__, ability, bound.arguments)
        return createCommand
    return decorator

class MowerCommands:
    
    @staticmethod
    @command(Abilities.mower)
    def park_until_further_notice():
        """
        Park a mower until further notice.
        """

    @staticmethod
    @command(Abilities.mower)
    def park_until_next_timer():
        """
        Park a mower until next timer.
        """
        
    @staticmethod
    @command(Abilities.mower)
    def start_override_timer(duration: int):
        """
        Manually override the mower timer.
        
        :param duration: the duration that the mower should mow, in minutes
        """
        
    @staticmethod
    @command(Abilities.mower)
    def start_resume_schedule():
        """
        Resume the mower scheduler.
        """

class SensorCommands:
    
    @staticmethod
    @command(Abilities.ambient_temperature)
    def measure_ambient_temperature():
        """
        Measure the ambient temperature.
        """

    @staticmethod
    @command(Abilities.light)
    def measure_light():
        """
        Measure the light.
        """

    @staticmethod
    @command(Abilities.humidity)
    def measure_soil_humidity():
        """
        Measure the soil humidity.
        """
    
    @staticmethod
    @command(Abilities.soil_temperature)
    def measure_soil_temperature():
        """
        Measure the soil temperature.
        """

class OutletCommands:
    
    @staticmethod
    @command(Abilities.outlet)
    def manual_override(duration: int, manual_override="open"):
        """
        Start the manual watering.
        
        :param duration: the duration that the manual override lasts, in minutes
        """
    
    @staticmethod
    @command(Abilities.outlet)
    def cancel_override():
        """
        Cancel the manual watering.
        """

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
        return convert(List[Location], data.get("locations", []))
    
    def retrieve_devices(self, location):
        _LOGGER.info("Retrieving devices for location id %s", location.id)
        response = self.requestSession.get("devices", params={
            "locationId": location.id
        })
        data = response.json()
        _LOGGER.debug("Got devices %s", data)
        return convert(List[Device], data.get("devices", []))
    
    def send_command(self, location: Location, device: Device, command: Command):
        """
        Sends a command for the given device at the location.
        This methods does not check if the device actually implements the ability necessary for the command.
        """
        _LOGGER.info("Sending command for location id %s, device id %s: %s", location.id, device.id, command)
        url = "devices/{device.id}/abilities/{command.ability}/command".format(device=device, command=command)
        json = {
            "name": command.name
        }
        if command.parameters:
            json["parameters"] = command.parameters
        self.requestSession.post(url, params={
            "locationId": location.id
        }, json=json)
