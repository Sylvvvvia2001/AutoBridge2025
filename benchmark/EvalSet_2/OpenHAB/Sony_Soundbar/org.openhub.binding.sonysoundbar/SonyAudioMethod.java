
package org.openhab.binding.sonyaudio.internal.protocol;

import java.util.List;


public abstract class SonyAudioMethod {
    protected int id = 1;
    protected String method;
    protected String version;

    public SonyAudioMethod(String method, String version) {
        this.method = method;
        this.version = version;
    }
}


class GetPowerStatus extends SonyAudioMethod {
    public String[] params = new String[] {};

    public GetPowerStatus() {
        super("getPowerStatus", "1.1");
    }
}


class GetCurrentExternalTerminalsStatus extends SonyAudioMethod {
    public String[] params = new String[] {};

    public GetCurrentExternalTerminalsStatus() {
        super("getCurrentExternalTerminalsStatus", "1.0");
    }
}


class SetPowerStatus extends SonyAudioMethod {
    public Param[] params;

    class Param {
        public String status;

        Param(boolean power) {
            status = power ? "active" : "off";
        }
    }

    SetPowerStatus(boolean power) {
        super("setPowerStatus", "1.1");
        Param param = new Param(power);
        params = new Param[] { param };
    }
}


class SetActiveTerminal extends SonyAudioMethod {
    public Param[] params;

    class Param {
        public String active;
        public String uri;

        Param(boolean power, int zone) {
            active = power ? "active" : "inactive";
            if (zone > 0) {
                uri = "extOutput:zone?zone=" + Integer.toString(zone);
            }
        }
    }

    SetActiveTerminal(boolean power, int zone) {
        super("setActiveTerminal", "1.0");
        Param param = new Param(power, zone);
        params = new Param[] { param };
    }
}


class GetPlayingContentInfo extends SonyAudioMethod {
    public Param[] params;

    class Param {
        String output = "";

        Param() {
        }

        Param(int zone) {
            if (zone > 0) {
                output = "extOutput:zone?zone=" + Integer.toString(zone);
            }
        }
    }

    GetPlayingContentInfo() {
        super("getPlayingContentInfo", "1.2");
        Param param = new Param();
        params = new Param[] { param };
    }

    GetPlayingContentInfo(int zone) {
        super("getPlayingContentInfo", "1.2");
        Param param = new Param(zone);
        params = new Param[] { param };
    }
}

class SetPlayContent extends SonyAudioMethod {
    public Param[] params;

    class Param {
        String output = "";
        String uri;

        Param(String input) {
            uri = input;
        }

        Param(String input, int zone) {
            uri = input;
            if (zone > 0) {
                output = "extOutput:zone?zone=" + Integer.toString(zone);
            }
        }
    }

    SetPlayContent(String input) {
        super("setPlayContent", "1.2");
        params = new Param[] { new Param(input) };
    }

    SetPlayContent(String input, int zone) {
        super("setPlayContent", "1.2");
        params = new Param[] { new Param(input, zone) };
    }
}


class GetVolumeInformation extends SonyAudioMethod {
    public Param[] params;

    class Param {
        String output = "";

        Param() {
        }

        Param(int zone) {
            if (zone > 0) {
                output = "extOutput:zone?zone=" + Integer.toString(zone);
            }
        }
    }

    GetVolumeInformation() {
        this(0);
    }

    GetVolumeInformation(int zone) {
        super("getVolumeInformation", "1.1");
        params = new Param[] { new Param(zone) };
    }
}


class SetAudioVolume extends SonyAudioMethod {
    public Param[] params;

    class Param {
        String output = "";
        String volume;

        Param(long new_volume) {
            volume = Long.toString(new_volume);
        }

        Param(String volume_change) {
            volume = volume_change;
        }

        Param(long new_volume, int zone) {
            volume = Long.toString(new_volume);
            if (zone > 0) {
                output = "extOutput:zone?zone=" + Integer.toString(zone);
            }
        }

        Param(String volume_change, int zone) {
            volume = volume_change;
            if (zone > 0) {
                output = "extOutput:zone?zone=" + Integer.toString(zone);
            }
        }
    }

