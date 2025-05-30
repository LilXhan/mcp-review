import requests
import datetime
from pathlib import Path
from typing import Any
from mcp.server.fastmcp import FastMCP


THIS_FOLDER = Path(__file__).parent.absolute()
ACTIVITY_LOGS_FILE = THIS_FOLDER / 'activity.log'

mcp = FastMCP('Binance MCP')

def get_symbol_from_name(name: str) -> str: 
    if name.lower() in ['bitcoin', 'btc']:
        return "BTCUSDT"
    elif name.lower() in ['ethereum', 'eth']:
        return 'ETHUSDT' 
    else: 
        return name.upper()

@mcp.prompt()
def executive_summary() -> str:
    """ Returns an executive summary of Bitcoin and Ethereum """

    return """
    Get the current price of the following crypto asset: btc, eth
    
    Provide me with an esecutive summary including the two-sentence summary of the
    crypto asset, the current price, the price change in the last 24 hours, and the percentage
    change in the last 24 hours.
    
    When using the get_price and get_price_change tools, use the symbol as the argument
    Symbols: for bitcoin/btc, the symbol is "BTCUSDT".
    Symbols: for ethereum/eth, the symbos is "ETHUSDT".
    """

@mcp.prompt()
def crypto_summary(crypto) -> str:
    """ Returns a summary of a crypto asset """

    return f"""
    Get the current price of the following crypto asset:
    { crypto }
    and also provide a summary of the price changes in the last 24 hours.

    When using the get_price and get_price_change tools, use the symbol as the argument
    Symbols: for bitcoin/btc, the symbol is "BTCUSDT".
    Symbols: for ethereum/eth, the symbos is "ETHUSDT".
    """


@mcp.tool()
def get_price(symbol: str) -> Any:
    """
        Get the current price of a crypto asset from Binance
        Args:
            symbol(str): The symbol of the crypto asset to get the price of binance
        Returns:
            Any: The current price of the crypto asset
    """
    symbol = get_symbol_from_name(symbol)
    url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(url)
    
    if response.status_code != 200:
        with open(ACTIVITY_LOGS_FILE, 'a') as f:
            f.write(
                f'\nError getting price change for {symbol}: { response.status_code } { response.text }'
            )
        raise Exception(
            f'Error getting price change for {symbol}: { response.status_code } { response.text }'
        )
    else:
        price = response.json()['price']
        with open(ACTIVITY_LOGS_FILE, 'a') as f:
            f.write(
                f'\nSuccesfully got price change for {symbol}. The current price is { price }. Current time is { datetime.date }'
            )
    return f'The current price of { symbol } is { price }'

@mcp.resource('file://activity.log')
def activity_log() -> str:
    with open(ACTIVITY_LOGS_FILE, 'r') as f:
        return f.read()

@mcp.resource('resource://crypto_price/{symbol}')
def get_crypto_price(symbol: str) -> str:
    return get_price(symbol)

@mcp.resource('file://symbol_map.csv')
def symbol_map() -> str:
    return """crypto_name, symbol
    btc,BTCUSDT
    eth,ETHUSDT
    bitcoin,BTCUSDT
    eth,ETHUSDT
    my_favorite,ETCUSDT
    """

@mcp.tool()
def get_price_change(symbol: str) -> Any:
    """
        Get the price change of the last 24 hours of a crypto asset from Binance

        Args:
            symbol(str): The symbol of the crypto asset to get the price of binance
        Returns:
            Any: The current price of the crypto asset
    """
    symbol = get_symbol_from_name(symbol)
    url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    if not Path(ACTIVITY_LOGS_FILE).exists():
        Path(ACTIVITY_LOGS_FILE).touch()
    mcp.run(transport='stdio')