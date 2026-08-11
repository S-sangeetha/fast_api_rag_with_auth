import os
import dotenv

dotenv.load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL" ,"")
DATABASE_NAME = os.getenv("DATABASE_NAME","")
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
)