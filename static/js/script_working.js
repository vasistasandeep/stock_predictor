// Enhanced stock list script with filtering
let allStocks = [];
let allStockDetails = [];
let filteredStocks = [];
let allSignals = [];

window.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Stock Predictor initialized');
    fetchStockData();
    fetchAllSignals();
    setupFilters();
});

function fetchStockData() {
    console.log('🔄 Fetching stock data...');
    
    // Get selected data source
    const dataSource = document.getElementById('dataSource')?.value || 'yahoo';
    
    fetch(`/get_top_20_stocks?source=${dataSource}`)
        .then(response => response.json())
        .then(data => {
            console.log('📊 Stock data received:', data);
            allStocks = data.stocks || [];
            allStockDetails = data.stock_details || [];
            filteredStocks = [...allStocks];
            updateStockDisplay(data);
            updateDataSourceStatus(dataSource, data.data_source, data.cache_status);
            showNotification(`✅ Loaded ${allStocks.length} stocks from ${dataSource}`, 'success');
        })
        .catch(error => {
            console.error('❌ Error fetching stocks:', error);
            showNotification(`❌ Failed to load stocks from ${dataSource}`, 'danger');
        });
}

function updateDataSourceStatus(selectedSource, actualSource, cacheStatus) {
    const statusElement = document.getElementById('dataSourceStatus');
    if (!statusElement) return;
    
    let statusIcon = '';
    let statusText = '';
    let statusClass = '';
    
    if (actualSource === 'emergency-fallback' || actualSource === 'error-fallback') {
        statusIcon = '🔴';
        statusText = `${selectedSource} failed - using fallback`;
        statusClass = 'text-danger';
    } else if (cacheStatus === 'fresh') {
        statusIcon = '🟢';
        statusText = `${actualSource} - Fresh data`;
        statusClass = 'text-success';
    } else {
        statusIcon = '🟡';
        statusText = `${actualSource} - Cached data`;
        statusClass = 'text-warning';
    }
    
    statusElement.innerHTML = `<i class="fas fa-circle ${statusClass}"></i> ${statusText}`;
}

function checkDataSources() {
    console.log('🔍 Checking data source availability...');
    
    fetch('/get_data_sources')
        .then(response => response.json())
        .then(data => {
            console.log('📊 Data source status:', data);
            updateDataSourceDropdown(data.sources);
            showNotification('✅ Data source status updated', 'success');
        })
        .catch(error => {
            console.error('❌ Error checking data sources:', error);
            showNotification('❌ Failed to check data sources', 'danger');
        });
}

function updateDataSourceDropdown(sources) {
    const dataSourceSelect = document.getElementById('dataSource');
    if (!dataSourceSelect) return;
    
    // Clear existing options
    dataSourceSelect.innerHTML = '';
    
    // Add options with status indicators
    Object.keys(sources).forEach(sourceKey => {
        const source = sources[sourceKey];
        const option = document.createElement('option');
        option.value = sourceKey;
        
        let icon = '';
        let label = '';
        
        if (sourceKey === 'yahoo') {
            icon = '🌐';
            label = 'Yahoo Finance';
        } else if (sourceKey === 'google') {
            icon = '🔍';
            label = 'Google Finance';
        } else if (sourceKey === 'alpha_vantage') {
            icon = '📊';
            label = 'Alpha Vantage';
        } else if (sourceKey === 'fmp') {
            icon = '🏦';
            label = 'Financial Modeling Prep';
        }
        
        option.textContent = `${icon} ${label}`;
        
        if (source.available) {
            option.classList.add('text-success');
        } else {
            option.classList.add('text-muted');
            option.disabled = true;
        }
        
        dataSourceSelect.appendChild(option);
    });
}

function fetchAllSignals() {
    console.log('🔄 Fetching all signals...');
    
    fetch('/get_all_signals')
        .then(response => response.json())
        .then(data => {
            console.log('📊 Signals received:', data);
            allSignals = data.signals || [];
            updateSignalFilters();
        })
        .catch(error => {
            console.error('❌ Error fetching signals:', error);
        });
}

