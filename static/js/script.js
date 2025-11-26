let allStocks = [];
let filteredStocks = [];

window.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing application...');
    fetchStockData();
    setupEventListeners();
    setupChartFilters();
    setupRiskButtonListeners();
    
    // Check if first-time user and show onboarding
    checkFirstTimeUser();
    
    // Test analyze button exists
    let fetchBtn = document.getElementById('fetchBtn');
    if (fetchBtn) {
        console.log('✅ Analyze button found');
    } else {
        console.error('❌ Analyze button not found');
    }
    
    // Test risk buttons
    let riskButtons = document.querySelectorAll('input[name="risk"]');
    console.log('🎯 Risk buttons found:', riskButtons.length);
    
    // Test chart canvas exists
    let chartCanvas = document.getElementById('stockChart');
    if (chartCanvas) {
        console.log('✅ Chart canvas found');
    } else {
        console.error('❌ Chart canvas not found');
    }
    
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


// Setup risk button listeners to auto-analyze when risk changes
function setupRiskButtonListeners() {
    let riskButtons = document.querySelectorAll('input[name="risk"]');
    let tickerInput = document.getElementById('tickerInput');
    let customRiskInput = document.getElementById('customRiskInput');
    
    riskButtons.forEach(button => {
        button.addEventListener('change', function() {
            // Extract risk appetite correctly - fix the ID mapping
            let riskAppetite;
            if (this.id === 'lowRisk') {
                riskAppetite = 'Low';
            } else if (this.id === 'mediumRisk') {
                riskAppetite = 'Medium';
            } else if (this.id === 'highRisk') {
                riskAppetite = 'High';
            } else if (this.id === 'customRisk') {
                riskAppetite = 'Custom';
            } else {
                riskAppetite = 'Medium'; // fallback
            }
            
            console.log('🔄 Risk changed to:', this.id, 'Risk Appetite:', riskAppetite);
            
            // Show/hide custom risk input
            if (this.id === 'customRisk') {
                customRiskInput.style.display = 'block';
                console.log('⚙️ Custom risk input shown');
            } else {
                customRiskInput.style.display = 'none';
                console.log('🙈 Custom risk input hidden');
            }
            
            // If we have a ticker in the input field, re-analyze with new risk level
            if (tickerInput && tickerInput.value) {
                console.log('🔄 Re-analyzing with new risk level for:', tickerInput.value);
                analyzeStockWithCurrentRisk();
            } else {
                // Just show the selected risk level
                updateRiskSelectionDisplay();
            }
        });
    });
    
    // Add event listeners for custom risk inputs
    let customStopLoss = document.getElementById('customStopLoss');
    let customExitTarget = document.getElementById('customExitTarget');
    
    if (customStopLoss) {
        customStopLoss.addEventListener('input', function() {
            console.log('⚙️ Custom stop-loss changed to:', this.value + '%');
            if (tickerInput && tickerInput.value) {
                analyzeStockWithCurrentRisk();
            }
        });
    }
    
    if (customExitTarget) {
        customExitTarget.addEventListener('input', function() {
            console.log('⚙️ Custom exit target changed to:', this.value + '%');
            if (tickerInput && tickerInput.value) {
                analyzeStockWithCurrentRisk();
            }
        });
    }
}

