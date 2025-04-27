"""Config flow for Planviewer integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_MUNICIPALITY, CONF_INSTANCE_NAME, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

MIN_SCAN_INTERVAL_SECONDS = 300 # 5 minutes

async def validate_municipality(hass: HomeAssistant, municipality: str) -> bool:
    """Validate if the municipality is likely valid (basic check)."""
    # For now, we'll just check if it's not empty. More sophisticated checks
    # might involve trying to access the Planviewer page for this municipality.
    return bool(municipality.strip())

def validate_scan_interval(scan_interval: int) -> bool:
    """Validate if the scan interval meets the minimum requirement."""
    return scan_interval >= MIN_SCAN_INTERVAL_SECONDS

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Planviewer."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            municipality = user_input.get(CONF_MUNICIPALITY)
            instance_name = user_input.get(CONF_INSTANCE_NAME)
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL) # Get scan interval

            if not municipality:
                errors[CONF_MUNICIPALITY] = "required"
            if not instance_name:
                errors[CONF_INSTANCE_NAME] = "required"
            if not validate_scan_interval(scan_interval): # Validate scan interval
                 errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"

            if not errors:
                for entry in self._async_current_entries():
                    if (entry.data.get(CONF_MUNICIPALITY) == municipality and
                            entry.data.get(CONF_INSTANCE_NAME) == instance_name):
                        return self.async_abort(reason="already_configured")

                if await validate_municipality(self.hass, municipality):
                    # Store municipality and instance name in data, scan interval in options
                    return self.async_create_entry(
                        title=f"Planviewer ({instance_name})",
                        data={
                            CONF_MUNICIPALITY: municipality,
                            CONF_INSTANCE_NAME: instance_name,
                        },
                         options={
                            CONF_SCAN_INTERVAL: scan_interval,
                        },
                    )
                else:
                    errors["base"] = "invalid_municipality"

        # Show form for initial setup
        data_schema = vol.Schema(
            {
                vol.Required(CONF_MUNICIPALITY): str,
                vol.Required(CONF_INSTANCE_NAME): str, # No default, user must choose
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int, # Optional with default
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a options flow for Planviewer."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Handle options flow."""
        if user_input is not None:
            scan_interval = user_input.get(CONF_SCAN_INTERVAL)

            if not validate_scan_interval(scan_interval): # Validate scan interval
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema({
                        vol.Required(
                            CONF_SCAN_INTERVAL,
                            default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                        ): int,
                    }),
                    errors={CONF_SCAN_INTERVAL: "invalid_scan_interval"},
                )

            # Update the config entry options
            return self.async_create_entry(title="", data=user_input)

        # Show the options form
        options_schema = vol.Schema({
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ): int,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )