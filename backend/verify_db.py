import sqlalchemy
from sqlalchemy import create_engine, inspect, text
import os

# DATABASE_URL doit correspondre à ce qui se trouve dans votre .env pour le développement local
DATABASE_URL = "sqlite:///./test_local.db" # Suppose que test_local.db est dans le répertoire courant (backend/)

def verify_tables_in_db():
    db_file_path = "test_local.db"
    print(f"Tentative de connexion à : {DATABASE_URL}")
    print(f"Vérification de l'existence du fichier : {os.path.abspath(db_file_path)}")

    if not os.path.exists(db_file_path):
        print(f"ERREUR : Le fichier '{db_file_path}' n'a pas été trouvé dans le répertoire '{os.getcwd()}'.")
        print("Veuillez vous assurer que vous exécutez ce script depuis le répertoire 'backend' et que le fichier de base de données existe.")
        return

    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)

        print("\nTables dans la base de données :")
        tables = inspector.get_table_names()
        if not tables:
            print("  Aucune table trouvée.")
        for table_name in tables:
            print(f"  - {table_name}")

        if "audits" in tables:
            print("\nColonnes dans la table 'audits' :")
            columns = inspector.get_columns("audits")
            for column in columns:
                print(f"  - Nom : {column['name']}, Type : {column['type']}")
        else:
            print("\nLa table 'audits' n'a pas été trouvée.")

        if "alembic_version" in tables:
            print("\nVérification de la table alembic_version...")
            with engine.connect() as connection:
                result = connection.execute(text("SELECT version_num FROM alembic_version"))
                version_row = result.fetchone() # Utiliser fetchone() pour obtenir la ligne
                if version_row:
                    print(f"  Version actuelle d'Alembic : {version_row[0]}")
                else:
                    print("  La table Alembic version est vide ou version_num n'a pas été trouvée.")
        else:
            print("\nLa table 'alembic_version' n'a pas été trouvée.")

    except Exception as e:
        print(f"\nUne erreur est survenue : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_tables_in_db()
