"""
Module d'authentification commun
-------------------------------
Fonctions et classes d'authentification partagées
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuration de la sécurité
SECRET_KEY = "dynamopro-secret-key-for-development"  # À remplacer par une clé sécurisée en production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modèles de données pour l'authentification
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    is_active: bool = True

class UserInDB(User):
    hashed_password: str

# Utilitaires pour la gestion des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Vérifie si le mot de passe en clair correspond au hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Génère un hash pour un mot de passe en clair"""
    return pwd_context.hash(password)

# Gestion des tokens JWT
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """Crée un token JWT avec les données spécifiées"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fonctions de récupération d'utilisateur
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Récupère l'utilisateur actuel à partir du token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # Pour les besoins de test, on crée un utilisateur fictif
    # En production, il faudrait récupérer l'utilisateur depuis la base de données
    user = UserInDB(
        id="00000000-0000-0000-0000-000000000000",
        email=token_data.email,
        is_active=True,
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "password"
    )
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Vérifie que l'utilisateur actuel est actif"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user
