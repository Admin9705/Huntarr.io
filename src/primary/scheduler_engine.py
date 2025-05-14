#!/usr/bin/env python3
"""
Scheduler Engine for Huntarr
Handles execution of scheduled actions from schedule.json
"""

import os
import json
import threading
import datetime
import time
import traceback
from typing import Dict, List, Any
import collections

from src.primary.utils.logger import get_logger

# Initialize logger
scheduler_logger = get_logger("scheduler")

# Scheduler constants
SCHEDULE_CHECK_INTERVAL = 60  # Check schedule every minute
SCHEDULE_DIR = "/config/scheduler"
SCHEDULE_FILE = os.path.join(SCHEDULE_DIR, "schedule.json")

# Track last executed actions to prevent duplicates
last_executed_actions = {}

# Track execution history for logging
max_history_entries = 50
execution_history = collections.deque(maxlen=max_history_entries)

stop_event = threading.Event()
scheduler_thread = None

def load_schedule():
    """Load the schedule configuration from file"""
    try:
        os.makedirs(SCHEDULE_DIR, exist_ok=True)  # Ensure directory exists
        
        if os.path.exists(SCHEDULE_FILE):
            try:
                # Check if file is empty
                if os.path.getsize(SCHEDULE_FILE) == 0:
                    scheduler_logger.warning(f"Schedule file is empty: {SCHEDULE_FILE}")
                    return {"global": [], "sonarr": [], "radarr": [], "lidarr": [], "readarr": [], "whisparr": [], "eros": []}
                
                # Attempt to load JSON
                with open(SCHEDULE_FILE, 'r') as f:
                    content = f.read()
                    scheduler_logger.debug(f"Schedule file content (first 100 chars): {content[:100]}...")
                    schedule_data = json.loads(content)
                    
                    # Ensure the schedule data has the expected structure
                    for app_type in ["global", "sonarr", "radarr", "lidarr", "readarr", "whisparr", "eros"]:
                        if app_type not in schedule_data:
                            scheduler_logger.warning(f"Missing app type {app_type} in schedule data, adding empty list")
                            schedule_data[app_type] = []
                    
                    return schedule_data
            except json.JSONDecodeError as json_err:
                scheduler_logger.error(f"Invalid JSON in schedule file: {json_err}")
                scheduler_logger.error(f"Attempting to repair JSON file...")
                
                # Backup the corrupted file
                backup_file = f"{SCHEDULE_FILE}.backup.{int(time.time())}"
                os.rename(SCHEDULE_FILE, backup_file)
                scheduler_logger.info(f"Backed up corrupted file to {backup_file}")
                
                # Create a new empty schedule file
                default_schedule = {"global": [], "sonarr": [], "radarr": [], "lidarr": [], "readarr": [], "whisparr": [], "eros": []}
                with open(SCHEDULE_FILE, 'w') as f:
                    json.dump(default_schedule, f, indent=2)
                scheduler_logger.info(f"Created new empty schedule file")
                
                return default_schedule
        else:
            scheduler_logger.warning(f"Schedule file not found: {SCHEDULE_FILE}")
            # Create the default schedule file
            default_schedule = {"global": [], "sonarr": [], "radarr": [], "lidarr": [], "readarr": [], "whisparr": [], "eros": []}
            with open(SCHEDULE_FILE, 'w') as f:
                json.dump(default_schedule, f, indent=2)
            scheduler_logger.info(f"Created new schedule file with default structure")
            return default_schedule
    except Exception as e:
        scheduler_logger.error(f"Error loading schedule: {e}")
        scheduler_logger.error(traceback.format_exc())
        return {"global": [], "sonarr": [], "radarr": [], "lidarr": [], "readarr": [], "whisparr": [], "eros": []}

def add_to_history(action_entry, status, message):
    """Add an action execution to the history log"""
    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    history_entry = {
        "timestamp": time_str,
        "id": action_entry.get("id", "unknown"),
        "action": action_entry.get("action", "unknown"),
        "app": action_entry.get("app", "unknown"),
        "status": status,
        "message": message
    }
    
    execution_history.appendleft(history_entry)
    scheduler_logger.info(f"Scheduler history: {time_str} - {action_entry.get('action')} for {action_entry.get('app')} - {status} - {message}")

