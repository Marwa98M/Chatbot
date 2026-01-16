from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse

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
        fulfillment_text = f"Received order {intent} in the backend"
        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })
    return JSONResponse(content={
        "fulfillmentText": "Not Recieved in the backend"
    })
