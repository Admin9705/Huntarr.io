/**
 * Settings form generation for Huntarr apps
 * This file contains functions to generate settings form content for each app
 */

const SettingsForms = {
    // Generate Sonarr settings form
    generateSonarrForm: function(container, settings = {}) {
        const huntarr = settings.huntarr || {};
        const advanced = settings.advanced || {};
        
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
                <div class="setting-item">
                    <button id="testSonarrConnection" class="test-button">
                        <i class="fas fa-plug"></i> Test Connection
                    </button>
                    <span id="sonarrConnectionStatus" class="connection-badge not-connected">Not Configured</span>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Search Settings</h3>
                <div class="setting-item">
                    <label for="hunt_missing_shows">Missing Shows to Search:</label>
                    <input type="number" id="hunt_missing_shows" min="0" value="${huntarr.hunt_missing_shows || 1}">
                    <p class="setting-help">Number of missing shows to search per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="hunt_upgrade_episodes">Episodes to Upgrade:</label>
                    <input type="number" id="hunt_upgrade_episodes" min="0" value="${huntarr.hunt_upgrade_episodes || 0}">
                    <p class="setting-help">Number of episodes to search for quality upgrades per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="sleep_duration">Search Interval:</label>
                    <input type="number" id="sleep_duration" min="60" value="${huntarr.sleep_duration || 900}">
                    <p class="setting-help">Time between searches in seconds (<span id="sleep_duration_hours"></span>)</p>
                </div>
                <div class="setting-item">
                    <label for="state_reset_interval_hours">Reset Interval:</label>
                    <input type="number" id="state_reset_interval_hours" min="1" value="${huntarr.state_reset_interval_hours || 168}">
                    <p class="setting-help">Hours between state resets (default: 168 = 7 days)</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Additional Options</h3>
                <div class="setting-item">
                    <label for="monitored_only">Monitored Only:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="monitored_only" ${huntarr.monitored_only !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Only search for monitored items</p>
                </div>
                <div class="setting-item">
                    <label for="skip_future_episodes">Skip Future Releases:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_future_episodes" ${huntarr.skip_future_episodes !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip searching for episodes with future air dates</p>
                </div>
                <div class="setting-item">
                    <label for="skip_series_refresh">Skip Series Refresh:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_series_refresh" ${huntarr.skip_series_refresh === true ? 'checked' : ''}>
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
                        <input type="checkbox" id="random_missing" ${advanced.random_missing !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random missing items instead of sequential order</p>
                </div>
                <div class="setting-item">
                    <label for="random_upgrades">Random Upgrades:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="random_upgrades" ${advanced.random_upgrades !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random items for quality upgrades</p>
                </div>
                <div class="setting-item">
                    <label for="debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="debug_mode" ${advanced.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable verbose logging for troubleshooting</p>
                </div>
            </div>
        `;
    },
    
    // Generate Radarr settings form
    generateRadarrForm: function(container, settings = {}) {
        const huntarr = settings.huntarr || {};
        const advanced = settings.advanced || {};
        
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
                <div class="setting-item">
                    <button id="testRadarrConnection" class="test-button">
                        <i class="fas fa-plug"></i> Test Connection
                    </button>
                    <span id="radarrConnectionStatus" class="connection-badge not-connected">Not Configured</span>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Search Settings</h3>
                <div class="setting-item">
                    <label for="hunt_missing_movies">Missing Movies to Search:</label>
                    <input type="number" id="hunt_missing_movies" min="0" value="${huntarr.hunt_missing_movies || 1}">
                    <p class="setting-help">Number of missing movies to search per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="hunt_upgrade_movies">Movies to Upgrade:</label>
                    <input type="number" id="hunt_upgrade_movies" min="0" value="${huntarr.hunt_upgrade_movies || 0}">
                    <p class="setting-help">Number of movies to search for quality upgrades per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_sleep_duration">Search Interval:</label>
                    <input type="number" id="radarr_sleep_duration" min="60" value="${huntarr.sleep_duration || 900}">
                    <p class="setting-help">Time between searches in seconds (<span id="radarr_sleep_duration_hours"></span>)</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_state_reset_interval_hours">Reset Interval:</label>
                    <input type="number" id="radarr_state_reset_interval_hours" min="1" value="${huntarr.state_reset_interval_hours || 168}">
                    <p class="setting-help">Hours between state resets (default: 168 = 7 days)</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Additional Options</h3>
                <div class="setting-item">
                    <label for="radarr_monitored_only">Monitored Only:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="radarr_monitored_only" ${huntarr.monitored_only !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Only search for monitored items</p>
                </div>
                <div class="setting-item">
                    <label for="skip_future_releases">Skip Future Releases:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_future_releases" ${huntarr.skip_future_releases !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip searching for movies with future release dates</p>
                </div>
                <div class="setting-item">
                    <label for="skip_movie_refresh">Skip Movie Refresh:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_movie_refresh" ${huntarr.skip_movie_refresh === true ? 'checked' : ''}>
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
                        <input type="checkbox" id="radarr_random_missing" ${advanced.random_missing !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random missing items instead of sequential order</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_random_upgrades">Random Upgrades:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="radarr_random_upgrades" ${advanced.random_upgrades !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random items for quality upgrades</p>
                </div>
                <div class="setting-item">
                    <label for="radarr_debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="radarr_debug_mode" ${advanced.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable verbose logging for troubleshooting</p>
                </div>
            </div>
        `;
    },
    
    // Generate Lidarr settings form
    generateLidarrForm: function(container, settings = {}) {
        const huntarr = settings.huntarr || {};
        const advanced = settings.advanced || {};
        
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
                <div class="setting-item">
                    <button id="testLidarrConnection" class="test-button">
                        <i class="fas fa-plug"></i> Test Connection
                    </button>
                    <span id="lidarrConnectionStatus" class="connection-badge not-connected">Not Configured</span>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Search Settings</h3>
                <div class="setting-item">
                    <label for="hunt_missing_albums">Missing Albums to Search:</label>
                    <input type="number" id="hunt_missing_albums" min="0" value="${huntarr.hunt_missing_albums || 1}">
                    <p class="setting-help">Number of missing albums to search per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="hunt_upgrade_tracks">Tracks to Upgrade:</label>
                    <input type="number" id="hunt_upgrade_tracks" min="0" value="${huntarr.hunt_upgrade_tracks || 0}">
                    <p class="setting-help">Number of tracks to search for quality upgrades per cycle (0 to disable)</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_sleep_duration">Search Interval:</label>
                    <input type="number" id="lidarr_sleep_duration" min="60" value="${huntarr.sleep_duration || 900}">
                    <p class="setting-help">Time between searches in seconds (<span id="lidarr_sleep_duration_hours"></span>)</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_state_reset_interval_hours">Reset Interval:</label>
                    <input type="number" id="lidarr_state_reset_interval_hours" min="1" value="${huntarr.state_reset_interval_hours || 168}">
                    <p class="setting-help">Hours between state resets (default: 168 = 7 days)</p>
                </div>
            </div>
            
            <div class="settings-group">
                <h3>Additional Options</h3>
                <div class="setting-item">
                    <label for="lidarr_monitored_only">Monitored Only:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_monitored_only" ${huntarr.monitored_only !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Only search for monitored items</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_skip_future_releases">Skip Future Releases:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_skip_future_releases" ${huntarr.skip_future_releases !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Skip searching for albums with future release dates</p>
                </div>
                <div class="setting-item">
                    <label for="skip_artist_refresh">Skip Artist Refresh:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="skip_artist_refresh" ${huntarr.skip_artist_refresh === true ? 'checked' : ''}>
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
                        <input type="checkbox" id="lidarr_random_missing" ${advanced.random_missing !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random missing items instead of sequential order</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_random_upgrades">Random Upgrades:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_random_upgrades" ${advanced.random_upgrades !== false ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Select random items for quality upgrades</p>
                </div>
                <div class="setting-item">
                    <label for="lidarr_debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="lidarr_debug_mode" ${advanced.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable verbose logging for troubleshooting</p>
                </div>
            </div>
        `;
    },
    
    // Generate Global settings form
    generateGlobalForm: function(container, settings = {}) {
        const advanced = settings.advanced || {};
        
        container.innerHTML = `
            <div class="settings-group">
                <h3>General Settings</h3>
                <div class="setting-item">
                    <label for="debug_mode">Debug Mode:</label>
                    <label class="toggle-switch">
                        <input type="checkbox" id="debug_mode" ${advanced.debug_mode === true ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                    <p class="setting-help">Enable detailed debug logging</p>
                </div>
                <div class="setting-item">
                    <label for="command_wait_delay">Command Wait Delay:</label>
                    <input type="number" id="command_wait_delay" min="1" step="1" value="${advanced.command_wait_delay || 1}">
                    <p class="setting-help">Delay in seconds between checking for command status</p>
                </div>
                <div class="setting-item">
                    <label for="command_wait_attempts">Command Wait Attempts:</label>
                    <input type="number" id="command_wait_attempts" min="10" step="1" value="${advanced.command_wait_attempts || 600}">
                    <p class="setting-help">Number of attempts to check for command completion</p>
                </div>
                <div class="setting-item">
                    <label for="minimum_download_queue_size">Minimum Queue Size:</label>
                    <input type="number" id="minimum_download_queue_size" min="-1" step="1" value="${advanced.minimum_download_queue_size || -1}">
                    <p class="setting-help">Minimum download queue size before stopping searches</p>
                </div>
            </div>
        `;
    },

    // Helper function to update duration display
    updateDurationDisplay: function() {
        // Update sleep duration displays
        const updateSleepDisplay = (inputId, spanId) => {
            const input = document.getElementById(inputId);
            const span = document.getElementById(spanId);
            if (input && span) {
                const seconds = parseInt(input.value) || 900;
                const hours = (seconds / 3600).toFixed(2);
                span.textContent = `${hours} hours`;
            }
        };

        // Update for each app
        updateSleepDisplay('sleep_duration', 'sleep_duration_hours');
        updateSleepDisplay('radarr_sleep_duration', 'radarr_sleep_duration_hours');
        updateSleepDisplay('lidarr_sleep_duration', 'lidarr_sleep_duration_hours');
    }
};
