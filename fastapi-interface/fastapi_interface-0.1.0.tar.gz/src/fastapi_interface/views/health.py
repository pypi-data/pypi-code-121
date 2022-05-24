from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_description="Сервер работает")
def get_health() -> None:
    """Для проверки работоспособности сервера"""
    pass
