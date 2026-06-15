"""
API Usage Configuration

Controls how aggressively the system uses AI for report generation.
Adjust these settings based on your API quota and requirements.
"""
import os

# ══════════════════════════════════════════════════════════════════════════════
# API USAGE MODES
# ══════════════════════════════════════════════════════════════════════════════

# Mode options: "production", "balanced", "conservative"
API_USAGE_MODE = os.getenv("API_USAGE_MODE", "balanced")

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION PROFILES
# ══════════════════════════════════════════════════════════════════════════════

USAGE_PROFILES = {
    "production": {
        "description": "Full AI for all reports - highest quality, high API usage",
        "cooldowns": {
            "CRITICAL": 0,      # Immediate
            "HIGH": 600,        # 10 minutes
            "MEDIUM": 1800,     # 30 minutes
            "LOW": 3600,        # 1 hour
        },
        "use_ai_for": ["CRITICAL", "HIGH", "MEDIUM"],
        "enable_caching": True,
        "max_reports_per_hour": 20,
    },
    
    "balanced": {
        "description": "AI for critical issues, templates for routine - good balance (DEFAULT for free tier)",
        "cooldowns": {
            "CRITICAL": 0,      # Immediate
            "HIGH": 1800,       # 30 minutes  
            "MEDIUM": 3600,     # 1 hour
            "LOW": 7200,        # 2 hours
        },
        "use_ai_for": ["CRITICAL", "HIGH"],  # MEDIUM uses templates
        "enable_caching": True,
        "max_reports_per_hour": 6,  # ~150 per day max
    },
    
    "conservative": {
        "description": "Minimal API usage - only CRITICAL alerts use AI",
        "cooldowns": {
            "CRITICAL": 300,    # 5 minutes (even critical has cooldown)
            "HIGH": 3600,       # 1 hour
            "MEDIUM": 7200,     # 2 hours
            "LOW": 14400,       # 4 hours
        },
        "use_ai_for": ["CRITICAL"],  # Only CRITICAL uses AI
        "enable_caching": True,
        "max_reports_per_hour": 3,  # ~70 per day max
    },
}


def get_api_config():
    """Get current API usage configuration"""
    mode = API_USAGE_MODE.lower()
    
    if mode not in USAGE_PROFILES:
        print(f"⚠️ Unknown API_USAGE_MODE '{mode}', falling back to 'balanced'")
        mode = "balanced"
    
    config = USAGE_PROFILES[mode]
    print(f"📊 API Usage Mode: {mode.upper()} - {config['description']}")
    
    return config


def should_use_ai_for_severity(severity: str) -> bool:
    """Determine if AI should be used for this severity level"""
    config = get_api_config()
    return severity in config["use_ai_for"]


def get_cooldown_seconds(severity: str) -> int:
    """Get cooldown period for severity level"""
    config = get_api_config()
    return config["cooldowns"].get(severity, 3600)


def is_caching_enabled() -> bool:
    """Check if response caching is enabled"""
    config = get_api_config()
    return config["enable_caching"]


# ══════════════════════════════════════════════════════════════════════════════
# API QUOTA MONITORING (Optional - for future use)
# ══════════════════════════════════════════════════════════════════════════════

_api_calls_this_hour = 0
_hour_start_time = None


def track_api_call():
    """Track API call for quota monitoring"""
    global _api_calls_this_hour, _hour_start_time
    from datetime import datetime
    
    now = datetime.now()
    
    # Reset counter every hour
    if _hour_start_time is None or (now - _hour_start_time).seconds >= 3600:
        _api_calls_this_hour = 0
        _hour_start_time = now
    
    _api_calls_this_hour += 1
    
    config = get_api_config()
    max_calls = config["max_reports_per_hour"]
    
    if _api_calls_this_hour > max_calls:
        print(f"⚠️ WARNING: API quota exceeded ({_api_calls_this_hour}/{max_calls} calls this hour)")
    
    return _api_calls_this_hour


def get_api_usage_stats():
    """Get current API usage statistics"""
    global _api_calls_this_hour, _hour_start_time
    from datetime import datetime
    
    config = get_api_config()
    
    time_remaining = 3600
    if _hour_start_time:
        time_remaining = 3600 - (datetime.now() - _hour_start_time).seconds
    
    return {
        "calls_this_hour": _api_calls_this_hour,
        "max_calls_per_hour": config["max_reports_per_hour"],
        "remaining_calls": config["max_reports_per_hour"] - _api_calls_this_hour,
        "quota_percentage": (_api_calls_this_hour / config["max_reports_per_hour"]) * 100,
        "time_until_reset_seconds": time_remaining,
        "mode": API_USAGE_MODE,
    }
