import os
from fastapi import FastAPI
from app.routes import nytimes
from dotenv import load_dotenv

# load .env 
load_dotenv()

app = FastAPI(title="NYTimes Article Microservice")

# register endpoint
app.include_router(nytimes.router, prefix="/nytimes")
