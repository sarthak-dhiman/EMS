from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import ALGORITHM, SECRET_KEY
from app.services.user import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        # include message to aid debugging (avoid printing token itself)
        raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")
    
    user = get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
