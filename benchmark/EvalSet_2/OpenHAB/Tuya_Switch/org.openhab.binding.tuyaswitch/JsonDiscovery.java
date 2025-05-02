
package org.openhab.binding.tuya.internal.discovery;


public class JsonDiscovery {

    private String gwId;
    private Integer active;
    private Integer ability;
    private Boolean encrypt;
    private String productKey;
    private String version;
    private String ip;

    public JsonDiscovery() {
    }

    public JsonDiscovery(String gwId, String version, String ip) {
        this.gwId = gwId;
        this.version = version;
        this.ip = ip;
        encrypt = true;
    }

    public String getGwId() {
        return gwId;
    }

    public Integer getActive() {
        return active;
    }

    public Integer getAbility() {
        return ability;
    }

    public Boolean isEncrypt() {
        return encrypt;
    }

    public String getProductKey() {
        return productKey;
    }

    public String getVersion() {
        return version;
    }

    public String getIp() {
        return ip;
    }
}