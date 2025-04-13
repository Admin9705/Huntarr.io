#!/usr/bin/env python3
"""
Configuration module for Huntarr
Handles all configuration settings with defaults
"""

import os
import logging
import importlib
from src.primary import settings_manager
from src.primary import keys_manager
from src.primary.utils.logger import logger

# Get app type
APP_TYPE = settings_manager.get_app_type()

# API Configuration directly from settings_manager
API_URL = settings_manager.get_api_url()
API_KEY = settings_manager.get_api_key()

# Web UI is always enabled
ENABLE_WEB_UI = True

# Base settings common to all apps - read directly from app section instead of nested
API_TIMEOUT = settings_manager.get_setting(APP_TYPE, "api_timeout", 60)
DEBUG_MODE = settings_manager.get_setting(APP_TYPE, "debug_mode", False)
COMMAND_WAIT_DELAY = settings_manager.get_setting(APP_TYPE, "command_wait_delay", 1)
COMMAND_WAIT_ATTEMPTS = settings_manager.get_setting(APP_TYPE, "command_wait_attempts", 600)
MINIMUM_DOWNLOAD_QUEUE_SIZE = settings_manager.get_setting(APP_TYPE, "minimum_download_queue_size", -1)
MONITORED_ONLY = settings_manager.get_setting(APP_TYPE, "monitored_only", True)
SLEEP_DURATION = settings_manager.get_setting(APP_TYPE, "sleep_duration", 900)
STATE_RESET_INTERVAL_HOURS = settings_manager.get_setting(APP_TYPE, "state_reset_interval_hours", 168)
RANDOM_MISSING = settings_manager.get_setting(APP_TYPE, "random_missing", True)
RANDOM_UPGRADES = settings_manager.get_setting(APP_TYPE, "random_upgrades", True)
# Add a new variable for log refresh interval
LOG_REFRESH_INTERVAL_SECONDS = settings_manager.get_setting(APP_TYPE, "log_refresh_interval_seconds", 30)

# Initialize all app-specific variables to default values first,
# then override based on the current app type
HUNT_MISSING_SHOWS = 0
HUNT_UPGRADE_EPISODES = 0
HUNT_MISSING_MOVIES = 0
HUNT_UPGRADE_MOVIES = 0
HUNT_MISSING_ALBUMS = 0
HUNT_UPGRADE_TRACKS = 0
HUNT_MISSING_BOOKS = 0
HUNT_UPGRADE_BOOKS = 0
SKIP_FUTURE_EPISODES = True
SKIP_FUTURE_RELEASES = True
SKIP_SERIES_REFRESH = False
SKIP_MOVIE_REFRESH = False
SKIP_ARTIST_REFRESH = False
SKIP_AUTHOR_REFRESH = False

# App-specific settings based on APP_TYPE - all read directly from app section
if APP_TYPE == "sonarr":
    HUNT_MISSING_SHOWS = settings_manager.get_setting(APP_TYPE, "hunt_missing_shows", 1)
    HUNT_UPGRADE_EPISODES = settings_manager.get_setting(APP_TYPE, "hunt_upgrade_episodes", 0)
    SKIP_FUTURE_EPISODES = settings_manager.get_setting(APP_TYPE, "skip_future_episodes", True)
    SKIP_SERIES_REFRESH = settings_manager.get_setting(APP_TYPE, "skip_series_refresh", False)
    
elif APP_TYPE == "radarr":
    HUNT_MISSING_MOVIES = settings_manager.get_setting(APP_TYPE, "hunt_missing_movies", 1)
    HUNT_UPGRADE_MOVIES = settings_manager.get_setting(APP_TYPE, "hunt_upgrade_movies", 0)
    SKIP_FUTURE_RELEASES = settings_manager.get_setting(APP_TYPE, "skip_future_releases", True)
    SKIP_MOVIE_REFRESH = settings_manager.get_setting(APP_TYPE, "skip_movie_refresh", False)
    
