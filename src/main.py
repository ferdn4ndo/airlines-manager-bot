from modules.airplanes import fetch_all_airplanes
from modules.lines import fetch_all_lines
from modules.travel_cards_wheel import spin_travel_cards_wheel_if_available
from modules.login import get_cookies
from modules.card_holder import get_free_card_holder_if_available
from modules.workshop import get_free_workshop_items

cookies = get_cookies()

# Fetch the airplanes
airplanes = fetch_all_airplanes(cookies=cookies)

# Fetch the lines
lines = fetch_all_lines(cookies=cookies)

# Travel cards wheel
spin_travel_cards_wheel_if_available(cookies=cookies)

# Free card holder
get_free_card_holder_if_available(cookies=cookies)

# Free workshop items
get_free_workshop_items(cookies)
