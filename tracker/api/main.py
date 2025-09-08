from fastapi import FastAPI
import uvicorn
from .store import InMemoryStore
from .services import TrackerService
from .api import init_router


def create_app():
    store = InMemoryStore()
    service = TrackerService(store)
    app = FastAPI(title="P2P Tracker", version="0.1.0")
    app.include_router(init_router(service))
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=9000, reload=True)