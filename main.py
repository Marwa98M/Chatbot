from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()
inprogress_orders = {}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_context = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_context[0]['name'])

    intent_handler_dict = {
        "order.add -context: ongoing-order": add_to_order,
        "track.order - context: ongoing-order": track_order,
        # "order.complete - context: ongoing-order": completed_order,
        # "order.remove - context: ongoing-order": remove_order
    }
    return intent_handler_dict[intent](parameters, session_id)

# def completed_order(parameters: dict, session_id: str):
#     food_items = parameters["food-item"]
#     quantities = parameters["number"]
#     if session_id not in inprogress_orders:
#         fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place new order"
#     else:
#         order = inprogress_orders[session_id]
#         db_helper.save_to_db(order)


# def save_to_db(order: dict):
#     for



#
# def add_to_order(parameters: dict, session_id: str):
#     food_items = parameters["food-item"]
#     quantities = parameters["number"]
#     order_id = int(parameters['order_id'])
#
#     db_helper.add_items(order_id, food_items, quantities)
#

def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    # user typed sth like i want 2 pizza and milk
    # it should be i want 2 pizza and one milk - one quantity for each
    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        # new_food_dict --> what user wants to add
        # [2, 3], ["apple", "tomatoes"] --> {apple: 2, tomatoes: 3}
        new_food_dict = dict(zip(food_items, quantities))

        # if a user wants to add more food items to the existing order
        # step 1: get current food items of the session id
        # step 2: add the new food items to the inprogress_orders dict
        if session_id in inprogress_orders:
            inprogress_orders[session_id].update(new_food_dict)
        else:
            # if a user wants to add more food items to an empty order
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"{order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })



def track_order(parameters: dict, session_id: str):
    if 'order_id' not in parameters:
        return JSONResponse(content={
            "fulfillmentText": "Please provide an order ID."
        })
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })