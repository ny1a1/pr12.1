from aiocoap.resource import Resource
from aiocoap import Message, CONTENT

class SwitchResource(Resource):
    def __init__(self):
        super().__init__()
        self.state = "OFF"

    async def render_get(self, request):
        return Message(code=CONTENT, payload=self.state.encode('utf-8'))

    async def render_put(self, request):
        new_state = request.payload.decode('utf-8').upper()
        if new_state in ["ON", "OFF"]:
            self.state = new_state
            return Message(code=CONTENT, payload=b"Updated")
        else:
            return Message(code=CONTENT, payload=b"Invalid state")

    async def render_post(self, request):
        return await self.render_put(request)

    async def render_delete(self, request):
        self.state = "OFF"
        return Message(code=CONTENT, payload=b"Reset to OFF")