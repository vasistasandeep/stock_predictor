let allStocks = [];
let filteredStocks = [];

window.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing application...');
    fetchStockData();
    setupEventListeners();
    setupChartFilters();
    
    // Check if first-time user and show onboarding
    checkFirstTimeUser();
    
    // Test analyze button exists
    let fetchBtn = document.getElementById('fetchBtn');
    if (fetchBtn) {
        console.log('✅ Analyze button found');
        fetchBtn.addEventListener('click', function() {
            console.log('🔍 Analyze button clicked!');
        });
    } else {
        console.error('❌ Analyze button not found');
    }
    
    // Test risk buttons
    let riskButtons = document.querySelectorAll('input[name="risk"]');
    console.log('🎯 Risk buttons found:', riskButtons.length);
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            delay: { show: 300, hide: 100 },
            trigger: 'hover focus'
        });
    });
    console.log('💡 Tooltips initialized:', tooltipList.length);
});

// Onboarding functionality
function checkFirstTimeUser() {
    // Check if user has seen onboarding before
    const hasSeenOnboarding = localStorage.getItem('stockPredictorOnboarding');
    
    if (!hasSeenOnboarding) {
        console.log('🎓 First-time user detected - showing onboarding');
        // Show onboarding modal after a short delay to let page load
        setTimeout(function() {
            const onboardingModal = new bootstrap.Modal(document.getElementById('onboardingModal'));
            onboardingModal.show();
        }, 1000);
    } else {
        console.log('👋 Returning user - skipping onboarding');
    }
}

function finishOnboarding() {
    // Check if "Don't show again" is checked
    const dontShowAgain = document.getElementById('dontShowAgain').checked;
    
    if (dontShowAgain) {
        // Save preference to localStorage
        localStorage.setItem('stockPredictorOnboarding', 'true');
        console.log('✅ User opted out of future onboarding');
    } else {
        console.log('🔄 User may see onboarding again');
    }
    
    // Show welcome notification
    showNotification('🎉 Welcome! Ready to analyze some stocks?', 'success');
}

// Function to show onboarding manually (for help menu)
function showOnboarding() {
    const onboardingModal = new bootstrap.Modal(document.getElementById('onboardingModal'));
    onboardingModal.show();
}

// Function to reset onboarding preference
function resetOnboarding() {
    localStorage.removeItem('stockPredictorOnboarding');
    console.log('🔄 Onboarding preference reset');
    showNotification('Onboarding will show on next page refresh', 'info');
}

function fetchStockData() {
    fetch('/get_top_20_stocks')
        .then(response => response.json())
        .then(data => {
            allStocks = data.stocks || [];
            filteredStocks = [...allStocks];
            updateStockDisplay(data);
            updateStockCount();
        })
        .catch(error => {
            console.error('Error fetching stocks:', error);
            showError('Failed to load stock data');
        });
}

function updateStockDisplay(data) {
    let list = document.getElementById('top20list');
    list.innerHTML = ''; // Clear existing items
    
    // Add timestamp information
    if (data.last_updated) {
        let timestampLi = document.createElement('li');
        timestampLi.className = 'list-group-item list-group-item-info';
        timestampLi.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <small>
                        <strong>📅 Last Updated:</strong> ${data.last_updated}<br>
                        <strong>📊 Status:</strong> ${data.is_fresh ? '✅ Fresh' : '⚠️ Stale'}<br>
                        <strong>⏰ Next Update:</strong> ${data.next_update_in_minutes} minutes
                    </small>
                </div>
                <button class="btn btn-sm btn-outline-primary" onclick="refreshStockData()">
                    🔄 Refresh
                </button>
            </div>
        `;
        list.appendChild(timestampLi);
    }
    
    // Add stocks with enhanced display
    filteredStocks.forEach((stock, index) => {
        let li = document.createElement('li');
        li.className = 'list-group-item list-group-item-action new-stock-item';
        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${stock.replace('.NS', '')}</strong>
                    <small class="text-muted d-block">NSE</small>
                </div>
                <div class="text-end">
                    <span class="badge bg-secondary signal-badge" data-stock="${stock}">
                        <span class="spinner-border spinner-border-sm d-none"></span>
                        <span class="signal-text">Analyze</span>
                    </span>
                </div>
            </div>
        `;
        
        // Add click event for the entire row
        li.addEventListener('click', function(e) {
            if (!e.target.closest('.signal-badge')) {
                selectStock(stock, li);
            }
        });
        
        // Add click event for the signal badge
        let signalBadge = li.querySelector('.signal-badge');
        signalBadge.addEventListener('click', function(e) {
            e.stopPropagation();
            getQuickSignal(stock, signalBadge);
        });
        
        list.appendChild(li);
    });
}

