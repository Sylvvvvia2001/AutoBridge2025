
package org.openhab.binding.appletv.internal;

import static org.openhab.binding.appletv.internal.AppleTVBindingConstants.UPDATE_STATUS_INTERVAL;

import org.eclipse.jdt.annotation.NonNull;


public class AppleTVBindingConfiguration {
    public String remoteName;
    public Integer updateInterval = UPDATE_STATUS_INTERVAL;
    public String libPath = "";

    public void update(@NonNull AppleTVBindingConfiguration newConfiguration) {
        this.remoteName = newConfiguration.remoteName;
        this.libPath = newConfiguration.libPath;
        this.updateInterval = newConfiguration.updateInterval;
    }
}