// Analyze stock with current risk level
function analyzeStockWithCurrentRisk() {
    let ticker = window.lastAnalyzedTicker || document.getElementById('tickerInput').value;
    let selectedRiskButton = document.querySelector('input[name="risk"]:checked');
    
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
    
    console.log('🔄 Re-analyzing:', ticker, 'Risk Appetite:', riskAppetite, 
                'Custom Stop-Loss:', customStopLoss, 'Custom Exit Target:', customExitTarget);
    
    if (ticker) {
        // Get current chart settings
        let chartPeriod = document.getElementById('chartPeriod') ? document.getElementById('chartPeriod').value : '2y';
        let chartFrequency = document.getElementById('chartFrequency') ? document.getElementById('chartFrequency').value : 'daily';
        let chartType = document.getElementById('chartType') ? document.getElementById('chartType').value : 'line';
        
        // Show loading state
        let fetchBtn = document.getElementById('fetchBtn');
        if (fetchBtn) {
            fetchBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Updating...';
            fetchBtn.disabled = true;
        }
        
        // Build URL
        let url = '/get_stock_data/' + encodeURIComponent(ticker) + '/' + encodeURIComponent(riskAppetite);
        let params = new URLSearchParams();
        params.append('period', chartPeriod);
        params.append('frequency', chartFrequency);
        
        // Add custom parameters if custom risk is selected
        if (riskAppetite === 'Custom' && customStopLoss !== null && customExitTarget !== null) {
            params.append('customStopLoss', customStopLoss.toString());
            params.append('customExitTarget', customExitTarget.toString());
        }
        
        console.log('📡 Fetching URL:', url + '?' + params.toString());
        
        fetch(url + '?' + params.toString())
            .then(response => response.json())
            .then(response => {
                console.log('🔄 Updated response:', response);
                updatePredictionDisplay(response);
                updateChart(response, chartType);
                
                // Reset button
                if (fetchBtn) {
                    fetchBtn.innerHTML = '<span>🔍 Analyze</span>';
                    fetchBtn.disabled = false;
                }
                
                showNotification(`Analysis updated with ${riskAppetite} risk level`, 'success');
            })
            .catch(error => {
                console.error('Error re-analyzing:', error);
                showNotification('Error updating analysis: ' + error.message, 'error');
                
                // Reset button
                if (fetchBtn) {
                    fetchBtn.innerHTML = '<span>🔍 Analyze</span>';
                    fetchBtn.disabled = false;
                }
            });
    }
}

// Update risk selection display
function updateRiskSelectionDisplay() {
    let selectedRisk = document.querySelector('input[name="risk"]:checked');
    if (selectedRisk) {
        let riskText = selectedRisk.id.replace('Risk', '');
        console.log('📊 Current risk selection:', riskText);
        showNotification(`Risk level changed to: ${riskText.charAt(0).toUpperCase() + riskText.slice(1)}`, 'info');
    }
}


function fetchStockData() {
    console.log('🔄 Fetching stock data...');
    
    // Show loading state
    let list = document.getElementById('top20list');
    if (list) {
        list.innerHTML = '<li class="list-group-item text-center"><div class="spinner-border spinner-border-sm me-2"></div> Loading stocks...</li>';
    }
    
    fetch('/get_top_20_stocks')
        .then(response => {
            console.log('📡 API response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Stock data received:', data);
            console.log('📈 Number of stocks:', data.stocks ? data.stocks.length : 0);
            
            allStocks = data.stocks || [];
            filteredStocks = [...allStocks];
            
            // Update display
            updateStockDisplay(data);
            updateStockCount();
            
            // Show success message
            if (allStocks.length > 0) {
                showNotification(`✅ Loaded ${allStocks.length} stocks successfully`, 'success');
            } else {
                showNotification('⚠️ No stocks loaded', 'warning');
            }
        })
        .catch(error => {
            console.error('❌ Error fetching stocks:', error);
            showError('Failed to load stock data: ' + error.message);
            
            // Show error in list
            if (list) {
                list.innerHTML = `
                    <li class="list-group-item list-group-item-danger">
                        <div class="text-center">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <strong>Error loading stocks</strong><br>
                            <small>${error.message}</small><br>
                            <button class="btn btn-sm btn-outline-danger mt-2" onclick="fetchStockData()">
                                🔄 Retry
                            </button>
                        </div>
                    </li>
                `;
            }
        });
}

