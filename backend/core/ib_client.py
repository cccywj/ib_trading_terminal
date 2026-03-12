import asyncio
from ib_async import IB

class IBBridge:
    def __init__(self):
        self.ib = IB()

    async def connect(self, host: str = '127.0.0.1', port: int = 4002, client_id: int = 1):
        """Main connection point for the terminal."""
        if not self.ib.isConnected():
            await self.ib.connectAsync(host, port, clientId=client_id)
            # Set to live data by default
            self.ib.reqMarketDataType(1)
        return self.ib

    def disconnect(self):
        self.ib.disconnect()