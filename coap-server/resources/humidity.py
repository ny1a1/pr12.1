from aiocoap.resource import Resource
from aiocoap import Message, CONTENT

class HumidityResource(Resource):
    def __init__(self):
        super().__init__()
        self.value = 45.0

    async def render_get(self, request):
        payload = str(self.value).encode('utf-8')
        return Message(code=CONTENT, payload=payload)

    async def render_put(self, request):
        try:
            self.value = float(request.payload.decode('utf-8'))
            return Message(code=CONTENT, payload=b"Updated")
        except:
            return Message(code=CONTENT, payload=b"Invalid value")

    async def render_post(self, request):
        return await self.render_put(request)

    async def render_delete(self, request):
        self.value = None
        return Message(code=CONTENT, payload=b"Deleted")