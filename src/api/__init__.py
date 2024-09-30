from fastapi import APIRouter

from .auth import router as auth_routers
from .task import router as task_routers

router = APIRouter(
    prefix='/api'
)
router.include_router(auth_routers)
router.include_router(task_routers)
