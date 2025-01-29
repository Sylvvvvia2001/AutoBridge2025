
package org.openhab.binding.sonyaudio.internal.protocol;

import java.net.URI;

import com.google.gson.JsonObject;


public interface SonyAudioClientSocketEventListener {
    void handleEvent(JsonObject json);

    void onConnectionClosed();

    void onConnectionOpened(URI resource);
}