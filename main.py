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
        "order.complete - context: ongoing-order": complete_order,
        "order.remove - context: ongoing-order": remove_from_order,
        "new.order": new_order
    }

    return intent_handler_dict[intent](parameters, session_id)


def new_order(parameters: dict, session_id: str):
    inprogress_orders.pop(session_id, None)



def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })

    food_items = parameters["food-item"]
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    # Check if items are removed and display them
    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'
    # Check if items are not ordered by the user and display the current order items.
    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'
    # Display order items weather its empty or have some items.
    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = f"{session_id} I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)
        if order_id == -1:
            fulfillment_text = f"{order_id}Sorry, I couldn't process your order due to a backend error. " \
                               "Please place a new order again"
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. We have placed your order. " \
                           f"Here is your order id # {order_id}. " \
                           f"Your order total is {order_total} which you can pay at the time of delivery!"
        del inprogress_orders[session_id]
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def save_to_db(order: dict):
    # to add food-items
    # step 1: if list is empty new order = 1
    # step 2: if list is not empty new order = retrieve the max order id and add one
    next_order_id = db_helper.get_next_order_id()

    # Insert individual items along with quantity and total price in orders table
    for food_item, quantity in order.items(): # e.g. ['milk': 1, 'banana':2]
        rcode = db_helper.insert_order_item(food_item,quantity,next_order_id)

        if rcode == -1:
            return -1

    # Now insert order tracking status
    db_helper.insert_order_tracking(next_order_id, "in progress")

    return next_order_id


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