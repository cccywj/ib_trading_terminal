import ChartWidget from './components/ChartWidget';

function App() {
    const params = new URLSearchParams(window.location.search);
    
    // Get symbols and timeframes as arrays
    const symbols = (params.get('symbols') || 'USDJPY,USDJPY').split(',');
    const timeframes = (params.get('timeframes') || '10s,1D').split(',');

    return (
        <div style={{ backgroundColor: '#121212', height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column' }}>
            {symbols.map((symbol, index) => (
                <div key={`${symbol}-${index}`} style={{ 
                    flex: 1, 
                    borderBottom: index < symbols.length - 1 ? '2px solid #333' : 'none' 
                }}>
                    <ChartWidget 
                        symbol={symbol} 
                        initialTimeframe={timeframes[index] || '1m'} 
                    />
                </div>
            ))}
        </div>
    );
}

export default App;