function selectStock(stock, element) {
    // Remove previous selection
    document.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active-stock');
    });
    
    // Add selection to current element
    element.classList.add('active-stock');
    
    // Set ticker and analyze
    document.getElementById('tickerInput').value = stock;
    document.getElementById('fetchBtn').click();
}

function getQuickSignal(stock, badgeElement) {
    // Show loading
    badgeElement.querySelector('.spinner-border').classList.remove('d-none');
    badgeElement.querySelector('.signal-text').textContent = 'Loading...';
    
    // Get signal for this stock
    let riskAppetite = document.querySelector('input[name="risk"]:checked').id.replace('Risk', '');
    
    fetch(`/get_stock_data/${stock}/${riskAppetite}`)
        .then(response => response.json())
        .then(data => {
            updateSignalBadge(badgeElement, data.signal);
        })
        .catch(error => {
            console.error('Error getting signal:', error);
            badgeElement.querySelector('.spinner-border').classList.add('d-none');
            badgeElement.querySelector('.signal-text').textContent = 'Error';
        });
}

function updateSignalBadge(badgeElement, signal) {
    badgeElement.querySelector('.spinner-border').classList.add('d-none');
    badgeElement.querySelector('.signal-text').textContent = signal;
    
    // Update badge color based on signal
    badgeElement.className = 'badge bg-secondary signal-badge';
    if (signal === 'Buy') {
        badgeElement.classList.add('bg-success');
    } else if (signal === 'Sell') {
        badgeElement.classList.add('bg-danger');
    } else {
        badgeElement.classList.add('bg-warning');
    }
}

function setupEventListeners() {
    // Stock search functionality
    document.getElementById('stockSearch').addEventListener('input', function(e) {
        let searchTerm = e.target.value.toLowerCase();
        filteredStocks = allStocks.filter(stock => 
            stock.toLowerCase().includes(searchTerm)
        );
        
        // Update display with filtered results
        let data = {
            stocks: filteredStocks,
            last_updated: document.querySelector('.list-group-item-info')?.innerHTML.includes('Last Updated') ? 
                document.querySelector('.list-group-item-info small strong').nextSibling.textContent.trim() : null
        };
        updateStockDisplay(data);
        updateStockCount();
    });
    
    // Risk filter change event
    document.getElementById('riskFilter').addEventListener('change', function(e) {
        let selectedRisk = e.target.value;
        if (selectedRisk !== 'all') {
            // Update the main risk appetite selector
            let riskRadio = document.getElementById(selectedRisk + 'Risk');
            if (riskRadio) {
                riskRadio.checked = true;
                showNotification(`Risk level changed to ${selectedRisk} risk`, 'info');
            }
        }
    });
    
    // Filter buttons
    document.getElementById('applyFilters').addEventListener('click', applyFilters);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
    
    // Quick action buttons
    document.getElementById('analyzeAllBtn').addEventListener('click', analyzeAllStocks);
    document.getElementById('exportBtn').addEventListener('click', exportCurrentView);
}

