from miio import DeskLamp
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Device setup
lamp = DeskLamp(ip=config['device']['ip_address'], token=config['device']['token'])

# Example functions
def turn_on():
    lamp.on()

def turn_off():
    lamp.off()

def set_brightness(brightness):
    # Brightness: 0-100
    lamp.set_brightness(brightness)

def set_color_temperature(temperature):
    # Color temperature range: 2600K-5000K
    lamp.set_color_temperature(temperature)

if __name__ == "__main__":
    # Example usage
    turn_on()
    set_brightness(50)
    set_color_temperature(4000)
    turn_off()
