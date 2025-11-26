// Function to populate filter dropdowns with actual data from stocks
function populateFilterDropdowns() {
    console.log('🔧 Populating filter dropdowns...');

    if (!allStockDetails || allStockDetails.length === 0) {
        console.warn('⚠️ No stock details available to populate filters');
        return;
    }

    // Populate Sector Filter
    const sectorFilter = document.getElementById('top20SectorFilter');
    if (sectorFilter) {
        // Get unique sectors from stock details
        const sectors = [...new Set(allStockDetails.map(stock => stock.sector).filter(s => s && s !== 'Unknown'))];
        sectors.sort();

        // Clear and repopulate
        sectorFilter.innerHTML = '<option value="all">All Sectors</option>';
        sectors.forEach(sector => {
            const option = document.createElement('option');
            option.value = sector;
            option.textContent = sector;
            sectorFilter.appendChild(option);
        });

        console.log(`✅ Populated sector filter with ${sectors.length} sectors:`, sectors);
    }

    // Populate Signal Filter (Top 20)
    const signalFilter = document.getElementById('top20SignalFilter');
    if (signalFilter && allSignals && allSignals.length > 0) {
        const signals = [...new Set(allSignals.map(s => s.signal).filter(s => s))];
        signals.sort();

        // Clear and repopulate
        signalFilter.innerHTML = '<option value="all">All Signals</option>';
        signals.forEach(signal => {
            const option = document.createElement('option');
            option.value = signal;
            option.textContent = signal;
            signalFilter.appendChild(option);
        });

        console.log(`✅ Populated signal filter with ${signals.length} signals:`, signals);
    }
}

// Call this after fetching stock data
// Add to fetchStockData() success callback:
// populateFilterDropdowns();

// Also add to fetchAllSignals() success callback:
// populateFilterDropdowns();
