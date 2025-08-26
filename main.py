import uvicorn
from fastapi import FastAPI
from fastapi_cloud_cli.commands.login import login

from src.api.v1.auth import login_router
from src.api.v1.test import test_router

app = FastAPI()



app.include_router(login_router)
app.include_router(test_router)



if __name__ == '__main__':
    uvicorn.run('main:app', reload=True, port=8002)