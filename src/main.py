import debugpy
from fastapi import FastAPI

app = FastAPI(
    tile='TODO list'
)

debugpy.listen(('0.0.0.0', 5678))
debugpy.wait_for_client()
