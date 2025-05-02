"""Platform for Yeelight LED Bulb 1S (Color) light integration."""
import logging
import socket
import json
import colorsys
from typing import Any, Callable, Dict, List, Optional, Tuple

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.util.color import (
    color_temperature_kelvin_to_mired,
    color_temperature_mired_to_kelvin,
)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "yeelight_custom"

# Yeelight constants
YEELIGHT_PORT = 55443
YEELIGHT_TRANSITION_FAST = 30  # ms
YEELIGHT_TRANSITION_SMOOTH = 300  # ms
YEELIGHT_BULB_MIN_KELVIN = 1700
YEELIGHT_BULB_MAX_KELVIN = 6500

# Supported features
SUPPORT_YEELIGHT = (
    LightEntityFeature.BRIGHTNESS
    | LightEntityFeature.COLOR
    | LightEntityFeature.COLOR_TEMP
    | LightEntityFeature.EFFECT
    | LightEntityFeature.TRANSITION
)

# Effects
EFFECT_PULSE = "Pulse"
EFFECT_COLOR_FLOW = "Color Flow"
EFFECT_STROBE = "Strobe"
EFFECT_NAMES = [EFFECT_PULSE, EFFECT_COLOR_FLOW, EFFECT_STROBE]

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Yeelight light platform."""
    if discovery_info is None:
        return

    lights = []
    for host, device_config in hass.data[DOMAIN].items():
        try:
            light = YeelightLight(
                device_config["name"], 
                device_config["host"],
            )
            lights.append(light)
        except (socket.error, OSError) as ex:
            _LOGGER.error("Failed to connect to Yeelight at %s: %s", host, ex)

    add_entities(lights, True)


class YeelightLight(LightEntity):
    """Representation of a Yeelight light."""

    def __init__(self, name, host):
        """Initialize the light."""
        self._name = name
        self._host = host
        self._port = YEELIGHT_PORT
        self._id = 1
        self._brightness = None
        self._is_on = None
        self._rgb_color = None
        self._color_temp = None
        self._hs_color = None
        self._effect = None
        self._available = False
        self._color_modes = {ColorMode.COLOR_TEMP, ColorMode.HS}
        self._color_mode = ColorMode.COLOR_TEMP
        self._min_mireds = color_temperature_kelvin_to_mired(YEELIGHT_BULB_MAX_KELVIN)
        self._max_mireds = color_temperature_kelvin_to_mired(YEELIGHT_BULB_MIN_KELVIN)

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def hs_color(self):
        """Return the hs color value."""
        return self._hs_color

    @property
    def color_temp(self):
        """Return the color temperature."""
        return self._color_temp

    @property
    def min_mireds(self):
        """Return minimum supported color temperature."""
        return self._min_mireds

    @property
    def max_mireds(self):
        """Return maximum supported color temperature."""
        return self._max_mireds

    @property
    def color_mode(self):
        """Return the color mode of the light."""
        return self._color_mode

    @property
    def supported_color_modes(self):
        """Return the color modes supported by the light."""
        return self._color_modes

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_YEELIGHT

    @property
    def effect_list(self):
        """Return the list of supported effects."""
        return EFFECT_NAMES

    @property
    def effect(self):
        """Return the current effect."""
        return self._effect

    @property
    def available(self):
        """Return if light is available."""
        return self._available

    def turn_on(self, **kwargs):
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp = kwargs.get(ATTR_COLOR_TEMP)
        hs_color = kwargs.get(ATTR_HS_COLOR)
        rgb_color = kwargs.get(ATTR_RGB_COLOR)
        effect = kwargs.get(ATTR_EFFECT)

        # Send power on command
        self._send_command("set_power", ["on", "sudden", 0])
        
        # Handle brightness
        if brightness is not None:
            brightness_percent = int(brightness / 255 * 100)
            self._send_command("set_bright", [brightness_percent])
            self._brightness = brightness
        
        # Handle color temperature
        if color_temp is not None:
            temp_in_k = int(color_temperature_mired_to_kelvin(color_temp))
            temp_in_k = max(YEELIGHT_BULB_MIN_KELVIN, min(YEELIGHT_BULB_MAX_KELVIN, temp_in_k))
            self._send_command("set_ct_abx", [temp_in_k, "smooth", YEELIGHT_TRANSITION_SMOOTH])
            self._color_temp = color_temp
            self._color_mode = ColorMode.COLOR_TEMP
        
        # Handle color
        if hs_color is not None:
            hue, sat = hs_color
            self._send_command("set_hsv", [int(hue), int(sat * 100), "smooth", YEELIGHT_TRANSITION_SMOOTH])
            self._hs_color = hs_color
            self._color_mode = ColorMode.HS
        elif rgb_color is not None:
            r, g, b = rgb_color
            h, s, _ = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            self._send_command("set_hsv", [int(h*360), int(s*100), "smooth", YEELIGHT_TRANSITION_SMOOTH])
            self._hs_color = (h*360, s)
            self._color_mode = ColorMode.HS
        
        # Handle effects
        if effect is not None:
            if effect == EFFECT_PULSE:
                self._send_command("start_cf", [1, 0, "1000, 2, 4500, 100, 1000, 2, 4500, 1"])
            elif effect == EFFECT_COLOR_FLOW:
                flow = "4, 0, 1000, 2, 2700, 100, 500, 1, 255, 10, 500, 2, 5000, 100"
                self._send_command("start_cf", [0, 0, flow])
            elif effect == EFFECT_STROBE:
                flow = "6, 0, 500, 2, 5000, 100, 250, 2, 5000, 1, 250, 2, 5000, 100"
                self._send_command("start_cf", [0, 0, flow])
            self._effect = effect
        
        self._is_on = True

    def turn_off(self, **kwargs):
        """Turn the light off."""
        self._send_command("set_power", ["off", "sudden", 0])
        self._is_on = False

    def update(self):
        """Fetch new state data for this light."""
        try:
            response = self._send_command("get_prop", ["power", "bright", "ct", "hue", "sat", "rgb"])
            if response and "result" in response:
                result = response["result"]
                if len(result) >= 6:
                    self._is_on = result[0] == "on"
                    self._brightness = int(int(result[1]) * 255 / 100)
                    self._color_temp = color_temperature_kelvin_to_mired(int(result[2]))
                    hue = int(result[3])
                    sat = int(result[4]) / 100
                    self._hs_color = (hue, sat)
                    
                    # Determine color mode
                    if self._is_on:
                        if hue == 0 and sat == 0:
                            self._color_mode = ColorMode.COLOR_TEMP
                        else:
                            self._color_mode = ColorMode.HS
                
                self._available = True
        except (socket.error, ValueError, TypeError) as ex:
            self._available = False
            _LOGGER.error("Unable to update Yeelight: %s", ex)

    def _send_command(self, method, params=None):
        """Send command to the bulb."""
        if params is None:
            params = []
            
        command = {
            "id": self._id,
            "method": method,
            "params": params,
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self._host, self._port))
            
            msg = json.dumps(command) + "\r\n"
            sock.send(msg.encode())
            
            data = sock.recv(2048)
            sock.close()
            
            response = json.loads(data.decode().strip())
            self._id += 1
            return response
        except (socket.error, ValueError, TypeError) as ex:
            _LOGGER.error("Error communicating with Yeelight: %s", ex)
            self._available = False
            return None 