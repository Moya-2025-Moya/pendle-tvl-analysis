"""
Shared utilities for Pendle TVL analysis.
"""

import json
import time
import requests
import pandas as pd
from web3 import Web3
from pathlib import Path

# ── RPC endpoints ─────────────────────────────────────────────────────────────
ETH_RPC  = "https://eth-mainnet.g.alchemy.com/v2/TBTri88WcPoFSqH9luU86"
ARB_RPC  = "https://arb-mainnet.g.alchemy.com/v2/TBTri88WcPoFSqH9luU86"
BNB_RPC  = "https://bnb-mainnet.g.alchemy.com/v2/TBTri88WcPoFSqH9luU86"

# ── Known contract addresses ───────────────────────────────────────────────────
ADDRESSES = {
    # Pendle
    "PENDLE_TOKEN":   "0x808507121B80c02388fAd14726482e061B8da827",
    "vePENDLE":       "0x4f30A9D41B80ecC5B94306AB4364951AE3170210",
    # sPENDLE: confirmed at https://docs.pendle.finance/pendle-v2/Developers/Contracts/sPENDLE
    "sPENDLE":        "0x999999999991E178D52Cd95AFd4b00d066664144",

    # Ethena
    "sUSDe":  "0x9D39A5DE30e57443BfF2A8307A4256c8797A3497",
    "USDe":   "0x4c9EDD5852cd905f086C759E8383e09bff1E68B3",

    # Aave V3 Ethereum
    "AAVE_POOL":          "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
    "AAVE_DATA_PROVIDER": "0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3",

    # Stablecoins
    "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
}

# ── Minimal ABIs ───────────────────────────────────────────────────────────────
ERC20_ABI = [
    {"inputs": [], "name": "totalSupply",
     "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals",
     "outputs": [{"type": "uint8"}],  "stateMutability": "view", "type": "function"},
]

