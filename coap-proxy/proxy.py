import asyncio
import logging
from quart import Quart, jsonify, request
from quart_cors import cors
from aiocoap import Context, Message, GET, PUT

app = Quart(__name__)
app = cors(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coap-proxy")

coap_context = None

@app.before_serving
async def setup_coap():
    global coap_context
    coap_context = await Context.create_client_context()
    logger.info("CoAP Context initialized and ready")

async def coap_get_async(path, retries=3):
    delay = 1
    for attempt in range(retries):
        try:
            request_msg = Message(code=GET, uri=f'coap://coap-server:5683/{path}')
            response = await asyncio.wait_for(coap_context.request(request_msg).response, timeout=3)
            if response.code.is_successful():
                return response.payload.decode('utf-8'), 200
            return f"CoAP Error: {response.code}", 502
        except Exception as e:
            logger.error(f"Attempt {attempt+1} failed for {path}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
    return "Gateway Timeout", 504

@app.route("/temperature")
async def temperature():
    raw, status = await coap_get_async("temperature")
    if status != 200: return jsonify({"error": raw}), status
    return jsonify({"device": "sensor1", "unit": "C", "value": float(raw)})

@app.route("/humidity")
async def humidity():
    raw, status = await coap_get_async("humidity")
    if status != 200: return jsonify({"error": raw}), status
    return jsonify({"device": "sensor2", "unit": "%", "value": float(raw)})

@app.route("/switch", methods=["GET", "PUT"])
async def switch():
    if request.method == "PUT":
        if request.is_json:
            data = await request.get_json()
            payload = data.get("state", "").upper()
        else:
            payload = (await request.get_data(as_text=True)).strip().upper()

        logger.info(f"---> Received COMMAND from OpenHAB: {payload}")

        coap_request = Message(
            code=PUT, 
            payload=payload.encode('utf-8'), 
            uri='coap://coap-server:5683/switch'
        )
        
        try:
            response = await asyncio.wait_for(coap_context.request(coap_request).response, timeout=3)
            if response.code.is_successful():
                logger.info(f"<--- CoAP Server confirmed: {response.code}")
                return jsonify({"status": "Updated", "state": payload}), 200
            return jsonify({"error": f"CoAP Error: {response.code}"}), 502
        except Exception as e:
            logger.error(f"CoAP PUT failed: {e}")
            return jsonify({"error": "CoAP server unreachable"}), 504

    raw, status = await coap_get_async("switch")
    if status != 200:
        return jsonify({"error": raw}), status
    return jsonify({"device": "switch1", "state": raw})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)