function setupFilters() {
    console.log('🔧 Setting up event listeners...');
    
    // Signal filter
    document.getElementById('signalFilter')?.addEventListener('change', applyFilters);
    document.getElementById('sectorFilter')?.addEventListener('change', applyFilters);
    document.getElementById('marketCapFilter')?.addEventListener('change', applyFilters);
    
    // Search filter
    document.getElementById('stockSearch')?.addEventListener('input', applyFilters);
    
    // Data source filter
    document.getElementById('dataSource')?.addEventListener('change', function(e) {
        console.log('🔄 Data source changed to:', e.target.value);
        fetchStockData(); // Refresh data with new source
    });
    
    // Apply Filters button
    document.getElementById('applyFilters')?.addEventListener('click', function() {
        console.log('🔍 Applying filters...');
        applyFilters();
        showNotification('✅ Filters applied', 'success');
    });
    
    // Reset Filters button
    document.getElementById('resetFilters')?.addEventListener('click', function() {
        console.log('🔄 Resetting filters...');
        resetFilters();
        showNotification('🔄 Filters reset', 'info');
    });
    
    // Analyze All button
    const analyzeAllBtn = document.getElementById('analyzeAllBtn');
    if (analyzeAllBtn) {
        analyzeAllBtn.addEventListener('click', analyzeAllStocks);
        console.log('✅ Analyze All button listener added');
    } else {
        console.log('❌ Analyze All button not found');
    }
    
    // Refresh Data button
    const refreshDataBtn = document.getElementById('refreshDataBtn');
    if (refreshDataBtn) {
        refreshDataBtn.addEventListener('click', function() {
            console.log('🔄 Refreshing data...');
            fetchStockData();
            showNotification('🔄 Data refreshed', 'success');
        });
        console.log('✅ Refresh Data button listener added');
    } else {
        console.log('❌ Refresh Data button not found');
    }
    
    // Check Sources button
    const checkSourcesBtn = document.getElementById('checkSourcesBtn');
    if (checkSourcesBtn) {
        checkSourcesBtn.addEventListener('click', function() {
            console.log('🔍 Checking data sources...');
            checkDataSources();
        });
        console.log('✅ Check Sources button listener added');
    } else {
        console.log('❌ Check Sources button not found');
    }
    
    // Stock analysis fetch button
    const fetchBtn = document.getElementById('fetchBtn');
    if (fetchBtn) {
        fetchBtn.addEventListener('click', fetchStockDataForTicker);
        console.log('✅ Get Recommendation button listener added');
    } else {
        console.log('❌ Get Recommendation button not found');
    }
    
    // Check data sources on page load
    setTimeout(checkDataSources, 2000);
}

function resetFilters() {
    document.getElementById('signalFilter').value = 'all';
    document.getElementById('riskFilter').value = 'all';
    document.getElementById('sectorFilter').value = 'all';
    document.getElementById('marketCapFilter').value = 'all';
    document.getElementById('sortBy').value = 'marketcap';
    document.getElementById('stockSearch').value = '';
    
    filteredStocks = [...allStocks];
    updateStockDisplay({stock_details: allStockDetails});
}

function applyFilters() {
    const signalFilter = document.getElementById('signalFilter')?.value || 'all';
    const sectorFilter = document.getElementById('sectorFilter')?.value || 'all';
    const marketCapFilter = document.getElementById('marketCapFilter')?.value || 'all';
    const searchTerm = document.getElementById('stockSearch')?.value || '';
    
    filteredStocks = allStocks.filter((stock, index) => {
        const stockDetail = allStockDetails[index];
        if (!stockDetail) return true;
        
        // Search filter
        if (searchTerm) {
            const searchLower = searchTerm.toLowerCase();
            const symbolMatch = stock.toLowerCase().includes(searchLower);
            const nameMatch = stockDetail.name?.toLowerCase().includes(searchLower);
            if (!symbolMatch && !nameMatch) return false;
        }
        
        // Signal filter
        if (signalFilter !== 'all') {
            const signal = allSignals.find(s => s.symbol === stock);
            if (!signal || signal.signal !== signalFilter) return false;
        }
        
        // Sector filter
        if (sectorFilter !== 'all' && stockDetail.sector !== sectorFilter) {
            return false;
        }
        
        // Market cap filter
        if (marketCapFilter !== 'all' && stockDetail.market_cap_category !== marketCapFilter) {
            return false;
        }
        
        return true;
    });
    
    // Update display with filtered results
    updateFilteredDisplay();
    console.log(`🔍 Filtered to ${filteredStocks.length} stocks`);
}

