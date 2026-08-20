from fastapi import FastAPI
from src.api.user import router as user_router
from src.api.auth import router as auth_router
from src.api.document import router as doc_router
from src.api.search import router as search_router
app = FastAPI()
from src.database import Database
db = Database()

@app.on_event("startup")
async def startup():
   
    await db.create_indexes()  

@app.get("/")
def root():
    return {"message": "API is Running"}


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(doc_router)
app.include_router(search_router)