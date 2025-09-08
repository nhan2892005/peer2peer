from pydantic import BaseModel
from typing import List, Optional


class File(BaseModel):
    name: str
    size: int
    sha256: str
    def __str__(self):
        return f"File(name={self.name}, size={self.size}, sha256={self.sha256[:8]}...)"

class Peer(BaseModel):
    ip: str
    port: int


class AnnounceIn(BaseModel):
    ip: str
    port: int
    files: List[File]
    def __str__(self):
        files_str = ", ".join(str(f) for f in self.files)
        return f"AnnounceIn(ip={self.ip}, port={self.port}, files=[{files_str}])"

class FileOut(File):
    pass


class PeerOut(Peer):
    pass


class FileCompleteIn(BaseModel):
    peer_ip: str
    port: int
    name: str
    def __str__(self):
        return f"FileCompleteIn(peer_ip={self.peer_ip}, port={self.port}, name={self.name})"