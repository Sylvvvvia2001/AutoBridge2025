
package org.openhab.binding.miio.internal.robot;

import org.eclipse.jdt.annotation.NonNullByDefault;


@NonNullByDefault
public enum FanModeType {

    SILENT(38, "Silent"),
    STANDARD(60, "Standard"),
    TURBO(75, "Turbo"),
    POWER(77, "Power"),
    FULL(90, "Full"),
    MAX(100, "Max"),
    QUIET(101, "Quiet"),
    BALANCED(102, "Balanced"),
    TURBO2(103, "Turbo"),
    MAX2(104, "Max"),
    MOB(105, "Mob"),
    CUSTOM(-1, "Custom");

    private final int id;
    private final String description;

    FanModeType(int id, String description) {
        this.id = id;
        this.description = description;
    }

    public int getId() {
        return id;
    }

    public static FanModeType getType(int value) {
        for (FanModeType st : FanModeType.values()) {
            if (st.getId() == value) {
                return st;
            }
        }
        return CUSTOM;
    }

    public String getDescription() {
        return description;
    }

    @Override
    public String toString() {
        return "Status " + Integer.toString(id) + ": " + description;
    }
}