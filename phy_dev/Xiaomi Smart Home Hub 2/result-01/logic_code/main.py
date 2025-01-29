import aiohttp
import yaml
from pydantic import BaseModel

# Load configuration
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

class Device(BaseModel):
    ip_address: str
    token: str
    model: str

async def list_devices(device: Device):
    url = f"http://{device.ip_address}/api/device/list"
    headers = {"Authorization": f"Bearer {device.token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            devices = await response.json()
            print(devices)

# Example usage
device = Device(**config)
# asyncio.run(list_devices(device))
