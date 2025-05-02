
package org.openhab.binding.miio.internal.robot;

import org.eclipse.jdt.annotation.NonNullByDefault;
import org.eclipse.smarthome.core.thing.type.ChannelTypeUID;


@NonNullByDefault
public enum RobotCababilities {

    WATERBOX_STATUS("water_box_status", "status#water_box_status", "miio:water_box_status"),
    LOCKSTATUS("lock_status", "status#lock_status", "miio:lock_status"),
    WATERBOX_MODE("water_box_mode", "status#water_box_mode", "miio:water_box_mode"),
    WATERBOX_CARRIAGE("water_box_carriage_status", "status#water_box_carriage_status",
            "miio:water_box_carriage_status"),
    MOP_FORBIDDEN("mop_forbidden_enable", "status#mop_forbidden_enable", "miio:mop_forbidden_enable"),
    SEGMENT_CLEAN("", "actions#segment", "miio:segment");

    private final String statusFieldName;
    private final String channel;
    private final String channelType;

    RobotCababilities(String statusKey, String channel, String channelType) {
        this.statusFieldName = statusKey;
        this.channel = channel;
        this.channelType = channelType;
    }

    public String getStatusFieldName() {
        return statusFieldName;
    }

    public String getChannel() {
        return channel;
    }

    public ChannelTypeUID getChannelType() {
        return new ChannelTypeUID(channelType);
    }

    @Override
    public String toString() {
        return String.format("Capability %s: status field name: '%s', channel: '%s', channeltype: '%s'.", this.name(),
                statusFieldName, channel, channelType);
    }
}