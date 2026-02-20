import asyncio
from aiocoap import Context
from aiocoap.resource import Site
from resources.temperature import TemperatureResource
from resources.humidity import HumidityResource
from resources.switch import SwitchResource

async def main():
    root = Site()
    root.add_resource(('temperature',), TemperatureResource())
    root.add_resource(('humidity',), HumidityResource())
    root.add_resource(('switch',), SwitchResource())

    await Context.create_server_context(root, bind=('0.0.0.0', 5683))

    print("CoAP server running on coap://0.0.0.0:5683")
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())