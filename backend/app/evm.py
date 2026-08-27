import asyncio
import re
from dataclasses import dataclass

import httpx

EVM_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
SUPPORTED_CHAINS = {"ethereum"}


class InvalidEVMAddress(ValueError):
    pass


def normalize_evm_address(address: str) -> str:
    value = address.strip()
    if not EVM_ADDRESS_RE.fullmatch(value):
        raise InvalidEVMAddress("Invalid EVM address")
    return value.lower()


@dataclass(frozen=True)
class OnChainObservation:
    address: str
    chain: str
    balance_wei: int
    transaction_count: int
    is_contract: bool
    block_number: int


class EVMRPC:
    def __init__(self, rpc_url: str, timeout_seconds: float = 4.0):
        self.rpc_url = rpc_url
        self.timeout = httpx.Timeout(timeout_seconds, connect=2.0)

    async def call(self, method: str, params: list) -> object:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(2):
                try:
                    response = await client.post(self.rpc_url, json=payload)
                    response.raise_for_status()
                    body = response.json()
                    if "error" in body or "result" not in body:
                        raise RuntimeError("RPC returned an error")
                    return body["result"]
                except (httpx.HTTPError, RuntimeError):
                    if attempt == 1:
                        raise
                    await asyncio.sleep(0.15)
        raise RuntimeError("RPC request failed")

    async def observe(self, chain: str, address: str) -> OnChainObservation:
        if chain not in SUPPORTED_CHAINS:
            raise ValueError("Unsupported chain")
        address = normalize_evm_address(address)
        balance, tx_count, code, block = await asyncio.gather(
            self.call("eth_getBalance", [address, "latest"]),
            self.call("eth_getTransactionCount", [address, "latest"]),
            self.call("eth_getCode", [address, "latest"]),
            self.call("eth_blockNumber", []),
        )
        return OnChainObservation(address, chain, int(balance, 16), int(tx_count, 16), code != "0x", int(block, 16))
