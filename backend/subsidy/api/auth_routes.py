"""
Routes d'authentification pour l'API de subventions
-------------------------------------------------
Endpoints pour l'authentification des utilisateurs
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import (
    Token, login_for_access_token, get_current_active_subsidy_user,
    UserInDB
)
from ..database.database import get_db
from ..database import crud

# Création du routeur
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"description": "Non autorisé"}},
)


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Obtient un token d'accès JWT pour l'authentification.
    
    - **username**: Email de l'utilisateur
    - **password**: Mot de passe de l'utilisateur
    
    Retourne un token d'accès JWT qui doit être inclus dans l'en-tête Authorization
    de toutes les requêtes authentifiées sous la forme "Bearer {token}".
    """
    return await login_for_access_token(form_data, db)


@router.get("/me", response_model=dict)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_subsidy_user)):
    """
    Retourne les informations de l'utilisateur actuellement authentifié.
    
    Cette route nécessite un token d'authentification valide.
    """
    # Convertir l'utilisateur en dictionnaire et supprimer le mot de passe haché
    user_dict = current_user.dict()
    if "hashed_password" in user_dict:
        del user_dict["hashed_password"]
    
    return user_dict


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: dict, db: Session = Depends(get_db)):
    """
    Enregistre un nouvel utilisateur.
    
    - **email**: Email de l'utilisateur
    - **password**: Mot de passe de l'utilisateur
    - **first_name**: Prénom de l'utilisateur (optionnel)
    - **last_name**: Nom de famille de l'utilisateur (optionnel)
    
    Retourne les informations de l'utilisateur créé.
    """
    # Vérifier si l'email est déjà utilisé
    existing_user = crud.get_user_by_email(db, user_data["email"])
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà enregistré"
        )
    
    # Créer le nouvel utilisateur
    new_user = crud.create_user(
        db=db,
        email=user_data["email"],
        password=user_data["password"],
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name")
    )
    
    # Convertir l'utilisateur en dictionnaire et supprimer le mot de passe haché
    user_dict = {
        "id": new_user.id,
        "email": new_user.email,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "is_active": new_user.is_active,
        "is_superuser": new_user.is_superuser
    }
    
    return user_dict
