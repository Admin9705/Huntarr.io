#!/usr/bin/env python3
"""
Sonarr cutoff upgrade processing module for Huntarr
"""

import time
import random
from typing import List, Dict, Any, Set, Callable
from src.primary.utils.logger import get_logger
from src.primary.apps.sonarr import api as sonarr_api
from src.primary.stats_manager import increment_stat

# Get logger for the app
sonarr_logger = get_logger("sonarr")

def process_cutoff_upgrades(
    app_settings: Dict[str, Any],
    stop_check: Callable[[], bool] # Function to check if stop is requested
) -> bool:
    """
    Process quality cutoff upgrades for Sonarr based on settings.

    Args:
        app_settings: Dictionary containing all settings for Sonarr.
        stop_check: A function that returns True if the process should stop.

    Returns:
        True if any episodes were processed, False otherwise.
    """
    sonarr_logger.info("Starting quality cutoff upgrades processing cycle for Sonarr.")
    processed_any = False

    # Extract necessary settings
    api_url = app_settings.get("api_url", "").strip()
    api_key = app_settings.get("api_key", "").strip()
    api_timeout = app_settings.get("api_timeout", 90)
    monitored_only = app_settings.get("monitored_only", True)
    skip_series_refresh = app_settings.get("skip_series_refresh", False)
    random_upgrades = app_settings.get("random_upgrades", False)
    hunt_upgrade_items = app_settings.get("hunt_upgrade_items", 0)
    hunt_missing_mode = app_settings.get("hunt_missing_mode", "episodes")
    command_wait_delay = app_settings.get("command_wait_delay", 5)
    command_wait_attempts = app_settings.get("command_wait_attempts", 12)

    # Improved validation of API URL and key
    if not api_url:
        sonarr_logger.error("API URL is empty or not set")
        return False
        
    if not api_key:
        sonarr_logger.error("API Key is not set")
        return False
        
    # Ensure URL has proper format with auto-correction
    if not (api_url.startswith('http://') or api_url.startswith('https://')):
        old_url = api_url
        api_url = f"http://{api_url}"
        sonarr_logger.warning(f"API URL is missing http:// or https:// scheme: {old_url}")
        sonarr_logger.warning(f"Auto-correcting URL to: {api_url}")
        
    sonarr_logger.debug(f"Using API URL: {api_url}")

    if hunt_upgrade_items <= 0:
        sonarr_logger.info("'hunt_upgrade_items' setting is 0 or less. Skipping upgrade processing.")
        return False
        
    sonarr_logger.info(f"Checking for {hunt_upgrade_items} quality upgrades in {hunt_missing_mode} mode...")

    # Handle different modes
    if hunt_missing_mode == "episodes":
        sonarr_logger.info("Episode-based quality upgrade mode selected")
        return process_upgrade_episodes_mode(
            api_url, api_key, api_timeout, monitored_only, 
            skip_series_refresh, random_upgrades, hunt_upgrade_items, 
            command_wait_delay, command_wait_attempts, stop_check
        )
    elif hunt_missing_mode == "seasons":
        sonarr_logger.info("Season-based quality upgrade mode selected")
        return process_upgrade_seasons_mode(
            api_url, api_key, api_timeout, monitored_only, 
            skip_series_refresh, random_upgrades, hunt_upgrade_items, 
            command_wait_delay, command_wait_attempts, stop_check
        )
    elif hunt_missing_mode == "shows":
        sonarr_logger.info("Show-based quality upgrade mode selected")
        return process_upgrade_shows_mode(
            api_url, api_key, api_timeout, monitored_only, 
            skip_series_refresh, random_upgrades, hunt_upgrade_items, 
            command_wait_delay, command_wait_attempts, stop_check
        )
    else:
        sonarr_logger.error(f"Invalid hunt_missing_mode: {hunt_missing_mode}. Valid options are 'episodes', 'seasons', or 'shows'.")
        return False

