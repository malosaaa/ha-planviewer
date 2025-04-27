"""The Planviewer integration."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PlanviewerApiClient
from .const import DOMAIN, CONF_MUNICIPALITY, PLATFORMS, DEFAULT_SCAN_INTERVAL, CONF_SCAN_INTERVAL
from .coordinator import PlanviewerDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Planviewer from a config entry."""
    _LOGGER.debug("Setting up Planviewer entry: %s", entry.entry_id)
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    api_client = PlanviewerApiClient(session)

    scan_interval_seconds = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = PlanviewerDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
    )

    # Store the config entry in the coordinator (you might need this later)
    coordinator.config_entry = entry

    # Fetch initial data so we have it when entities are set up
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms (sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up listener for options updates (scan interval)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Planviewer entry: %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("Successfully unloaded Planviewer entry: %s", entry.entry_id)

    return unload_ok

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug("Reloading Planviewer entry due to options update: %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id) # Reload entry to apply new options