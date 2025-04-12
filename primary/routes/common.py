from flask import Blueprint, render_template, request, redirect, session, jsonify, send_from_directory, Response, stream_with_context
import datetime, os
from primary.auth import (
    authenticate_request, user_exists, create_user, verify_user, create_session, logout, 
    SESSION_COOKIE_NAME, is_2fa_enabled, generate_2fa_secret, verify_2fa_code, disable_2fa, 
    change_username, change_password
)
from primary import settings_manager

common_bp = Blueprint('common', __name__)
LOG_FILE = "/tmp/huntarr-logs/huntarr.log"

@common_bp.before_request
def before_common():
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

@common_bp.route('/')
def index():
    from primary.config import SLEEP_DURATION as sleep_duration
    return render_template('index.html', sleep_duration=sleep_duration)

@common_bp.route('/settings')
def settings_page():
    return render_template('index.html')

@common_bp.route('/user')
def user_page():
    return render_template('user.html')

@common_bp.route('/setup', methods=['GET'])
def setup_page():
    if user_exists():
        return redirect('/')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp} - huntarr-web - INFO - Accessed setup page - no user exists yet\n")
    return render_template('setup.html')

@common_bp.route('/login', methods=['GET'])
def login_page():
    if not user_exists():
        return redirect('/setup')
    return render_template('login.html')

@common_bp.route('/login', methods=['POST'])
def api_login_form():
    username = request.form.get('username')
    password = request.form.get('password')
    otp_code = request.form.get('otp_code')
    auth_success, needs_2fa = verify_user(username, password, otp_code)
    if auth_success:
        session_id = create_session(username)
        session[SESSION_COOKIE_NAME] = session_id
        return redirect('/')
    elif needs_2fa:
        return render_template('login.html', username=username, password=password, needs_2fa=True)
    else:
        return render_template('login.html', error="Invalid username or password")

@common_bp.route('/logout')
def logout_page():
    logout()
    return redirect('/login')

@common_bp.route('/api/setup', methods=['POST'])
def api_setup():
    if user_exists():
        return jsonify({"success": False, "message": "User already exists"}), 400
    data = request.json
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    # Add more detailed validation
    if not username:
        return jsonify({"success": False, "message": "Username is required"}), 400
    if not password:
        return jsonify({"success": False, "message": "Password is required"}), 400
    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400
    
    # Log setup attempt
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"{timestamp} - huntarr-web - INFO - Attempting to create first user: {username}\n")
    
    # Try to create user and catch specific exceptions
    try:
        success = create_user(username, password)
        if success:
            with open(LOG_FILE, 'a') as f:
                f.write(f"{timestamp} - huntarr-web - INFO - Successfully created first user\n")
            session_id = create_session(username)
            session[SESSION_COOKIE_NAME] = session_id
            return jsonify({"success": True})
        else:
            with open(LOG_FILE, 'a') as f:
                f.write(f"{timestamp} - huntarr-web - ERROR - Failed to create user\n")
            return jsonify({"success": False, "message": "Failed to create user account"}), 500
    except Exception as e:
        with open(LOG_FILE, 'a') as f:
            f.write(f"{timestamp} - huntarr-web - ERROR - Exception during user creation: {str(e)}\n")
        return jsonify({"success": False, "message": f"Error creating user: {str(e)}"}), 500

@common_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    otp_code = data.get('otp_code')
    auth_success, needs_2fa = verify_user(username, password, otp_code)
    if auth_success:
        session_id = create_session(username)
        session[SESSION_COOKIE_NAME] = session_id
        return jsonify({"success": True})
    elif needs_2fa:
        return jsonify({"success": False, "needs_2fa": True})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@common_bp.route('/api/user/2fa-status')
def api_2fa_status():
    return jsonify({"enabled": is_2fa_enabled()})