function updateSignalFilters() {
    const signalFilter = document.getElementById('signalFilter');
    if (!signalFilter) return;
    
    // Clear existing options
    signalFilter.innerHTML = '<option value="all">All Signals</option>';
    
    // Add signal options
    if (allSignals && Array.isArray(allSignals)) {
        const signals = [...new Set(allSignals.map(s => s.signal))];
        signals.forEach(signal => {
            const option = document.createElement('option');
            option.value = signal;
            option.textContent = signal;
            signalFilter.appendChild(option);
        });
    }
}

function updateFilteredDisplay() {
    const list = document.getElementById('top20list');
    if (!list) return;
    
    // Clear existing items
    list.innerHTML = '';
    
    // Add filtered stocks
    if (!filteredStocks || !Array.isArray(filteredStocks)) {
        list.innerHTML = '<li class="list-group-item">No stocks available</li>';
        return;
    }
    
    filteredStocks.forEach((stock, index) => {
        const originalIndex = allStocks.indexOf(stock);
        const stockDetail = allStockDetails[originalIndex] || {};
        const signal = allSignals.find(s => s.symbol === stock);
        
        let li = document.createElement('li');
        li.className = 'list-group-item list-group-item-action';
        
        let signalBadge = '';
        if (signal && signal.signal) {
            signalBadge = `<span class="badge bg-${signal.signal_color || 'secondary'} me-2">${signal.signal}</span>`;
        }
        
        let sectorBadge = '';
        if (stockDetail && stockDetail.sector && stockDetail.sector !== 'Unknown') {
            sectorBadge = `<span class="badge bg-info me-2">${stockDetail.sector}</span>`;
        }
        
        let marketCapBadge = '';
        if (stockDetail && stockDetail.market_cap_category && stockDetail.market_cap_category !== 'Unknown') {
            marketCapBadge = `<span class="badge bg-secondary me-2">${stockDetail.market_cap_category}</span>`;
        }
        
        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${stock.replace('.NS', '')}</strong>
                    <small class="text-muted d-block">
                        ${signalBadge}${sectorBadge}${marketCapBadge}NSE
                        ${stockDetail && stockDetail.market_cap_inr_cr ? `• ₹${stockDetail.market_cap_inr_cr.toLocaleString()} cr` : ''}
                    </small>
                </div>
                <div class="text-end">
                    <span class="badge bg-primary">Analyze</span>
                </div>
            </div>
        `;
        
        // Add click event for stock selection
        li.addEventListener('click', function() {
            selectStock(stock, li);
        });
        
        // Add click event for analyze button
        li.querySelector('.badge.bg-primary').addEventListener('click', function(e) {
            e.stopPropagation();
            analyzeStock(stock);
        });
        
        list.appendChild(li);
    });
    
    // Show count
    const countBadge = document.getElementById('stockCount');
    if (countBadge) {
        countBadge.textContent = filteredStocks.length;
    }
}

function updateStockDisplay(data) {
    let list = document.getElementById('top20list');
    if (!list) {
        console.error('❌ Stock list element not found');
        return;
    }
    
    list.innerHTML = '';
    
    // Add timestamp
    if (data.last_updated) {
        let timestampLi = document.createElement('li');
        timestampLi.className = 'list-group-item list-group-item-info';
        timestampLi.innerHTML = `
            <small>
                <strong>📅 Last Updated:</strong> ${data.last_updated}<br>
                <strong>📊 Status:</strong> ${data.is_fresh ? '✅ Fresh' : '⚠️ Stale'}
            </small>
        `;
        list.appendChild(timestampLi);
    }
    
    // Add stocks
    if (filteredStocks && Array.isArray(filteredStocks)) {
        filteredStocks.forEach((stock, index) => {
            let li = document.createElement('li');
            li.className = 'list-group-item list-group-item-action';
            li.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${stock.replace('.NS', '')}</strong>
                        <small class="text-muted d-block">NSE</small>
                    </div>
                    <div class="text-end">
                        <span class="badge bg-secondary">Analyze</span>
                    </div>
                </div>
            `;
            list.appendChild(li);
        });
    } else {
        list.innerHTML = '<li class="list-group-item">No stocks available</li>';
    }
    
    console.log(`✅ Displayed ${filteredStocks.length} stocks`);
}

function selectStock(stock, element) {
    console.log('📊 Stock selected:', stock);
    
    // Remove previous selection
    document.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active-stock');
        item.style.backgroundColor = '';
    });
    
    // Add selection to current element
    element.classList.add('active-stock');
    element.style.backgroundColor = '#e3f2fd';
    
    // Set ticker in input field
    const tickerInput = document.getElementById('tickerInput');
    if (tickerInput) {
        tickerInput.value = stock;
        console.log('📝 Ticker set to:', stock);
    }
    
    // Show notification
    showNotification(`📊 ${stock.replace('.NS', '')} selected for analysis`, 'info');
}

