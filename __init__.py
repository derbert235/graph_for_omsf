from .const import DOMAIN

async def async_setup_entry(hass, entry):
    """Set up graph_for_omsf from a Config Entry (UI)."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass, entry):
    """Unload the config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
