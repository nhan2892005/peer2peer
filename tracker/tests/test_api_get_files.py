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
async def test_get_all_files():
    store = InMemoryStore()
    app = create_app(store)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # announce 2 files
        body = {
            "ip": "127.0.0.1",
            "port": 9001,
            "files": [
                {"name": "file1.txt", "size": 10, "sha256": "aaa111"},
                {"name": "file2.bin", "size": 20, "sha256": "bbb222"},
            ],
        }
        res = await ac.post("/api/v1/announce", json=body)
        assert res.status_code == 200

        # gọi /files
        res = await ac.get("/api/v1/files")
        assert res.status_code == 200
        files = res.json()

        names = {f["name"] for f in files}
        hashes = {f["sha256"] for f in files}

        assert "file1.txt" in names
        assert "file2.bin" in names
        assert "aaa111" in hashes
        assert "bbb222" in hashes