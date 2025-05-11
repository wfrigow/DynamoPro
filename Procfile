release: alembic -c backend/alembic.ini upgrade head
web: uvicorn backend.db_connection_test_api:app --host 0.0.0.0 --port $PORT
