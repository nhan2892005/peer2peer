import pytest
import httpx
from fastapi import FastAPI
from app.store import InMemoryStore
from app.services import TrackerService
from app.api import init_router
from app.models import File, Peer


def create_app(store: InMemoryStore | None = None) -> FastAPI:
    if store is None:
        store = InMemoryStore()
    service = TrackerService(store)
    app = FastAPI(title="P2P Tracker", version="0.1.0")
    app.include_router(init_router(service))
    return app


@pytest.mark.asyncio
async def test_announce_and_store():
    store = InMemoryStore()
    app = create_app(store)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        body = {
            "ip": "127.0.0.1",
            "port": 7001,
            "files": [
                {"name": "hello.txt", "size": 12, "sha256": "abcd1234"}
            ],
        }
        res = await ac.post("/api/v1/announce", json=body)
        assert res.status_code == 200
        assert res.json() == {"ok": True}

    # kiểm tra trực tiếp store
    assert store.files == [File(name='hello.txt', size=12, sha256='abcd1234')]
    assert store.peers == [Peer(ip="127.0.0.1", port=7001)]
    assert store.file_peers == [(0,0)]


@pytest.mark.asyncio
async def test_files_and_file_detail():
    store = InMemoryStore()
    app = create_app(store)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        body = {
            "ip": "127.0.0.2",
            "port": 7002,
            "files": [
                {"name": "data.bin", "size": 100, "sha256": "ffff9999"}
            ],
        }
        await ac.post("/api/v1/announce", json=body)

        # check /files
        res = await ac.get("/api/v1/files")
        assert res.status_code == 200
        files = res.json()
        assert files == [
            {"name": "data.bin", "size": 100, "sha256": "ffff9999"}
        ]

        # check /file/data.bin
        res = await ac.get("/api/v1/file/data.bin")
        assert res.status_code == 200
        payload = res.json()
        assert payload["file"] == {
            "name": "data.bin", "size": 100, "sha256": "ffff9999"
        }
        assert payload["peers"] == [
            {"ip": "127.0.0.2", "port": 7002}
        ]

    # kiểm tra trực tiếp store
    assert store.files == [File(name="data.bin", size=100, sha256="ffff9999")]
    assert store.peers == [Peer(ip="127.0.0.2", port=7002)]
    assert store.file_peers == [(0,0)]