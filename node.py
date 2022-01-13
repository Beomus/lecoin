import asyncio

from lecoin.blockchain import Blockchain
from lecoin.connections import ConnectionPool
from lecoin.peers import P2PProtocol
from lecoin.server import Server

blockchain = Blockchain()  # <1>
connection_pool = ConnectionPool()  # <2>

server = Server(blockchain, connection_pool, P2PProtocol)


async def main():
    # Start the server
    await server.listen()


asyncio.run(main())
