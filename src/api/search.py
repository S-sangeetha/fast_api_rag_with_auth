from fastapi import APIRouter , Depends
from src.service.search import chat_service
from src.dependencies import get_current_user

router = APIRouter(
    prefix="/rag",
    tags=["Search"],
    dependencies=[Depends(get_current_user)]

)

@router.post("/chat")
async def chat(question: str):

    return await chat_service.generate_rag_answer(question)