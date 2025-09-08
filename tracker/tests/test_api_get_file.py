import pytest
import httpx
from fastapi import FastAPI
from app.store import InMemoryStore
from app.services import TrackerService
from app.api import init_router


def create_app(store: InMemoryStore | None = None) -> FastAPI:
    if store is None:
        store = InMemoryStore()
    service = TrackerService(store)
    app = FastAPI(title="P2P Tracker Test")
    app.include_router(init_router(service))
    return app


@pytest.mark.asyncio
async def test_get_file_peers():
    store = InMemoryStore()
    app = create_app(store)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # announce file
        body = {
            "ip": "127.0.0.1",
            "port": 8001,
            "files": [
                {"name": "data.txt", "size": 50, "sha256": "hash123"}
            ],
        }
        res = await ac.post("/api/v1/announce", json=body)
        assert res.status_code == 200

        # gọi /file/data.txt
        res = await ac.get("/api/v1/file/data.txt")
        assert res.status_code == 200
        payload = res.json()

        assert payload["file"]["name"] == "data.txt"
        assert payload["file"]["sha256"] == "hash123"
        assert len(payload["peers"]) == 1
        assert payload["peers"][0]["ip"] == "127.0.0.1"
        assert payload["peers"][0]["port"] == 8001