function analyzeStock(stock) {
    console.log('🔄 Analyzing stock:', stock);
    
    // Set ticker and trigger analysis
    const tickerInput = document.getElementById('tickerInput');
    if (tickerInput) {
        tickerInput.value = stock.replace('.NS', ''); // Remove .NS for cleaner display
        console.log('📝 Ticker set to:', tickerInput.value);
    }
    
    // Trigger analysis directly
    showNotification(`🔄 Analyzing ${stock.replace('.NS', '')}...`, 'info');
    fetchStockDataForTicker();
}

function analyzeAllStocks() {
    console.log('🔄 Analyzing all stocks...');
    showNotification('🔄 Analyzing all stocks...', 'info');
    
    // Get the analyze all button
    const analyzeBtn = document.getElementById('analyzeAllBtn');
    if (!analyzeBtn) {
        console.error('❌ Analyze All button not found');
        showNotification('❌ Analyze All button not found', 'danger');
        return;
    }
    
    const originalText = analyzeBtn.innerHTML;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Analyzing...';
    analyzeBtn.disabled = true;
    
    fetch('/get_all_signals')
        .then(response => {
            console.log('📡 Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Analysis complete:', data);
            
            if (!data.status || data.status !== 'success') {
                throw new Error(data.message || 'Analysis failed');
            }
            
            // Update signals
            allSignals = data.signals || [];
            console.log('🔢 Signals received:', allSignals.length);
            
            // Update filters and display
            updateSignalFilters();
            applyFilters();
            
            // Show detailed summary
            const buyCount = allSignals.filter(s => s.signal === 'BUY').length;
            const sellCount = allSignals.filter(s => s.signal === 'SELL').length;
            const holdCount = allSignals.filter(s => s.signal === 'HOLD').length;
            
            console.log(`📈 Signal summary: ${buyCount} BUY, ${sellCount} SELL, ${holdCount} HOLD`);
            
            showNotification(
                `✅ Analysis complete: ${buyCount} BUY, ${sellCount} SELL, ${holdCount} HOLD signals`, 
                'success'
            );
            
            // Reset button
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        })
        .catch(error => {
            console.error('❌ Error analyzing stocks:', error);
            showNotification(`❌ Failed to analyze stocks: ${error.message}`, 'danger');
            
            // Reset button
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        });
}

