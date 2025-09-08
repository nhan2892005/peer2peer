from fastapi import APIRouter, Request
from .models import AnnounceIn, PeerOut, FileOut, FileCompleteIn
from .services import TrackerService

router = APIRouter(prefix="/api/v1")
service: TrackerService 


def init_router(_service: TrackerService):
    global service
    service = _service
    return router

@router.post("/announce")
async def announce(req: Request, body: AnnounceIn):
    print(body)
    service.announce( body.ip, body.port, body.files)
    return {"ok": True}

@router.post("/complete")
async def file_complete(body: FileCompleteIn):
    print(body)
    service.complete(body.peer_ip, body.port, body.name)
    return {"ok": True}

@router.get("/file/{filename}")
async def get_peers_for_file(filename: str):
    f, peers = service.get_file_peers(filename)
    if not f:
        return {"file": None, "peers": []}
    return {
        "file": FileOut(name=f.name, size=f.size, sha256=f.sha256),
        "peers": [PeerOut(ip=p.ip, port=p.port) for p in peers],
    }

@router.get("/files")
async def get_all_files():
    files = service.list_files()
    return [FileOut(name=f.name, size=f.size, sha256=f.sha256) for f in files]