elif APP_TYPE == "lidarr":
    HUNT_MISSING_ALBUMS = settings_manager.get_setting(APP_TYPE, "hunt_missing_albums", 1)
    HUNT_UPGRADE_TRACKS = settings_manager.get_setting(APP_TYPE, "hunt_upgrade_tracks", 0)
    SKIP_FUTURE_RELEASES = settings_manager.get_setting(APP_TYPE, "skip_future_releases", True)
    SKIP_ARTIST_REFRESH = settings_manager.get_setting(APP_TYPE, "skip_artist_refresh", False)
    
elif APP_TYPE == "readarr":
    HUNT_MISSING_BOOKS = settings_manager.get_setting(APP_TYPE, "hunt_missing_books", 1)
    HUNT_UPGRADE_BOOKS = settings_manager.get_setting(APP_TYPE, "hunt_upgrade_books", 0)
    SKIP_FUTURE_RELEASES = settings_manager.get_setting(APP_TYPE, "skip_future_releases", True)
    SKIP_AUTHOR_REFRESH = settings_manager.get_setting(APP_TYPE, "skip_author_refresh", False)
    
# For backward compatibility with Sonarr (the initial implementation)
if APP_TYPE != "sonarr":
    # Add Sonarr specific variables for backward compatibility
    HUNT_MISSING_SHOWS = 0
    HUNT_UPGRADE_EPISODES = 0
    SKIP_FUTURE_EPISODES = True
    SKIP_SERIES_REFRESH = False

# Determine hunt mode
def determine_hunt_mode():
    """Determine the hunt mode based on current settings"""
    if APP_TYPE == "sonarr":
        if HUNT_MISSING_SHOWS > 0 and HUNT_UPGRADE_EPISODES > 0:
            return "both"
        elif HUNT_MISSING_SHOWS > 0:
            return "missing"
        elif HUNT_UPGRADE_EPISODES > 0:
            return "upgrade"
        else:
            return "disabled"
    elif APP_TYPE == "radarr":
        if HUNT_MISSING_MOVIES > 0 and HUNT_UPGRADE_MOVIES > 0:
            return "both"
        elif HUNT_MISSING_MOVIES > 0:
            return "missing"
        elif HUNT_UPGRADE_MOVIES > 0:
            return "upgrade"
        else:
            return "disabled"
    elif APP_TYPE == "lidarr":
        if HUNT_MISSING_ALBUMS > 0 and HUNT_UPGRADE_TRACKS > 0:
            return "both"
        elif HUNT_MISSING_ALBUMS > 0:
            return "missing"
        elif HUNT_UPGRADE_TRACKS > 0:
            return "upgrade"
        else:
            return "disabled"
    elif APP_TYPE == "readarr":
        if HUNT_MISSING_BOOKS > 0 and HUNT_UPGRADE_BOOKS > 0:
            return "both"
        elif HUNT_MISSING_BOOKS > 0:
            return "missing"
        elif HUNT_UPGRADE_BOOKS > 0:
            return "upgrade"
        else:
            return "disabled"
    else:
        return "disabled"

# Set the initial hunt mode
HUNT_MODE = determine_hunt_mode()

