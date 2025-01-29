
package org.openhab.binding.appletv.internal;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class AppleTVLogger {

   
    private Logger logger;
    private static final String binding = "Apple-TV";
    private final String prefix;

    public AppleTVLogger(Class<?> clazz, String module) {
        logger = LoggerFactory.getLogger(clazz);
        prefix = "Apple-TV." + module + ": ";
    }

    public void error(String message, Object... a) {
        logger.error(prefix + message, a);
    }

    public void info(String message, Object... a) {
        logger.info(prefix + message, a);
    }

    public void debug(String message, Object... a) {
        logger.debug(prefix + message, a);
    }

    public void trace(String message, Object... a) {
        logger.trace(prefix + message, a);
    }
}
