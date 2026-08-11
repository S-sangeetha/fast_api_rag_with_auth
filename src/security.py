from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated ="auto"
)


class Security:
    def hash_password(self , password:str) ->str:
        return pwd_context.hash(password)


    def verify_password(self, plain_pasword : str , hashed_password:str) -> bool :
        return pwd_context.verify(
            plain_pasword,
            hashed_password
        )

security = Security()