function applyFilters() {
    let signalFilter = document.getElementById('signalFilter').value;
    let riskFilter = document.getElementById('riskFilter').value;
    let sectorFilter = document.getElementById('sectorFilter').value;
    let marketCapFilter = document.getElementById('marketCapFilter').value;
    let sortBy = document.getElementById('sortBy').value;
    
    // Apply filters
    filteredStocks = [...allStocks];
    
    // Apply signal filter (if signals have been analyzed)
    if (signalFilter !== 'all') {
        // This would require storing signal data for each stock
        // For now, we'll just show a notification
        showNotification('Signal filter applied (requires stock analysis)', 'info');
    }
    
    // Apply risk filter
    if (riskFilter !== 'all') {
        // Update the main risk selector to match filter
        let riskRadio = document.getElementById(riskFilter + 'Risk');
        if (riskRadio) {
            riskRadio.checked = true;
        }
    }
    
    // Apply sector filter (simplified - would need actual sector data)
    if (sectorFilter !== 'all') {
        showNotification(`Sector filter: ${sectorFilter} (requires sector data)`, 'info');
    }
    
    // Apply market cap filter (simplified - would need actual market cap data)
    if (marketCapFilter !== 'all') {
        showNotification(`Market cap filter: ${marketCapFilter} (requires market cap data)`, 'info');
    }
    
    // Sort stocks
    if (sortBy === 'name') {
        filteredStocks.sort();
    } else if (sortBy === 'marketcap') {
        // Would need actual market cap data
        showNotification('Sorting by market cap (requires market cap data)', 'info');
    } else if (sortBy === 'rsi') {
        // Would need RSI data for all stocks
        showNotification('Sorting by RSI (requires stock analysis)', 'info');
    } else if (sortBy === 'signal') {
        // Would need signal data for all stocks
        showNotification('Sorting by signal strength (requires stock analysis)', 'info');
    }
    
    // Update display
    let data = { stocks: filteredStocks };
    updateStockDisplay(data);
    updateStockCount();
    
    // Show filter applied indicator
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('filter-applied');
    });
    
    showNotification('Filters applied successfully', 'success');
}

function resetFilters() {
    // Reset filter values
    document.getElementById('signalFilter').value = 'all';
    document.getElementById('riskFilter').value = 'all';
    document.getElementById('sectorFilter').value = 'all';
    document.getElementById('marketCapFilter').value = 'all';
    document.getElementById('sortBy').value = 'marketcap';
    document.getElementById('stockSearch').value = '';
    
    // Reset stocks
    filteredStocks = [...allStocks];
    
    // Update display
    fetchStockData();
    
    // Remove filter indicator
    document.querySelectorAll('.card').forEach(card => {
        card.classList.remove('filter-applied');
    });
    
    showNotification('Filters reset successfully', 'success');
}

function analyzeAllStocks() {
    let riskAppetite = document.querySelector('input[name="risk"]:checked').id.replace('Risk', '');
    let stockBadges = document.querySelectorAll('.signal-badge');
    let totalStocks = stockBadges.length;
    let analyzedCount = 0;
    
    if (totalStocks === 0) {
        showNotification('No stocks to analyze', 'warning');
        return;
    }
    
    showNotification(`Analyzing ${totalStocks} stocks with ${riskAppetite} risk...`, 'info');
    
    // Analyze each stock
    stockBadges.forEach((badge, index) => {
        let stock = badge.getAttribute('data-stock');
        if (stock) {
            // Add loading state
            badge.querySelector('.spinner-border').classList.remove('d-none');
            badge.querySelector('.signal-text').textContent = 'Loading...';
            
            // Get signal for this stock
            fetch(`/get_stock_data/${stock}/${riskAppetite}`)
                .then(response => response.json())
                .then(data => {
                    updateSignalBadge(badge, data.signal);
                    analyzedCount++;
                    
                    // Show progress
                    if (analyzedCount === totalStocks) {
                        showNotification(`Analysis complete! ${analyzedCount} stocks analyzed`, 'success');
                    }
                })
                .catch(error => {
                    console.error('Error analyzing stock:', error);
                    badge.querySelector('.spinner-border').classList.add('d-none');
                    badge.querySelector('.signal-text').textContent = 'Error';
                    analyzedCount++;
                });
        }
    });
}