function updateStockDisplay(data) {
    let list = document.getElementById('top20list');
    if (!list) {
        console.error('❌ Stock list element not found');
        return;
    }
    
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
    
    console.log('🎯 Displaying stocks:', filteredStocks.length);
    
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
    
    // If no stocks are displayed, show a fallback
    if (filteredStocks.length === 0) {
        console.log('⚠️ No stocks to display, showing fallback');
        let fallbackLi = document.createElement('li');
        fallbackLi.className = 'list-group-item list-group-item-warning';
        fallbackLi.innerHTML = `
            <div class="text-center">
                <i class="fas fa-info-circle me-2"></i>
                <strong>No stocks available</strong><br>
                <small>Trying to load stock data...</small><br>
                <button class="btn btn-sm btn-outline-warning mt-2" onclick="fetchStockData()">
                    🔄 Reload Stocks
                </button>
            </div>
        `;
        list.appendChild(fallbackLi);
    }
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
    
    console.log('🔍 Applying filters:', {
        signal: signalFilter,
        risk: riskFilter,
        sector: sectorFilter,
        marketCap: marketCapFilter,
        sort: sortBy
    });
    
    // Apply filters
    filteredStocks = [...allStocks];
    
    // Apply signal filter (if signals have been analyzed)
    if (signalFilter !== 'all') {
        // For now, just filter by stock name patterns as a demo
        if (signalFilter === 'buy') {
            // Filter stocks that might be good buys (simplified)
            filteredStocks = filteredStocks.filter(stock => 
                stock.includes('INFY') || stock.includes('TCS') || stock.includes('HDFC')
            );
        } else if (signalFilter === 'sell') {
            // Filter stocks that might be sells (simplified)
            filteredStocks = filteredStocks.filter(stock => 
                !stock.includes('INFY') && !stock.includes('TCS') && !stock.includes('HDFC')
            );
        }
    }
    
    // Apply risk filter - update the main risk selector
    if (riskFilter !== 'all') {
        let riskRadio = document.getElementById(riskFilter + 'Risk');
        if (riskRadio) {
            riskRadio.checked = true;
            console.log('✅ Risk filter applied:', riskFilter);
        }
    }
    
    // Apply sector filter (simplified demo)
    if (sectorFilter !== 'all') {
        let sectorKeywords = {
            'tech': ['INFY', 'TCS', 'WIPRO', 'HCLTECH'],
            'banking': ['HDFC', 'ICICI', 'KOTAK', 'SBIN'],
            'fmcg': ['HINDUNILVR', 'ITC', 'NESTLEIND'],
            'pharma': ['SUNPHARMA', 'DRREDDY', 'CIPLA'],
            'auto': ['TATAMOTORS', 'MARUTI', 'M&M']
        };
        
        let keywords = sectorKeywords[sectorFilter] || [];
        if (keywords.length > 0) {
            filteredStocks = filteredStocks.filter(stock => 
                keywords.some(keyword => stock.includes(keyword))
            );
            console.log('✅ Sector filter applied:', sectorFilter, 'Keywords:', keywords);
        }
    }
    
    // Apply market cap filter (simplified demo)
    if (marketCapFilter !== 'all') {
        // Simple demo - filter by stock name patterns
        if (marketCapFilter === 'large') {
            // Large cap - well-known companies
            filteredStocks = filteredStocks.filter(stock => 
                stock.includes('RELIANCE') || stock.includes('TCS') || 
                stock.includes('HDFC') || stock.includes('INFY')
            );
        } else if (marketCapFilter === 'small') {
            // Small cap - exclude large caps
            filteredStocks = filteredStocks.filter(stock => 
                !stock.includes('RELIANCE') && !stock.includes('TCS') && 
                !stock.includes('HDFC') && !stock.includes('INFY')
            );
        }
        console.log('✅ Market cap filter applied:', marketCapFilter);
    }
    
    // Sort stocks
    if (sortBy === 'name') {
        filteredStocks.sort();
        console.log('✅ Sorted by name');
    } else if (sortBy === 'marketcap') {
        // Simple reverse sort for demo (assuming longer names = larger caps)
        filteredStocks.sort((a, b) => b.length - a.length);
        console.log('✅ Sorted by market cap (demo)');
    } else if (sortBy === 'rsi') {
        // For demo, just randomize
        filteredStocks.sort(() => Math.random() - 0.5);
        console.log('✅ Sorted by RSI (demo)');
    } else if (sortBy === 'signal') {
        // For demo, put certain stocks first
        let priorityStocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS'];
        filteredStocks.sort((a, b) => {
            let aPriority = priorityStocks.includes(a) ? 0 : 1;
            let bPriority = priorityStocks.includes(b) ? 0 : 1;
            return aPriority - bPriority;
        });
        console.log('✅ Sorted by signal (demo)');
    }
    
    // Update the display
    updateStockDisplay({ stocks: filteredStocks });
    showNotification(`Filters applied: ${filteredStocks.length} stocks found`, 'success');
    console.log('✅ Filters applied successfully, found:', filteredStocks.length, 'stocks');
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
    let selectedRiskButton = document.querySelector('input[name="risk"]:checked');
    
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
    
    if (ticker) {
        // Store the last analyzed ticker for risk changes
        window.lastAnalyzedTicker = ticker;
        
        // Show loading state
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing...';
        this.disabled = true;
        
        // Build URL safely
        let url = '/get_stock_data/' + encodeURIComponent(ticker) + '/' + encodeURIComponent(riskAppetite);
        let params = new URLSearchParams();
        params.append('period', chartPeriod);
        params.append('frequency', chartFrequency);
        
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
                updateChart(response, chartType);
                
                // Reset button
                this.innerHTML = '<span>🔍 Analyze</span>';
                this.disabled = false;
                
                showNotification(`Analysis complete for ${ticker}`, 'success');
            })
            .catch(error => {
                console.error('❌ Error details:', error);
                showNotification('Error fetching stock data: ' + error.message, 'error');
                this.innerHTML = '<span>🔍 Analyze</span>';
                this.disabled = false;
            });
    } else {
        showNotification('Please enter a stock ticker (e.g., RELIANCE.NS)', 'warning');
    }
});

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
}

