from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .models import Base, init_db
from .config import DevelopmentConfig
from app.routes.auth import router as auth_router

# Load environment variables
load_dotenv()

# Initialize database
database_url = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
engine = init_db(database_url)  # Capture the returned engine

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the auth router
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

import os
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse

def drop_all_tables(uri=None):
    if uri is None:
        uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    conn_params = {
        'dbname': (result := urlparse(uri)).path.lstrip('/'),
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            # Get all tables in the public schema
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
            tables = cursor.fetchall()
            
            # Drop each table with CASCADE
            for table in tables:
                cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(sql.Identifier(table[0])))
            conn.commit()


# print("Starting database initialization...")
# try:
#     print("Attempting to drop all tables...")
#     drop_all_tables()
#     print("Successfully dropped all tables")
    
#     print("Creating new tables...")
#     Base.metadata.create_all(bind=engine)
#     print("Successfully created all tables")
# except Exception as e:
#     print(f"Error during database initialization: {str(e)}")
# print("Database initialization complete")