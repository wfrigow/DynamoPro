release: alembic -c backend/alembic.ini upgrade head
web: uvicorn backend.text_audit_api:app --host 0.0.0.0 --port $PORT