def process_upgrade_episodes_mode(
    api_url: str,
    api_key: str,
    api_timeout: int,
    monitored_only: bool,
    skip_series_refresh: bool,
    random_upgrades: bool,
    hunt_upgrade_items: int,
    command_wait_delay: int,
    command_wait_attempts: int,
    stop_check: Callable[[], bool]
) -> bool:
    """Process upgrades in episode mode (original implementation)."""
    processed_any = False
    
    # Use different methods based on random setting and library size
    episodes_to_search = []
    
    if random_upgrades:
        # Use the efficient random page selection method
        sonarr_logger.debug(f"Using random selection for cutoff unmet episodes")
        episodes_to_search = sonarr_api.get_cutoff_unmet_episodes_random_page(
            api_url, api_key, api_timeout, monitored_only, hunt_upgrade_items)
            
        # If we didn't get enough episodes, we might need to try another page
        if len(episodes_to_search) < hunt_upgrade_items and len(episodes_to_search) > 0:
            sonarr_logger.debug(f"Got {len(episodes_to_search)} episodes from random page, fewer than requested {hunt_upgrade_items}")
    else:
        # Use the sequential approach for non-random selection
        sonarr_logger.debug(f"Using sequential selection for cutoff unmet episodes (oldest first)")
        cutoff_unmet_episodes = sonarr_api.get_cutoff_unmet_episodes(
            api_url, api_key, api_timeout, monitored_only)
            
        if not cutoff_unmet_episodes:
            sonarr_logger.info("No cutoff unmet episodes found in Sonarr.")
            return False
            
        # Filter out future episodes if configured
        if skip_series_refresh:
            now_unix = time.time()
            original_count = len(cutoff_unmet_episodes)
            # Ensure airDateUtc exists and is not None before parsing
            cutoff_unmet_episodes = [
                ep for ep in cutoff_unmet_episodes
                if ep.get('airDateUtc') and time.mktime(time.strptime(ep['airDateUtc'], '%Y-%m-%dT%H:%M:%SZ')) < now_unix
            ]
            skipped_count = original_count - len(cutoff_unmet_episodes)
            if skipped_count > 0:
                sonarr_logger.info(f"Skipped {skipped_count} future episodes based on air date for upgrades.")
                
        # Select the first N episodes
        episodes_to_search = cutoff_unmet_episodes[:hunt_upgrade_items]

    if stop_check(): 
        sonarr_logger.info("Stop requested during upgrade processing.")
        return processed_any
        
    # Filter out future episodes for random selection approach
    if random_upgrades and skip_series_refresh:
        now_unix = time.time()
        original_count = len(episodes_to_search)
        episodes_to_search = [
            ep for ep in episodes_to_search
            if ep.get('airDateUtc') and time.mktime(time.strptime(ep['airDateUtc'], '%Y-%m-%dT%H:%M:%SZ')) < now_unix
        ]
        skipped_count = original_count - len(episodes_to_search)
        if skipped_count > 0:
            sonarr_logger.info(f"Skipped {skipped_count} future episodes based on air date for upgrades.")

    if not episodes_to_search:
        sonarr_logger.info("No cutoff unmet episodes left to process for upgrades after filtering.")
        return False

    sonarr_logger.info(f"Selected {len(episodes_to_search)} cutoff unmet episodes to search for upgrades.")
    
    # Add detailed listing of episodes being upgraded
    if episodes_to_search:
        sonarr_logger.info(f"Episodes selected for quality upgrades in this cycle:")
        for idx, episode in enumerate(episodes_to_search):
            series_title = episode.get('series', {}).get('title', 'Unknown Series')
            episode_title = episode.get('title', 'Unknown Episode')
            season_number = episode.get('seasonNumber', 'Unknown Season')
            episode_number = episode.get('episodeNumber', 'Unknown Episode')
            
            # Get quality information
            quality_name = "Unknown"
            if "quality" in episode and episode["quality"]:
                quality_name = episode["quality"].get("quality", {}).get("name", "Unknown")
                
            episode_id = episode.get("id")
            try:
                season_episode = f"S{season_number:02d}E{episode_number:02d}"
            except (ValueError, TypeError):
                season_episode = f"S{season_number}E{episode_number}"
                
            sonarr_logger.info(f" {idx+1}. {series_title} - {season_episode} - \"{episode_title}\" - Current quality: {quality_name} (ID: {episode_id})")
    
    # Group episodes by series for potential refresh
    series_to_process: Dict[int, List[int]] = {}
    series_titles: Dict[int, str] = {} # Store titles for logging
    for episode in episodes_to_search:
        series_id = episode.get('seriesId')
        if series_id:
            if series_id not in series_to_process:
                series_to_process[series_id] = []
                # Store title when first encountering the series ID
                series_titles[series_id] = episode.get('series', {}).get('title', f"Series ID {series_id}")
            series_to_process[series_id].append(episode['id'])

    # Process each series
    for series_id, episode_ids in series_to_process.items():
        if stop_check(): 
            sonarr_logger.info("Stop requested before processing next series for upgrades.")
            break
            
        series_title = series_titles.get(series_id, f"Series ID {series_id}")
        sonarr_logger.info(f"Processing series for upgrades: {series_title} (ID: {series_id}) with {len(episode_ids)} episodes.")

        # Refresh series metadata if not skipped
        refresh_command_id = None
        if not skip_series_refresh:
            sonarr_logger.debug(f"Attempting to refresh series ID: {series_id} before upgrade search.")
            refresh_command_id = sonarr_api.refresh_series(api_url, api_key, api_timeout, series_id)
            if refresh_command_id:
                # Wait for refresh command to complete
                if not wait_for_command(
                    api_url, api_key, api_timeout, refresh_command_id,
                    command_wait_delay, command_wait_attempts, "Series Refresh (Upgrade)", stop_check
                ):
                    sonarr_logger.warning(f"Series refresh command (ID: {refresh_command_id}) for series {series_id} did not complete successfully or timed out. Proceeding with upgrade search anyway.")
            else:
                 sonarr_logger.warning(f"Failed to trigger refresh command for series ID: {series_id}. Proceeding without refresh.")
        else:
            sonarr_logger.debug(f"Skipping series refresh for series ID: {series_id} as configured.")

        if stop_check(): 
            sonarr_logger.info("Stop requested after series refresh attempt for upgrades.")
            break

        # Trigger search for the selected episodes in this series
        sonarr_logger.debug(f"Attempting upgrade search for episode IDs: {episode_ids}")
        search_command_id = sonarr_api.search_episode(api_url, api_key, api_timeout, episode_ids)

        if search_command_id:
            # Wait for search command to complete
            if wait_for_command(
                api_url, api_key, api_timeout, search_command_id,
                command_wait_delay, command_wait_attempts, "Episode Upgrade Search", stop_check
            ):
                # Mark episodes as processed if search command completed successfully
                processed_any = True # Mark that we did something
                sonarr_logger.info(f"Successfully processed and searched for {len(episode_ids)} episodes in series {series_id}.")
                
                # Increment the upgraded statistics
                increment_stat("sonarr", "upgraded", len(episode_ids))
                sonarr_logger.debug(f"Incremented sonarr upgraded statistics by {len(episode_ids)}")
            else:
                sonarr_logger.warning(f"Episode upgrade search command (ID: {search_command_id}) for series {series_id} did not complete successfully or timed out. Episodes will not be marked as processed yet.")
        else:
            sonarr_logger.error(f"Failed to trigger upgrade search command for episodes {episode_ids} in series {series_id}.")

    sonarr_logger.info("Finished quality cutoff upgrades processing cycle for Sonarr.")
    return processed_any

