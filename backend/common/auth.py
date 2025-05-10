"""
Gestion de l'authentification et des autorisations
-------------------------------------------------
Module partagé pour la gestion de l'authentification et des autorisations
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, UUID4

from .config import settings


# Modèles pour l'authentification
class Token(BaseModel):
    """Modèle de token d'authentification"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Données extraites du token"""
    sub: Optional[str] = None
    scopes: Optional[list[str]] = None


class UserInDB(BaseModel):
    """Utilisateur stocké en base de données"""
    id: UUID4
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False


# Configuration du contexte de hachage pour les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration du schéma OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe correspond à sa version hachée"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Génère un hash pour un mot de passe"""
    return pwd_context.hash(password)


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT d'accès"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm="HS256"
    )
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Récupère l'utilisateur courant à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(sub=user_id)
    except JWTError:
        raise credentials_exception
        
    # À implémenter: récupération de l'utilisateur depuis la base de données
    # user = get_user_by_id(token_data.sub)
    
    # Stub pour le développement
    user = UserInDB(
        id=token_data.sub,
        email="user@example.com",
        hashed_password="hashed_password"
    )
    
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Vérifie que l'utilisateur courant est actif"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilisateur inactif"
        )
    return current_user


async def get_current_superuser(
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """Vérifie que l'utilisateur courant est un super utilisateur"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    return current_user
