import json
import math
import random
import structlog

from time import time
from hashlib import sha256
from typing import List, Optional

logger = structlog.getLogger(__name__)


class Blockchain:
    def __init__(self) -> None:
        self.chain: List[dict] = []
        self.pending_transactions: List[dict] = []
        self.target = "0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

        # Create the genesis block
        logger.info("Creating genesis block")
        self.chain.append(self.new_block())

    def new_block(self) -> dict:
        # Generate a new block and add it to the chain
        block = self.create_block(
            height=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.last_block["hash"] if self.last_block else None,
            nonce=format(random.getrandbits(64), "x"),
            target=self.target,
            timestamp=time()
        )

        # Reset the list of transactions
        self.pending_transactions = []

        return block

    @staticmethod
    def create_block(
        height: int,
        transactions: List[dict],
        previous_hash: str,
        nonce: str,
        target: str,
        timestamp: Optional[float] = None
    ) -> dict:
        block = {
            "height": height,
            "transactions": transactions,
            "previous_hash": previous_hash,
            "nonce": nonce,
            "target": target,
            "timestamp": timestamp or time(),
        }

        block_string = json.dumps(block, sort_keys=True).encode()
        block["hash"] = sha256(block_string).hexdigest()

        return block

    @staticmethod
    def hash(block: dict) -> str:
        # Hash a block
        # Sort dictionary to get consistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()

        return sha256(block_string).hexdigest()

    def new_transaction(
        self,
        sender: str,
        recipient: str,
        amount: float,
    ) -> None:
        self.pending_transactions.append(
            {
                "recipient": recipient,
                "sender": sender,
                "amount": amount,
            }
        )

    @property
    def last_block(self) -> Optional[dict]:
        # Get the last block in the chain
        return self.chain[-1] if self.chain else None

    def valid_block(self, block: dict) -> bool:
        return block["hash"] < self.target

    def add_block(self, block: dict) -> None:
        # TODO: Add proper validation logic here!
        self.chain.append(block)

    def recalculate_target(self, block_index: int) -> str:
        """
        Returns the target number to mine a new block.
        """
        # Check if we need to recalculate
        if block_index % 10 == 0:
            # Expected time span of 10 blocks
            expected_timespan = 10 * 10

            # Calculate the actual time span
            actual_timespan = self.chain[-1]["timestamp"] - self.chain[-10]["timestamp"]

            # Figure out what the offset is
            ratio = actual_timespan / expected_timespan

            # Adjust ratio to not be extreme
            ratio = max(0.25, ratio)
            ratio = min(4.00, ratio)

            # Calculate the new target
            new_target = int(self.target, 16) * ratio

            self.target = format(math.floor(new_target), "x").zfill(64)
            logger.info(f"Calculated new mining target: {self.target}")

            return self.target

    async def get_blocks_after_timestamp(self, timestamp: float) -> List[dict]:
        for index, block in enumerate(self.chain):
            if timestamp < block["timestamp"]:
                return self.chain[index:]

    async def mine_new_block(self) -> None:
        self.recalculate_target(block_index=self.last_block["index"] + 1)
        while True:
            new_block = self.new_block()
            if self.valid_block(new_block):
                break

        self.chain.append(new_block)
        logger.info(f"Found a new block: {new_block}")

    def proof_of_work(self):
        while True:
            new_block = self.new_block()
            if self.valid_block(new_block):
                break
        self.chain.append(new_block)
        print(f"Found a new block: {new_block}")

    def valid_hash(self):
        pass