@common_bp.route('/api/user/generate-2fa')
def api_generate_2fa():
    try:
        secret, qr_code_url = generate_2fa_secret()
        return jsonify({"success": True, "secret": secret, "qr_code_url": qr_code_url})
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to generate 2FA: {str(e)}"}), 500

@common_bp.route('/api/user/verify-2fa', methods=['POST'])
def api_verify_2fa():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({"success": False, "message": "Verification code is required"}), 400
    if verify_2fa_code(code):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid verification code"}), 400

@common_bp.route('/api/user/disable-2fa', methods=['POST'])
def api_disable_2fa():
    data = request.json
    password = data.get('password')
    if not password:
        return jsonify({"success": False, "message": "Password is required"}), 400
    if disable_2fa(password):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid password"}), 400

@common_bp.route('/api/user/change-username', methods=['POST'])
def api_change_username():
    data = request.json
    current_username = data.get('current_username')
    new_username = data.get('new_username')
    password = data.get('password')
    if not current_username or not new_username or not password:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    if change_username(current_username, new_username, password):
        logout()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 400

@common_bp.route('/api/user/change-password', methods=['POST'])
def api_change_password():
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    if not current_password or not new_password:
        return jsonify({"success": False, "message": "All fields are required"}), 400
    if change_password(current_password, new_password):
        logout()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid current password"}), 400

@common_bp.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('../static', path)

@common_bp.route('/logs')
def stream_logs():
    app_type = request.args.get('app', 'sonarr')
    def generate():
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()[-100:]
                for line in lines:
                    if app_type == 'sonarr' or app_type in line.lower():
                        yield f"data: {line}\n\n"
        with open(LOG_FILE, 'r') as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    if app_type == 'sonarr' or app_type in line.lower():
                        yield f"data: {line}\n\n"
                else:
                    import time
                    time.sleep(0.1)
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@common_bp.route('/api/settings', methods=['GET'])
def get_settings():
    settings = settings_manager.get_all_settings()
    apps = ['sonarr', 'radarr', 'lidarr', 'readarr']
    
    # Get the current app type
    current_app = settings.get('app_type', 'sonarr')
    
    # Provide backward compatibility for the frontend
    # Map app-specific settings to the legacy huntarr and advanced sections
    # This ensures the UI can read settings with minimal changes
    if current_app in settings:
        if 'huntarr' not in settings:
            settings['huntarr'] = {}
        if 'advanced' not in settings:
            settings['advanced'] = {}
        
        # Copy app-specific settings to both the legacy structure and keep the app-specific structure
        for key, value in settings[current_app].items():
            # Advanced settings
            if key in ['api_timeout', 'debug_mode', 'command_wait_delay', 
                    'command_wait_attempts', 'minimum_download_queue_size',
                    'random_missing', 'random_upgrades']:
                settings['advanced'][key] = value
            # Huntarr settings
            else:
                settings['huntarr'][key] = value
    
    # Add API connection info for the current app
    for app_name in apps:
        api_url, api_key = __import__("primary.keys_manager", fromlist=[""]).get_api_keys(app_name)
        if app_name == current_app:
            settings['api_url'] = api_url
            settings['api_key'] = api_key
    
    return jsonify(settings)

@common_bp.route('/api/app-settings', methods=['GET'])
def get_app_settings():
    app_name = request.args.get('app')
    if not app_name:
        return jsonify({"success": False, "message": "App parameter required"}), 400
    api_url, api_key = __import__("primary.keys_manager", fromlist=[""]).get_api_keys(app_name)
    return jsonify({"success": True, "app": app_name, "api_url": api_url, "api_key": api_key})

@common_bp.route('/api/configured-apps', methods=['GET'])
def get_configured_apps():
    return jsonify(__import__("primary.keys_manager", fromlist=[""]).list_configured_apps())

