/**
 * Huntarr - Statistics Tooltips
 * Provides detailed tooltip information for dashboard statistics
 */

document.addEventListener('DOMContentLoaded', function() {
    // Create tooltip container
    const tooltipContainer = document.createElement('div');
    tooltipContainer.id = 'stats-tooltip';
    tooltipContainer.className = 'stats-tooltip';
    document.body.appendChild(tooltipContainer);
    
    // Add tooltip styles
    const tooltipStyles = document.createElement('style');
    tooltipStyles.id = 'stats-tooltip-styles';
    tooltipStyles.textContent = `
        .stats-tooltip {
            position: absolute;
            display: none;
            background: rgba(20, 27, 38, 0.95);
            color: #fff;
            border-radius: 8px;
            padding: 12px 15px;
            font-size: 13px;
            z-index: 1000;
            max-width: 280px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(85, 97, 215, 0.3);
            opacity: 0;
            transition: opacity 0.2s ease-in-out;
            animation: tooltip-glow 2s infinite alternate;
            pointer-events: none;
        }
        
        @keyframes tooltip-glow {
            from { box-shadow: 0 0 8px rgba(85, 97, 215, 0.4); }
            to { box-shadow: 0 0 15px rgba(85, 97, 215, 0.8); }
        }
        
        .stats-tooltip h4 {
            margin: 0 0 8px 0;
            font-size: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
            padding-bottom: 6px;
        }
        
        .stats-tooltip .tooltip-row {
            display: flex;
            justify-content: space-between;
            margin: 6px 0;
        }
        
        .stats-tooltip .tooltip-label {
            color: #a7c7fd;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .stats-tooltip .tooltip-description {
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .stats-tooltip .tooltip-date {
            font-size: 11px;
            margin-top: 10px;
            color: rgba(255, 255, 255, 0.6);
            text-align: right;
        }
        
        .stat-number {
            cursor: pointer;
            transition: color 0.2s;
        }
        
        .stat-number:hover {
            color: #a7c7fd;
        }
    `;
    document.head.appendChild(tooltipStyles);
    
    // Initialize tooltips on all stat numbers
    initStatsTooltips();
});

/**
 * Format large numbers with appropriate suffixes (K, MIL, BIL, TRI)
 * @param {number} num - Number to format
 * @returns {string} Formatted number string
 */
function formatLargeNumber(num) {
    if (num < 1000) {
        // 0-999: Display as is
        return num.toString();
    } else if (num < 10000) {
        // 1,000-9,999: Display with single decimal and K (e.g., 5.2K)
        return (num / 1000).toFixed(1) + 'K';
    } else if (num < 100000) {
        // 10,000-99,999: Display with single decimal and K (e.g., 75.4K)
        return (num / 1000).toFixed(1) + 'K';
    } else if (num < 1000000) {
        // 100,000-999,999: Display with K (no decimal) (e.g., 982K)
        return Math.floor(num / 1000) + 'K';
    } else if (num < 10000000) {
        // 1M-9.9M: Display with single decimal and MIL (e.g., 2.4 MIL)
        return (num / 1000000).toFixed(1) + ' MIL';
    } else if (num < 1000000000) {
        // 10M-999M: Display with MIL (no decimal) (e.g., 234 MIL)
        return Math.floor(num / 1000000) + ' MIL';
    } else if (num < 1000000000000) {
        // 1B-999B: Display with BIL (e.g., 4.5 BIL)
        return (num / 1000000000).toFixed(1) + ' BIL';
    } else {
        // 1T+: Display with TRI
        return (num / 1000000000000).toFixed(1) + ' TRI';
    }
}

/**
 * Initialize tooltips on all stat number elements
 */
function initStatsTooltips() {
    // Add event listeners to statistics numbers
    const apps = ['sonarr', 'radarr', 'lidarr', 'readarr', 'whisparr', 'eros', 'swaparr'];
    const statTypes = ['hunted', 'upgraded'];
    
    apps.forEach(app => {
        statTypes.forEach(type => {
            const element = document.getElementById(`${app}-${type}`);
            if (element) {
                // Add data attributes for tooltip use
                element.setAttribute('data-app', app);
                element.setAttribute('data-type', type);
                
                // Add hover events
                element.addEventListener('mouseenter', showStatsTooltip);
                element.addEventListener('mouseleave', hideStatsTooltip);
                element.addEventListener('mousemove', moveStatsTooltip);
            }
        });
    });
}

/**
 * Show tooltip with detailed statistics
 * @param {MouseEvent} e - Mouse event
 */