def execute_action(action_entry):
    """Execute a scheduled action"""
    action_type = action_entry.get("action")
    app_type = action_entry.get("app")
    app_id = action_entry.get("id")
    
    # Generate a unique key for this action to track execution
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    execution_key = f"{app_id}_{current_date}"
    
    # Check if this action was already executed today
    if execution_key in last_executed_actions:
        message = f"Action {app_id} for {app_type} already executed today, skipping"
        scheduler_logger.debug(message)
        add_to_history(action_entry, "skipped", message)
        return False  # Already executed
    
    try:
        if action_type == "pause":
            # Pause logic for global or specific app
            if app_type == "global":
                message = "Executing global pause action"
                scheduler_logger.info(message)
                try:
                    apps = ['sonarr', 'radarr', 'lidarr', 'readarr', 'whisparr', 'eros']
                    for app in apps:
                        config_file = f"/config/{app}.json"
                        if os.path.exists(config_file):
                            with open(config_file, 'r') as f:
                                config_data = json.load(f)
                            config_data['enabled'] = False
                            with open(config_file, 'w') as f:
                                json.dump(config_data, f, indent=2)
                    result_message = "All apps paused successfully"
                    scheduler_logger.info(result_message)
                    add_to_history(action_entry, "success", result_message)
                except Exception as e:
                    error_message = f"Error pausing all apps: {str(e)}"
                    scheduler_logger.error(error_message)
                    add_to_history(action_entry, "error", error_message)
                    return False
            else:
                message = f"Executing pause action for {app_type}"
                scheduler_logger.info(message)
                try:
                    config_file = f"/config/{app_type}.json"
                    if os.path.exists(config_file):
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                        config_data['enabled'] = False
                        with open(config_file, 'w') as f:
                            json.dump(config_data, f, indent=2)
                    result_message = f"{app_type} paused successfully"
                    scheduler_logger.info(result_message)
                    add_to_history(action_entry, "success", result_message)
                except Exception as e:
                    error_message = f"Error pausing {app_type}: {str(e)}"
                    scheduler_logger.error(error_message)
                    add_to_history(action_entry, "error", error_message)
                    return False
        
        elif action_type == "resume":
            # Resume logic for global or specific app
            if app_type == "global":
                message = "Executing global resume action"
                scheduler_logger.info(message)
                try:
                    apps = ['sonarr', 'radarr', 'lidarr', 'readarr', 'whisparr', 'eros']
                    for app in apps:
                        config_file = f"/config/{app}.json"
                        if os.path.exists(config_file):
                            with open(config_file, 'r') as f:
                                config_data = json.load(f)
                            config_data['enabled'] = True
                            with open(config_file, 'w') as f:
                                json.dump(config_data, f, indent=2)
                    result_message = "All apps resumed successfully"
                    scheduler_logger.info(result_message)
                    add_to_history(action_entry, "success", result_message)
                except Exception as e:
                    error_message = f"Error resuming all apps: {str(e)}"
                    scheduler_logger.error(error_message)
                    add_to_history(action_entry, "error", error_message)
                    return False
            else:
                message = f"Executing resume action for {app_type}"
                scheduler_logger.info(message)
                try:
                    config_file = f"/config/{app_type}.json"
                    if os.path.exists(config_file):
                        with open(config_file, 'r') as f:
                            config_data = json.load(f)
                        config_data['enabled'] = True
                        with open(config_file, 'w') as f:
                            json.dump(config_data, f, indent=2)
                    result_message = f"{app_type} resumed successfully"
                    scheduler_logger.info(result_message)
                    add_to_history(action_entry, "success", result_message)
                except Exception as e:
                    error_message = f"Error resuming {app_type}: {str(e)}"
                    scheduler_logger.error(error_message)
                    add_to_history(action_entry, "error", error_message)
                    return False
        
        # Handle the API limit actions based on the predefined values
        elif action_type.startswith("api-") or action_type.startswith("API Limits "):
            # Extract the API limit value from the action type
            try:
                # Handle both formats: "api-5" and "API Limits 5"
                if action_type.startswith("api-"):
                    api_limit = int(action_type.replace("api-", ""))
                else:
                    api_limit = int(action_type.replace("API Limits ", ""))
                
                if app_type == "global":
                    message = f"Setting global API cap to {api_limit}"
                    scheduler_logger.info(message)
                    try:
                        apps = ['sonarr', 'radarr', 'lidarr', 'readarr', 'whisparr', 'eros']
                        for app in apps:
                            config_file = f"/config/{app}.json"
                            if os.path.exists(config_file):
                                with open(config_file, 'r') as f:
                                    config_data = json.load(f)
                                config_data['hourly_cap'] = api_limit
                                with open(config_file, 'w') as f:
                                    json.dump(config_data, f, indent=2)
                        result_message = f"API cap set to {api_limit} for all apps"
                        scheduler_logger.info(result_message)
                        add_to_history(action_entry, "success", result_message)
                    except Exception as e:
                        error_message = f"Error setting global API cap to {api_limit}: {str(e)}"
                        scheduler_logger.error(error_message)
                        add_to_history(action_entry, "error", error_message)
                        return False
                else:
                    message = f"Setting API cap for {app_type} to {api_limit}"
                    scheduler_logger.info(message)
                    try:
                        config_file = f"/config/{app_type}.json"
                        if os.path.exists(config_file):
                            with open(config_file, 'r') as f:
                                config_data = json.load(f)
                            config_data['hourly_cap'] = api_limit
                            with open(config_file, 'w') as f:
                                json.dump(config_data, f, indent=2)
                        result_message = f"API cap set to {api_limit} for {app_type}"
                        scheduler_logger.info(result_message)
                        add_to_history(action_entry, "success", result_message)
                    except Exception as e:
                        error_message = f"Error setting API cap for {app_type} to {api_limit}: {str(e)}"
                        scheduler_logger.error(error_message)
                        add_to_history(action_entry, "error", error_message)
                        return False
            except ValueError:
                error_message = f"Invalid API limit format: {action_type}"
                scheduler_logger.error(error_message)
                add_to_history(action_entry, "error", error_message)
                return False
        
        # Mark this action as executed for today
        last_executed_actions[execution_key] = datetime.datetime.now()
        return True
    
    except Exception as e:
        scheduler_logger.error(f"Error executing action {action_type} for {app_type}: {e}")
        scheduler_logger.error(traceback.format_exc())
        return False

