from miio import Plug
import yaml

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

plug_ip = config['ip_address']
plug_token = config['token']

# Initialize the plug
plug = Plug(ip=plug_ip, token=plug_token)

# Example commands
plug.on()  # Turn the plug on
plug.off()  # Turn the plug off

# To check the status
status = plug.status()
print(f"Power: {status.power}")
print(f"Temperature: {status.temperature}°C")