function exportCurrentView() {
    let stockData = [];
    let stockItems = document.querySelectorAll('.list-group-item:not(.list-group-item-info)');
    
    stockItems.forEach(item => {
        let stockName = item.querySelector('strong').textContent;
        let signalBadge = item.querySelector('.signal-badge');
        let signal = signalBadge ? signalBadge.querySelector('.signal-text').textContent : 'Not analyzed';
        
        stockData.push({
            'Stock': stockName,
            'Signal': signal,
            'Risk': document.querySelector('input[name="risk"]:checked').id.replace('Risk', '')
        });
    });
    
    // Convert to CSV
    let csv = 'Stock,Signal,Risk\n';
    stockData.forEach(row => {
        csv += `${row.Stock},${row.Signal},${row.Risk}\n`;
    });
    
    // Download CSV
    let blob = new Blob([csv], { type: 'text/csv' });
    let url = window.URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    a.download = `stock_analysis_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    showNotification('Data exported successfully', 'success');
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    document.querySelectorAll('.notification-toast').forEach(toast => toast.remove());
    
    // Create notification element
    let notification = document.createElement('div');
    notification.className = `notification-toast alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3-5 seconds based on type
    let timeout = type === 'success' ? 3000 : type === 'error' ? 5000 : 4000;
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, timeout);
}

function updateStockCount() {
    document.getElementById('stockCount').textContent = `${filteredStocks.length} stocks`;
}

function showError(message) {
    // Create error alert
    let alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the container
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function refreshStockData() {
    fetch('/refresh_data')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Reload the stocks list
                location.reload();
            } else {
                alert('Error refreshing data: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error refreshing data');
        });
}

document.getElementById('fetchBtn').addEventListener('click', function() {
    let ticker = document.getElementById('tickerInput').value;
    let riskAppetite = document.querySelector('input[name="risk"]:checked').id.replace('Risk', '');
    
    // Safely get chart filtering options with fallbacks
    let chartPeriod = document.getElementById('chartPeriod') ? document.getElementById('chartPeriod').value : '2y';
    let chartFrequency = document.getElementById('chartFrequency') ? document.getElementById('chartFrequency').value : 'daily';
    let chartType = document.getElementById('chartType') ? document.getElementById('chartType').value : 'line';
    
    console.log('Analyzing:', ticker, 'Risk:', riskAppetite, 'Period:', chartPeriod, 'Frequency:', chartFrequency);
    
    if (ticker) {
        // Show loading state
        document.getElementById('fetchBtn').innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing...';
        document.getElementById('fetchBtn').disabled = true;
        
        // Build URL safely
        let url = '/get_stock_data/' + encodeURIComponent(ticker) + '/' + encodeURIComponent(riskAppetite);
        let params = new URLSearchParams();
        params.append('period', chartPeriod);
        params.append('frequency', chartFrequency);
        
        console.log('Fetching URL:', url + '?' + params.toString());
        
        fetch(url + '?' + params.toString())
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                }
                return response.json();
            })
            .then(response => {
                console.log('Response data:', response);
                updatePredictionDisplay(response);
                updateChart(response, chartType);
                
                // Reset button
                document.getElementById('fetchBtn').innerHTML = '<span>🔍 Analyze</span>';
                document.getElementById('fetchBtn').disabled = false;
            })
            .catch(error => {
                console.error('Error details:', error);
                showNotification('Error fetching stock data: ' + error.message, 'error');
                document.getElementById('fetchBtn').innerHTML = '<span>🔍 Analyze</span>';
                document.getElementById('fetchBtn').disabled = false;
            });
    } else {
        showNotification('Please enter a stock ticker (e.g., RELIANCE.NS)', 'warning');
    }
});

function updatePredictionDisplay(response) {
    let signalElement = document.getElementById('signal');
    signalElement.textContent = response.signal;
    if (response.signal === 'Buy') {
        signalElement.className = 'badge bg-success';
    } else if (response.signal === 'Sell') {
        signalElement.className = 'badge bg-danger';
    } else {
        signalElement.className = 'badge bg-warning';
    }
    document.getElementById('entryPrice').textContent = response.entry_price;
    document.getElementById('exitPrice').textContent = response.exit_price;
    document.getElementById('stopLoss').textContent = response.stop_loss;
    document.getElementById('sma50').textContent = response.attributes.SMA50;
    document.getElementById('sma200').textContent = response.attributes.SMA200;
    document.getElementById('rsi').textContent = response.attributes.RSI;
    document.getElementById('atr').textContent = response.attributes.ATR;
}

