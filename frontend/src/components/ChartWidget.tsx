import React, { useEffect, useRef, useState } from 'react';
import { init, dispose, type Chart, LineType } from 'klinecharts';

// 1. Add it to the interface so TypeScript knows it's a valid prop
interface ChartWidgetProps {
    symbol: string;
    initialTimeframe: string; 
}

// 2. Add it inside the curly braces here so the component can actually use it!
const ChartWidget: React.FC<ChartWidgetProps> = ({ symbol, initialTimeframe }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<Chart | null>(null);
    
    // 3. Now this will work perfectly
    const [timeframe, setTimeframe] = useState(initialTimeframe);

    const availableTimeframes = ['10s', '1m', '5m', '15m', '1H', '1D']

    // --- 1. Create the Buffer Refs ---
    // We use refs instead of state so they don't trigger re-renders
    const isHistoryLoaded = useRef(false);
    const tickBuffer = useRef<any[]>([]);

    useEffect(() => {
       if (containerRef.current) {
            chartRef.current = init(containerRef.current);
            
            // --- THE FIX: Force 5 decimals for Price, 2 for Volume ---
            chartRef.current?.setPriceVolumePrecision(5, 2);

            const fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

            chartRef.current?.setStyles({
                xAxis: {
                    tickText: { family: fontFamily }
                },
                yAxis: {
                    tickText: { family: fontFamily }
                },
                crosshair: {
                    horizontal: { text: { family: fontFamily } },
                    vertical: { text: { family: fontFamily } }
                },
                indicator: {
                    lastValueMark: { 
                        text: { family: fontFamily } 
                    },
                    tooltip: {
                        text: { family: fontFamily }
                    }
                },        
                grid: { show: true, horizontal: { style: LineType.Dashed, color: '#333' }, vertical: { show: false } },
                candle: { tooltip: { text: { family: fontFamily } } },
            });

            const ws = new WebSocket('ws://localhost:8000');

            ws.onopen = () => {
                // Reset buffer on new connection
                isHistoryLoaded.current = false;
                tickBuffer.current = [];
                
                ws.send(JSON.stringify({
                    type: 'subscribe',
                    symbol: symbol,
                    timeframe: timeframe
                }));
            };

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                
                if (message.symbol === symbol && message.timeframe === timeframe) {
                    const chart = chartRef.current;
                    if (!chart) return;

                    if (message.type === 'history') {
                        // 1. Apply the historical baseline
                        chart.applyNewData(message.data);
                        isHistoryLoaded.current = true;

                        // 2. Flush the buffer: apply all ticks that happened while we waited
                        if (tickBuffer.current.length > 0) {
                            const lastHistoryCandle = message.data[message.data.length - 1];
                            
                            tickBuffer.current.forEach(bufferedTick => {
                                // Only apply buffered ticks that are newer than or equal to the last historical timestamp
                                if (bufferedTick.timestamp >= lastHistoryCandle.timestamp) {
                                    applyTickToChart(chart, bufferedTick, timeframe);
                                }
                            });
                            // Empty the buffer
                            tickBuffer.current = [];
                        }

                    } else if (message.type === 'tick') {
                        if (!isHistoryLoaded.current) {
                            // History isn't here yet! Hold this live tick in the waiting room.
                            tickBuffer.current.push(message.data);
                        } else {
                            // History is loaded, send tick straight to the chart.
                            applyTickToChart(chart, message.data, timeframe);
                        }
                    }
                }
            };

            return () => {
                ws.close();
                dispose(containerRef.current!);
            };
        }
    }, [symbol, timeframe]);

    const applyTickToChart = (chart: Chart, tick: any, tf: string) => {
        const dataList = chart.getDataList();
        if (dataList.length === 0) return;

        const lastCandle = dataList[dataList.length - 1];
        let alignedTimestamp = tick.timestamp;

        // --- THE FIX: Map timeframes to their millisecond grids ---
        const timeGrids: { [key: string]: number } = {
            '10s': 10000,
            '1m': 60000,
            '5m': 300000,
            '15m': 900000,
            '1H': 3600000
        };

        if (tf === '1D') {
            // Daily grid: Snap to midnight UTC
            const d = new Date(tick.timestamp);
            d.setUTCHours(0, 0, 0, 0); 
            alignedTimestamp = d.getTime();
        } else if (timeGrids[tf]) {
            // Intraday grids: Snap to the nearest block for that timeframe
            alignedTimestamp = Math.floor(tick.timestamp / timeGrids[tf]) * timeGrids[tf]; 
        }

        // Fold the tick into the candle, or start a new one
        if (alignedTimestamp === lastCandle.timestamp) {
            tick.timestamp = alignedTimestamp;
            tick.open = lastCandle.open; // Preserve the historical open!
            tick.high = Math.max(lastCandle.high, tick.high);
            tick.low = Math.min(lastCandle.low, tick.low);
            tick.volume = lastCandle.volume + (tick.volume || 0);
        } else {
            tick.timestamp = alignedTimestamp;
        }

        chart.updateData(tick);
    };

    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#121212' }}>
            
            {/* --- TOP TOOLBAR --- */}
            <div style={{ padding: '6px', borderBottom: '1px solid #2B2B2B', display: 'flex', gap: '6px' }}>
                {availableTimeframes.map(tf => (
                    <button
                        key={tf}
                        onClick={() => setTimeframe(tf)}
                        style={{
                            backgroundColor: timeframe === tf ? '#2962FF' : 'transparent',
                            color: timeframe === tf ? '#FFFFFF' : '#B2B5BE',
                            border: 'none',
                            borderRadius: '4px',
                            padding: '4px 10px',
                            cursor: 'pointer',
                            fontSize: '12px',
                            fontWeight: '600',
                            transition: 'background-color 0.2s'
                        }}
                    >
                        {tf}
                    </button>
                ))}
                
                {/* Optional: Show the active symbol on the right side of the toolbar */}
                <div style={{ marginLeft: 'auto', color: '#B2B5BE', fontSize: '13px', fontWeight: 'bold', alignSelf: 'center', paddingRight: '8px' }}>
                    {symbol}
                </div>
            </div>

            {/* --- CHART CANVAS --- */}
            <div ref={containerRef} style={{ flex: 1, width: '100%' }} />
        </div>
    );
};

export default ChartWidget;