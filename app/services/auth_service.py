from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token, create_service_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def login(self, username: str, password: str):
        user = self.user_repository.get_user_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        token = create_access_token({"sub": user.username, "role": user.role})
        return {"access_token": token, "token_type": "bearer"}

    def generate_pipeline_token(self, service_name: str):
        token = create_service_token(service_name)
        return {"service_token": token, "service_name": service_name}
