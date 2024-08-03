from api.services.throttling import BaseRateThrottle


class LoginAttemptThrottle(BaseRateThrottle):
    scope = 'loginAttemptThrottleScope'
