from fastapi import FastAPI

app = FastAPI(title="FastCTX API")


@app.post("/query")
async def query_database():
    return {"Message:", "Hello, world"}
    pass
