from datetime import datetime

from api.models import Airport


class HealthService:

    def __init__(self, airports_count: int = -1, created_at : str = ""):
        self.airports_count = airports_count if airports_count != -1 else Airport.objects.count()
        self.created_at = created_at or datetime.now()
