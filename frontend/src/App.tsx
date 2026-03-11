import ChartWidget from './components/ChartWidget';

function App() {
    const params = new URLSearchParams(window.location.search);
    const symbol = params.get('symbol') || 'UNKNOWN';

    return (
        <div style={{ backgroundColor: '#121212', height: '100vh', margin: 0 }}>
            <ChartWidget symbol={symbol} />
        </div>
    );
}

export default App;