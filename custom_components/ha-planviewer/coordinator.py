"""DataUpdateCoordinator for Planviewer."""
import asyncio
from datetime import timedelta, datetime, timezone
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import (
    PlanviewerApiClient,
    PlanviewerApiConnectionError,
    PlanviewerApiNotFoundError,
)
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class PlanviewerDataUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator for Planviewer."""

    _last_update_error: Exception | None = None # Instance variable
    last_data: list[dict] | None = None # Store last successful data

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize DataUpdateCoordinator."""
        self.api_client = PlanviewerApiClient(session=hass.helpers.aiohttp_client.async_get_clientsession())
        self.config_entry = config_entry
        self.municipality = config_entry.data["municipality"]
        self.last_update_success = False
        self.last_update_success_timestamp: datetime | None = None
        self._error_count = 0
        scan_interval_seconds = config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval_seconds), # Use the value from options
        )

    @property
    def error_count(self) -> int:
        """Return the number of consecutive errors."""
        return self._error_count

    @property
    def last_update_error(self) -> Exception | None:
        """Return the last update error."""
        return self._last_update_error

    async def _async_update_data(self) -> list[dict] | None:
        """Update data via library."""
        _LOGGER.debug("Fetching Planviewer data for %s", self.municipality)
        try:
            data = await self.api_client.async_scrape_data(self.municipality)
            self._last_update_error = None
            self._error_count = 0
            if data is not None:
                self.last_update_success_timestamp = dt_util.utcnow() # Using UTC now for consistency
                self.last_data = data # Store the new data
                return data
            else:
                _LOGGER.debug("No data received from Planviewer for %s", self.municipality)
                return self.last_data # Return previous data if available
        except PlanviewerApiConnectionError as err:
            self._last_update_error = err
            self._error_count += 1
            _LOGGER.error("Error communicating with Planviewer API: %s", err)
            return self.last_data # Return previous data on error
        except PlanviewerApiNotFoundError as err:
            self._last_update_error = err
            self._error_count += 1
            _LOGGER.warning("Planviewer page not found for municipality: %s", self.municipality)
            return self.last_data # Return previous data on error
        except Exception as err:
            self._last_update_error = err
            self._error_count += 1
            _LOGGER.error("Error fetching Planviewer data: %s", err)
            return self.last_data # Return previous data on error