// Helper function to safely update element text
function updateElementText(elementId, text) {
    let element = document.getElementById(elementId);
    if (element) {
        element.textContent = text || 'N/A';
        console.log(`✅ ${elementId} updated:`, text);
    } else {
        console.error(`❌ Element not found: ${elementId}`);
    }
}

function updateChart(response, chartType) {
    try {
        console.log('📈 Updating chart with response:', response);
        
        // Store current data for chart type changes
        window.currentChartData = response;
        
        // Check if response has data
        if (!response.data) {
            console.error('❌ No data in response');
            showNotification('No chart data available', 'warning');
            return;
        }
        
        let chartData;
        try {
            chartData = JSON.parse(response.data);
        } catch (parseError) {
            console.error('❌ Error parsing chart data:', parseError);
            showNotification('Error parsing chart data', 'error');
            return;
        }
        
        console.log('📊 Parsed chart data keys:', Object.keys(chartData));
        
        // Check if we have the required data
        if (!chartData.Close) {
            console.error('❌ Missing Close price data');
            showNotification('Missing price data in response', 'warning');
            return;
        }
        
        let dates = Object.keys(chartData.Close).map(ts => new Date(parseInt(ts)).toLocaleDateString());
        let closePrices = Object.values(chartData.Close);
        let sma50 = chartData.SMA50 ? Object.values(chartData.SMA50) : [];
        let sma200 = chartData.SMA200 ? Object.values(chartData.SMA200) : [];
        
        console.log('📊 Data points - Dates:', dates.length, 'Prices:', closePrices.length, 'SMA50:', sma50.length, 'SMA200:', sma200.length);

        let ctx = document.getElementById('stockChart');
        if (!ctx) {
            console.error('❌ Chart canvas not found');
            showNotification('Chart element not found', 'error');
            return;
        }
        
        // Get 2D context
        let canvasContext = ctx.getContext('2d');
        if (!canvasContext) {
            console.error('❌ Could not get canvas context');
            return;
        }
        
        // Destroy existing chart if it exists
        if (window.myChart) {
            window.myChart.destroy();
            console.log('🔄 Previous chart destroyed');
        }
        
        // Build datasets dynamically based on available data
        let datasets = [
            {
                label: '📈 Stock Price',
                data: closePrices,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            }
        ];
        
        // Add SMA50 if available
        if (sma50.length > 0) {
            datasets.push({
                label: '📊 50-Day SMA (Short-term Trend)',
                data: sma50,
                borderColor: '#ff9800',
                backgroundColor: 'rgba(255, 152, 0, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            });
        }
        
        // Add SMA200 if available
        if (sma200.length > 0) {
            datasets.push({
                label: '📉 200-Day SMA (Long-term Trend)',
                data: sma200,
                borderColor: '#f44336',
                backgroundColor: 'rgba(244, 67, 54, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1
            });
        }

        let chartConfig = {
            type: chartType === 'candlestick' ? 'line' : (chartType || 'line'), // Fallback to line
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
                            size: 16,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            color: '#333',
                            font: {
                                color: '#333'
                            }
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#ddd',
                        borderWidth: 1,
                        callbacks: {
                            title: function(context) {
                                return '📅 Date: ' + context[0].label;
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += '₹' + context.parsed.y.toFixed(2);
                                }
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
                            text: '📅 Date',
                            font: {
                                weight: 'bold',
                                color: '#333'
                            },
                            color: '#333'
                        },
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#333',
                            font: {
                                color: '#333'
                            }
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: '💰 Price (₹)',
                            font: {
                                weight: 'bold',
                                color: '#333'
                            },
                            color: '#333'
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toFixed(0);
                            },
                            color: '#333',
                            font: {
                                color: '#333'
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        };

        // Create new chart
        window.myChart = new Chart(canvasContext, chartConfig);
        console.log('✅ Chart updated successfully with', datasets.length, 'datasets');
        showNotification('Chart updated successfully', 'success');
        
    } catch (error) {
        console.error('❌ Error updating chart:', error);
        showNotification('Error updating chart: ' + error.message, 'error');
    }
}

// Chart filter event listeners - safely add only if elements exist
function setupChartFilters() {
    let chartFrequency = document.getElementById('chartFrequency');
    let chartPeriod = document.getElementById('chartPeriod');
    let chartType = document.getElementById('chartType');
    
    console.log('🔍 Setting up chart filters...');
    console.log('📊 chartFrequency found:', !!chartFrequency);
    console.log('📊 chartPeriod found:', !!chartPeriod);
    console.log('📊 chartType found:', !!chartType);
    
    if (chartFrequency) {
        chartFrequency.addEventListener('change', function() {
            let ticker = document.getElementById('tickerInput').value;
            if (ticker) {
                console.log('📊 Chart frequency changed to:', this.value);
                showNotification(`Updating chart frequency to ${this.value}...`, 'info');
                document.getElementById('fetchBtn').click();
            } else {
                showNotification('Please select a stock first', 'warning');
            }
        });
    } else {
        console.error('❌ chartFrequency element not found');
    }
    
    if (chartPeriod) {
        chartPeriod.addEventListener('change', function() {
            let ticker = document.getElementById('tickerInput').value;
            if (ticker) {
                console.log('📊 Chart period changed to:', this.value);
                showNotification(`Updating chart period to ${this.value}...`, 'info');
                document.getElementById('fetchBtn').click();
            } else {
                showNotification('Please select a stock first', 'warning');
            }
        });
    } else {
        console.error('❌ chartPeriod element not found');
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

// Function to select and analyze a stock
function selectStock(stock, listItem) {
    console.log('📊 Stock selected:', stock);
    
    // Update the input field
    let tickerInput = document.getElementById('tickerInput');
    if (tickerInput) {
        tickerInput.value = stock;
        
        // Add visual feedback
        tickerInput.classList.add('border-success');
        setTimeout(() => {
            tickerInput.classList.remove('border-success');
        }, 1000);
        
        // Highlight selected stock in list
        document.querySelectorAll('.list-group-item').forEach(item => {
            item.classList.remove('active-stock');
        });
        if (listItem) {
            listItem.classList.add('active-stock');
        }
        
        // Trigger analysis
        let fetchBtn = document.getElementById('fetchBtn');
        if (fetchBtn) {
            fetchBtn.click();
        }
        
        showNotification(`Analyzing ${stock}...`, 'info');
    } else {
        console.error('❌ Ticker input not found');
    }
}

// Function to toggle chart visibility
function toggleChart() {
    let showChart = document.getElementById('showChart');
    let chartContainer = document.getElementById('chartContainer');
    
    if (showChart.checked) {
        chartContainer.style.display = 'block';
        console.log('📈 Chart shown');
        showNotification('Chart enabled - for advanced users', 'info');
    } else {
        chartContainer.style.display = 'none';
        console.log('🙈 Chart hidden');
        showNotification('Chart hidden - keeping it simple', 'info');
    }
}

// Setup chart filters when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setupChartFilters();
});

// Additional utility functions for stock display
function refreshStockData() {
    console.log('🔄 Manual refresh triggered');
    showNotification('🔄 Refreshing stock data...', 'info');
    fetchStockData();
}

function showError(message) {
    console.error('❌ Error:', message);
    showNotification(message, 'danger');
}

function showNotification(message, type = 'info') {
    // Create or update notification container
    let notificationContainer = document.getElementById('notificationContainer');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notificationContainer';
        notificationContainer.className = 'position-fixed top-0 end-0 p-3';
        notificationContainer.style.zIndex = '1050';
        document.body.appendChild(notificationContainer);
    }
    
    // Create notification element
    const notificationId = 'notification-' + Date.now();
    const notification = document.createElement('div');
    notification.id = notificationId;
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const element = document.getElementById(notificationId);
        if (element) {
            element.remove();
        }
    }, 5000);
    
    console.log(`🔔 Notification shown: ${message}`);
}