def process_upgrade_seasons_mode(
    api_url: str,
    api_key: str,
    api_timeout: int,
    monitored_only: bool,
    skip_series_refresh: bool,
    random_upgrades: bool,
    hunt_upgrade_items: int,
    command_wait_delay: int,
    command_wait_attempts: int,
    stop_check: Callable[[], bool]
) -> bool:
    """Process upgrades in season mode - groups episodes by season."""
    processed_any = False
    
    # Get all cutoff unmet episodes
    cutoff_unmet_episodes = sonarr_api.get_cutoff_unmet_episodes(api_url, api_key, api_timeout, monitored_only)
    sonarr_logger.info(f"Received {len(cutoff_unmet_episodes)} cutoff unmet episodes from Sonarr API (before filtering).")
    
    if not cutoff_unmet_episodes:
        sonarr_logger.info("No cutoff unmet episodes found in Sonarr.")
        return False
        
    # Filter out future episodes if configured
    if skip_series_refresh:
        now_unix = time.time()
        original_count = len(cutoff_unmet_episodes)
        # Ensure airDateUtc exists and is not None before parsing
        cutoff_unmet_episodes = [
            ep for ep in cutoff_unmet_episodes
            if ep.get('airDateUtc') and time.mktime(time.strptime(ep['airDateUtc'], '%Y-%m-%dT%H:%M:%SZ')) < now_unix
        ]
        skipped_count = original_count - len(cutoff_unmet_episodes)
        if skipped_count > 0:
            sonarr_logger.info(f"Skipped {skipped_count} future episodes based on air date for upgrades.")
    
    if stop_check(): 
        sonarr_logger.info("Stop requested during upgrade processing.")
        return processed_any
    
    # Group episodes by series and season
    series_season_episodes: Dict[int, Dict[int, List[Dict]]] = {}
    for episode in cutoff_unmet_episodes:
        series_id = episode.get('seriesId')
        season_number = episode.get('seasonNumber')
        
        if series_id is not None and season_number is not None:
            if series_id not in series_season_episodes:
                series_season_episodes[series_id] = {}
            
            if season_number not in series_season_episodes[series_id]:
                series_season_episodes[series_id][season_number] = []
                
            series_season_episodes[series_id][season_number].append(episode)
    
    # Create a list of (series_id, season_number) tuples for selection
    available_seasons = []
    for series_id, seasons in series_season_episodes.items():
        for season_number, episodes in seasons.items():
            # Get series title from the first episode for this season
            series_title = episodes[0].get('series', {}).get('title', f"Series ID {series_id}")
            available_seasons.append((series_id, season_number, len(episodes), series_title))
    
    if not available_seasons:
        sonarr_logger.info("No valid seasons with cutoff unmet episodes found.")
        return False
    
    # Select seasons to process - either randomly or sequentially
    seasons_to_process = []
    if random_upgrades:
        # Randomly shuffle the available seasons
        random.shuffle(available_seasons)
        seasons_to_process = available_seasons[:hunt_upgrade_items]
    else:
        # Sort by number of unmet episodes (descending) for most impactful processing
        available_seasons.sort(key=lambda x: x[2], reverse=True)
        seasons_to_process = available_seasons[:hunt_upgrade_items]
    
    sonarr_logger.info(f"Selected {len(seasons_to_process)} seasons with cutoff unmet episodes to process")
    
    # Log selected seasons
    for idx, (series_id, season_number, episode_count, series_title) in enumerate(seasons_to_process):
        sonarr_logger.info(f" {idx+1}. {series_title} - Season {season_number} - {episode_count} cutoff unmet episodes")
    
    # Process each selected season
    for series_id, season_number, _, series_title in seasons_to_process:
        if stop_check(): 
            sonarr_logger.info("Stop requested before processing next season.")
            break
            
        episodes = series_season_episodes[series_id][season_number]
        episode_ids = [episode["id"] for episode in episodes]
        
        sonarr_logger.info(f"Processing {series_title} - Season {season_number} with {len(episode_ids)} cutoff unmet episodes")
        
        # Refresh series metadata if not skipped
        if not skip_series_refresh:
            sonarr_logger.debug(f"Attempting to refresh series ID: {series_id}")
            refresh_command_id = sonarr_api.refresh_series(api_url, api_key, api_timeout, series_id)
            if refresh_command_id:
                # Wait for refresh command to complete
                if not wait_for_command(
                    api_url, api_key, api_timeout, refresh_command_id,
                    command_wait_delay, command_wait_attempts, "Series Refresh (Upgrade)", stop_check
                ):
                    sonarr_logger.warning(f"Series refresh command for {series_title} did not complete successfully or timed out.")
            else:
                sonarr_logger.warning(f"Failed to trigger refresh command for series {series_title}")
                
        if stop_check(): 
            sonarr_logger.info("Stop requested after series refresh attempt.")
            break
            
        # Trigger search for the selected episodes in this season
        sonarr_logger.debug(f"Attempting to search for {len(episode_ids)} episodes in {series_title} Season {season_number} for upgrades")
        search_command_id = sonarr_api.search_episode(api_url, api_key, api_timeout, episode_ids)
        
        if search_command_id:
            # Wait for search command to complete
            if wait_for_command(
                api_url, api_key, api_timeout, search_command_id,
                command_wait_delay, command_wait_attempts, "Episode Upgrade Search", stop_check
            ):
                # Mark as processed if search command completed successfully
                processed_any = True
                sonarr_logger.info(f"Successfully processed {len(episode_ids)} cutoff unmet episodes in {series_title} Season {season_number}")
                
                # Increment the upgraded statistics
                increment_stat("sonarr", "upgraded", len(episode_ids))
                sonarr_logger.debug(f"Incremented sonarr upgraded statistics by {len(episode_ids)}")
            else:
                sonarr_logger.warning(f"Episode upgrade search command for {series_title} Season {season_number} did not complete successfully")
        else:
            sonarr_logger.error(f"Failed to trigger upgrade search command for {series_title} Season {season_number}")
    
    sonarr_logger.info("Finished quality cutoff upgrades processing cycle (season mode) for Sonarr.")
    return processed_any

