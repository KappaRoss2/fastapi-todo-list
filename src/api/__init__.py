__all__ = (
    'all_routers',
)

from .auth import router as auth_routers


all_routers = (auth_routers, )
