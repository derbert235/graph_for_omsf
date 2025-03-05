import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    CONF_PEAKTIME_SENSORS,
    CONF_SUN_RISING,
    CONF_SUN_SETTING,
    CONF_ENERGY_REDUZIERT,
    DEFAULT_ENERGY_REDUZIERT
)

class SolarForecastConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für graph_for_omsf."""
    VERSION = 1

    def __init__(self):
        self._errors = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Options Flow zurückgeben (für nachträgliches Ändern)."""
        return SolarForecastOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Erster Schritt (User-Formular)."""
        if user_input is not None:
            # Sammle 1..5 Peak-Sensoren
            peaktime_sensors = []
            for i in range(1, 6):
                field = f"sensor_{i}"
                if field in user_input and user_input[field].strip():
                    peaktime_sensors.append(user_input[field].strip())

            if not peaktime_sensors:
                # Mindestens 1 Sensor muss eingetragen sein
                self._errors["base"] = "no_peaks"
            else:
                user_input[CONF_PEAKTIME_SENSORS] = peaktime_sensors
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )
        else:
            # Default
            user_input = {}
            user_input[CONF_NAME] = DEFAULT_NAME
            for i in range(1, 6):
                user_input[f"sensor_{i}"] = ""
            user_input[CONF_SUN_RISING] = "sensor.sun_next_rising"
            user_input[CONF_SUN_SETTING] = "sensor.sun_next_setting"
            user_input[CONF_ENERGY_REDUZIERT] = DEFAULT_ENERGY_REDUZIERT

        return await self._show_form(user_input)

    async def _show_form(self, user_input):
        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default=user_input[CONF_NAME]): cv.string,

            # 5 Felder
            vol.Optional("sensor_1", default=user_input["sensor_1"]): cv.string,
            vol.Optional("sensor_2", default=user_input["sensor_2"]): cv.string,
            vol.Optional("sensor_3", default=user_input["sensor_3"]): cv.string,
            vol.Optional("sensor_4", default=user_input["sensor_4"]): cv.string,
            vol.Optional("sensor_5", default=user_input["sensor_5"]): cv.string,

            # Sun-Sensoren
            vol.Optional(CONF_SUN_RISING, default=user_input[CONF_SUN_RISING]): cv.string,
            vol.Optional(CONF_SUN_SETTING, default=user_input[CONF_SUN_SETTING]): cv.string,

            # energy_reduziert
            vol.Required(CONF_ENERGY_REDUZIERT, default=user_input[CONF_ENERGY_REDUZIERT]): vol.Coerce(float),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors
        )


class SolarForecastOptionsFlowHandler(config_entries.OptionsFlow):
    """Options Flow, um dieselben Felder nachträglich zu ändern."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self._errors = {}

    async def async_step_init(self, user_input=None):
        """Start der Optionen."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        """Zeigt dieselben Felder nochmal."""
        if user_input is not None:
            # Wieder Mind. 1 Sensor?
            peaktime_sensors = []
            for i in range(1, 6):
                field = f"sensor_{i}"
                if field in user_input and user_input[field].strip():
                    peaktime_sensors.append(user_input[field].strip())

            if not peaktime_sensors:
                self._errors["base"] = "no_peaks"
            else:
                user_input[CONF_PEAKTIME_SENSORS] = peaktime_sensors
                return self.async_create_entry(title="", data=user_input)
        else:
            # Bestehende Daten + Options
            data = {**self.config_entry.data, **self.config_entry.options}

            user_input = {}
            user_input[CONF_NAME] = data.get(CONF_NAME, DEFAULT_NAME)
            peak_sensors = data.get(CONF_PEAKTIME_SENSORS, [])
            for i in range(1, 6):
                try:
                    user_input[f"sensor_{i}"] = peak_sensors[i-1]
                except IndexError:
                    user_input[f"sensor_{i}"] = ""

            user_input[CONF_SUN_RISING] = data.get(CONF_SUN_RISING, "sensor.sun_next_rising")
            user_input[CONF_SUN_SETTING] = data.get(CONF_SUN_SETTING, "sensor.sun_next_setting")
            user_input[CONF_ENERGY_REDUZIERT] = data.get(CONF_ENERGY_REDUZIERT, DEFAULT_ENERGY_REDUZIERT)

        data_schema = vol.Schema({
            vol.Required(CONF_NAME, default=user_input[CONF_NAME]): cv.string,

            vol.Optional("sensor_1", default=user_input["sensor_1"]): cv.string,
            vol.Optional("sensor_2", default=user_input["sensor_2"]): cv.string,
            vol.Optional("sensor_3", default=user_input["sensor_3"]): cv.string,
            vol.Optional("sensor_4", default=user_input["sensor_4"]): cv.string,
            vol.Optional("sensor_5", default=user_input["sensor_5"]): cv.string,

            vol.Optional(CONF_SUN_RISING, default=user_input[CONF_SUN_RISING]): cv.string,
            vol.Optional(CONF_SUN_SETTING, default=user_input[CONF_SUN_SETTING]): cv.string,

            vol.Required(CONF_ENERGY_REDUZIERT, default=user_input[CONF_ENERGY_REDUZIERT]): vol.Coerce(float),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=self._errors
        )
        
