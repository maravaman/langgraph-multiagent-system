# light_main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"msg": "Server is up"}
