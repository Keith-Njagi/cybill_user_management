from flask import request

from .platform_fetcher import compute_platform_version


def generate_device_data():
    user_agent = str(request.user_agent)
    user_agent_platform = request.user_agent.platform
    device_os = compute_platform_version(user_agent, user_agent_platform)
    if device_os is None:
        return{'error': 'This request has been rejected. Please use a recognised device'}
    return {'device_os': device_os}

