from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/")
async def handle_request(request: Request):
    pyload = await request.json()
    intent = pyload['queryResult']['intent']['displayName']
    parameters = pyload['queryResult']['parameters']
    #output_context = ['queryResult']['outputContexts']

    if intent == "track.order - context: ongoing-tracking":
        return track_order(parameters)
    intent_handler_dict = {
        "order.add - context: ongoing-order" : add_to_order,
        "track.order - context: ongoing-order" : track_order
    }
    return intent_handler_dict[intent](parameters)


def add_to_order(parameters: dict):
    food_items = parameters["food-item"]
    quantities = parameters["number"]
    if len(food_items) != len(quantities):
        fulfillment_text = f"No order found with order id: {food_items}"
    else:
        fulfillment_text = f"The order: {food_items} has: {quantities}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def track_order(parameters: dict):
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })