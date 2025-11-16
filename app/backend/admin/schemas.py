import bcrypt
from pydantic import BaseModel, Field, model_validator
from app.backend.admin.models import AdminUser


class AdminLogin(BaseModel):
    username: str
    password: str = Field(..., max_length=128)
    
    @model_validator(mode='after')
    def check_credentials(self):
        user = AdminUser.active().filter_by(username=self.username).first()
        if not user:
            raise ValueError("Login credentials are incorrect.")

        try:
            credentials_match = bcrypt.checkpw(
                self.password.encode(),
                user.password.encode())
        except Exception as exc:
            raise exc

        if not credentials_match:
            raise ValueError("Login credentials are incorrect.")

        return self
