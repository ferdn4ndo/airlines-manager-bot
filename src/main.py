from modules.airplanes import fetch_all_airplanes
from modules.lines import fetch_all_lines
from modules.login import get_cookies

cookies = get_cookies()

# Fetch the airplanes
airplanes = fetch_all_airplanes(cookies=cookies)

# Fetch the lines
lines = fetch_all_lines(cookies=cookies)
