#!/usr/bin/env python3
"""
Stateful Management API Routes
Handles API endpoints for stateful management
"""

from flask import Blueprint, jsonify, request, Response
import json
from src.primary.stateful_manager import (
    get_stateful_management_info,
    reset_stateful_management,
    update_lock_expiration
)
from src.primary.utils.logger import get_logger

# Create logger
stateful_logger = get_logger("stateful")

# Create blueprint
stateful_api = Blueprint('stateful_api', __name__)

@stateful_api.route('/info', methods=['GET'])
def get_stateful_info():
    """Get information about the stateful management system."""
    try:
        info = get_stateful_management_info()
        stateful_logger.debug(f"Stateful info: {info}")
        
        # Ensure we're returning a valid JSON structure with required data
        if 'created_date' not in info or 'expires_date' not in info:
            stateful_logger.warning("Missing date information in stateful info")
            # Add default values if they don't exist
            if 'created_at' in info:
                try:
                    from datetime import datetime
                    created_date = datetime.fromtimestamp(info['created_at']).strftime("%Y-%m-%d %H:%M:%S")
                    info['created_date'] = created_date
                except Exception as e:
                    stateful_logger.error(f"Error formatting created_date: {e}")
                    info['created_date'] = "Invalid timestamp"
            else:
                info['created_date'] = "Unknown"
            
            if 'expires_at' in info:
                try:
                    from datetime import datetime
                    expires_date = datetime.fromtimestamp(info['expires_at']).strftime("%Y-%m-%d %H:%M:%S")
                    info['expires_date'] = expires_date
                except Exception as e:
                    stateful_logger.error(f"Error formatting expires_date: {e}")
                    info['expires_date'] = "Invalid timestamp"
            else:
                info['expires_date'] = "Unknown"
        
        # Add CORS headers to allow access from frontend
        response = Response(json.dumps(info))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        stateful_logger.debug("Returning stateful info with proper headers")
        return response
        
    except Exception as e:
        stateful_logger.error(f"Error getting stateful info: {e}", exc_info=True)
        # Return error response with proper headers
        error_data = {"error": str(e), "created_date": "Error", "expires_date": "Error"}
        response = Response(json.dumps(error_data), status=500)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@stateful_api.route('/reset', methods=['POST'])
def reset_stateful():
    """Reset the stateful management system."""
    try:
        success = reset_stateful_management()
        if success:
            # Add CORS headers to allow access from frontend
            response = Response(json.dumps({"success": True, "message": "Stateful management reset successfully"}))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            # Add CORS headers to allow access from frontend
            response = Response(json.dumps({"success": False, "message": "Failed to reset stateful management"}), status=500)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
    except Exception as e:
        stateful_logger.error(f"Error resetting stateful management: {e}")
        # Return error response with proper headers
        error_data = {"error": str(e)}
        response = Response(json.dumps(error_data), status=500)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

@stateful_api.route('/update-expiration', methods=['POST'])
def update_expiration():
    """Update the stateful management expiration time."""
    try:
        hours = request.json.get('hours')
        if hours is None or not isinstance(hours, int) or hours <= 0:
            stateful_logger.error(f"Invalid hours value for update-expiration: {hours}")
            # Return error response with proper headers
            error_data = {"success": False, "message": f"Invalid hours value: {hours}. Must be a positive integer."}
            response = Response(json.dumps(error_data), status=400)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        
        updated = update_lock_expiration(hours)
        if updated:
            # Get updated info
            info = get_stateful_management_info()
            # Add CORS headers to allow access from frontend
            response_data = {
                "success": True, 
                "message": f"Expiration updated to {hours} hours",
                "expires_at": info.get("expires_at"),
                "expires_date": info.get("expires_date")
            }
            response = Response(json.dumps(response_data))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            # Add CORS headers to allow access from frontend
            response = Response(json.dumps({"success": False, "message": "Failed to update expiration"}), status=500)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
    except Exception as e:
        stateful_logger.error(f"Error updating expiration: {e}", exc_info=True)
        # Return error response with proper headers
        error_data = {"success": False, "message": f"Error updating expiration: {str(e)}"}
        response = Response(json.dumps(error_data), status=500)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
