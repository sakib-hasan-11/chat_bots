from fastapi import APIRouter  # organize all the routes
from schema.request import ChatRequest
from schema.responce import ChatResponse
from services.chat_services import generate_response
from services.redis_services import load_history
router = APIRouter(prefix="/chat", tags=["chat"])


# endpoint of the router . endpoint must have the output validator function
@router.post(
    "/message",  # endpoint name
    response_model=ChatResponse,  # ChatResponse will validate endpoint output
)





# endpoint function that will be called in the endpoint
async def chat(request: ChatRequest):# router output validator here .
    # ChatRequest validate the endpoint input. so in this input must need the user_id + message as given in the chatrequest.
    response = await generate_response(request.user_id, request.message)

    return ChatResponse(response=response)# validate router output





# endpoint the will bring histry chat from redis.
@router.get("/history/{user_id}")
async def get_history(user_id: str):
    return load_history(user_id=user_id)


    