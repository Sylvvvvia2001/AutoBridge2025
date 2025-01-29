
package org.openhab.binding.tuya.internal.discovery;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.openhab.binding.tuya.internal.net.TuyaClientService;
import org.openhab.core.config.discovery.AbstractDiscoveryService;
import org.openhab.core.config.discovery.DiscoveryService;
import org.openhab.core.thing.ThingTypeUID;
import org.osgi.service.component.annotations.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


@Component(service = DiscoveryService.class)
public class TuyaDiscoveryService extends AbstractDiscoveryService {

    private static Set<ThingTypeUID> supportedThingsTypes;
    private Logger logger = LoggerFactory.getLogger(TuyaDiscoveryService.class);

    public static Set<ThingTypeUID> getSupportedTypes() {
        if (supportedThingsTypes == null) {
            supportedThingsTypes = new HashSet<>();
        }
        return supportedThingsTypes;
    }

    public TuyaDiscoveryService() {
        super(getSupportedTypes(), 5, true);
    }

    public void activate() {
        logger.debug("Starting Tuya discovery...");
        // removeOlderResults(System.currentTimeMillis(), getSupportedTypes());
        startBackgroundDiscovery();
    }

    @Override
    public void deactivate() {
        logger.debug("Stopping Tuya discovery...");
        stopBackgroundDiscovery();
        stopScan();
    }

    @Override
    protected void startBackgroundDiscovery() {
        DeviceRepository.getInstance().start(scheduler);
        try {
            TuyaClientService.getInstance().start();
        } catch (IOException e) {
        }
    }

    @Override
    protected void stopBackgroundDiscovery() {
        DeviceRepository.getInstance().stop();
        TuyaClientService.getInstance().stop();
    }

    @Override
    protected void startScan() {
        logger.debug("Starting device search...");
    }

    @Override
    protected synchronized void stopScan() {
        removeOlderResults(getTimestampOfLastScan());
        super.stopScan();
    }
}