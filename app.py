import os
from typing import List

import jwt
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from jwt import PyJWTError
import snowflake.connector
from pydantic import BaseModel

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_ALGORITHM = "HS256"

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")

TRANSACTIONS_TABLE = os.getenv("TRANSACTIONS_TABLE", "TRANSACTIONS")

app = FastAPI(title="Snowflake Transactions API")


class Transaction(BaseModel):
    account_id: str
    transaction_date: str
    payee: str
    transaction_amount: float


def get_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            account=SNOWFLAKE_ACCOUNT,
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA,
            role=SNOWFLAKE_ROLE,
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snowflake connection error: {e}")


def validate_jwt(authorization: str = Header(...)):
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = parts[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT token")


@app.get("/transactions", response_model=List[Transaction])
def get_transactions(
    aid: str = Query(..., description="Account ID"),
    _claims: dict = Depends(validate_jwt),
):
    conn = get_snowflake_connection()
    try:
        sql = f"""
            SELECT
                account_id,
                transaction_date,
                payee,
                transaction_amount
            FROM {TRANSACTIONS_TABLE}
            WHERE account_id = %s
        """
        cur = conn.cursor()
        try:
            cur.execute(sql, (aid,))
            rows = cur.fetchall()
        finally:
            cur.close()
    finally:
        conn.close()

    return [
        Transaction(
            account_id=row[0],
            transaction_date=str(row[1]),
            payee=row[2],
            transaction_amount=float(row[3]),
        )
        for row in rows
    ]


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})