import React, { useEffect, useRef, useState } from 'react';
import { init, dispose, type Chart, LineType } from 'klinecharts';

interface ChartWidgetProps {
    symbol: string;
}

const ChartWidget: React.FC<ChartWidgetProps> = ({ symbol }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<Chart | null>(null);
    
    // Track active states for our UI buttons
    const [timeframe, setTimeframe] = useState('1m');
    const [activeMainIndicators, setActiveMainIndicators] = useState<string[]>([]);
    const [activeSubIndicators, setActiveSubIndicators] = useState<string[]>([]);

    useEffect(() => {
        if (containerRef.current) {
            chartRef.current = init(containerRef.current);

            chartRef.current?.setStyles({
                grid: { show: true, horizontal: { style: LineType.Dashed, color: '#333' }, vertical: { show: false } },
                candle: { tooltip: { text: { family: "'Trebuchet MS', sans-serif" } } },
                xAxis: { tickText: { family: "'Trebuchet MS', sans-serif", color: '#888' }, axisLine: { color: '#333' } },
                yAxis: { tickText: { family: "'Trebuchet MS', sans-serif", color: '#888' }, axisLine: { color: '#333' } },
                crosshair: {
                    horizontal: { text: { family: "'Trebuchet MS', sans-serif" }, line: { color: '#888' } },
                    vertical: { text: { family: "'Trebuchet MS', sans-serif" }, line: { color: '#888' } }
                },
                indicator: { tooltip: { text: { family: "'Trebuchet MS', sans-serif" } } }
            });

            chartRef.current?.applyNewData([
                { timestamp: Date.now() - 120000, open: 149, high: 151, low: 148, close: 150, volume: 800 },
                { timestamp: Date.now() - 60000, open: 150, high: 155, low: 145, close: 152, volume: 1000 },
                { timestamp: Date.now(), open: 152, high: 153, low: 150, close: 151, volume: 500 }
            ]);
            
            const handleResize = () => {
                    chartRef.current?.resize();
                };
            window.addEventListener('resize', handleResize);

            // Cleanup
            return () => {
                window.removeEventListener('resize', handleResize);
                if (containerRef.current) dispose(containerRef.current);
            };
        }
    }, [symbol]);

    // --- TOOLBAR FUNCTIONS ---

    const changeTimeframe = (tf: string) => {
        setTimeframe(tf);
        // Later, this will send a WebSocket message to Python to request new historical bars
        console.log(`Switched to ${tf} data`); 
    };

    const toggleMainIndicator = (name: string) => {
        if (!chartRef.current) return;
        
        if (activeMainIndicators.includes(name)) {
            // Remove it
            chartRef.current.removeIndicator('candle_pane', name);
            setActiveMainIndicators(prev => prev.filter(i => i !== name));
        } else {
            // Add it to the main candle pane
            chartRef.current.createIndicator(name, true, { id: 'candle_pane' });
            setActiveMainIndicators(prev => [...prev, name]);
        }
    };

    const toggleSubIndicator = (name: string) => {
        if (!chartRef.current) return;

        // Create a predictable ID based on the indicator's name
        const paneId = `pane_${name}`;

        if (activeSubIndicators.includes(name)) {
            // Remove the indicator from that exact pane
            chartRef.current.removeIndicator(paneId, name);
            setActiveSubIndicators(prev => prev.filter(i => i !== name));
        } else {
            // Create a new pane and force it to use our predictable ID
            chartRef.current.createIndicator(name, false, { id: paneId });
            setActiveSubIndicators(prev => [...prev, name]);
        }
    };

    // --- INLINE STYLES FOR BUTTONS ---
    const btnStyle = (isActive: boolean) => ({
        backgroundColor: isActive ? '#4caf50' : '#2d2d2d',
        color: isActive ? '#fff' : '#aaa',
        border: 'none',
        padding: '5px 10px',
        marginRight: '5px',
        borderRadius: '4px',
        cursor: 'pointer',
        fontFamily: "'Trebuchet MS', sans-serif",
        fontSize: '12px',
        fontWeight: 'bold' as const
    });

    return (
        <div style={{ 
            width: '100%', 
            height: '100vh', 
            backgroundColor: '#121212', 
            display: 'flex', 
            flexDirection: 'column',
            overflow: 'hidden' // <-- Add this
        }}>
            
            {/* Custom Toolbar */}
            <div style={{ 
                display: 'flex', 
                alignItems: 'center',
                padding: '8px 15px', 
                borderBottom: '1px solid #333',
                backgroundColor: '#1e1e1e'
            }}>
                <div style={{ color: '#fff', fontWeight: 'bold', fontFamily: "'Trebuchet MS', sans-serif", marginRight: '20px' }}>
                    {symbol}
                </div>

                {/* Timescale Selectors */}
                <div style={{ borderRight: '1px solid #444', paddingRight: '10px', marginRight: '10px' }}>
                    {['1m', '5m', '15m', '1H'].map(tf => (
                        <button key={tf} style={btnStyle(timeframe === tf)} onClick={() => changeTimeframe(tf)}>
                            {tf}
                        </button>
                    ))}
                </div>

                {/* Overlays (Main Pane) */}
                <div style={{ borderRight: '1px solid #444', paddingRight: '10px', marginRight: '10px' }}>
                    <button style={btnStyle(activeMainIndicators.includes('MA'))} onClick={() => toggleMainIndicator('MA')}>MA</button>
                    <button style={btnStyle(activeMainIndicators.includes('EMA'))} onClick={() => toggleMainIndicator('EMA')}>EMA</button>
                    <button style={btnStyle(activeMainIndicators.includes('BOLL'))} onClick={() => toggleMainIndicator('BOLL')}>BOLL</button>
                </div>

                {/* Sub-Pane Indicators */}
                <div>
                    <button style={btnStyle(activeSubIndicators.includes('VOL'))} onClick={() => toggleSubIndicator('VOL')}>Volume</button>
                    <button style={btnStyle(activeSubIndicators.includes('MACD'))} onClick={() => toggleSubIndicator('MACD')}>MACD</button>
                    <button style={btnStyle(activeSubIndicators.includes('RSI'))} onClick={() => toggleSubIndicator('RSI')}>RSI</button>
                </div>
            </div>
            
            {/* The Chart Canvas */}
            <div ref={containerRef} style={{ 
                flex: 1, 
                width: '100%', 
                minHeight: 0 // <-- ADD THIS. This is the magic CSS fix!
            }} /> 
        </div>
    );
};

export default ChartWidget;