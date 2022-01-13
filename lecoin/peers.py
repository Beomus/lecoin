import asyncio

import structlog

from asyncio import StreamWriter

from .messages import create_peers_message, create_block_message, create_transaction_message, create_ping_message
# from .transactions import validate_transaction
from .server import Server

logger = structlog.getLogger(__name__)


class P2PError(Exception):
    pass


class P2PProtocol:
    def __init__(self, server: Server) -> None:
        self.server = server
        self.blockchain = server.blockchain
        self.connection_pool = server.connection_pool

    @staticmethod
    async def send_message(writer: StreamWriter, message_text: str) -> None:
        writer.write(message_text.encode() + b"\n")

    @staticmethod
    async def handle_message(self, message: dict, writer: StreamWriter):
        message_handlers = {
            "block": self.handle_block,
            "ping": self.handle_ping,
            "peers": self.handle_peers,
            "transaction": self.handle_transaction,
        }

        handler = message_handlers.get(message["name"])

        if not handler:
            raise P2PError("Missing handler for message")

        await handler(message, writer)

    async def handle_ping(self, message: dict, writer: StreamWriter) -> None:
        """
        Execute when a `ping` message is received
        """
        block_height = message["payload"]["block_height"]

        # If they're a miner, let's mark them as such
        writer.is_miner = message["payload"]["is_miner"]

        # Let's send our 20 most "alive" peers to this user
        peers = self.connection_pool.get_alive_peers(20)
        peers_message = create_peers_message(
            self.server.external_ip, self.server.external_port, peers
        )

        await self.send_message(writer, peers_message)

        # Let's send them blocks if they have less than us
        if block_height < self.blockchain.last_block["height"]:
            # Send them each block in succession, from their height
            for block in self.blockchain.chain[block_height + 1:]:
                await self.send_message(
                    writer,
                    create_block_message(
                        self.server.external_ip, self.server.external_port, block
                    ),
                )

    async def handle_transaction(self, message: dict) -> None:
        """
        Execute when a transaction was broadcast by a peer
        """
        logger.info("Received transaction")

        tx = message["payload"]

        if validate_transaction(tx):
            if tx not in self.blockchain.pending_transactions:
                self.blockchain.pending_transactions.append(tx)

                for peer in self.connection_pool.get_alive_peers(20):
                    await self.send_message(
                        peer,
                        create_transaction_message(
                            self.server.external_ip,
                            self.server.external_port,
                            tx
                        )
                    )
        else:
            logger.warning("Received invalid transaction")

    async def handle_block(self, message: dict, writer: StreamWriter) -> None:
        """
        Execute when receiving a block from a peer
        """
        logger.info("Receive new block")

        block = message["block"]

        self.blockchain.add_block(block)

        # Transmit the block to peers
        for peer in self.connection_pool.get_alive_peers(20):
            await self.send_message(
                peer,
                create_block_message(
                    self.server.external_ip,
                    self.server.external_port,
                    block
                )
            )

    async def handle_peers(self, message: dict) -> None:
        """
        Execute when receiving new peers
        """

        logger.info("Received new peers")

        peers = message["payload"]

        ping_message = create_ping_message(
            self.server.external_ip,
            self.server.external_port,
            len(self.blockchain.chain),
            len(self.connection_pool.get_alive_peers(50)),
            False
        )

        for peer in peers:
            # Create connection and add them to the pool
            reader, writer = await asyncio.open_connection(peer["ip"], peer["port"])

            self.connection_pool.add_peer(writer)

            # send a ping message
            await self.send_message(writer, ping_message)
