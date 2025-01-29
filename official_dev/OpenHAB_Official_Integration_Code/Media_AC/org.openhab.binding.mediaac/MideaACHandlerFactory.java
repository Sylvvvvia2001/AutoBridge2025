
package org.openhab.binding.mideaac.internal;

import static org.openhab.binding.mideaac.internal.MideaACBindingConstants.SUPPORTED_THING_TYPES_UIDS;

import org.eclipse.jdt.annotation.NonNullByDefault;
import org.eclipse.jdt.annotation.Nullable;
import org.eclipse.jetty.client.HttpClient;
import org.openhab.binding.mideaac.internal.handler.MideaACHandler;
import org.openhab.core.i18n.UnitProvider;
import org.openhab.core.io.net.http.HttpClientFactory;
import org.openhab.core.net.NetworkAddressService;
import org.openhab.core.thing.Thing;
import org.openhab.core.thing.ThingTypeUID;
import org.openhab.core.thing.binding.BaseThingHandlerFactory;
import org.openhab.core.thing.binding.ThingHandler;
import org.openhab.core.thing.binding.ThingHandlerFactory;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


@NonNullByDefault
@Component(configurationPid = "binding.mideaac", service = ThingHandlerFactory.class)
public class MideaACHandlerFactory extends BaseThingHandlerFactory {

    // private static final Set<ThingTypeUID> SUPPORTED_THING_TYPES_UIDS = Set.of(THING_TYPE_SAMPLE);
    private final NetworkAddressService networkAddressService;
    private UnitProvider unitProvider;
    private final HttpClient httpClient;

    private final Logger logger = LoggerFactory.getLogger(MideaACHandlerFactory.class);

    @Override
    public boolean supportsThingType(ThingTypeUID thingTypeUID) {
        return SUPPORTED_THING_TYPES_UIDS.contains(thingTypeUID);
    }

    // @Override
    // protected @Nullable ThingHandler createHandler(Thing thing) {
    // ThingTypeUID thingTypeUID = thing.getThingTypeUID();
    //
    // if (THING_TYPE_MIDEAAC.equals(thingTypeUID)) {
    // return new MideaACHandler(thing);
    // }
    //
    // return null;
    // }

    @Activate
    public MideaACHandlerFactory(@Reference NetworkAddressService networkAddressService,
            @Reference UnitProvider unitProvider, @Reference HttpClientFactory httpClientFactory) {
        this.networkAddressService = networkAddressService;
        this.unitProvider = unitProvider;
        this.httpClient = httpClientFactory.getCommonHttpClient();

    }

    @Override
    protected @Nullable ThingHandler createHandler(Thing thing) {
        ThingTypeUID thingTypeUID = thing.getThingTypeUID();
        if (SUPPORTED_THING_TYPES_UIDS.contains(thingTypeUID)) {
            String primaryIpv4HostAddress = networkAddressService.getPrimaryIpv4HostAddress();
            if (primaryIpv4HostAddress != null) {
                logger.debug("Primary Address {}", primaryIpv4HostAddress);
                return new MideaACHandler(thing, primaryIpv4HostAddress, unitProvider, httpClient);
            }
        }
        return null;
    }
}