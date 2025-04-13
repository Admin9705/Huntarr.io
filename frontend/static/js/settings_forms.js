/**
 * Settings forms for Huntarr
 * This file handles generating HTML forms for each app's settings
 */

const SettingsForms = {
    // Generate Sonarr settings form - Updated to use direct app settings without nesting
    generateSonarrForm: function(container, settings = {}) {
        const appSettings = settings.sonarr || {};
        
        container.innerHTML = `
            <div class="settings-group">
                <h3>Sonarr Connection</h3>
                <div class="setting-item">
                    <label for="sonarr_api_url">URL:</label>
                    <input type="text" id="sonarr_api_url" value="${settings.api_url || ''}">
                    <p class="setting-help">Base URL for Sonarr (e.g., http://localhost:8989)</p>
                </div>
                <div class="setting-item">
                    <label for="sonarr_api_key">API Key:</label>
                    <input type="text" id="sonarr_api_key" value="${settings.api_key || ''}">
                    <p class="setting-help">API key for Sonarr</p>
                </div>
                <!-- Removed the connection status indicator -->
            </div>
            
            <div class="settings-group">
                <h3>Search Settings</h3>
                <div class="setting-item">
                    <label for="hunt_missing_shows">Missing Shows to Search:</label>
                    <input type="number" id="hunt_missing_shows" min="0" value="${appSettings.hunt_missing_shows || 1}">
                    <p class="setting-help">Number of missing shows to search per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="hunt_upgrade_episodes">Episodes to Upgrade:</label>
                    <input type="number" id="hunt_upgrade_episodes" min="0" value="${appSettings.hunt_upgrade_episodes || 0}">
                    <p class="setting-help">Number of episodes to search for quality upgrades per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="sleep_duration">Search Interval:</label>
                    <input type="number" id="sleep_duration" min="60" value="${appSettings.sleep_duration || 900}">
                    <p class="setting-help">Time between searches in seconds (<span id="sleep_duration_hours"></span>)</p>
                </div>
                <div class="setting-item">
                    <label for="state_reset_interval_hours">Reset Interval:</label>
                    <input type="number" id="state_reset_interval_hours" min="1" value="${appSettings.state_reset_interval_hours || 168}">
                    <p class="setting-help">Hours between state resets (default: 168 = 7 days)</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Additional Options</h3>
                <div class="setting-item">
                    <label for="monitored_only">Monitored Only:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="monitored_only" ${appSettings.monitored_only !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Only search for monitored items</p>
                </div>
                <div class="setting-item">
                    <label for="skip_future_episodes">Skip Future Releases:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_future_episodes" ${appSettings.skip_future_episodes !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip searching for episodes with future air dates</p>
                </div>
                <div class="setting-item">
                    <label for="skip_series_refresh">Skip Series Refresh:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_series_refresh" ${appSettings.skip_series_refresh === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip refreshing series metadata before searching</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Advanced Settings</h3>
                <div class="setting-item">
                    <label for="random_missing">Random Missing:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="random_missing" ${appSettings.random_missing !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random missing items instead of sequential order</p>
                </div>
                <div class="setting-item">
                    <label for="random_upgrades">Random Upgrades:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="random_upgrades" ${appSettings.random_upgrades !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random items for quality upgrades</p>
                </div>
                <div class="setting-item">
                    <label for="debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="debug_mode" ${appSettings.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable verbose logging for troubleshooting</p>
                </div>
                <div class="setting-item">
                    <label for="api_timeout">API Timeout:</label>
                    <input type="number" id="api_timeout" min="10" max="300" value="${appSettings.api_timeout || 60}">
                    <p class="setting-help">Timeout for API requests in seconds</p>
                </div>
                <div class="setting-item">
                    <label for="command_wait_delay">Command Wait Delay:</label>
                    <input type="number" id="command_wait_delay" min="1" value="${appSettings.command_wait_delay || 1}">
                    <p class="setting-help">Delay between checking command status in seconds</p>
                </div>
                <div class="setting-item">
                    <label for="command_wait_attempts">Command Wait Attempts:</label>
                    <input type="number" id="command_wait_attempts" min="1" value="${appSettings.command_wait_attempts || 600}">
                    <p class="setting-help">Maximum number of status check attempts</p>
                </div>
                <div class="setting-item">
                    <label for="minimum_download_queue_size">Min Download Queue Size:</label>
                    <input type="number" id="minimum_download_queue_size" min="-1" value="${appSettings.minimum_download_queue_size || -1}">
                    <p class="setting-help">Minimum download queue size to pause searching (-1 to disable)</p>
                </div>
            </div>
        `;
    },
    
    // Generate Radarr settings form
    generateRadarrForm: function(container, settings = {}) {
        const appSettings = settings.radarr || {};
        
        container.innerHTML = `
            <div class="settings-group">
                <h3>Radarr Connection</h3>
                <div class="setting-item">
                    <label for="radarr_api_url">URL:</label>
                    <input type="text" id="radarr_api_url" value="${settings.api_url || ''}">
                    <p class="setting-help">Base URL for Radarr (e.g., http://localhost:7878)</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_api_key">API Key:</label>
                    <input type="text" id="radarr_api_key" value="${settings.api_key || ''}">
                    <p class="setting-help">API key for Radarr</p>
                </div>
                <!-- Removed the connection status indicator -->
            </div>
            
            <div class="settings-group">
                <h3>Search Settings</h3>
                <div class="setting-item">
                    <label for="hunt_missing_movies">Missing Movies to Search:</label>
                    <input type="number" id="hunt_missing_movies" min="0" value="${appSettings.hunt_missing_movies || 1}">
                    <p class="setting-help">Number of missing movies to search per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="hunt_upgrade_movies">Movies to Upgrade:</label>
                    <input type="number" id="hunt_upgrade_movies" min="0" value="${appSettings.hunt_upgrade_movies || 0}">
                    <p class="setting-help">Number of movies to search for quality upgrades per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_sleep_duration">Search Interval:</label>
                    <input type="number" id="radarr_sleep_duration" min="60" value="${appSettings.sleep_duration || 900}">
                    <p class="setting-help">Time between searches in seconds (<span id="radarr_sleep_duration_hours"></span>)</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_state_reset_interval_hours">Reset Interval:</label>
                    <input type="number" id="radarr_state_reset_interval_hours" min="1" value="${appSettings.state_reset_interval_hours || 168}">
                    <p class="setting-help">Hours between state resets (default: 168 = 7 days)</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Additional Options</h3>
                <div class="setting-item">
                    <label for="radarr_monitored_only">Monitored Only:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="radarr_monitored_only" ${appSettings.monitored_only !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Only search for monitored items</p>
                </div>
                <div class="setting-item">
                    <label for="skip_future_releases">Skip Future Releases:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_future_releases" ${appSettings.skip_future_releases !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip searching for movies with future release dates</p>
                </div>
                <div class="setting-item">
                    <label for="skip_movie_refresh">Skip Movie Refresh:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_movie_refresh" ${appSettings.skip_movie_refresh === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip refreshing movie metadata before searching</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Advanced Settings</h3>
                <div class="setting-item">
                    <label for="radarr_random_missing">Random Missing:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="radarr_random_missing" ${appSettings.random_missing !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random missing items instead of sequential order</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_random_upgrades">Random Upgrades:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="radarr_random_upgrades" ${appSettings.random_upgrades !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random items for quality upgrades</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="radarr_debug_mode" ${appSettings.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable verbose logging for troubleshooting</p>
                </div>
            </div>
        `;
    },
    
    // Generate Lidarr settings form
    generateLidarrForm: function(container, settings = {}) {
        const appSettings = settings.lidarr || {};
        
        container.innerHTML = `
            <div class="settings-group">
                <h3>Lidarr Connection</h3>
                <div class="setting-item">
                    <label for="lidarr_api_url">URL:</label>
                    <input type="text" id="lidarr_api_url" value="${settings.api_url || ''}">
                    <p class="setting-help">Base URL for Lidarr (e.g., http://localhost:8686)</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_api_key">API Key:</label>
                    <input type="text" id="lidarr_api_key" value="${settings.api_key || ''}">
                    <p class="setting-help">API key for Lidarr</p>
                </div>
                <!-- Removed the connection status indicator -->
            </div>
            
            <div class="settings-group">
                <h3>Search Settings</h3>
                <div class="setting-item">
                    <label for="hunt_missing_albums">Missing Albums to Search:</label>
                    <input type="number" id="hunt_missing_albums" min="0" value="${appSettings.hunt_missing_albums || 1}">
                    <p class="setting-help">Number of missing albums to search per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="hunt_upgrade_tracks">Tracks to Upgrade:</label>
                    <input type="number" id="hunt_upgrade_tracks" min="0" value="${appSettings.hunt_upgrade_tracks || 0}">
                    <p class="setting-help">Number of tracks to search for quality upgrades per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_sleep_duration">Search Interval:</label>
                    <input type="number" id="lidarr_sleep_duration" min="60" value="${appSettings.sleep_duration || 900}">
                    <p class="setting-help">Time between searches in seconds (<span id="lidarr_sleep_duration_hours"></span>)</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_state_reset_interval_hours">Reset Interval:</label>
                    <input type="number" id="lidarr_state_reset_interval_hours" min="1" value="${appSettings.state_reset_interval_hours || 168}">
                    <p class="setting-help">Hours between state resets (default: 168 = 7 days)</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Additional Options</h3>
                <div class="setting-item">
                    <label for="lidarr_monitored_only">Monitored Only:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_monitored_only" ${appSettings.monitored_only !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Only search for monitored items</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_skip_future_releases">Skip Future Releases:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_skip_future_releases" ${appSettings.skip_future_releases !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip searching for albums with future release dates</p>
                </div>
                <div class="setting-item">
                    <label for="skip_artist_refresh">Skip Artist Refresh:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_artist_refresh" ${appSettings.skip_artist_refresh === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip refreshing artist metadata before searching</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Advanced Settings</h3>
                <div class="setting-item">
                    <label for="lidarr_random_missing">Random Missing:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_random_missing" ${appSettings.random_missing !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random missing items instead of sequential order</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_random_upgrades">Random Upgrades:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_random_upgrades" ${appSettings.random_upgrades !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random items for quality upgrades</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_debug_mode" ${appSettings.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable verbose logging for troubleshooting</p>
                </div>
            </div>
        `;
    },
    
    // Generate Readarr settings form
    generateReadarrForm: function(container, settings = {}) {
        const appSettings = settings.readarr || {};
        
        container.innerHTML = `
            <div class="settings-group">
                <h3>Readarr Connection</h3>
                <div class="setting-item">
                    <label for="readarr_api_url">URL:</label>
                    <input type="text" id="readarr_api_url" value="${settings.api_url || ''}">
                    <p class="setting-help">Base URL for Readarr (e.g., http://localhost:8787)</p>
                </div>
                <div class="setting-item">
                    <label for="readarr_api_key">API Key:</label>
                    <input type="text" id="readarr_api_key" value="${settings.api_key || ''}">
                    <p class="setting-help">API key for Readarr</p>
                </div>
                <!-- Removed the connection status indicator -->
            </div>
            
            <div class="settings-group">
                <h3>Search Settings</h3>
                <div class="setting-item">
                    <label for="hunt_missing_books">Missing Books to Search:</label>
                    <input type="number" id="hunt_missing_books" min="0" value="${appSettings.hunt_missing_books || 1}">
                    <p class="setting-help">Number of missing books to search per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="hunt_upgrade_books">Books to Upgrade:</label>
                    <input type="number" id="hunt_upgrade_books" min="0" value="${appSettings.hunt_upgrade_books || 0}">
                    <p class="setting-help">Number of books to search for quality upgrades per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="readarr_sleep_duration">Search Interval:</label>
                    <input type="number" id="readarr_sleep_duration" min="60" value="${appSettings.sleep_duration || 900}">
                    <p class="setting-help">Time between searches in seconds (<span id="readarr_sleep_duration_hours"></span>)</p>
                </div>
                <div class="setting-item">
                    <label for="readarr_state_reset_interval_hours">Reset Interval:</label>
                    <input type="number" id="readarr_state_reset_interval_hours" min="1" value="${appSettings.state_reset_interval_hours || 168}">
                    <p class="setting-help">Hours between state resets (default: 168 = 7 days)</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Additional Options</h3>
                <div class="setting-item">
                    <label for="readarr_monitored_only">Monitored Only:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="readarr_monitored_only" ${appSettings.monitored_only !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Only search for monitored items</p>
                </div>
                <div class="setting-item">
                    <label for="readarr_skip_future_releases">Skip Future Releases:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="readarr_skip_future_releases" ${appSettings.skip_future_releases !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip searching for books with future release dates</p>
                </div>
                <div class="setting-item">
                    <label for="skip_author_refresh">Skip Author Refresh:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_author_refresh" ${appSettings.skip_author_refresh === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip refreshing author metadata before searching</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Advanced Settings</h3>
                <div class="setting-item">
                    <label for="readarr_random_missing">Random Missing:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="readarr_random_missing" ${appSettings.random_missing !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random missing items instead of sequential order</p>
                </div>
                <div class="setting-item">
                    <label for="readarr_random_upgrades">Random Upgrades:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="readarr_random_upgrades" ${appSettings.random_upgrades !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random items for quality upgrades</p>
                </div>
                <div class="setting-item">
                    <label for="readarr_debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="readarr_debug_mode" ${appSettings.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable verbose logging for troubleshooting</p>
                </div>
            </div>
        `;
    },
    
    // Generate Global settings form
    generateGlobalForm: function(container, settings = {}) {
        const globalSettings = settings.global || {};
        
        container.innerHTML = `
            <div class="settings-group">
                <h3>General Settings</h3>
                <div class="setting-item">
                    <label for="debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="debug_mode" ${globalSettings.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable detailed debug logging</p>
                </div>
                <div class="setting-item">
                    <label for="command_wait_delay">Command Wait Delay:</label>
                    <input type="number" id="command_wait_delay" min="1" step="1" value="${globalSettings.command_wait_delay || 1}">
                    <p class="setting-help">Delay in seconds between checking for command status</p>
                </div>
                <div class="setting-item">
                    <label for="command_wait_attempts">Command Wait Attempts:</label>
                    <input type="number" id="command_wait_attempts" min="1" value="${globalSettings.command_wait_attempts || 600}">
                    <p class="setting-help">Maximum number of status check attempts</p>
                </div>
                <div class="setting-item">
                    <label for="minimum_download_queue_size">Min Download Queue Size:</label>
                    <input type="number" id="minimum_download_queue_size" min="-1" value="${globalSettings.minimum_download_queue_size || -1}">
                    <p class="setting-help">Minimum download queue size to pause searching (-1 to disable)</p>
                </div>
            </div>
        `;
    },
    
    // Update duration display - e.g., convert seconds to hours
    updateDurationDisplay: function() {
        // Function to update a specific sleep duration display
        const updateSleepDisplay = function(inputId, spanId) {
            const input = document.getElementById(inputId);
            const span = document.getElementById(spanId);
            if (!input || !span) return;
            
            const seconds = parseInt(input.value);
            if (isNaN(seconds)) return;
            
            const hours = (seconds / 3600).toFixed(1);
            if (hours < 1) {
                const minutes = Math.round(seconds / 60);
                span.textContent = `${minutes} minutes`;
            } else {
                span.textContent = `${hours} hours`;
            }
        };

        // Update for each app
        updateSleepDisplay('sleep_duration', 'sleep_duration_hours');
        updateSleepDisplay('radarr_sleep_duration', 'radarr_sleep_duration_hours');
        updateSleepDisplay('lidarr_sleep_duration', 'lidarr_sleep_duration_hours');
        updateSleepDisplay('readarr_sleep_duration', 'readarr_sleep_duration_hours');
    }
};
