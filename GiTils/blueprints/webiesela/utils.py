import asyncio

from vibora.client.websocket import WebsocketClient


async def test_giesela_websocket(host: str, port: int, timeout: float) -> bool:
    client = WebsocketClient(host, port, "/gitils")
    try:
        await asyncio.wait_for(client.connect(), timeout)
    except asyncio.TimeoutError:
        return False
    else:
        # TODO get information and close connection
        return True


def generate_regtoken(length: int) -> str:
    pass
