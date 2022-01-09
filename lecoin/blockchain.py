import json

from datetime import datetime
from hashlib import sha256
from typing import Optional


class Blockchain:
    def __init__(self) -> None:
        self.chain = []
        self.pending_transactions = []

        # Create the genesis block
        print("Creating genesis block")
        self.new_block()

    def new_block(self, previous_hash: str = None) -> dict:
        # Generate a new block and add it to the chain
        block = {
            "index": len(self.chain),
            "timestamp": datetime.utcnow().isoformat(),
            "transactions": self.pending_transactions,
            "previous_hash": previous_hash,
        }

        block_hash = self.hash(block)
        block["hash"] = block_hash

        # Reset the list of transactions
        self.pending_transactions = []

        # Add the block to the chain
        # self.chain.append(block)
        # print(f"Created block {block['index']}")

        return block

    def new_transaction(
        self,
        sender: str,
        recipient: str,
        amount: float,
    ) -> None:
        self.pending_transactions.append({
            "recipient": recipient,
            "sender": sender,
            "amount": amount,
        })

    @staticmethod
    def hash(block: dict) -> str:
        # Hash a block
        # Sort dictionary to get consistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()

        return sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Optional(dict, None):
        # Get the last block in the chain
        return self.chain[-1] if self.chain else None

    @staticmethod
    def valid_block(block: dict) -> int:
        return block["hash"].startswith("0000")

    def proof_of_work(self):
        while True:
            new_block = self.new_block()
            if self.valid_block(new_block):
                break
        self.chain.append(new_block)
        print(f"Found a new block: {new_block}")

    def valid_hash(self):
        pass
