"""
Windows path fix for Huntarr
Ensures that config paths work correctly on Windows systems
"""

import os
import sys
import logging
import traceback
from pathlib import Path, PurePath
import platform
import json
import builtins
import importlib
import shutil

def setup_windows_paths():
    """
    Setup Windows-specific paths for Huntarr
    This function ensures that the config directory is properly created and accessible
    on Windows, resolving potential 500 errors related to path issues.
    """
    # Set up basic logging to stdout in case file logging isn't working yet
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("WindowsPathFix")
    
    try:
        # When running as installed app or PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle
            app_path = os.path.dirname(sys.executable)
            logger.info(f"Running as PyInstaller bundle from: {app_path}")
            
            # Alternative paths to try if the default doesn't work
            alt_paths = [
                app_path,
                os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 'Huntarr'),
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\' + os.environ.get('USERNAME', 'Default') + '\\AppData\\Local'), 'Huntarr')
            ]
        else:
            # Running as script
            app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            logger.info(f"Running as script from: {app_path}")
            alt_paths = [app_path]
        
        # Try the primary path first
        config_dir = os.path.join(app_path, 'config')
        
        # Try to create the config directory and test if it's writable
        success = False
        error_messages = []
        
        for path in alt_paths:
            try:
                config_dir = os.path.join(path, 'config')
                logger.info(f"Attempting to use config directory: {config_dir}")
                
                # Create directory if it doesn't exist
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)
                    logger.info(f"Created config directory at: {config_dir}")
                
                # Test if directory is writable by creating a test file
                test_file = os.path.join(config_dir, 'write_test.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                
                if os.path.exists(test_file):
                    os.remove(test_file)
                    success = True
                    logger.info(f"Successfully verified write access to: {config_dir}")
                    break
            except Exception as e:
                error_msg = f"Failed to use config directory {config_dir}: {str(e)}"
                logger.warning(error_msg)
                error_messages.append(error_msg)
                continue
        
        if not success:
            # If all paths failed, try user's home directory as last resort
            try:
                home_dir = str(Path.home())
                config_dir = os.path.join(home_dir, 'Huntarr', 'config')
                logger.warning(f"All standard paths failed, trying home directory: {config_dir}")
                
                if not os.path.exists(config_dir):
                    os.makedirs(config_dir)
                
                test_file = os.path.join(config_dir, 'write_test.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                
                if os.path.exists(test_file):
                    os.remove(test_file)
                    success = True
                    logger.info(f"Successfully using home directory fallback: {config_dir}")
            except Exception as e:
                error_msg = f"Failed to use home directory fallback: {str(e)}"
                logger.error(error_msg)
                error_messages.append(error_msg)
        
        # Set up file logging now that we have a logs directory
        logs_dir = os.path.join(config_dir, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
        log_file = os.path.join(logs_dir, 'windows_path.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

        if not success:
            logger.error("CRITICAL: Could not find a writable location for config directory!")
            logger.error("Errors encountered: " + "\n".join(error_messages))
            return None
        
        # Set up environment variables to ensure consistent path usage throughout the application
        os.environ['HUNTARR_CONFIG_DIR'] = config_dir
        os.environ['HUNTARR_LOGS_DIR'] = logs_dir
        os.environ['HUNTARR_USER_DIR'] = os.path.join(config_dir, 'user')
        os.environ['HUNTARR_STATEFUL_DIR'] = os.path.join(config_dir, 'stateful')
        
        # Create other needed directories
        needed_dirs = ['user', 'stateful', 'settings', 'scheduler', 'tally']
        for dir_name in needed_dirs:
            dir_path = os.path.join(config_dir, dir_name)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logger.info(f"Created directory: {dir_path}")

        # Ensure templates directory exists and has necessary files
        templates_dir = os.path.join(app_path, "templates")
        static_dir = os.path.join(app_path, "static")
        
        try:
            # Create templates and static directories if they don't exist
            if not os.path.exists(templates_dir):
                os.makedirs(templates_dir)
                logger.info(f"Created templates directory at: {templates_dir}")
                
            if not os.path.exists(static_dir):
                os.makedirs(static_dir)
                logger.info(f"Created static directory at: {static_dir}")
            
            # Create essential static subdirectories for CSS and JS
            css_dir = os.path.join(static_dir, "css")
            js_dir = os.path.join(static_dir, "js")
            logo_dir = os.path.join(static_dir, "logo")
            
            for dir_path in [css_dir, js_dir, logo_dir]:
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    logger.info(f"Created static subdirectory at: {dir_path}")
                
            # IMPORTANT: Extract templates from setup_html.py
            try:
                logger.info("Attempting to extract templates from setup_html module")
                from src.primary.setup_html import extract_templates, SETUP_HTML, INDEX_HTML
                
                # Extract templates directly to the templates directory
                extract_templates(templates_dir)
                logger.info(f"Templates extracted successfully to {templates_dir}")
                
                # Verify the templates were created correctly
                setup_html_path = os.path.join(templates_dir, 'setup.html')
                index_html_path = os.path.join(templates_dir, 'index.html')
                
                if os.path.exists(setup_html_path) and os.path.exists(index_html_path):
                    logger.info("Verified template files exist")
                else:
                    # If extract_templates failed to create the files, create them directly
                    if not os.path.exists(setup_html_path):
                        logger.info("Creating setup.html directly")
                        with open(setup_html_path, 'w') as f:
                            f.write(SETUP_HTML)
                    
                    if not os.path.exists(index_html_path):
                        logger.info("Creating index.html directly")
                        with open(index_html_path, 'w') as f:
                            f.write(INDEX_HTML)
                            
                    logger.info("Created template files directly")
                
                # Create essential CSS and JS files
                bootstrap_css_path = os.path.join(css_dir, "bootstrap.min.css")
                if not os.path.exists(bootstrap_css_path):
                    with open(bootstrap_css_path, 'w') as f:
                        f.write("""/*!
 * Bootstrap v5.1.3 (https://getbootstrap.com/)
 * Copyright 2011-2021 The Bootstrap Authors
 * Copyright 2011-2021 Twitter, Inc.
 * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
 */:root{--bs-blue:#0d6efd;--bs-indigo:#6610f2;--bs-purple:#6f42c1;--bs-pink:#d63384;--bs-red:#dc3545;--bs-orange:#fd7e14;--bs-yellow:#ffc107;--bs-green:#198754;--bs-teal:#20c997;--bs-cyan:#0dcaf0;--bs-white:#fff;--bs-gray:#6c757d;--bs-gray-dark:#343a40;--bs-gray-100:#f8f9fa;--bs-gray-200:#e9ecef;--bs-gray-300:#dee2e6;--bs-gray-400:#ced4da;--bs-gray-500:#adb5bd;--bs-gray-600:#6c757d;--bs-gray-700:#495057;--bs-gray-800:#343a40;--bs-gray-900:#212529;--bs-primary:#0d6efd;--bs-secondary:#6c757d;--bs-success:#198754;--bs-info:#0dcaf0;--bs-warning:#ffc107;--bs-danger:#dc3545;--bs-light:#f8f9fa;--bs-dark:#212529;--bs-primary-rgb:13,110,253;--bs-secondary-rgb:108,117,125;--bs-success-rgb:25,135,84;--bs-info-rgb:13,202,240;--bs-warning-rgb:255,193,7;--bs-danger-rgb:220,53,69;--bs-light-rgb:248,249,250;--bs-dark-rgb:33,37,41;--bs-white-rgb:255,255,255;--bs-black-rgb:0,0,0;--bs-body-color-rgb:33,37,41;--bs-body-bg-rgb:255,255,255;--bs-font-sans-serif:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans","Liberation Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji";--bs-font-monospace:SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace;--bs-gradient:linear-gradient(180deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0));--bs-body-font-family:var(--bs-font-sans-serif);--bs-body-font-size:1rem;--bs-body-font-weight:400;--bs-body-line-height:1.5;--bs-body-color:#212529;--bs-body-bg:#fff}*,::after,::before{box-sizing:border-box}@media (prefers-reduced-motion:no-preference){:root{scroll-behavior:smooth}}body{margin:0;font-family:var(--bs-body-font-family);font-size:var(--bs-body-font-size);font-weight:var(--bs-body-font-weight);line-height:var(--bs-body-line-height);color:var(--bs-body-color);text-align:var(--bs-body-text-align);background-color:var(--bs-body-bg);-webkit-text-size-adjust:100%;-webkit-tap-highlight-color:transparent}hr{margin:1rem 0;color:inherit;background-color:currentColor;border:0;opacity:.25}hr:not([size]){height:1px}h1,h2,h3,h4,h5,h6{margin-top:0;margin-bottom:.5rem;font-weight:500;line-height:1.2}h1{font-size:calc(1.375rem + 1.5vw)}@media (min-width:1200px){h1{font-size:2.5rem}}h2{font-size:calc(1.325rem + .9vw)}@media (min-width:1200px){h2{font-size:2rem}}h3{font-size:calc(1.3rem + .6vw)}@media (min-width:1200px){h3{font-size:1.75rem}}h4{font-size:calc(1.275rem + .3vw)}@media (min-width:1200px){h4{font-size:1.5rem}}h5{font-size:1.25rem}h6{font-size:1rem}p{margin-top:0;margin-bottom:1rem}""")
                    logger.info(f"Created bootstrap.min.css at: {bootstrap_css_path}")
                
                style_css_path = os.path.join(css_dir, "style.css")
                if not os.path.exists(style_css_path):
                    with open(style_css_path, 'w') as f:
                        f.write("""
/* Custom styles for Huntarr */
body {
    background-color: #121212 !important;
    color: #f8f9fa !important;
}
.bg-black {
    background-color: #000 !important;
}
.card-header {
    font-weight: bold;
}
.navbar {
    background-color: #000000 !important;
}
.bg-dark {
    background-color: #1a1d24 !important;
}
.bg-secondary {
    background-color: #252a34 !important;
}
.bg-primary {
    background-color: #0e639c !important;
}
.card {
    margin-bottom: 1rem;
    border: 1px solid #2c3038;
}
.btn-primary {
    background-color: #0e639c !important;
    border-color: #0e639c !important;
}
.btn-success {
    background-color: #198754 !important;
    border-color: #198754 !important;
}
.form-control {
    background-color: #2c3038 !important;
    color: #f8f9fa !important;
    border: 1px solid #444;
}
.form-control:focus {
    background-color: #3c3f48 !important;
    color: #f8f9fa !important;
}
a {
    color: #0dcaf0;
}
.text-light {
    color: #adb5bd !important;
}
.table-dark {
    background-color: #252a34 !important;
}
""")
                    logger.info(f"Created style.css at: {style_css_path}")
                
                bootstrap_js_path = os.path.join(js_dir, "bootstrap.bundle.min.js")
                if not os.path.exists(bootstrap_js_path):
                    with open(bootstrap_js_path, 'w') as f:
                        f.write("""/*!
 * Bootstrap v5.1.3 (https://getbootstrap.com/)
 * Copyright 2011-2021 The Bootstrap Authors (https://github.com/twbs/bootstrap/graphs/contributors)
 * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
 */
!function(t,e){"object"==typeof exports&&"undefined"!=typeof module?module.exports=e():"function"==typeof define&&define.amd?define(e):(t="undefined"!=typeof globalThis?globalThis:t||self).bootstrap=e()}(this,(function(){"use strict";const t="transitionend",e=t=>{let e=t.getAttribute("data-bs-target");if(!e||"#"===e){let i=t.getAttribute("href");if(!i||!i.includes("#")&&!i.startsWith("."))return null;i.includes("#")&&!i.startsWith("#")&&(i=`#${i.split("#")[1]}`),e=i&&"#"!==i?i.trim():null}return e},i=t=>{const i=e(t);return i&&document.querySelector(i)?i:null},n=t=>{const i=e(t);return i?document.querySelector(i):null},s=t=>{t.dispatchEvent(new Event(n))};return{dropdown:{setDropdownList:function(){},clearDropdownList:function(){}}}}))""")
                    logger.info(f"Created bootstrap.bundle.min.js at: {bootstrap_js_path}")
                
                # Create a minimal logo file
                logo_file = os.path.join(logo_dir, "256.png")
                if not os.path.exists(logo_file):
                    try:
                        # Add base64 encoded small logo
                        import base64
                        logo_data = "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"
                        logo_bytes = base64.b64decode(logo_data)
                        with open(logo_file, 'wb') as f:
                            f.write(logo_bytes)
                        logger.info(f"Created logo file at: {logo_file}")
                    except Exception as e:
                        logger.error(f"Error creating logo file: {str(e)}")
            except Exception as e:
                logger.error(f"Error extracting templates from setup_html: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Fallback: Try to copy from source directory
                try:
                    # Try to copy template files from frontend directory as a fallback
                    frontend_dir = os.path.join(app_path, "src", "frontend")
                    if os.path.exists(frontend_dir):
                        logger.info(f"Attempting to copy frontend files from {frontend_dir}")
                        
                        # Copy all files from frontend/templates to templates
                        frontend_templates = os.path.join(frontend_dir, "templates")
                        if os.path.exists(frontend_templates):
                            for file in os.listdir(frontend_templates):
                                src_file = os.path.join(frontend_templates, file)
                                dest_file = os.path.join(templates_dir, file)
                                if os.path.isfile(src_file):
                                    shutil.copy2(src_file, dest_file)
                                    logger.info(f"Copied template file: {file}")
                        
                        # Copy all files from frontend/static to static
                        frontend_static = os.path.join(frontend_dir, "static")
                        if os.path.exists(frontend_static):
                            for root, dirs, files in os.walk(frontend_static):
                                for file in files:
                                    src_file = os.path.join(root, file)
                                    rel_path = os.path.relpath(src_file, frontend_static)
                                    dest_file = os.path.join(static_dir, rel_path)
                                    dest_dir = os.path.dirname(dest_file)
                                    if not os.path.exists(dest_dir):
                                        os.makedirs(dest_dir)
                                    shutil.copy2(src_file, dest_file)
                                    logger.info(f"Copied static file: {rel_path}")
                except Exception as fallback_error:
                    logger.error(f"Error in fallback template copy: {str(fallback_error)}")
        except Exception as e:
            logger.error(f"Error setting up template directories: {str(e)}")

        # Create a translation function to convert /config paths to Windows paths
        def convert_unix_to_windows_path(original_path):
            if original_path is None:
                return None
                
            # Convert to string if it's a Path object
            if isinstance(original_path, PurePath):
                original_path = str(original_path)
                
            # Only process string paths
            if isinstance(original_path, str):
                if original_path.startswith('/config'):
                    return original_path.replace('/config', config_dir).replace('/', '\\')
                elif original_path.startswith('\\config'):
                    return original_path.replace('\\config', config_dir)
                
            return original_path
        
        # Add a startswith method to the PathLib Path class if needed
        if platform.system() == 'Windows' and not hasattr(Path, 'startswith'):
            # Create a safer monkey patch that doesn't mess with internal attributes
            original_path_str = Path.__str__
            
            def patch_startswith(self, prefix):
                return str(self).startswith(prefix)
                
            # Add the startswith method to Path
            Path.startswith = patch_startswith
            
            logger.info("Added startswith method to Path class")
            
        # Create json config files
        for app in ['sonarr', 'radarr', 'lidarr', 'readarr', 'whisparr', 'swaparr', 'eros', 'general']:
            json_file = os.path.join(config_dir, f'{app}.json')
            if not os.path.exists(json_file):
                try:
                    with open(json_file, 'w') as f:
                        f.write('{}')
                    logger.info(f"Created empty settings file: {json_file}")
                except Exception as e:
                    logger.error(f"Error creating settings file {json_file}: {str(e)}")
                    
        # Create empty scheduler file
        scheduler_file = os.path.join(config_dir, 'scheduler', 'schedule.json')
        if not os.path.exists(scheduler_file):
            try:
                scheduler_dir = os.path.dirname(scheduler_file)
                if not os.path.exists(scheduler_dir):
                    os.makedirs(scheduler_dir)
                with open(scheduler_file, 'w') as f:
                    f.write('{"schedules":[]}')
                logger.info(f"Created empty scheduler file: {scheduler_file}")
            except Exception as e:
                logger.error(f"Error creating scheduler file {scheduler_file}: {str(e)}")
                
        # Create tally tracking files
        tally_dir = os.path.join(config_dir, 'tally')
        if not os.path.exists(tally_dir):
            os.makedirs(tally_dir)
            
        media_stats_file = os.path.join(tally_dir, 'media_stats.json')
        if not os.path.exists(media_stats_file):
            try:
                with open(media_stats_file, 'w') as f:
                    f.write('{}')
                logger.info(f"Created empty media stats file: {media_stats_file}")
            except Exception as e:
                logger.error(f"Error creating media stats file {media_stats_file}: {str(e)}")
                
        hourly_cap_file = os.path.join(tally_dir, 'hourly_cap.json')
        if not os.path.exists(hourly_cap_file):
            try:
                with open(hourly_cap_file, 'w') as f:
                    f.write('{}')
                logger.info(f"Created empty hourly cap file: {hourly_cap_file}")
            except Exception as e:
                logger.error(f"Error creating hourly cap file {hourly_cap_file}: {str(e)}")
        
        # Monkey patch the open function and os.path operations
        original_open = builtins.open
        
        def patched_open(file, *args, **kwargs):
            # Skip binary files (prevent errors with non-string file paths)
            if len(args) > 0 and 'b' in args[0]:
                return original_open(file, *args, **kwargs)
                
            try:
                # Convert the path if it's a string or Path object
                if isinstance(file, (str, PurePath)):
                    converted_path = convert_unix_to_windows_path(file)
                    return original_open(converted_path, *args, **kwargs)
                return original_open(file, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in patched_open with path {file}: {str(e)}")
                raise
        
        builtins.open = patched_open
        
        # Patch os.path functions
        original_exists = os.path.exists
        original_isfile = os.path.isfile
        original_isdir = os.path.isdir
        original_join = os.path.join
        
        def patched_exists(path):
            return original_exists(convert_unix_to_windows_path(path))
        
        def patched_isfile(path):
            return original_isfile(convert_unix_to_windows_path(path))
        
        def patched_isdir(path):
            return original_isdir(convert_unix_to_windows_path(path))
        
        def patched_join(path, *paths):
            # Only process the first argument (the base path)
            converted_path = convert_unix_to_windows_path(path)
            if converted_path != path:
                return original_join(converted_path, *paths)
            return original_join(path, *paths)
        
        os.path.exists = patched_exists
        os.path.isfile = patched_isfile
        os.path.isdir = patched_isdir
        os.path.join = patched_join
        
        # Fix for directory operations
        original_makedirs = os.makedirs
        original_listdir = os.listdir
        original_remove = os.remove
        
        def patched_makedirs(path, *args, **kwargs):
            return original_makedirs(convert_unix_to_windows_path(path), *args, **kwargs)
        
        def patched_listdir(path):
            return original_listdir(convert_unix_to_windows_path(path))
        
        def patched_remove(path):
            return original_remove(convert_unix_to_windows_path(path))
        
        os.makedirs = patched_makedirs
        os.listdir = patched_listdir
        os.remove = patched_remove
        
        # Modify sys.path to ensure all imports work
        if config_dir not in sys.path:
            sys.path.append(config_dir)
            
        if app_path not in sys.path:
            sys.path.append(app_path)
            
        # Set Flask environment variables 
        os.environ['FLASK_APP'] = 'src.primary.web_server'
        os.environ['TEMPLATE_FOLDER'] = templates_dir
        os.environ['STATIC_FOLDER'] = static_dir
        
        logger.info(f"Windows path setup complete. Using config dir: {config_dir}")
        return config_dir
    except Exception as e:
        logger.error(f"Windows path setup failed with error: {str(e)}")
        logger.error(traceback.format_exc())
        return None

# Call setup_windows_paths automatically when imported on Windows
if platform.system() == 'Windows':
    CONFIG_DIR = setup_windows_paths()
else:
    CONFIG_DIR = "/config"  # Default for non-Windows 