import os

from fastapi import APIRouter

router = APIRouter(prefix="/hostname", tags=["hostname"])


@router.get("/", response_description="Имя хоста")
def get_hostname() -> str:
    """
    Позволяет узнать какое имя хоста у контейнера в котором работает сервер.
    Нужно для проверки, что запросы попадают в разные контейнеры при
    развертывании в Kubernetes
    """
    return os.uname()[1]
