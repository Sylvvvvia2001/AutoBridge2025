

package org.openhab.binding.ipcamera.internal;

import org.eclipse.jdt.annotation.NonNullByDefault;
import org.eclipse.jdt.annotation.Nullable;
import org.eclipse.smarthome.core.thing.Thing;
import org.eclipse.smarthome.core.thing.ThingTypeUID;
import org.eclipse.smarthome.core.thing.binding.BaseThingHandlerFactory;
import org.eclipse.smarthome.core.thing.binding.ThingHandler;
import org.eclipse.smarthome.core.thing.binding.ThingHandlerFactory;
import org.openhab.binding.ipcamera.handler.IpCameraHandler;
import org.osgi.service.component.annotations.Component;


@Component(service = ThingHandlerFactory.class, immediate = true, configurationPid = "binding.ipcamera")
@NonNullByDefault
public class IpCameraHandlerFactory extends BaseThingHandlerFactory {

    @Override
    public boolean supportsThingType(ThingTypeUID thingTypeUID) {
        return IpCameraHandler.SUPPORTED_THING_TYPES.contains(thingTypeUID);
    }

    @Override
    protected @Nullable ThingHandler createHandler(Thing thing) {
        ThingTypeUID thingTypeUID = thing.getThingTypeUID();

        if (IpCameraHandler.SUPPORTED_THING_TYPES.contains(thingTypeUID)) {
            return new IpCameraHandler(thing);
        }
        return null;
    }
}
