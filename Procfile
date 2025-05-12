release: alembic -c backend/alembic.ini upgrade head
web: uvicorn backend.standalone_api:app --host 0.0.0.0 --port $PORT
