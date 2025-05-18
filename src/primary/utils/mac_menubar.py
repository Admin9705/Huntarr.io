#!/usr/bin/env python3
"""
Mac OS X menubar icon for Huntarr
This module creates a macOS menubar icon with options to donate or quit the application
"""

import os
import sys
import threading
import webbrowser
import logging

logger = logging.getLogger(__name__)

# Check if we're on macOS
is_macos = sys.platform == 'darwin'

if is_macos:
    try:
        import rumps
    except ImportError:
        logger.warning("rumps package not installed, menubar icon won't be available")
        rumps = None
else:
    rumps = None

# Donation URL
DONATION_URL = "https://donate.plex.one"

class HuntarrMenubar(object):
    """Huntarr menubar application for macOS"""
    
    def __init__(self, app=None, quit_callback=None):
        """Initialize the menubar application
        
        Args:
            app: The main Huntarr application instance
            quit_callback: Function to call when quitting
        """
        self.app = app
        self.quit_callback = quit_callback
        self.menubar = None
        self.thread = None
    
    @rumps.clicked("Donate")
    def donate(self, _):
        """Open donation page in the default browser"""
        logger.info("Opening donation page")
        webbrowser.open(DONATION_URL)
    
    @rumps.clicked("Quit")
    def quit(self, _):
        """Quit the application"""
        logger.info("Quitting from menubar")
        if self.quit_callback:
            self.quit_callback()
        else:
            # Fallback if no callback was provided
            rumps.quit_application()
    
    def run(self):
        """Run the menubar application in a separate thread"""
        if not is_macos or not rumps:
            logger.warning("Cannot create menubar icon: not on macOS or rumps not available")
            return
        
        try:
            # Get the icon path - icon must be added to the package
            icon_path = None
            if getattr(sys, 'frozen', False):
                # We're running from the bundled package
                bundle_dir = os.path.dirname(sys.executable)
                candidates = [
                    os.path.join(bundle_dir, 'static', 'img', 'favicon.ico'),
                    os.path.join(bundle_dir, '..', 'Resources', 'frontend', 'static', 'img', 'favicon.ico'),
                    os.path.join(bundle_dir, 'frontend', 'static', 'img', 'favicon.ico')
                ]
                for path in candidates:
                    if os.path.exists(path):
                        icon_path = path
                        break
            else:
                # Normal Python execution
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                icon_path = os.path.join(base_dir, 'frontend', 'static', 'img', 'favicon.ico')
                if not os.path.exists(icon_path):
                    logger.warning(f"Icon not found at {icon_path}")
                    icon_path = None
            
            # Create the menubar app
            self.menubar = rumps.App("Huntarr", icon=icon_path, quit_button=None)
            
            # Start the menubar app in a separate thread
            self.thread = threading.Thread(target=self._run_in_thread, daemon=True)
            self.thread.start()
            logger.info("Menubar icon started")
            
        except Exception as e:
            logger.error(f"Failed to create menubar icon: {e}")
    
    def _run_in_thread(self):
        """Run the menubar app in a thread"""
        try:
            self.menubar.run()
        except Exception as e:
            logger.error(f"Error in menubar application: {e}")


def create_menubar(app=None, quit_callback=None):
    """Create and run the menubar application
    
    Args:
        app: The main Huntarr application instance
        quit_callback: Function to call when quitting
    
    Returns:
        The menubar application instance or None if not on macOS
    """
    if not is_macos or not rumps:
        return None
    
    try:
        menubar = HuntarrMenubar(app, quit_callback)
        menubar.run()
        return menubar
    except Exception as e:
        logger.error(f"Failed to create menubar: {e}")
        return None