function fetchStockDataForTicker() {
    console.log('🎯 Get Recommendation button clicked!');
    
    let ticker = document.getElementById('tickerInput').value;
    console.log('📝 Ticker input value:', ticker);
    
    let selectedRiskButton = document.querySelector('input[name="risk"]:checked');
    console.log('⚖️ Selected risk button:', selectedRiskButton ? selectedRiskButton.id : 'None');
    
    // Fix the risk appetite mapping
    let riskAppetite;
    let customStopLoss = null;
    let customExitTarget = null;
    
    if (selectedRiskButton) {
        if (selectedRiskButton.id === 'lowRisk') {
            riskAppetite = 'Low';
        } else if (selectedRiskButton.id === 'mediumRisk') {
            riskAppetite = 'Medium';
        } else if (selectedRiskButton.id === 'highRisk') {
            riskAppetite = 'High';
        } else if (selectedRiskButton.id === 'customRisk') {
            riskAppetite = 'Custom';
            // Get custom values
            let customStopLossInput = document.getElementById('customStopLoss');
            let customExitTargetInput = document.getElementById('customExitTarget');
            customStopLoss = customStopLossInput ? parseFloat(customStopLossInput.value) : 5;
            customExitTarget = customExitTargetInput ? parseFloat(customExitTargetInput.value) : 10;
        } else {
            riskAppetite = 'Medium'; // fallback
        }
    } else {
        riskAppetite = 'Medium'; // default
    }
    
    // Safely get chart filtering options with fallbacks
    let chartPeriod = document.getElementById('chartPeriod') ? document.getElementById('chartPeriod').value : '2y';
    let chartFrequency = document.getElementById('chartFrequency') ? document.getElementById('chartFrequency').value : 'daily';
    let chartType = document.getElementById('chartType') ? document.getElementById('chartType').value : 'line';
    
    console.log('🔍 Analyzing:', ticker, 'Risk:', riskAppetite, 'Period:', chartPeriod, 'Frequency:', chartFrequency, 
                'Custom Stop-Loss:', customStopLoss, 'Custom Exit Target:', customExitTarget);
    
    if (ticker && ticker.trim() !== '') {
        // Store the last analyzed ticker for risk changes
        window.lastAnalyzedTicker = ticker;
        
        // Show loading state
        const fetchBtn = document.getElementById('fetchBtn');
        fetchBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing...';
        fetchBtn.disabled = true;
        
        // Build URL safely with data source
        let url = '/get_stock_data/' + encodeURIComponent(ticker) + '/' + encodeURIComponent(riskAppetite);
        let params = new URLSearchParams();
        params.append('period', chartPeriod);
        params.append('frequency', chartFrequency);
        
        // Add data source parameter
        const dataSource = document.getElementById('dataSource')?.value || 'yahoo';
        params.append('source', dataSource);
        
        // Add custom parameters if custom risk is selected
        if (riskAppetite === 'Custom' && customStopLoss !== null && customExitTarget !== null) {
            params.append('customStopLoss', customStopLoss.toString());
            params.append('customExitTarget', customExitTarget.toString());
        }
        
        console.log('📡 Fetching URL:', url + '?' + params.toString());
        
        fetch(url + '?' + params.toString())
            .then(response => {
                console.log('📡 Response status:', response.status);
                if (!response.ok) {
                    throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                }
                return response.json();
            })
            .then(response => {
                console.log('📊 Response data:', response);
                updatePredictionDisplay(response);
                
                // Reset button
                fetchBtn.innerHTML = '<span>🎯 Get Recommendation</span>';
                fetchBtn.disabled = false;
                
                showNotification(`Analysis complete for ${ticker}`, 'success');
            })
            .catch(error => {
                console.error('❌ Error details:', error);
                showNotification('Error fetching stock data: ' + error.message, 'danger');
                fetchBtn.innerHTML = '<span>🎯 Get Recommendation</span>';
                fetchBtn.disabled = false;
            });
    } else {
        console.log('⚠️ No ticker entered or empty ticker');
        showNotification('Please enter a stock ticker (e.g., RELIANCE, TCS, INFY)', 'warning');
    }
}

function updatePredictionDisplay(response) {
    console.log('📊 Updating prediction display with:', response);
    
    // Update signal
    let signalElement = document.getElementById('signal');
    if (signalElement) {
        signalElement.textContent = response.signal || 'N/A';
        signalElement.className = 'badge';
        if (response.signal === 'Buy') {
            signalElement.classList.add('bg-success');
        } else if (response.signal === 'Sell') {
            signalElement.classList.add('bg-danger');
        } else {
            signalElement.classList.add('bg-warning');
        }
        console.log('✅ Signal updated:', response.signal);
    } else {
        console.error('❌ Signal element not found');
    }
    
    // Update prices with safe checks
    updateElementText('entryPrice', response.entry_price);
    updateElementText('exitPrice', response.exit_price);
    updateElementText('stopLoss', response.stop_loss);
    
    // Update technical indicators with safe checks
    if (response.attributes) {
        updateElementText('sma50', response.attributes.SMA50);
        updateElementText('sma200', response.attributes.SMA200);
        updateElementText('rsi', response.attributes.RSI);
        updateElementText('atr', response.attributes.ATR);
        console.log('✅ Technical indicators updated');
    } else {
        console.error('❌ No attributes in response');
    }
    
    // Update market news and analyst data
    updateMarketInsights(response);
}

function updateMarketInsights(response) {
    console.log('📰 Updating market insights...');
    
    // Update analyst recommendations
    if (response.analyst_recommendations) {
        updateAnalystRecommendations(response.analyst_recommendations);
    }
    
    // Update market news
    if (response.market_news) {
        updateMarketNews(response.market_news);
    }
    
    // Update market sentiment
    if (response.market_sentiment) {
        updateMarketSentiment(response.market_sentiment);
    }
    
    // Update analysis summary
    if (response.analysis_summary) {
        updateAnalysisSummary(response.analysis_summary);
    }
}

