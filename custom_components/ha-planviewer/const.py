DOMAIN = "planviewer"
MANUFACTURER = "Planviewer"
DEFAULT_SCAN_INTERVAL = 3600  # Example: Check every 5 minutes
CONF_MUNICIPALITY = "municipality"
CONF_INSTANCE_NAME = "instance_name"
CONF_SCAN_INTERVAL = "scan_interval"

PLATFORMS = ["sensor"]

SCRAPED_DATA_KEYS = [
    "vergunning",
    "datum_start",
    "datum_eind",
    "link",  # To store the link to the details page (optional but useful)
]
