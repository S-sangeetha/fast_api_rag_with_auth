from fastapi import APIRouter , Depends
from src.service.search import chat_service
from src.dependencies import get_current_user
from fastapi import APIRouter, WebSocket, WebSocketDisconnect


# http
# router = APIRouter(
#     prefix="/rag",
#     tags=["Search"],
#     dependencies=[Depends(get_current_user)]

# )

# @router.post("/chat")
# async def chat(question: str):

#     return await chat_service.generate_rag_answer(question)

# websocket
router = APIRouter()

@router.websocket("/rag/ws")
async def chat_websocket(websocket : WebSocket):
    await websocket.accept()
    try:
        while True:
            question = await websocket.receive_text()
            print(question)
            result = await chat_service.generate_rag_answer(question)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        print("clinet disconnected")