def process_upgrade_shows_mode(
    api_url: str,
    api_key: str,
    api_timeout: int,
    monitored_only: bool,
    skip_series_refresh: bool,
    random_upgrades: bool,
    hunt_upgrade_items: int,
    command_wait_delay: int,
    command_wait_attempts: int,
    stop_check: Callable[[], bool]
) -> bool:
    """Process upgrades in show mode - gets all cutoff unmet episodes for entire shows."""
    processed_any = False
    
    # Get all cutoff unmet episodes
    cutoff_unmet_episodes = sonarr_api.get_cutoff_unmet_episodes(api_url, api_key, api_timeout, monitored_only)
    sonarr_logger.info(f"Received {len(cutoff_unmet_episodes)} cutoff unmet episodes from Sonarr API (before filtering).")
    
    if not cutoff_unmet_episodes:
        sonarr_logger.info("No cutoff unmet episodes found in Sonarr.")
        return False
        
    # Filter out future episodes if configured
    if skip_series_refresh:
        now_unix = time.time()
        original_count = len(cutoff_unmet_episodes)
        # Ensure airDateUtc exists and is not None before parsing
        cutoff_unmet_episodes = [
            ep for ep in cutoff_unmet_episodes
            if ep.get('airDateUtc') and time.mktime(time.strptime(ep['airDateUtc'], '%Y-%m-%dT%H:%M:%SZ')) < now_unix
        ]
        skipped_count = original_count - len(cutoff_unmet_episodes)
        if skipped_count > 0:
            sonarr_logger.info(f"Skipped {skipped_count} future episodes based on air date for upgrades.")
    
    if stop_check(): 
        sonarr_logger.info("Stop requested during upgrade processing.")
        return processed_any
    
    # Group episodes by series
    series_episodes: Dict[int, List[Dict]] = {}
    series_titles: Dict[int, str] = {}  # Keep track of series titles
    
    for episode in cutoff_unmet_episodes:
        series_id = episode.get('seriesId')
        if series_id is not None:
            if series_id not in series_episodes:
                series_episodes[series_id] = []
                # Store series title when first encountering the series ID
                series_titles[series_id] = episode.get('series', {}).get('title', f"Series ID {series_id}")
            
            series_episodes[series_id].append(episode)
    
    # Create a list of (series_id, episode_count, series_title) tuples for selection
    available_series = [(series_id, len(episodes), series_titles[series_id]) 
                         for series_id, episodes in series_episodes.items()]
    
    if not available_series:
        sonarr_logger.info("No series with cutoff unmet episodes found.")
        return False
    
    # Select series to process - either randomly or sequentially
    series_to_process = []
    if random_upgrades:
        # Randomly shuffle the available series
        random.shuffle(available_series)
        series_to_process = available_series[:hunt_upgrade_items]
    else:
        # Sort by unmet episode count (descending) for most impactful processing
        available_series.sort(key=lambda x: x[1], reverse=True)
        series_to_process = available_series[:hunt_upgrade_items]
    
    sonarr_logger.info(f"Selected {len(series_to_process)} series with cutoff unmet episodes to process")
    
    # Log selected series
    for idx, (series_id, episode_count, series_title) in enumerate(series_to_process):
        sonarr_logger.info(f" {idx+1}. {series_title} - {episode_count} cutoff unmet episodes")
    
    # Process each selected series
    for series_id, _, series_title in series_to_process:
        if stop_check(): 
            sonarr_logger.info("Stop requested before processing next series.")
            break
            
        episodes = series_episodes[series_id]
        episode_ids = [episode["id"] for episode in episodes]
        
        sonarr_logger.info(f"Processing {series_title} with {len(episode_ids)} cutoff unmet episodes")
        
        # Refresh series metadata if not skipped
        if not skip_series_refresh:
            sonarr_logger.debug(f"Attempting to refresh series ID: {series_id}")
            refresh_command_id = sonarr_api.refresh_series(api_url, api_key, api_timeout, series_id)
            if refresh_command_id:
                # Wait for refresh command to complete
                if not wait_for_command(
                    api_url, api_key, api_timeout, refresh_command_id,
                    command_wait_delay, command_wait_attempts, "Series Refresh (Upgrade)", stop_check
                ):
                    sonarr_logger.warning(f"Series refresh command for {series_title} did not complete successfully or timed out.")
            else:
                sonarr_logger.warning(f"Failed to trigger refresh command for series {series_title}")
                
        if stop_check(): 
            sonarr_logger.info("Stop requested after series refresh attempt.")
            break
            
        # Trigger search for all cutoff unmet episodes in this series
        sonarr_logger.debug(f"Attempting to search for {len(episode_ids)} episodes in {series_title} for upgrades")
        search_command_id = sonarr_api.search_episode(api_url, api_key, api_timeout, episode_ids)
        
        if search_command_id:
            # Wait for search command to complete
            if wait_for_command(
                api_url, api_key, api_timeout, search_command_id,
                command_wait_delay, command_wait_attempts, "Episode Upgrade Search", stop_check
            ):
                # Mark as processed if search command completed successfully
                processed_any = True
                sonarr_logger.info(f"Successfully processed {len(episode_ids)} cutoff unmet episodes in {series_title}")
                
                # Increment the upgraded statistics
                increment_stat("sonarr", "upgraded", len(episode_ids))
                sonarr_logger.debug(f"Incremented sonarr upgraded statistics by {len(episode_ids)}")
            else:
                sonarr_logger.warning(f"Episode upgrade search command for {series_title} did not complete successfully")
        else:
            sonarr_logger.error(f"Failed to trigger upgrade search command for {series_title}")
    
    sonarr_logger.info("Finished quality cutoff upgrades processing cycle (show mode) for Sonarr.")
    return processed_any

