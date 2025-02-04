
package org.openhab.binding.philipstv.internal;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.eclipse.jdt.annotation.NonNull;
import org.eclipse.jdt.annotation.NonNullByDefault;
import org.eclipse.jdt.annotation.Nullable;
import org.openhab.core.thing.Channel;
import org.openhab.core.thing.ChannelUID;
import org.openhab.core.thing.type.DynamicStateDescriptionProvider;
import org.openhab.core.types.StateDescription;
import org.openhab.core.types.StateDescriptionFragmentBuilder;
import org.openhab.core.types.StateOption;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;

@Component(service = { DynamicStateDescriptionProvider.class,
        PhilipsTvDynamicStateDescriptionProvider.class }, immediate = true)
@NonNullByDefault
public class PhilipsTvDynamicStateDescriptionProvider implements DynamicStateDescriptionProvider {
    private final Map<ChannelUID, List<@NonNull StateOption>> channelOptionsMap = new ConcurrentHashMap<>();

    // @SuppressWarnings("null")
    public void setStateOptions(ChannelUID channelUID, List<StateOption> options) {
        channelOptionsMap.put(channelUID, options);
    }

    @Override
    public @Nullable StateDescription getStateDescription(Channel channel, @Nullable StateDescription original,
            @Nullable Locale locale) {

        List<StateOption> options = channelOptionsMap.get(channel.getUID());

        if (options == null) {
            return null;
        }
        if (original != null) {
            return StateDescriptionFragmentBuilder.create(original).withOptions(options).build().toStateDescription();
        }

        return StateDescriptionFragmentBuilder.create().withOptions(options).build().toStateDescription();
    }

    @Deactivate
    public void deactivate() {
        channelOptionsMap.clear();
    }
}