def refresh_settings(app_type: str = None) -> None:
    """Refresh settings from the settings manager"""
    # Keep a reference to the original app type
    original_app_type = APP_TYPE
    
    # Update global variables
    global HUNT_MODE, HUNT_MISSING_SHOWS, HUNT_UPGRADE_EPISODES
    global HUNT_MISSING_MOVIES, HUNT_UPGRADE_MOVIES
    global HUNT_MISSING_ALBUMS, HUNT_UPGRADE_TRACKS
    global HUNT_MISSING_BOOKS, HUNT_UPGRADE_BOOKS
    global RANDOM_MISSING, RANDOM_UPGRADES, MONITORED_ONLY
    global API_TIMEOUT, COMMAND_WAIT_DELAY, COMMAND_WAIT_ATTEMPTS
    global MINIMUM_DOWNLOAD_QUEUE_SIZE, DEBUG_MODE, LOG_REFRESH_INTERVAL_SECONDS
    global SLEEP_DURATION, STATE_RESET_INTERVAL_HOURS
    global SKIP_FUTURE_EPISODES, SKIP_SERIES_REFRESH
    global SKIP_FUTURE_RELEASES, SKIP_MOVIE_REFRESH
    global SKIP_ARTIST_REFRESH, SKIP_AUTHOR_REFRESH
    
    # Get the actual app type we're refreshing settings for
    current_app_type = os.environ.get("APP_TYPE", original_app_type)
    
    # Common settings - read directly from app section
    RANDOM_MISSING = settings_manager.get_setting(current_app_type, "random_missing", True)
    RANDOM_UPGRADES = settings_manager.get_setting(current_app_type, "random_upgrades", True)
    MONITORED_ONLY = settings_manager.get_setting(current_app_type, "monitored_only", True)
    API_TIMEOUT = settings_manager.get_setting(current_app_type, "api_timeout", 60)
    COMMAND_WAIT_DELAY = settings_manager.get_setting(current_app_type, "command_wait_delay", 1)
    COMMAND_WAIT_ATTEMPTS = settings_manager.get_setting(current_app_type, "command_wait_attempts", 600)
    MINIMUM_DOWNLOAD_QUEUE_SIZE = settings_manager.get_setting(current_app_type, "minimum_download_queue_size", -1)
    DEBUG_MODE = settings_manager.get_setting(current_app_type, "debug_mode", False)
    LOG_REFRESH_INTERVAL_SECONDS = settings_manager.get_setting(current_app_type, "log_refresh_interval_seconds", 30)
    SLEEP_DURATION = settings_manager.get_setting(current_app_type, "sleep_duration", 900)
    STATE_RESET_INTERVAL_HOURS = settings_manager.get_setting(current_app_type, "state_reset_interval_hours", 168)
    
    # App-specific settings based on current app type
    if current_app_type == "sonarr":
        HUNT_MISSING_SHOWS = settings_manager.get_setting(current_app_type, "hunt_missing_shows", 1)
        HUNT_UPGRADE_EPISODES = settings_manager.get_setting(current_app_type, "hunt_upgrade_episodes", 0)
        SKIP_FUTURE_EPISODES = settings_manager.get_setting(current_app_type, "skip_future_episodes", True)
        SKIP_SERIES_REFRESH = settings_manager.get_setting(current_app_type, "skip_series_refresh", False)
        
    elif current_app_type == "radarr":
        HUNT_MISSING_MOVIES = settings_manager.get_setting(current_app_type, "hunt_missing_movies", 1)
        HUNT_UPGRADE_MOVIES = settings_manager.get_setting(current_app_type, "hunt_upgrade_movies", 0)
        SKIP_FUTURE_RELEASES = settings_manager.get_setting(current_app_type, "skip_future_releases", True)
        SKIP_MOVIE_REFRESH = settings_manager.get_setting(current_app_type, "skip_movie_refresh", False)
        
    elif current_app_type == "lidarr":
        HUNT_MISSING_ALBUMS = settings_manager.get_setting(current_app_type, "hunt_missing_albums", 1)
        HUNT_UPGRADE_TRACKS = settings_manager.get_setting(current_app_type, "hunt_upgrade_tracks", 0)
        SKIP_FUTURE_RELEASES = settings_manager.get_setting(current_app_type, "skip_future_releases", True)
        SKIP_ARTIST_REFRESH = settings_manager.get_setting(current_app_type, "skip_artist_refresh", False)
        
    elif current_app_type == "readarr":
        HUNT_MISSING_BOOKS = settings_manager.get_setting(current_app_type, "hunt_missing_books", 1)
        HUNT_UPGRADE_BOOKS = settings_manager.get_setting(current_app_type, "hunt_upgrade_books", 0)
        SKIP_FUTURE_RELEASES = settings_manager.get_setting(current_app_type, "skip_future_releases", True)
        SKIP_AUTHOR_REFRESH = settings_manager.get_setting(current_app_type, "skip_author_refresh", False)
    
    # Recalculate hunt mode based on the current settings
    global HUNT_MODE
    HUNT_MODE = determine_hunt_mode()

