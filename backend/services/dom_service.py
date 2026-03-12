import asyncio
from ib_async import Contract, Forex, Ticker

class DOMService:
    def __init__(self, bridge):
        self.bridge = bridge
        self.ib = bridge.ib
        # Track active subscriptions by Contract ID
        self.active_subs = {}

    async def subscribe_level2(self, contract: Contract, callback, num_rows: int = 10):
        """
        Subscribes to DOM data for any instrument concurrently.
        :param callback: A function that handles the (contract, asks, bids) data.
        """
        # Ensure the contract is fully recognized by IBKR
        await self.ib.qualifyContractsAsync(contract)
        
        con_id = contract.conId
        if con_id in self.active_subs:
            return

        # Request Depth
        ticker = self.ib.reqMktDepth(contract, numRows=num_rows)
        
        # Define the local update handler
        def on_update(updated_ticker):
            if updated_ticker.domBids or updated_ticker.domAsks:
                callback(contract, updated_ticker.domAsks, updated_ticker.domBids)

        # Attach the event
        ticker.updateEvent += on_update
        self.active_subs[con_id] = ticker
        
        print(f"DOM Service: Subscribed to {contract.localSymbol}")

    def unsubscribe(self, contract: Contract):
        con_id = contract.conId
        if con_id in self.active_subs:
            ticker = self.active_subs.pop(con_id)
            self.ib.cancelMktDepth(contract)