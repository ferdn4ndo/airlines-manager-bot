from api.services.throttling import BaseRateThrottle


class EmailValidationRateThrottle(BaseRateThrottle):
    scope = 'emailValidationThrottleScope'
