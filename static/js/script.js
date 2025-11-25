window.addEventListener('load', function() {
    fetch('/get_top_20_stocks')
        .then(response => response.json())
        .then(stocks => {
            let list = document.getElementById('top20list');
            stocks.forEach(stock => {
                let li = document.createElement('li');
                li.className = 'list-group-item list-group-item-action';
                li.textContent = stock;
                li.style.cursor = 'pointer';
                li.addEventListener('click', function() {
                    document.getElementById('tickerInput').value = stock;
                    document.getElementById('fetchBtn').click();
                });
                list.appendChild(li);
            });
        });
});

document.getElementById('fetchBtn').addEventListener('click', function() {
    let ticker = document.getElementById('tickerInput').value;
    let riskAppetite = document.querySelector('input[name="risk"]:checked').id.replace('Risk', '');
    if (ticker) {
        fetch('/get_stock_data/' + ticker + '/' + riskAppetite)
            .then(response => response.json())
            .then(response => {
                let signalElement = document.getElementById('signal');
                signalElement.textContent = response.signal;
                if (response.signal === 'Buy') {
                    signalElement.className = 'badge bg-success';
                } else if (response.signal === 'Sell') {
                    signalElement.className = 'badge bg-danger';
                } else {
                    signalElement.className = 'badge bg-secondary';
                }
                document.getElementById('entryPrice').textContent = response.entry_price;
                document.getElementById('exitPrice').textContent = response.exit_price;
                document.getElementById('stopLoss').textContent = response.stop_loss;
                document.getElementById('sma50').textContent = response.attributes.SMA50;
                document.getElementById('sma200').textContent = response.attributes.SMA200;
                document.getElementById('rsi').textContent = response.attributes.RSI;
                document.getElementById('atr').textContent = response.attributes.ATR;
                let chartData = JSON.parse(response.data);
                let dates = Object.keys(chartData.Close).map(ts => new Date(parseInt(ts)).toLocaleDateString());
                let closePrices = Object.values(chartData.Close);
                let sma50 = Object.values(chartData.SMA50);
                let sma200 = Object.values(chartData.SMA200);

                let ctx = document.getElementById('stockChart').getContext('2d');
                if (window.myChart) {
                    window.myChart.destroy();
                }
                window.myChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: dates,
                        datasets: [
                            {
                                label: 'Close Price',
                                data: closePrices,
                                borderColor: 'blue',
                                borderWidth: 1,
                                fill: false
                            },
                            {
                                label: '50-Day SMA',
                                data: sma50,
                                borderColor: 'orange',
                                borderWidth: 1,
                                fill: false
                            },
                            {
                                label: '200-Day SMA',
                                data: sma200,
                                borderColor: 'red',
                                borderWidth: 1,
                                fill: false
                            }
                        ]
                    }
                });
            })
            .catch(error => console.error('Error:', error));
    }
});