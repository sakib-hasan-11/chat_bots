from fastapi import FastAPI
from routers.chat import router as chat_router

app = FastAPI(title='chatbot api')

# this help to add more routes in one api.
app.include_router(chat_router)