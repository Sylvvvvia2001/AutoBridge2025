"""
Various utilities for Dahua cameras
"""
import json
import re


def dahua_brightness_to_hass_brightness(bri_str: str) -> int:
    """
    Converts a dahua brightness (which is 0 to 100 inclusive) and converts it to what HASS
    expects, which is 0 to 255 inclusive
    """
    bri = 100
    if bri_str:
        bri = int(bri_str)

    current = bri / 100
    return int(current * 255)


def hass_brightness_to_dahua_brightness(hass_brightness: int) -> int:
    """
    Converts a HASS brightness (which is 0 to 255 inclusive) to a Dahua brightness (which is 0 to 100 inclusive)
    """
    if hass_brightness is None:
        hass_brightness = 100
    return int((hass_brightness / 255) * 100)


def parse_event(data: str) -> list[dict[str, any]]:

    event_blocks = re.split(r'--myboundary\n', data)

    events = []

    for event_block in event_blocks:
        # Skip the first 3 lines... the first line looks like: Content-Type: text/plain
        s = event_block.split("\n", 3)
        if len(s) < 3:
            continue
        event_block = s[3].strip()
        if not event_block.startswith("Code="):
            continue

        # At this point we'll have something that looks like this...
        # Code=VideoMotion;action=Start;index=0;data={
        #    "Id" : [ 0 ],
        #    "RegionName" : [ "Region1" ],
        #    "SmartMotionEnable" : true
        # }
        # And we want to put each key/value pair into a dictionary...
        event = dict()
        for key_value in event_block.split(';'):
            key, value = key_value.split('=')
            event[key] = value

        # data is a json string, convert it to real json and add it back to the output dic
        if "data" in event:
            try:
                data = json.loads(event["data"])
                event["data"] = data
            except Exception:  # pylint: disable=broad-except
                pass
        events.append(event)

    return events