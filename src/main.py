import debugpy

from fastapi import FastAPI

from api import all_routers

from config import app_settings


app = FastAPI(
    tile='TODO list'
)

for router in all_routers:
    app.include_router(router)

if app_settings.debug:
    debugpy.listen(('0.0.0.0', 5678))
    debugpy.wait_for_client()