@common_bp.route('/api/settings', methods=['POST'])
def update_settings():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        # Get the app type from the data or use 'sonarr' as default
        app_type = data.get("app_type", "sonarr")
        
        # Handle API connection info if provided
        if "api_url" in data and "api_key" in data:
            from primary import keys_manager
            keys_manager.save_api_keys(app_type, data["api_url"], data["api_key"])
        
        old_settings = settings_manager.get_all_settings()
        changes_made = False
        changes_log = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Handle app-specific settings - put all settings in the appropriate app section
        for key, value in data.items():
            # Skip special keys that are handled separately
            if key in ["api_url", "api_key", "app_type"]:
                continue
                
            # Handle nested dictionaries (like "huntarr", "advanced", "ui" categories)
            if isinstance(value, dict):
                # For backwards compatibility, map "huntarr" and "advanced" categories to the app-specific section
                if key in ["huntarr", "advanced"]:
                    for setting_key, setting_value in value.items():
                        old_value = old_settings.get(app_type, {}).get(setting_key)
                        if old_value != setting_value:
                            changes_made = True
                            changes_log.append(f"{key}.{setting_key} from {old_value} to {setting_value}")
                        
                        # Update the setting in the app-specific section
                        settings_manager.update_setting(app_type, setting_key, setting_value)
                else:
                    # For other categories like "ui" or future ones
                    for setting_key, setting_value in value.items():
                        old_value = old_settings.get(key, {}).get(setting_key)
                        if old_value != setting_value:
                            changes_made = True
                            changes_log.append(f"{key}.{setting_key} from {old_value} to {setting_value}")
                        
                        # Update the setting directly in the category
                        settings_manager.update_setting(key, setting_key, setting_value)
        
        # Log the changes
        if changes_made or ("api_url" in data and "api_key" in data):
            with open(LOG_FILE, 'a') as f:
                f.write(f"{timestamp} - huntarr-web - INFO - Settings updated by user\n")
                
                # Log connection changes if any
                if "api_url" in data and "api_key" in data:
                    api_url_masked = data["api_url"]
                    api_key_masked = "****" + data["api_key"][-4:] if len(data["api_key"]) > 4 else "****" if data["api_key"] else ""
                    f.write(f"{timestamp} - huntarr-web - INFO - Updated {app_type} API connection: URL={api_url_masked}, Key={api_key_masked}\n")
                
                # Log other changes
                for change in changes_log:
                    f.write(f"{timestamp} - huntarr-web - INFO - Changed {change}\n")
            
            # Explicitly save all settings to ensure everything is written to disk
            all_settings = settings_manager.get_all_settings()
            settings_manager.save_settings(all_settings)
            
            return jsonify({"success": True, "message": "Settings saved successfully", "changes_made": True})
        else:
            return jsonify({"success": True, "message": "No changes detected", "changes_made": False})
    except Exception as e:
        with open(LOG_FILE, 'a') as f:
            f.write(f"{timestamp} - huntarr-web - ERROR - Error saving settings: {str(e)}\n")
        return jsonify({"success": False, "message": str(e)}), 500

@common_bp.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    try:
        settings_manager.save_settings(settings_manager.DEFAULT_SETTINGS)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, 'a') as f:
            f.write(f"{timestamp} - huntarr-web - INFO - Settings reset to defaults by user\n")
        return jsonify({"success": True, "message": "Settings reset to defaults successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@common_bp.route('/api/settings/theme', methods=['GET'])
def get_theme():
    dark_mode = settings_manager.get_setting("ui", "dark_mode", True)
    return jsonify({"dark_mode": dark_mode})

@common_bp.route('/api/settings/theme', methods=['POST'])
def update_theme():
    try:
        data = request.json
        old_value = settings_manager.get_setting("ui", "dark_mode", True)
        if "dark_mode" in data and old_value != data["dark_mode"]:
            settings_manager.update_setting("ui", "dark_mode", data["dark_mode"])
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_mode = 'Dark' if data['dark_mode'] else 'Light'
            with open(LOG_FILE, 'a') as f:
                f.write(f"{timestamp} - huntarr-web - INFO - Changed theme to {new_mode} Mode\n")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
