from api.services.env import variables
from api.services.logging import get_logger


class CorsMiddleware:
    def __init__(self, get_response):
        # One-time configuration and initialization.
        self.logger = get_logger(__name__)
        self.logger.info(f"CORS Application Backend URL: {self.get_application_url()}")

        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        # Prepares the list of allowed hosts to determine the origin response
        allowed_hosts = [
            "http://localhost:5000",
            "http://localhost:8080",
            self.get_application_url(),
            self.get_application_url("api"),
        ]
        origin = request.headers['Origin'] if 'Origin' in request.headers else ''
        response["Access-Control-Allow-Origin"] = origin if origin in allowed_hosts else 'null'

        # In addition to the CORS-safelisted request headers, the following are also allowed
        allowed_headers = [
            "Content-Type",
            "Authorization",
        ]
        response["Access-Control-Allow-Headers"] = ", ".join(allowed_headers)

        response["Access-Control-Allow-Methods"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Max-Age"] = 7200

        return response

    @staticmethod
    def get_application_url(subdomain: str = "") -> str:
        protocol = "https" if variables.get("LETSENCRYPT_HOST") is not None else "http"
        host = variables.get("APPLICATION_HOST")
        subdomain_with_dot = f"{subdomain}." if subdomain != "" else ""

        return f"{protocol}://{subdomain_with_dot}{host}"
