from fastapi import FastAPI, HTTPException, Query
import pyodbc
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For security, you can specify ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def home():
    return {"message": "FastAPI Server Running with CORS enabled!"}

# Database configuration
DB_CONFIG = {
    "DRIVER": "{SQL Server}",
    "SERVER": "26.67.197.81",
    "DATABASE": "Accounting",
    "UID": "sa",
    "PWD": "123456",
}

def get_db_connection():
    """Create a database connection"""
    try:
        return pyodbc.connect(
            f"DRIVER={DB_CONFIG['DRIVER']};"
            f"SERVER={DB_CONFIG['SERVER']};"
            f"DATABASE={DB_CONFIG['DATABASE']};"
            f"UID={DB_CONFIG['UID']};"
            f"PWD={DB_CONFIG['PWD']};"
        )
    except pyodbc.Error as ex:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {ex}")

@app.get("/users/")
def get_users(cardid: str = Query(..., description="Card ID of the student")):
    """Fetch student data from the database"""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT UniversityId, CardId, StudentName, Money FROM Students WHERE CardId = ?", (cardid,))
        result = cursor.fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="Student not found")

        columns = [column[0] for column in cursor.description]
        student_data = [dict(zip(columns, row)) for row in result]

        return {"Student": student_data}

    except pyodbc.Error as ex:
        raise HTTPException(status_code=500, detail=f"Query failed: {ex}")

    finally:
        cursor.close()
        connection.close()
