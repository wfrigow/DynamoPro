"""
Authentification pour l'API de subventions
----------------------------------------
Module d'authentification spécifique à l'API de subventions
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

import sys
import os
# Ajouter le répertoire parent au sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.auth import (
    Token, UserInDB, verify_password, get_password_hash,
    create_access_token, get_current_user, get_current_active_user
)
from .config import settings
from .database.database import get_db
from .database import crud

# Configuration du schéma OAuth2 spécifique à l'API de subventions
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/token"
)

# Fonctions d'authentification utilisant la base de données réelle


def get_user(db: Session, email: str) -> Optional[UserInDB]:
    """Récupère un utilisateur par son email"""
    db_user = crud.get_user_by_email(db, email)
    if db_user:
        return UserInDB(
            id=db_user.id,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser
        )
    return None


def get_user_by_id(db: Session, user_id: str) -> Optional[UserInDB]:
    """Récupère un utilisateur par son ID"""
    db_user = crud.get_user(db, user_id)
    if db_user:
        return UserInDB(
            id=db_user.id,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser
        )
    return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[UserInDB]:
    """Authentifie un utilisateur avec son email et son mot de passe"""
    user = get_user(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def login_for_access_token(form_data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Génère un token d'accès pour un utilisateur authentifié"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_subsidy_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
    """Récupère l'utilisateur courant pour l'API de subventions"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Utiliser la fonction commune pour décoder le token et obtenir l'ID de l'utilisateur
    user = await get_current_user(token)
    
    # Récupérer l'utilisateur complet depuis notre base de données
    db_user = get_user_by_id(db, user.id)
    
    if db_user is None:
        raise credentials_exception
    
    return db_user


async def get_current_active_subsidy_user(
    current_user: UserInDB = Depends(get_current_subsidy_user)
) -> UserInDB:
    """Vérifie que l'utilisateur courant est actif"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilisateur inactif"
        )
    return current_user


async def get_current_subsidy_admin(
    current_user: UserInDB = Depends(get_current_active_subsidy_user)
) -> UserInDB:
    """Vérifie que l'utilisateur courant est un administrateur"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    return current_user
