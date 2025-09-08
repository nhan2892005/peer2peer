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
async def test_file_complete_success():
    store = InMemoryStore()
    app = create_app(store)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        announce_body = {
            "ip": "127.0.0.1",
            "port": 7001,
            "files": [
                {"name": "hello.txt", "size": 12, "sha256": "abcd1234"}
            ],
        }
        res = await ac.post("/api/v1/announce", json=announce_body)
        assert res.status_code == 200

        complete_body = {
            "peer_ip": "127.0.0.1",
            "port": 7001,
            "name": "hello.txt",
        }
        res = await ac.post("/api/v1/complete", json=complete_body)
        assert res.status_code == 200
        assert res.json() == {"ok": True}

    file_index = next(i for i, f in enumerate(store.files) if f.sha256 == "abcd1234")
    peer_index = next(i for i, p in enumerate(store.peers) if p.ip == "127.0.0.1" and p.port == 7001)
    assert (file_index, peer_index) in store.file_peers
