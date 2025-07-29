import uvicorn
from fastapi import FastAPI

from src.api.v1.test import test_router

app = FastAPI()


app.include_router(test_router)



if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, port=8001)