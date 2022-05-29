from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/is-healthy",
    description="web app health checking")
async def health_check():
    return "🆗"
