from typing import List

import structlog

from more_itertools import take
from asyncio import StreamWriter

logger = structlog.getLogger(__name__)


class ConnectionPool:
    def __init__(self) -> None:
        self.connection_pool = dict()

    def broadcast(self, message: str):
        for user in self.connection_pool:
            user.write(f"{message}".encode())

    @staticmethod
    def get_address_string(writer: StreamWriter) -> str:
        ip = writer.address["ip"]
        port = writer.address["port"]
        return f"{ip}:{port}"

    def add_peer(self, writer: StreamWriter):
        address = self.get_address_string(writer=writer)
        self.connection_pool[address] = writer
        logger.info("Added new peer to pool", address=address)

    def remove_peer(self, writer: StreamWriter):
        address = self.get_address_string(writer=writer)
        self.connection_pool.pop(address)
        logger.info("Removed peer from pool", address=address)

    def get_alive_peers(self, count: int) -> List[StreamWriter]:
        # TODO: sort these by most active
        return take(count, self.connection_pool.items())