AAVE_DATA_PROVIDER_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "asset", "type": "address"}],
        "name": "getReserveData",
        "outputs": [
            {"internalType": "uint256", "name": "unbacked",               "type": "uint256"},
            {"internalType": "uint256", "name": "accruedToTreasuryScaled","type": "uint256"},
            {"internalType": "uint256", "name": "totalAToken",            "type": "uint256"},
            {"internalType": "uint256", "name": "totalStableDebt",        "type": "uint256"},
            {"internalType": "uint256", "name": "totalVariableDebt",      "type": "uint256"},
            {"internalType": "uint256", "name": "liquidityRate",          "type": "uint256"},
            {"internalType": "uint256", "name": "variableBorrowRate",     "type": "uint256"},
            {"internalType": "uint256", "name": "stableBorrowRate",       "type": "uint256"},
            {"internalType": "uint256", "name": "averageStableBorrowRate","type": "uint256"},
            {"internalType": "uint256", "name": "liquidityIndex",         "type": "uint256"},
            {"internalType": "uint256", "name": "variableBorrowIndex",    "type": "uint256"},
            {"internalType": "uint40",  "name": "lastUpdateTimestamp",    "type": "uint40"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]


# ── Block finder ───────────────────────────────────────────────────────────────
def get_web3(rpc_url: str = ETH_RPC) -> Web3:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    assert w3.is_connected(), f"Cannot connect to {rpc_url}"
    return w3


def get_block_by_timestamp(target_ts: int, w3: Web3, lo: int = 1, hi: int = None) -> int:
    """
    Binary-search for the first block whose timestamp >= target_ts.
    Returns the block number.
    """
    if hi is None:
        hi = w3.eth.block_number

    while lo < hi:
        mid = (lo + hi) // 2
        ts  = w3.eth.get_block(mid)["timestamp"]
        if ts < target_ts:
            lo = mid + 1
        else:
            hi = mid
    return lo


def blocks_for_dates(dates: list[str], w3: Web3) -> dict[str, int]:
    """
    dates: list of 'YYYY-MM-DD' UTC midnight strings.
    Returns {date_str: block_number}.
    """
    import datetime
    result = {}
    for d in dates:
        dt  = datetime.datetime.strptime(d, "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc)
        ts  = int(dt.timestamp())
        blk = get_block_by_timestamp(ts, w3)
        result[d] = blk
        print(f"  {d} → block {blk}")
    return result


# ── ERC-20 totalSupply at a block ──────────────────────────────────────────────
def erc20_total_supply(token_address: str, block: int, w3: Web3, decimals: int = 18) -> float:
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(token_address),
        abi=ERC20_ABI,
    )
    raw = contract.functions.totalSupply().call(block_identifier=block)
    return raw / 10**decimals


# ── Aave V3 reserve data at a block ──────────────────────────────────────────
RAY = 10**27

def aave_reserve_data(asset_address: str, block: int, w3: Web3) -> dict:
    """
    Returns reserve data from Aave V3 PoolDataProvider.
    Rates are stored as annual rates in RAY (1e27) — NOT per-second.
    APR% = rate_ray / RAY * 100
    """
    dp = w3.eth.contract(
        address=Web3.to_checksum_address(ADDRESSES["AAVE_DATA_PROVIDER"]),
        abi=AAVE_DATA_PROVIDER_ABI,
    )
    d = dp.functions.getReserveData(
        Web3.to_checksum_address(asset_address)
    ).call(block_identifier=block)

    return {
        "totalAToken":            d[2],
        "totalVariableDebt":      d[4],
        "liquidityRate_ray":      d[5],
        "variableBorrowRate_ray": d[6],
        "supplyAPR_%":            round(d[5] / RAY * 100, 4),
        "variableBorrowAPR_%":    round(d[6] / RAY * 100, 4),
    }


# ── Aave V3 subgraph (The Graph hosted service) ───────────────────────────────
AAVE_V3_SUBGRAPH = (
    "https://api.thegraph.com/subgraphs/name/aave/protocol-v3"
)

def query_subgraph(endpoint: str, query: str, variables: dict = None) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = requests.post(endpoint, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


# ── DefiLlama Yields API ──────────────────────────────────────────────────────
LLAMA_YIELDS_BASE = "https://yields.llama.fi"

def get_all_pendle_pools() -> pd.DataFrame:
    """Fetch all Pendle pools from DefiLlama Yields and return as DataFrame."""
    # Disable brotli to avoid decompression issues on some environments
    headers = {"Accept-Encoding": "gzip, deflate"}
    resp = requests.get(f"{LLAMA_YIELDS_BASE}/pools", timeout=60, headers=headers)
    resp.raise_for_status()
    pools = resp.json()["data"]
    df = pd.DataFrame(pools)
    pendle = df[df["project"].str.contains("pendle", case=False, na=False)].copy()
    return pendle.reset_index(drop=True)


def get_pool_yield_history(pool_id: str) -> pd.DataFrame:
    """Fetch daily APY history for a specific DefiLlama pool UUID."""
    headers = {"Accept-Encoding": "gzip, deflate"}
    resp = requests.get(f"{LLAMA_YIELDS_BASE}/chart/{pool_id}", timeout=30, headers=headers)
    resp.raise_for_status()
    data = resp.json()["data"]
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ── CoinGecko (free, no key) ──────────────────────────────────────────────────
COINGECKO_BASE = "https://api.coingecko.com/api/v3"

def coingecko_price_range(coin_id: str, from_ts: int, to_ts: int,
                           vs_currency: str = "usd") -> pd.DataFrame:
    """
    Fetch daily OHLC from CoinGecko free API (rate-limited: 30 req/min).
    from_ts / to_ts: Unix timestamps.
    """
    url = (
        f"{COINGECKO_BASE}/coins/{coin_id}/market_chart/range"
        f"?vs_currency={vs_currency}&from={from_ts}&to={to_ts}"
    )
    resp = requests.get(url, timeout=30)
    if resp.status_code == 429:
        print("CoinGecko rate limit hit — sleeping 60s")
        time.sleep(60)
        resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    raw = resp.json()
    prices = pd.DataFrame(raw["prices"], columns=["ts_ms", "price_usd"])
    prices["date"] = pd.to_datetime(prices["ts_ms"], unit="ms").dt.date
    prices = prices.groupby("date")["price_usd"].last().reset_index()
    prices.name = coin_id
    return prices


# ── DefiLlama protocol TVL history ───────────────────────────────────────────
LLAMA_API_BASE = "https://api.llama.fi"

def get_protocol_tvl(slug: str) -> pd.DataFrame:
    """
    Fetch daily TVL history for a protocol from DefiLlama.
    Returns DataFrame with columns: date, protocol, totalLiquidityUSD.
    """
    headers = {"Accept-Encoding": "gzip, deflate"}
    resp = requests.get(f"{LLAMA_API_BASE}/protocol/{slug}", timeout=30, headers=headers)
    resp.raise_for_status()
    data     = resp.json()
    tvl_list = data.get("tvl", [])
    # DefiLlama returns list of dicts: [{"date": unix_ts, "totalLiquidityUSD": val}, ...]
    if tvl_list and isinstance(tvl_list[0], dict):
        df = pd.DataFrame(tvl_list).rename(columns={"date": "unix_ts"})
    else:
        df = pd.DataFrame(tvl_list, columns=["unix_ts", "totalLiquidityUSD"])
    df["totalLiquidityUSD"] = pd.to_numeric(df["totalLiquidityUSD"], errors="coerce")
    df["date"]     = pd.to_datetime(df["unix_ts"], unit="s").dt.date.astype(str)
    df["protocol"] = slug
    return df[["date", "protocol", "totalLiquidityUSD"]].dropna()


# ── Pendle public API ─────────────────────────────────────────────────────────
PENDLE_API = "https://api-v2.pendle.finance/core/v1"

def get_pendle_markets(chain_id: int = 1) -> pd.DataFrame:
    url = f"{PENDLE_API}/{chain_id}/markets?order_by=name:1&skip=0&limit=200"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    markets = resp.json().get("markets", resp.json().get("results", []))
    return pd.DataFrame(markets)


# ── CSV helpers ───────────────────────────────────────────────────────────────
def save_csv(df: pd.DataFrame, path: str | Path, label: str = "") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    n = len(df)
    cols = list(df.columns)
    print(f"[saved] {path}  ({n} rows, cols: {cols})" + (f" — {label}" if label else ""))


def load_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)
