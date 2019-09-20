""" Chain class """

from typing import List

from .block import Block


class Chain(object):
    """ A chain of blocks """

    def __init__(self):
        """ Ctor. """
        self.chain: List[Block] = []
        self._init_chain_with_genesis_block()

    def _init_chain_with_genesis_block(self) -> None:
        """ Create a genesis block and append it to the chain. """
        genesis: Block = Block(0, None, "0")
        self.chain.append(genesis)
