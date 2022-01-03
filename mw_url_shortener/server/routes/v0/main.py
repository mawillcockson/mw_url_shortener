from fastapi import APIRouter

from .redirect import router as redirect_router
from .security import router as security_router
from .user import router as user_router

api_router = APIRouter()
api_router.include_router(user_router, prefix="/user")
api_router.include_router(redirect_router, prefix="/redirect")
api_router.include_router(security_router, prefix="/security")