def log_configuration(logger):
    """Log the current configuration settings"""
    # Refresh settings from the settings manager
    refresh_settings()
    
    logger.info(f"=== Huntarr [{APP_TYPE.title()} Edition] Starting ===")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"API Timeout: {API_TIMEOUT}s")
    
    # App-specific logging
    if APP_TYPE == "sonarr":
        logger.info(f"Missing Content Configuration: HUNT_MISSING_SHOWS={HUNT_MISSING_SHOWS}")
        logger.info(f"Upgrade Configuration: HUNT_UPGRADE_EPISODES={HUNT_UPGRADE_EPISODES}")
        logger.info(f"SKIP_FUTURE_EPISODES={SKIP_FUTURE_EPISODES}, SKIP_SERIES_REFRESH={SKIP_SERIES_REFRESH}")
    elif APP_TYPE == "radarr":
        logger.info(f"Missing Content Configuration: HUNT_MISSING_MOVIES={HUNT_MISSING_MOVIES}")
        logger.info(f"Upgrade Configuration: HUNT_UPGRADE_MOVIES={HUNT_UPGRADE_MOVIES}")
        logger.info(f"SKIP_FUTURE_RELEASES={SKIP_FUTURE_RELEASES}, SKIP_MOVIE_REFRESH={SKIP_MOVIE_REFRESH}")
    elif APP_TYPE == "lidarr":
        logger.info(f"Missing Content Configuration: HUNT_MISSING_ALBUMS={HUNT_MISSING_ALBUMS}")
        logger.info(f"Upgrade Configuration: HUNT_UPGRADE_TRACKS={HUNT_UPGRADE_TRACKS}")
        logger.info(f"SKIP_FUTURE_RELEASES={SKIP_FUTURE_RELEASES}, SKIP_ARTIST_REFRESH={SKIP_ARTIST_REFRESH}")
    elif APP_TYPE == "readarr":
        logger.info(f"Missing Content Configuration: HUNT_MISSING_BOOKS={HUNT_MISSING_BOOKS}")
        logger.info(f"Upgrade Configuration: HUNT_UPGRADE_BOOKS={HUNT_UPGRADE_BOOKS}")
        logger.info(f"SKIP_FUTURE_RELEASES={SKIP_FUTURE_RELEASES}, SKIP_AUTHOR_REFRESH={SKIP_AUTHOR_REFRESH}")
    
    # Common configuration logging
    logger.info(f"State Reset Interval: {STATE_RESET_INTERVAL_HOURS} hours")
    logger.info(f"Sleep Duration: {SLEEP_DURATION}s")
    logger.info(f"Minimum Download Queue Size: {MINIMUM_DOWNLOAD_QUEUE_SIZE}")
    logger.info(f"MONITORED_ONLY={MONITORED_ONLY}, RANDOM_MISSING={RANDOM_MISSING}, RANDOM_UPGRADES={RANDOM_UPGRADES}")
    logger.info(f"HUNT_MODE={HUNT_MODE}, SLEEP_DURATION={SLEEP_DURATION}s")
    logger.info(f"COMMAND_WAIT_DELAY={COMMAND_WAIT_DELAY}, COMMAND_WAIT_ATTEMPTS={COMMAND_WAIT_ATTEMPTS}")
    logger.info(f"ENABLE_WEB_UI=true, DEBUG_MODE={DEBUG_MODE}")

# Initial refresh of settings
refresh_settings()