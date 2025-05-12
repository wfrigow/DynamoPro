from setuptools import setup, find_packages

setup(
    name="dynamopro",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "alembic",
        "pydantic",
    ],
)