def should_execute_schedule(schedule_entry):
    """Check if a schedule entry should be executed now"""
    schedule_id = schedule_entry.get("id", "unknown")
    
    # Debug log the schedule we're checking
    scheduler_logger.debug(f"Checking if schedule {schedule_id} should be executed")
    
    if not schedule_entry.get("enabled", True):
        scheduler_logger.debug(f"Schedule {schedule_id} is disabled, skipping")
        return False
    
    # Check if specific days are configured
    days = schedule_entry.get("days", [])
    scheduler_logger.debug(f"Schedule {schedule_id} days: {days}")
    
    # If days array is empty, treat as "run every day"
    if not days:
        scheduler_logger.debug(f"Schedule {schedule_id} has no days specified, treating as 'run every day'")
    else:
        # If days array is not empty, check if today is in the list
        current_day = datetime.datetime.now().strftime("%A").lower()  # e.g., 'monday'
        
        # Debug what's being compared - print EXACTLY what we're comparing
        scheduler_logger.info(f"CRITICAL DEBUG - Today: '{current_day}', Schedule days: {days}")
        
        # Convert all days to lowercase for comparison
        lowercase_days = [str(day).lower() for day in days]
        scheduler_logger.info(f"CRITICAL DEBUG - Lowercase days: {lowercase_days}")
        
        # Direct check if current_day (lowercase) is in the lowercase days
        if current_day in lowercase_days:
            scheduler_logger.info(f"SUCCESS: Schedule {schedule_id} IS configured to run on {current_day}")
            return True
        else:
            scheduler_logger.info(f"FAILURE: Schedule {schedule_id} not configured to run on {current_day}, skipping")
            return False

    
    current_time = datetime.datetime.now()
    schedule_hour = schedule_entry.get("time", {}).get("hour")
    schedule_minute = schedule_entry.get("time", {}).get("minute")
    
    scheduler_logger.debug(f"Schedule {schedule_id} time: {schedule_hour}:{schedule_minute}, current time: {current_time.hour}:{current_time.minute}")
    
    if schedule_hour is None or schedule_minute is None:
        scheduler_logger.warning(f"Schedule entry missing time information: {schedule_entry}")
        return False
    
    # Check if the current time matches the scheduled time
    # Use a 5-minute window to ensure we don't miss it
    if current_time.hour == schedule_hour:
        # Execute if we're within 5 minutes after the scheduled time
        # This handles cases where the scheduler isn't running exactly at the specified time
        should_execute = current_time.minute >= schedule_minute and current_time.minute < schedule_minute + 5
        scheduler_logger.debug(f"Current hour matches schedule hour. Within 5-minute window? {should_execute}")
        return should_execute
    
    scheduler_logger.debug(f"Current hour {current_time.hour} doesn't match schedule hour {schedule_hour}, skipping")
    return False

