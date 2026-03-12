import asyncio
from ib_async import Contract
import math
import datetime

class ChartService:
    def __init__(self, bridge):
        self.bridge = bridge
        self.ib = bridge.ib
        self.live_tickers = {}
        self.current_candles = {}

    async def get_historical_data(self, contract: Contract, duration='900 S', bar_size='5 secs'):
        """Fetches historical bars and formats them for the React chart."""
        await self.ib.qualifyContractsAsync(contract)
        
        bars = await self.ib.reqHistoricalDataAsync(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow='MIDPOINT',
            useRTH=False
        )
        
        history = []
        for bar in bars:
            # --- THE FIX: Handle both datetime and date objects safely ---
            if isinstance(bar.date, datetime.datetime):
                # Intraday bars (10s, 1m, 1h) have a full datetime
                ts = int(bar.date.timestamp() * 1000)
            else:
                # Daily bars (1D) only have a date. We convert it to midnight UTC to get a valid timestamp.
                dt = datetime.datetime.combine(bar.date, datetime.time.min, tzinfo=datetime.timezone.utc)
                ts = int(dt.timestamp() * 1000)

            history.append({
                "timestamp": ts, 
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume
            })
        return history

    async def subscribe_live_ticks(self, contract: Contract, callback, bar_interval_secs=5):
        """Aggregates live ticks into a candle and fires the callback."""
        await self.ib.qualifyContractsAsync(contract)
        con_id = contract.conId

        if con_id in self.live_tickers:
            return

        self.current_candles[con_id] = None
        ticker = self.ib.reqMktData(contract, '', False, False)

        def on_tick(updated_ticker):
            # Check for NaN or missing values immediately
            if not updated_ticker.bid or not updated_ticker.ask or not updated_ticker.time:
                return
            
            # Use math.isnan to catch bad data
            if math.isnan(updated_ticker.bid) or math.isnan(updated_ticker.ask):
                return
            
            price = round((updated_ticker.bid + updated_ticker.ask) / 2, 5)
            current_time = int(updated_ticker.time.timestamp())
            
            # Bucket time into 5-second intervals and convert to ms for frontend
            bucket_time = (current_time // bar_interval_secs) * bar_interval_secs 
            bucket_time_ms = bucket_time * 1000 

            candle = self.current_candles[con_id]
            
            # Start a new candle if we crossed into a new bucket
            if candle is None or bucket_time_ms > candle["timestamp"]:
                candle = {
                    "timestamp": bucket_time_ms, 
                    "open": price, "high": price, "low": price, "close": price, 
                    "volume": 0
                }
                self.current_candles[con_id] = candle
            else:
                # Update existing candle highs and lows
                candle["high"] = max(candle["high"], price)
                candle["low"] = min(candle["low"], price)
                candle["close"] = price
                
            callback(contract, candle)

        ticker.updateEvent += on_tick
        self.live_tickers[con_id] = ticker

    async def subscribe_raw_ticks(self, contract, callback):
        """Subscribes to raw, unthrottled Level 1 market data."""
        
        # --- THE FIX: Must use the Async version so the event loop doesn't crash! ---
        await self.ib.qualifyContractsAsync(contract)
        
        ticker = self.ib.reqMktData(contract, '', False, False)
        ticker.updateEvent += callback
        return ticker

    def cancel_raw_ticks(self, ticker):
        """Cleans up the stream when switching timeframes."""
        if ticker:
            self.ib.cancelMktData(ticker.contract)