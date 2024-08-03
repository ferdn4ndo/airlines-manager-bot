from api.services.throttling import BaseRateThrottle


class ContactThrottle(BaseRateThrottle):
    scope = 'contactThrottleScope'
