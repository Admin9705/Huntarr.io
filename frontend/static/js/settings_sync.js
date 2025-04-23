/**
 * Settings synchronization utilities for Huntarr
 * Ensures all JS modules are updated when settings are saved
 */

// Event to notify system of settings changes
document.addEventListener('DOMContentLoaded', function() {
    // Create a custom event system for settings changes
    window.HuntarrEvents = window.HuntarrEvents || {
        // Dispatch a settings changed event
        dispatchSettingsChanged: function(app) {
            const event = new CustomEvent('huntarr:settings-changed', { 
                detail: { app: app }
            });
            document.dispatchEvent(event);
        },
        
        // Add a listener for settings changes
        onSettingsChanged: function(callback) {
            document.addEventListener('huntarr:settings-changed', callback);
        }
    };
    
    // Listen for clicks on save buttons and trigger proper reload
    // const saveButtons = document.querySelectorAll('.save-button, [id^="saveSettings"]');
    // saveButtons.forEach(button => {
    //     button.addEventListener('click', function() {
    //         // Determine which app's settings are being saved
    //         let app = 'global'; 
    //         const activeSettingsTab = document.querySelector('.settings-tab.active');
    //         if (activeSettingsTab) {
    //             app = activeSettingsTab.getAttribute('data-settings') || 'global';
    //         }
            
    //         // Dispatch the event after a short delay to allow save operation to potentially complete
    //         setTimeout(() => {
    //             console.log(`Settings sync: Dispatching settings-changed for ${app}`);
    //             window.HuntarrEvents.dispatchSettingsChanged(app);
    //         }, 100); // Delay to ensure save logic runs first
    //     });
    // });
});

// Helper to parse numeric values consistently
function parseNumericSetting(value, defaultValue = 0) {
    if (value === undefined || value === null) return defaultValue;
    if (typeof value === 'number') return value;
    
    const parsed = parseInt(value, 10);
    return isNaN(parsed) ? defaultValue : parsed;
}

// Export utility
window.parseNumericSetting = parseNumericSetting;
