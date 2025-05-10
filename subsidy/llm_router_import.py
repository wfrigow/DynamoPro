# Inclusion du routeur LLM dans le backend subsidy
from fastapi import FastAPI
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))
from app.api.llm import router as llm_router

def include_llm_router(app: FastAPI):
    app.include_router(llm_router)
