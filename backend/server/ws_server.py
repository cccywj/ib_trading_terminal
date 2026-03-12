import asyncio
import json
import websockets
from ib_async import Forex

class ChartWebSocketServer:
    def __init__(self, chart_service, host="localhost", port=8000):
        self.chart_service = chart_service
        self.host = host
        self.port = port
        self.connected_clients = set()

    async def ws_handler(self, websocket):
        import websockets
        import asyncio
        import time
        import math
        
        connection_active = True 
        raw_ticker = None  # Store this so we can cancel it later
        
        try:
            async for message in websocket:
                msg = json.loads(message)
                
                if msg.get('type') == 'subscribe':
                    symbol = msg['symbol']
                    tf = msg['timeframe']
                    
                    duration, bar_size, _ = self.parse_timeframe(tf)
                    contract = Forex(symbol)
                    
                    # --- 1. THE RAW TICK ENGINE ---
                    latest_tick = None
                    last_sent_ts = 0

                    def on_tick(ticker):
                        if not connection_active: return
                        
                        # --- THE FIX: Safely calculate Midpoint from Bid/Ask ---
                        bid = ticker.bid
                        ask = ticker.ask
                        
                        # Check if IBKR has sent valid bid/ask data yet
                        if math.isnan(bid) or math.isnan(ask) or bid <= 0 or ask <= 0:
                            # Fallback just in case
                            price = ticker.marketPrice()
                            if math.isnan(price) or price <= 0:
                                return
                        else:
                            price = (bid + ask) / 2.0
                            
                        nonlocal latest_tick
                        # Build the micro-candle
                        latest_tick = {
                            "timestamp": int(time.time() * 1000),
                            "open": price, "high": price, "low": price, "close": price, "volume": 0
                        }

                    # Start pulling the unthrottled data
                    raw_ticker = await self.chart_service.subscribe_raw_ticks(contract, on_tick)

                    # --- 2. THE 60 FPS THROTTLER ---
                    async def throttle_broadcaster():
                        nonlocal last_sent_ts
                        while connection_active:
                            # Only broadcast if there's a new tick we haven't sent yet
                            if latest_tick and latest_tick["timestamp"] != last_sent_ts:
                                last_sent_ts = latest_tick["timestamp"]
                                try:
                                    await websocket.send(json.dumps({
                                        "type": "tick", "symbol": symbol, "timeframe": tf, "data": latest_tick
                                    }))
                                except Exception:
                                    pass
                            
                            # Sleep for 16.6 milliseconds (60 FPS)
                            await asyncio.sleep(1 / 60)
                            
                    # Boot the throttle engine in the background
                    asyncio.create_task(throttle_broadcaster())

                    # --- 3. THE HISTORY DOWNLOAD ---
                    try:
                        history = await asyncio.shield(
                            self.chart_service.get_historical_data(
                                contract, duration=duration, bar_size=bar_size
                            )
                        )
                        
                        if connection_active:
                            await websocket.send(json.dumps({
                                "type": "history", "symbol": symbol, "timeframe": tf, "data": history
                            }))
                            
                    except asyncio.CancelledError:
                        pass 

        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"WS Handling Error: {e}")
        finally:
            connection_active = False
            # Clean up the raw data stream so we don't leak memory when switching timeframes
            if raw_ticker:
                self.chart_service.cancel_raw_ticks(raw_ticker)

    def parse_timeframe(self, tf: str):
        """
        Translates frontend strings into IBKR API parameters.
        Returns: (Duration String, Bar Size Setting, Bucket Seconds)
        """
        mapping = {
            '10s': ('1800 S', '10 secs', 10),      # 30 mins history
            '1m':  ('2 D', '1 min', 60),           # 2 days history
            '5m':  ('5 D', '5 mins', 300),         # 5 days history
            '15m': ('10 D', '15 mins', 900),       # 10 days history
            '1H':  ('1 M', '1 hour', 3600),        # 1 month history
            '1D':  ('1 Y', '1 day', 86400)         # 1 year history
        }
        
        # Look up the timeframe, default to 1m if not found
        return mapping.get(tf, ('2 D', '1 min', 60))

    async def start(self):
        print(f"Starting Chart WebSocket on ws://{self.host}:{self.port}...")
        async with websockets.serve(self.ws_handler, self.host, self.port):
            # This future keeps the server running indefinitely
            await asyncio.Future()