function updateAnalystRecommendations(recommendations) {
    const container = document.getElementById('analystRecommendations');
    if (!container) return;
    
    const total = recommendations.total_analysts || 0;
    const strongBuy = recommendations.strong_buy || 0;
    const buy = recommendations.buy || 0;
    const hold = recommendations.hold || 0;
    const sell = recommendations.sell || 0;
    const strongSell = recommendations.strong_sell || 0;
    
    let html = `
        <h6>📊 Analyst Recommendations (${total} analysts)</h6>
        <div class="row mb-2">
            <div class="col-6">
                <div class="progress mb-1" style="height: 20px;">
                    <div class="progress-bar bg-success" style="width: ${total > 0 ? (strongBuy/total)*100 : 0}%">Strong Buy: ${strongBuy}</div>
                </div>
                <div class="progress mb-1" style="height: 20px;">
                    <div class="progress-bar bg-info" style="width: ${total > 0 ? (buy/total)*100 : 0}%">Buy: ${buy}</div>
                </div>
            </div>
            <div class="col-6">
                <div class="progress mb-1" style="height: 20px;">
                    <div class="progress-bar bg-warning" style="width: ${total > 0 ? (hold/total)*100 : 0}%">Hold: ${hold}</div>
                </div>
                <div class="progress mb-1">
                    <div class="progress-bar bg-danger" style="width: ${total > 0 ? (sell/total)*100 : 0}%">Sell: ${sell}</div>
                </div>
            </div>
        </div>
        <small class="text-muted">Source: ${recommendations.source || 'Technical Analysis'}</small>
    `;
    
    container.innerHTML = html;
}

function updateMarketNews(news) {
    const container = document.getElementById('marketNews');
    if (!container) return;
    
    // Handle different news data structures
    let newsArray = [];
    if (news && news.news && Array.isArray(news.news)) {
        // Backend sends {news: [...]}
        newsArray = news.news;
    } else if (news && Array.isArray(news)) {
        // Direct array
        newsArray = news;
    } else if (news && typeof news === 'object') {
        // Single news object or other structure
        newsArray = [news];
    }
    
    if (!newsArray || newsArray.length === 0) {
        container.innerHTML = '<h6>📰 Market News</h6><p class="text-muted">No recent news available.</p>';
        return;
    }
    
    let html = '<h6>📰 Latest Market News</h6>';
    newsArray.forEach(article => {
        const publishDate = article.time_published ? new Date(article.time_published).toLocaleDateString() : 'Recent';
        html += `
            <div class="mb-2 p-2 border rounded">
                <small class="text-muted">${publishDate} - ${article.source || 'Market Data'}</small>
                <h6 class="mb-1"><a href="${article.url || '#'}" target="_blank">${article.title || 'Market Update'}</a></h6>
                <p class="mb-0 small">${article.summary ? article.summary.substring(0, 150) + '...' : 'No summary available.'}</p>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updateMarketSentiment(sentiment) {
    const container = document.getElementById('marketSentiment');
    if (!container) return;
    
    const sentimentClass = sentiment.sentiment === 'POSITIVE' ? 'text-success' : 
                          sentiment.sentiment === 'NEGATIVE' ? 'text-danger' : 'text-warning';
    
    const html = `
        <h6>💭 Market Sentiment</h6>
        <div class="alert alert-secondary">
            <span class="badge ${sentimentClass}">${sentiment.sentiment}</span>
            <p class="mb-0 mt-2">${sentiment.summary}</p>
        </div>
    `;
    
    container.innerHTML = html;
}

function updateAnalysisSummary(summary) {
    const container = document.getElementById('analysisSummary');
    if (!container) return;
    
    const html = `
        <h6>📋 Analysis Summary</h6>
        <div class="alert alert-info">
            <p class="mb-0">${summary}</p>
        </div>
    `;
    
    container.innerHTML = html;
}

// Helper function to safely update element text
function updateElementText(elementId, text) {
    let element = document.getElementById(elementId);
    if (element) {
        element.textContent = text || 'N/A';
        console.log(`✅ ${elementId} updated:`, text);
    } else {
        console.error(`❌ Element ${elementId} not found`);
    }
}

function showNotification(message, type = 'info') {
    let notificationContainer = document.getElementById('notificationContainer');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notificationContainer';
        notificationContainer.className = 'position-fixed top-0 end-0 p-3';
        notificationContainer.style.zIndex = '1050';
        document.body.appendChild(notificationContainer);
    }
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    notificationContainer.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
    
    console.log(`🔔 ${message}`);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded, initializing Stock Predictor...');
    setupFilters();
    fetchTopStocks();
});