function showStatsTooltip(e) {
    const tooltip = document.getElementById('stats-tooltip');
    if (!tooltip) return;
    
    const target = e.currentTarget;
    const app = target.getAttribute('data-app');
    const type = target.getAttribute('data-type');
    const rawValue = parseInt(target.textContent.replace(/[^0-9]/g, '') || '0');
    
    // App-specific details with proper color coding
    const appDetails = {
        'sonarr': { name: 'Sonarr', color: '#3498db', description: type === 'hunted' ? 'Episode searches triggered' : 'Episodes upgraded to better quality' },
        'radarr': { name: 'Radarr', color: '#f39c12', description: type === 'hunted' ? 'Movie searches triggered' : 'Movies upgraded to better quality' },
        'lidarr': { name: 'Lidarr', color: '#2ecc71', description: type === 'hunted' ? 'Album searches triggered' : 'Albums upgraded to better quality' },
        'readarr': { name: 'Readarr', color: '#e74c3c', description: type === 'hunted' ? 'Book searches triggered' : 'Books upgraded to better quality' },
        'whisparr': { name: 'Whisparr', color: '#9b59b6', description: type === 'hunted' ? 'Adult video searches triggered' : 'Adult videos upgraded to better quality' },
        'eros': { name: 'Eros', color: '#1abc9c', description: type === 'hunted' ? 'Audio searches triggered' : 'Audio files upgraded to better quality' },
        'swaparr': { name: 'Swaparr', color: '#e67e22', description: type === 'hunted' ? 'Content swap operations' : 'Content swap upgrades' }
    };
    
    const detail = appDetails[app] || { name: app, color: '#95a5a6', description: type === 'hunted' ? 'Searches triggered' : 'Content upgraded' };
    
    // Calculate averages
    const now = new Date();
    const startDate = localStorage.getItem('huntarr-stats-start-date') || 
                     new Date(now.getTime() - (30 * 24 * 60 * 60 * 1000)).toISOString(); // Default to 30 days ago
    
    const startTime = new Date(startDate);
    const daysDiff = Math.max(1, Math.floor((now - startTime) / (1000 * 60 * 60 * 24)));
    
    const dailyAvg = (rawValue / daysDiff).toFixed(1);
    const weeklyAvg = (rawValue / daysDiff * 7).toFixed(1);
    const monthlyAvg = (rawValue / daysDiff * 30).toFixed(1);
    
    // Build tooltip content
    tooltip.innerHTML = `
        <h4 style="color: ${detail.color}">${detail.name} ${type === 'hunted' ? 'Searches' : 'Upgrades'}</h4>
        <div class="tooltip-description">${detail.description}</div>
        
        <div class="tooltip-row">
            <span class="tooltip-label">Total count:</span>
            <span class="tooltip-value">${formatLargeNumber(rawValue)}</span>
        </div>
        
        <div class="tooltip-row">
            <span class="tooltip-label">Daily average:</span>
            <span class="tooltip-value">${dailyAvg}</span>
        </div>
        
        <div class="tooltip-row">
            <span class="tooltip-label">Weekly average:</span>
            <span class="tooltip-value">${weeklyAvg}</span>
        </div>
        
        <div class="tooltip-row">
            <span class="tooltip-label">Monthly average:</span>
            <span class="tooltip-value">${monthlyAvg}</span>
        </div>
        
        <div class="tooltip-date">
            Stats collected since: ${startTime.toLocaleDateString()}
        </div>
    `;
    
    // Position tooltip initially
    moveStatsTooltip(e);
    
    // Show tooltip
    tooltip.style.display = 'block';
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
}

/**
 * Hide tooltip
 */
function hideStatsTooltip() {
    const tooltip = document.getElementById('stats-tooltip');
    if (tooltip) {
        tooltip.style.opacity = '0';
        setTimeout(() => {
            tooltip.style.display = 'none';
        }, 200);
    }
}

/**
 * Move tooltip to follow cursor
 * @param {MouseEvent} e - Mouse event
 */
function moveStatsTooltip(e) {
    const tooltip = document.getElementById('stats-tooltip');
    if (!tooltip) return;
    
    // Get cursor position and tooltip dimensions
    const offsetX = 15;
    const offsetY = 10;
    const tooltipWidth = tooltip.offsetWidth;
    const tooltipHeight = tooltip.offsetHeight;
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    
    // Calculate position with smart boundary detection
    let posX = e.clientX + offsetX;
    let posY = e.clientY + offsetY;
    
    // Keep tooltip within viewport bounds
    if (posX + tooltipWidth > windowWidth - 10) {
        posX = e.clientX - tooltipWidth - offsetX;
    }
    
    if (posY + tooltipHeight > windowHeight - 10) {
        posY = e.clientY - tooltipHeight - offsetY;
    }
    
    // Set tooltip position
    tooltip.style.left = `${posX}px`;
    tooltip.style.top = `${posY}px`;
}

// Reset stats recording date when resetting statistics
document.addEventListener('click', function(e) {
    if (e.target.id === 'reset-stats') {
        localStorage.setItem('huntarr-stats-start-date', new Date().toISOString());
    }
});
