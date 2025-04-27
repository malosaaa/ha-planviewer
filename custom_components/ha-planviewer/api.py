import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class PlanviewerApiClientError(Exception):
    """Base exception for Planviewer API client errors."""
    pass

class PlanviewerApiConnectionError(PlanviewerApiClientError):
    """Exception for connection errors."""
    pass

class PlanviewerApiNotFoundError(PlanviewerApiClientError):
    """Exception for when the municipality page is not found."""
    pass

class PlanviewerApiDataError(PlanviewerApiClientError):
    """Exception for errors while parsing data."""
    pass

class PlanviewerApiClient:
    """API client for Planviewer."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the client."""
        self._session = session

    async def async_scrape_data(self, municipality: str) -> list[dict] | None:
        """Scrape the latest announcements from Planviewer for the given municipality."""
        base_url = "https://www.planviewer.nl"  # Include the base URL here
        municipality_url = f"{base_url}/lb/overheid/{municipality}"
        announcements_data = []
        headers = {"User-Agent": "HomeAssistant Planviewer Integration"}  # Be a good citizen

        try:
            async with self._session.get(municipality_url, headers=headers) as response:
                if response.status == 404:
                    raise PlanviewerApiNotFoundError(f"Municipality page not found: {municipality_url}")
                response.raise_for_status()  # Raise an exception for bad status codes
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")

                announcement_container = soup.select_one("div.container > div:nth-child(6) > div.col-12.imro-address-list-page > div")
                if not announcement_container:
                    _LOGGER.warning(f"Could not find announcement container on {municipality_url}")
                    return []

                # Select 'a' tags that contain the specific span for the message
                announcement_items = announcement_container.select("a:has(div > span.col-10.col-sm-6.col-md-7.tbl-btm-row-icon-col)")

                if not announcement_items:
                    _LOGGER.info(f"No announcements found on {municipality_url} using specific selector.")
                    return []

                for item in announcement_items:
                    title_element = item.select_one("div > span.col-10.col-sm-6.col-md-7.tbl-btm-row-icon-col")
                    date_start_element = item.select_one("div > span:nth-child(2)")
                    date_end_element = item.select_one("div > span:nth-child(3)")
                    relative_link = item.get("href")
                    link = f"{base_url}{relative_link}"

                    full_message = ""
                    start_date = None  # Initialize start_date here
                    try:
                        slug_parts = relative_link.split('/')
                        if len(slug_parts) > 1:
                            full_message_slug = slug_parts[-1]
                            full_message = full_message_slug.replace('-', ' ').strip()
                        else:
                            full_message = title_element.text.strip() if title_element else "Announcement"
                    except Exception as err:
                        _LOGGER.warning(f"Error extracting full message from link: {link} - {err}")
                        full_message = title_element.text.strip() if title_element else "Announcement"

                    date_start_str = date_start_element.text.strip() if date_start_element else None
                    date_end_str = date_end_element.text.strip() if date_end_element else None

                    if date_start_str:
                        try:
                            start_date = datetime.strptime(date_start_str, "%d-%m-%Y")
                        except ValueError:
                            _LOGGER.warning(f"Could not parse start date: {date_start_str}")

                    if title_element and relative_link:
                        date_end = date_end_str

                        announcement_data = {
                            "vergunning": full_message,  # Use the full message from the link
                            "datum_start": start_date,
                            "datum_eind": date_end,
                            "link": link,
                        }
                        announcements_data.append(announcement_data)
                    else:
                        _LOGGER.debug(f"Skipping item without expected elements: {item}")

                # Limit to the last 3 announcements
                announcements_data = announcements_data[:3]

                return announcements_data

        except aiohttp.ClientError as err:
            raise PlanviewerApiConnectionError(f"Error connecting to Planviewer: {err}") from err
        except Exception as err:
            raise PlanviewerApiDataError(f"Error while scraping data: {err}") from err