    SetAudioVolume(int volume, int min, int max) {
        super("setAudioVolume", "1.1");
        long scaled_volume = scaleVolume(volume, min, max);
        params = new Param[] { new Param(scaled_volume) };
    }

    SetAudioVolume(int zone, int volume, int min, int max) {
        super("setAudioVolume", "1.1");
        long scaled_volume = scaleVolume(volume, min, max);
        params = new Param[] { new Param(scaled_volume, zone) };
    }

    SetAudioVolume(String volume_change) {
        super("setAudioVolume", "1.1");
        params = new Param[] { new Param(volume_change) };
    }

    SetAudioVolume(int zone, String volume_change) {
        super("setAudioVolume", "1.1");
        params = new Param[] { new Param(volume_change, zone) };
    }

    long scaleVolume(int volume, int min, int max) {
        return Math.round(((max - min) * volume / 100.0) + min);
    }
}


class SetAudioMute extends SonyAudioMethod {
    public Param[] params;

    class Param {
        String output = "";
        String mute;

        Param(boolean mute) {
            this.mute = mute ? "on" : "off";
        }

        Param(boolean mute, int zone) {
            this.mute = mute ? "on" : "off";
            if (zone > 0) {
                output = "extOutput:zone?zone=" + Integer.toString(zone);
            }
        }
    }

    SetAudioMute(boolean mute) {
        super("setAudioMute", "1.1");
        params = new Param[] { new Param(mute) };
    }

    SetAudioMute(boolean mute, int zone) {
        super("setAudioMute", "1.1");
        params = new Param[] { new Param(mute, zone) };
    }
}


class GetSoundSettings extends SonyAudioMethod {
    public Param[] params;

    class Param {
        String target;

        Param(String target) {
            this.target = target;
        }
    }

    GetSoundSettings() {
        super("getSoundSettings", "1.1");
        params = new Param[] { new Param("") };
    }

    GetSoundSettings(String target) {
        super("getSoundSettings", "1.1");
        params = new Param[] { new Param(target) };
    }
}


class SetSoundSettings extends SonyAudioMethod {
    public Param[] params;

    class Settings {
        String value;
        String target;

        Settings(String target, String value) {
            this.target = target;
            this.value = value;
        }
    }

    class Param {

        Settings[] settings;

        Param(Settings[] settings) {
            this.settings = settings;
        }
    }

    SetSoundSettings() {
        super("setSoundSettings", "1.1");
    }

    SetSoundSettings(String target, String value) {
        super("setSoundSettings", "1.1");
        Settings[] settings = { new Settings(target, value) };
        params = new Param[] { new Param(settings) };
    }
}


class SetSoundField extends SetSoundSettings {
    SetSoundField(String soundField) {
        super("soundField", soundField);
    }
}


class SetPureDirect extends SetSoundSettings {
    SetPureDirect(boolean pureDirect) {
        super("pureDirect", pureDirect ? "on" : "off");
    }
}


class SetClearAudio extends SetSoundSettings {
    SetClearAudio(boolean clearAudio) {
        super("clearAudio", clearAudio ? "on" : "off");
    }
}

class SwitchNotifications extends SonyAudioMethod {
    public Param[] params;

    class Notification {
        String name;
        String version;

        @Override
        public String toString() {
            return "Notification{name='" + name + "' version='" + version + "'}";
        }
    }

    class Param {
        List<Notification> enabled;
        List<Notification> disabled;

        Param(List<Notification> enabled, List<Notification> disabled) {
            this.enabled = enabled;
            this.disabled = disabled;
        }
    }

    SwitchNotifications(List<Notification> enabled, List<Notification> disabled) {
        super("switchNotifications", "1.0");
        params = new Param[] { new Param(!enabled.isEmpty() ? enabled : null, !disabled.isEmpty() ? disabled : null) };
    }
}


class SeekBroadcastStation extends SonyAudioMethod {
    public Param[] params;

    class Param {
        String tuning = "auto";
        String direction;

        Param(boolean forward) {
            this.direction = forward ? "fwd" : "bwd";
        }
    }

    SeekBroadcastStation(boolean forward) {
        super("seekBroadcastStation", "1.0");
        params = new Param[] { new Param(forward) };
    }
}