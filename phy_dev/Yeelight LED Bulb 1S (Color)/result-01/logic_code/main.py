from yeelight import discover_bulbs, Bulb

def discover_and_control():
    bulbs = discover_bulbs()
    if bulbs:
        bulb_ip = bulbs[0]['ip']
        bulb = Bulb(bulb_ip)
        # Example controls
        bulb.turn_on()
        bulb.set_rgb(255, 0, 0)  # Set to red color
        print("Bulb found and controlled. IP:", bulb_ip)
    else:
        print("No bulbs found. Make sure your bulb is connected and LAN Control is enabled.")

if __name__ == "__main__":
    discover_and_control()
