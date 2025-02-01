import datetime
import logging
import requests
import voluptuous as vol

from homeassistant.components.camera import Camera, PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

CONF_ID = 'id'
CONF_KEY = 'key'
CONF_SEC = 'sec'
CONF_MAOYAN = 'ismaoyan'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ID): cv.string,
    vol.Required(CONF_KEY): cv.string,
    vol.Required(CONF_SEC): cv.string,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_MAOYAN, default='notmaoyan'): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Ezviz C6c camera platform."""
    add_devices([EzvizCamera(hass, config)])

class EzvizCamera(Camera):
    """Representation of an Ezviz C6c Camera."""

    def __init__(self, hass, config):
        """Initialize the Ezviz C6c camera."""
        super().__init__()

        self._name = config.get(CONF_NAME)
        self._is_maoyan = config.get(CONF_MAOYAN) == 'maoyan'
        self.app_key = config.get(CONF_KEY)
        self.app_secret = config.get(CONF_SEC)
        self.device_serial = config.get(CONF_ID)
        self.access_token = ""
        self.expire_time = 0
        self._last_image = None
        self._next_snapshot_at = None
        self._time_between_snapshots = datetime.timedelta(seconds=30)

        # Initial token acquisition
        self.update_token()

    def update_token(self):
        """Update the access token."""
        response = requests.post('https://open.ys7.com/api/lapp/token/get', data={'appKey': self.app_key, 'appSecret': self.app_secret})
        token_result = response.json()
        if token_result['code'] == '200':
            self.access_token = token_result['data']['accessToken']
            self.expire_time = token_result['data']['expireTime']
            _LOGGER.info("Ezviz access token updated successfully.")
        else:
            _LOGGER.error("Failed to update Ezviz access token: %s", token_result)

    def check_token_expired(self):
        """Check if the token has expired."""
        return dt_util.utcnow().timestamp() * 1000 > (self.expire_time - 1000)

    def get_camera_image(self):
        """Retrieve the camera image."""
        if self.check_token_expired():
            self.update_token()

        url = 'https://open.ys7.com/api/lapp/device/capture' if not self._is_maoyan else 'https://open.ys7.com/api/lapp/alarm/device/list'
        data = {'accessToken': self.access_token, 'deviceSerial': self.device_serial}
        if not self._is_maoyan:
            data['channelNo'] = 1
            data['quality'] = 1

        response = requests.post(url, data=data)
        result = response.json()

        if result['code'] == '200':
            pic_url = result['data']['picUrl'] if not self._is_maoyan else result['data'][0]['alarmPicUrl']
            try:
                image_response = requests.get(pic_url)
                return image_response.content
            except requests.exceptions.RequestException as error:
                _LOGGER.error("Error retrieving camera image: %s", error)
                return None
        else:
            _LOGGER.error("Failed to retrieve camera image: %s", result)
            return None

    def camera_image(self):
        """Return a still image response from the camera."""
        now = dt_util.utcnow()
        if self._next_snapshot_at is None or now > self._next_snapshot_at:
            self._last_image = self.get_camera_image()
            self._next_snapshot_at = now + self._time_between_snapshots
        return self._last_image

    @property
    def name(self):
        """Return the name of the camera."""
        return self._name

    @property
    def should_poll(self):
        """Camera should poll periodically."""
        return True
