from fastapi import FastAPI

app = FastAPI()

BOOKS = []

@app.get("/books")
async def read_all_books():
    return BOOKS