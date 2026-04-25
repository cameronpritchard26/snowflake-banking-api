## Snowflake Transactions API

Contains a FastAPI application that provides a simple interface for accessing transaction data from a Snowflake database.

## Notes
- How to run:
```
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

- How to test:
```
curl http://localhost:8000/transactions?aid=123456789
```

- How to view the API docs:
```
http://localhost:8000/docs
```