def wait_for_command(
    api_url: str,
    api_key: str,
    api_timeout: int,
    command_id: int,
    delay: int,
    attempts: int,
    command_name: str,
    stop_check: Callable[[], bool] # Pass stop check function
) -> bool:
    """
    Wait for a Sonarr command to complete, checking for stop requests.
    
    Args:
        api_url: The base URL of the Sonarr API
        api_key: The API key for authentication
        api_timeout: Timeout for the API request
        command_id: The ID of the command to wait for
        delay: Delay in seconds between status checks
        attempts: Maximum number of status check attempts
        command_name: Name of the command for logging
        stop_check: Function to check if stop is requested
        
    Returns:
        True if command completed successfully, False otherwise
    """
    for attempt in range(attempts):
        if stop_check():
            sonarr_logger.info(f"Stop requested while waiting for command '{command_name}' (ID: {command_id}).")
            return False
            
        # Wait for the specified delay
        time.sleep(delay)
        
        # Check the command status
        command_status = sonarr_api.get_command_status(api_url, api_key, api_timeout, command_id)
        
        if not command_status:
            sonarr_logger.warning(f"Failed to get status for command '{command_name}' (ID: {command_id})")
            continue
            
        status = command_status.get('status', '').lower()
        
        # If the command has completed, return the success result
        if status == 'completed':
            sonarr_logger.debug(f"Command '{command_name}' (ID: {command_id}) completed successfully")
            return True
            
        elif status == 'failed':
            message = command_status.get('message', 'No error message provided')
            sonarr_logger.error(f"Command '{command_name}' (ID: {command_id}) failed: {message}")
            return False
            
        sonarr_logger.debug(f"Command '{command_name}' (ID: {command_id}) status: {status} (attempt {attempt+1}/{attempts})")

    sonarr_logger.error(f"Sonarr command '{command_name}' (ID: {command_id}) timed out after {attempts} attempts.")
    return False