function updateChart(response, chartType) {
    try {
        console.log('Updating chart with response:', response);
        
        // Store current data for chart type changes
        window.currentChartData = response;
        
        // Check if response has data
        if (!response.data) {
            console.error('No data in response');
            showNotification('No chart data available', 'warning');
            return;
        }
        
        let chartData = JSON.parse(response.data);
        console.log('Parsed chart data:', chartData);
        
        // Check if we have the required data
        if (!chartData.Close || !chartData.SMA50 || !chartData.SMA200) {
            console.error('Missing required chart data fields');
            showNotification('Incomplete chart data received', 'warning');
            return;
        }
        
        let dates = Object.keys(chartData.Close).map(ts => new Date(parseInt(ts)).toLocaleDateString());
        let closePrices = Object.values(chartData.Close);
        let sma50 = Object.values(chartData.SMA50);
        let sma200 = Object.values(chartData.SMA200);
        
        console.log('Data points - Dates:', dates.length, 'Prices:', closePrices.length, 'SMA50:', sma50.length, 'SMA200:', sma200.length);

        let ctx = document.getElementById('stockChart');
        if (!ctx) {
            console.error('Chart canvas not found');
            return;
        }
        
        ctx = ctx.getContext('2d');
        if (window.myChart) {
            window.myChart.destroy();
        }
        
        let datasets = [
            {
                label: '📈 Stock Price',
                data: closePrices,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            },
            {
                label: '📊 50-Day SMA (Short-term Trend)',
                data: sma50,
                borderColor: '#ff9800',
                backgroundColor: 'rgba(255, 152, 0, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            },
            {
                label: '📉 200-Day SMA (Long-term Trend)',
                data: sma200,
                borderColor: '#f44336',
                backgroundColor: 'rgba(244, 67, 54, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            }
        ];

        let chartConfig = {
            type: chartType === 'candlestick' ? 'line' : 'line', // Fallback to line for now
            data: {
                labels: dates,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Stock Price Analysis with Moving Averages',
                        font: {
                            size: 16
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            title: function(context) {
                                return 'Date: ' + context[0].label;
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += '₹' + context.parsed.y.toFixed(2);
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Price (₹)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        };

        window.myChart = new Chart(ctx, chartConfig);
        console.log('Chart updated successfully');
        
    } catch (error) {
        console.error('Error updating chart:', error);
        showNotification('Error updating chart: ' + error.message, 'error');
    }
}

// Chart filter event listeners - safely add only if elements exist
function setupChartFilters() {
    let chartFrequency = document.getElementById('chartFrequency');
    let chartPeriod = document.getElementById('chartPeriod');
    let chartType = document.getElementById('chartType');
    
    if (chartFrequency) {
        chartFrequency.addEventListener('change', function() {
            let ticker = document.getElementById('tickerInput').value;
            if (ticker) {
                console.log('Chart frequency changed to:', this.value);
                document.getElementById('fetchBtn').click();
            }
        });
    }
    
    if (chartPeriod) {
        chartPeriod.addEventListener('change', function() {
            let ticker = document.getElementById('tickerInput').value;
            if (ticker) {
                console.log('Chart period changed to:', this.value);
                document.getElementById('fetchBtn').click();
            }
        });
    }
    
    if (chartType) {
        chartType.addEventListener('change', function() {
            let ticker = document.getElementById('tickerInput').value;
            if (ticker && window.myChart) {
                console.log('Chart type changed to:', this.value);
                let chartType = this.value;
                // Re-render chart with new type if we have data
                if (window.currentChartData) {
                    updateChart(window.currentChartData, chartType);
                } else {
                    // If no current data, re-fetch
                    document.getElementById('fetchBtn').click();
                }
            }
        });
    }
}

// Setup chart filters when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setupChartFilters();
});