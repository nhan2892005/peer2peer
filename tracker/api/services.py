from .store import InMemoryStore
from .models import File, Peer
from typing import List, Tuple, Optional


class TrackerService:
    def __init__(self, store: InMemoryStore):
        self.store = store

    def announce(self,ip: str, port: int, files: List[File]):
        self.store.announce(ip, port, files)

    def get_file_peers(self, filename: str) -> Tuple[Optional[File], List[Peer]]:
        return self.store.search_by_filename(filename)

    def list_files(self) -> List[File]:
        return self.store.list_files()

    def complete(self, ip: str, port: int, name: str):
        peer = self.store.get_peer(ip, port)
        if not peer:
            raise ValueError("Peer not found")

        f = self.store.get_file(name)
        if not f:
            raise ValueError("File not found")

        self.store.add_file_to_peer(f, peer)