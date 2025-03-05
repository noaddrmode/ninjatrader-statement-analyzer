from fastapi import FastAPI
from routes.trades import router as TradesRouter

app = FastAPI()
app.include_router(TradesRouter.router)


@app.get("/")
def index():
    return "OK"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