def check_and_execute_schedules():
    """Check all schedules and execute those that should run now"""
    try:
        # Format time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scheduler_logger.info(f"Checking schedules at {current_time}")
        
        # Check if schedule file exists and log its status
        if not os.path.exists(SCHEDULE_FILE):
            scheduler_logger.warning(f"Schedule file does not exist: {SCHEDULE_FILE}")
            add_to_history({"action": "check"}, "warning", f"Schedule file not found at {SCHEDULE_FILE}")
            return
        
        scheduler_logger.info(f"Schedule file exists at {SCHEDULE_FILE} with size {os.path.getsize(SCHEDULE_FILE)} bytes")
        
        # Load the schedule
        schedule_data = load_schedule()
        if not schedule_data:
            scheduler_logger.warning("No schedule data available")
            add_to_history({"action": "check"}, "warning", "No schedule data available")
            return
        
        # Log schedule data summary
        schedule_summary = {app: len(schedules) for app, schedules in schedule_data.items()}
        scheduler_logger.info(f"Loaded schedules: {schedule_summary}")
        
        # Add to history that we've checked schedules
        add_to_history({"action": "check"}, "info", f"Checking schedules at {current_time}")
        
        # Initialize counter for schedules found
        schedules_found = 0
        
        # Check for schedules to execute
        for app_type, schedules in schedule_data.items():
            for schedule_entry in schedules:
                schedules_found += 1
                if should_execute_schedule(schedule_entry):
                    # Check if we already executed this entry in the last 5 minutes
                    entry_id = schedule_entry.get("id")
                    if entry_id and entry_id in last_executed_actions:
                        last_time = last_executed_actions[entry_id]
                        now = datetime.datetime.now()
                        delta = (now - last_time).total_seconds() / 60  # Minutes
                        
                        if delta < 5:  # Don't re-execute if less than 5 minutes have passed
                            scheduler_logger.info(f"Skipping recently executed schedule '{entry_id}' ({delta:.1f} minutes ago)")
                            add_to_history(
                                schedule_entry, 
                                "skipped", 
                                f"Already executed {delta:.1f} minutes ago"
                            )
                            continue
                    
                    # Execute the action
                    schedule_entry["appType"] = app_type
                    execute_action(schedule_entry)
                    
                    # Update last executed time
                    if entry_id:
                        last_executed_actions[entry_id] = datetime.datetime.now()
        
        if schedules_found == 0:
            scheduler_logger.warning("No schedules found in the configuration")
            add_to_history({"action": "check"}, "warning", "No schedules found in the configuration")
    
    except Exception as e:
        error_msg = f"Error checking schedules: {e}"
        scheduler_logger.error(error_msg)
        scheduler_logger.error(traceback.format_exc())
        add_to_history({"action": "check"}, "error", error_msg)

def scheduler_loop():
    """Main scheduler loop - runs in a background thread"""
    scheduler_logger.info("Scheduler engine started")
    
    # Clean up expired entries from last_executed_actions
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    for key in list(last_executed_actions.keys()):
        if last_executed_actions[key] < yesterday:
            del last_executed_actions[key]
    
    while not stop_event.is_set():
        try:
            check_and_execute_schedules()
            
            # Sleep until the next check
            stop_event.wait(SCHEDULE_CHECK_INTERVAL)
            
        except Exception as e:
            scheduler_logger.error(f"Error in scheduler loop: {e}")
            scheduler_logger.error(traceback.format_exc())
            # Sleep briefly to avoid rapidly repeating errors
            time.sleep(5)
    
    scheduler_logger.info("Scheduler engine stopped")

def get_execution_history():
    """Get the execution history for the scheduler"""
    return list(execution_history)

def start_scheduler():
    """Start the scheduler engine"""
    global scheduler_thread
    
    if scheduler_thread and scheduler_thread.is_alive():
        scheduler_logger.info("Scheduler already running")
        return
    
    # Reset the stop event
    stop_event.clear()
    
    # Create and start the scheduler thread
    scheduler_thread = threading.Thread(target=scheduler_loop, name="SchedulerEngine", daemon=True)
    scheduler_thread.start()
    
    # Add a startup entry to the history
    startup_entry = {
        "id": "system",
        "action": "startup",
        "app": "scheduler"
    }
    add_to_history(startup_entry, "info", "Scheduler engine started")
    
    scheduler_logger.info(f"Scheduler engine started. Thread is alive: {scheduler_thread.is_alive()}")
    return True

def stop_scheduler():
    """Stop the scheduler engine"""
    global scheduler_thread
    
    if not scheduler_thread or not scheduler_thread.is_alive():
        scheduler_logger.info("Scheduler not running")
        return
    
    # Signal the thread to stop
    stop_event.set()
    
    # Wait for the thread to terminate (with timeout)
    scheduler_thread.join(timeout=5.0)
    
    if scheduler_thread.is_alive():
        scheduler_logger.warning("Scheduler did not terminate gracefully")
    else:
        scheduler_logger.info("Scheduler stopped gracefully")
