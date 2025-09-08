from typing import List, Tuple, Optional
from .models import File, Peer

class InMemoryStore:
    def __init__(self):
        self.files: List[File] = []                 # danh sách File
        self.peers: List[Peer] = []                 # danh sách Peer
        self.file_peers: List[Tuple[int, int]] = [] # danh sách cặp (file_index, peer_index)

    def announce(self, ip: str, port: int, files: List[File]):
        peer = Peer(ip=ip, port=port)
        self.peers.append(peer)
        peer_index = len(self.peers) - 1

        for f in files:
            try:
                file_index = self.files.index(f)
            except ValueError:
                self.files.append(f)
                file_index = len(self.files) - 1

            if (file_index, peer_index) not in self.file_peers:
                self.file_peers.append((file_index, peer_index))

    def search_by_filename(self, name: str) -> Tuple[Optional[File], List[Peer]]:
        file_index = next((i for i, f in enumerate(self.files) if f.name == name), None)
        if file_index is None:
            return None, []

        peer_indices = [peer_idx for f_idx, peer_idx in self.file_peers if f_idx == file_index]
        peers = [self.peers[i] for i in peer_indices]
        return self.files[file_index], peers

    def list_files(self) -> List[File]:
        return self.files.copy()

    def get_peer(self, ip: str, port: int) -> Optional[Peer]:
        for peer in self.peers:
            if peer.ip == ip and peer.port == port:
                return peer
        return None

    def get_file(self, name: str) -> Optional[File]:
        for f in self.files:
            if f.name == name:
                return f
        return None

    def add_file_to_peer(self, file: File, peer: Peer):
        try:
            file_index = self.files.index(file)
        except ValueError:
            self.files.append(file)
            file_index = len(self.files) - 1

        try:
            peer_index = self.peers.index(peer)
        except ValueError:
            self.peers.append(peer)
            peer_index = len(self.peers) - 1

        if (file_index, peer_index) not in self.file_peers:
            self.file_peers.append((file_index, peer_index))