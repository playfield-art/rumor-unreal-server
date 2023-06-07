from fastapi import FastAPI
updateInterval = 1

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}