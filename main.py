from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/")
async def handle_request(request: Request):
    pyload = await request.json()
    intent = pyload['queryResult']['intent']['displayName']
    parameters = pyload['queryResult']['parameters']
    output_context = ['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_context[0]['name'])

    intent_handler_dict = {
        "order.add -context: ongoing-order": add_to_order,
        "track.order - context: ongoing-order": track_order
    }
    return intent_handler_dict[intent](parameters, session_id)





def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]
    inprogress_orders = {}

    if len(food_items) != len(quantities):
        fulfillment_text = f"No order found with order id: {food_items}"
    else:
        new_food_dict = dict(zip(food_items, quantities))
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict
        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f'{order_str} Do you need anything else?'
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