import logging
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_PEAKTIME_SENSORS,
    CONF_SUN_RISING,
    CONF_SUN_SETTING,
    CONF_ENERGY_REDUZIERT,
    DEFAULT_ENERGY_REDUZIERT
)

_LOGGER = logging.getLogger(__name__)


def float_state(hass: HomeAssistant, entity_id: str, default: float = 0.0) -> float:
    """
    Liest den Status eines Sensors aus und konvertiert ihn zu float.
    Gibt 'default' zurück, falls nicht verfügbar oder konvertierbar.
    """
    state_obj = hass.states.get(entity_id)
    if not state_obj or state_obj.state in ("unknown", "unavailable", None):
        return default
    try:
        return float(state_obj.state)
    except ValueError:
        return default


def timestamp_state(hass: HomeAssistant, entity_id: str):
    """
    Versucht, den State als Unix-Timestamp (float) oder ISO-8601-Datum
    zu interpretieren. Gibt None zurück, falls es nicht klappt.
    """
    state_obj = hass.states.get(entity_id)
    if not state_obj or state_obj.state in ("unknown", "unavailable", None):
        return None
    val = state_obj.state
    # Versuch: float
    try:
        return float(val)
    except ValueError:
        pass
    # Versuch: ISO-8601
    try:
        dt = datetime.fromisoformat(val)
        return dt.timestamp()
    except ValueError:
        return None


def now_timestamp() -> float:
    """Aktuelle Unix-Time (float)."""
    return datetime.now().timestamp()


def midnight_timestamp() -> float:
    """
    Unix-Time für Mitternacht (heute).
    """
    now = datetime.now()
    mid = datetime(now.year, now.month, now.day, 0, 0)
    return mid.timestamp()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """
    Registriert sämtliche sfdb_-Sensoren.
    """
    data = entry.data

    peaktime_sensors = data.get(CONF_PEAKTIME_SENSORS, [])
    sun_rising = data.get(CONF_SUN_RISING, "sensor.sun_next_rising")
    sun_setting = data.get(CONF_SUN_SETTING, "sensor.sun_next_setting")
    energy_reduziert = data.get(CONF_ENERGY_REDUZIERT, DEFAULT_ENERGY_REDUZIERT)

    _LOGGER.debug("PeakTime-Sensoren: %s", peaktime_sensors)
    _LOGGER.debug("Sun Rising: %s, Sun Setting: %s", sun_rising, sun_setting)
    _LOGGER.debug("Energy Reduziert: %s", energy_reduziert)

    sensors = []

    #
    # (1) PEAK-TIME, SUN, ENERGY_REDUZIERT
    #
    sensors.append(SfdbPeakTimeAverageSensor(hass, entry))
    sensors.append(SfdbSunSensor(hass, entry, "sfdb_sun_rising", True))
    sensors.append(SfdbSunSensor(hass, entry, "sfdb_sun_setting", False))
    sensors.append(SfdbEnergyReduziertSensor(hass, entry))

    #
    # (2) High Peak Time (Today, Tomorrow), TimeDiff Today, SunRising/Setting
    #
    sensors.append(SfdbPowerHighestPeakTimeTodaySUMDaySensor(hass))
    sensors.append(SfdbPowerHighestPeakTimeTodaySUMDifSensor(hass))
    sensors.append(SfdbPowerHighestPeakTimeTodaySUMSensor(hass))
    sensors.append(SfdbEnergyTimedifTodaySensor(hass))

    sensors.append(SfdbPowerHighestPeakTimeTomorrowSUMDifSensor(hass))
    sensors.append(SfdbPowerHighestPeakTimeTomorrowSUMSensor(hass))
    sensors.append(SfdbEnergyTimedifTomorrowSensor(hass))

    sensors.append(SfdbPowerSunRisingTimeTodaySUMSensor(hass))
    sensors.append(SfdbPowerSunRisingTimeTodaySUMDifZSensor(hass))
    sensors.append(SfdbPowerSunRisingTimeTodaySUMDifSensor(hass))
    sensors.append(SfdbPowerSunSettingTimeTodaySUMSensor(hass))
    sensors.append(SfdbPowerSunSettingTimeTodaySUMDifZSensor(hass))
    sensors.append(SfdbPowerSunSettingTimeTodaySUMDifSensor(hass))

    #
    # (3) Time-Diff-Klassen (01h..24h) + Extra 1..4
    #

    sensors.append(SfdbEnergyTimedif02hSensor(hass))
    sensors.append(SfdbEnergyTimedif03hSensor(hass))
    sensors.append(SfdbEnergyTimedif04hSensor(hass))
    sensors.append(SfdbEnergyTimedif06hSensor(hass))
    sensors.append(SfdbEnergyTimedif09hSensor(hass))
    sensors.append(SfdbEnergyTimedif12hSensor(hass))
    sensors.append(SfdbEnergyTimedif15hSensor(hass))
    sensors.append(SfdbEnergyTimedif18hSensor(hass))
    sensors.append(SfdbEnergyTimedif21hSensor(hass))
    sensors.append(SfdbEnergyTimedif24hSensor(hass))

    sensors.append(SfdbEnergyTimedif1Sensor(hass))
    sensors.append(SfdbEnergyTimedif2Sensor(hass))
    sensors.append(SfdbEnergyTimedif3Sensor(hass))
    sensors.append(SfdbEnergyTimedif4Sensor(hass))

    #
    # (4) energy_reduziert_01_sum .. 04_sum
    #
    sensors.append(SfdbEnergyReduziert01(hass))
    sensors.append(SfdbEnergyReduziert02(hass))
    sensors.append(SfdbEnergyReduziert03(hass))
    sensors.append(SfdbEnergyReduziert04(hass))

    #
    # (5) Production
    #

    sensors.append(SfdbEnergyProductionTodayRemainingSUMDifSensor(hass))


    #
    # (6) Production SUM
    #

    sensors.append(SfdbEnergyProductionNextHourSensor(hass))
    sensors.append(SfdbEnergyProductionCurrentHourSensor(hass))
    sensors.append(SfdbEnergyProductionTodayRemainingSensor(hass))
    sensors.append(SfdbEnergyProductionTodaySensor(hass))
    sensors.append(SfdbEnergyProductionTomorrowSensor(hass))
    sensors.append(SfdbEnergyProductionD2Sensor(hass))
    sensors.append(SfdbEnergyProductionD3Sensor(hass))


    #
    # (7a) Forecast => EINE parametrisierte Klasse today
    #    Ersetzt die alten SfdbEnergyXXhSUMZSensor & SfdbEnergyXXhSUMSensor
    #

    sensors.append(SfdbEnergyForecastSensor02hToday(hass))
    sensors.append(SfdbEnergyForecastSensor03hToday(hass))
    sensors.append(SfdbEnergyForecastSensor04hToday(hass))
    sensors.append(SfdbEnergyForecastSensor06hToday(hass))
    sensors.append(SfdbEnergyForecastSensor09hToday(hass))
    sensors.append(SfdbEnergyForecastSensor12hToday(hass))


    #
    # (7b) Forecast => EINE parametrisierte Klasse tomorrow
    #    Ersetzt die alten SfdbEnergyXXhSUMZSensor & SfdbEnergyXXhSUMSensor
    #

    sensors.append(SfdbEnergyForecastSensor15hTomorrow(hass))
    sensors.append(SfdbEnergyForecastSensor18hTomorrow(hass))
    sensors.append(SfdbEnergyForecastSensor21hTomorrow(hass))
    sensors.append(SfdbEnergyForecastSensor24hTomorrow(hass))
    sensors.append(SfdbEnergyForecastSensor27hTomorrow(hass))
    sensors.append(SfdbEnergyForecastSensor30hTomorrow(hass))
    sensors.append(SfdbEnergyForecastSensor33hTomorrow(hass))
    sensors.append(SfdbEnergyForecastSensor36hTomorrow(hass))


    #
    # (7c) Forecast => EINE parametrisierte Klasse d2
    #    Ersetzt die alten SfdbEnergyXXhSUMZSensor & SfdbEnergyXXhSUMSensor
    #

    sensors.append(SfdbEnergyForecastSensor39hD2(hass))
    sensors.append(SfdbEnergyForecastSensor42hD2(hass))
    sensors.append(SfdbEnergyForecastSensor45hD2(hass))
    sensors.append(SfdbEnergyForecastSensor48hD2(hass))
    sensors.append(SfdbEnergyForecastSensor51hD2(hass))
    sensors.append(SfdbEnergyForecastSensor54hD2(hass))
    sensors.append(SfdbEnergyForecastSensor57hD2(hass))
    sensors.append(SfdbEnergyForecastSensor60hD2(hass))


    #
    # (7d) Forecast => EINE parametrisierte Klasse d3
    #    Ersetzt die alten SfdbEnergyXXhSUMZSensor & SfdbEnergyXXhSUMSensor
    #

    sensors.append(SfdbEnergyForecastSensor63hD3(hass))
    sensors.append(SfdbEnergyForecastSensor66hD3(hass))
    sensors.append(SfdbEnergyForecastSensor69hD3(hass))
    sensors.append(SfdbEnergyForecastSensor72hD3(hass))
    sensors.append(SfdbEnergyForecastSensor75hD3(hass))
    sensors.append(SfdbEnergyForecastSensor78hD3(hass))
    sensors.append(SfdbEnergyForecastSensor81hD3(hass))
    sensors.append(SfdbEnergyForecastSensor84hD3(hass))


    #
    # (8) ProdRemain
    #
    sensors.append(SfdbProdRemainSensor(hass))

    async_add_entities(sensors, True)


# ------------------------------------------------------------------------------
# (1) PEAK-TIME, SUN-SENSOR, ENERGY_REDUZIERT
# ------------------------------------------------------------------------------
class SfdbPeakTimeAverageSensor(Entity):
    """Summiert 1..5 Peak-Sensoren => Durchschnitt."""
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._entry = entry
        self._attr_name = "sfdb_peak_time_average"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        peaktime_sensors = self._entry.data.get(CONF_PEAKTIME_SENSORS, [])
        if not peaktime_sensors:
            self._state = 0
            return
        total = 0.0
        count = 0
        for ent in peaktime_sensors:
            val = float_state(self.hass, ent, 0.0)
            total += val
            count += 1
        if count > 0:
            avg = total / count
        else:
            avg = 0
        self._state = round(avg, 2)


class SfdbSunSensor(Entity):
    """Zeigt den float-Wert des konfigurierten Sun-Sensors (rising/setting)."""
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, sensor_name: str, is_rising: bool):
        self.hass = hass
        self._entry = entry
        self._sensor_name = sensor_name
        self._is_rising = is_rising
        self._state = None

    @property
    def name(self):
        return self._sensor_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        if self._is_rising:
            sensor_id = self._entry.data.get(CONF_SUN_RISING, "sensor.sun_next_rising")
        else:
            sensor_id = self._entry.data.get(CONF_SUN_SETTING, "sensor.sun_next_setting")
        val = float_state(self.hass, sensor_id)
        self._state = round(val, 2)


class SfdbEnergyReduziertSensor(Entity):
    """Liest 'energy_reduziert' (float, 2 Nachkommastellen)."""
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self._entry = entry
        self._state = None
        self._attr_name = "sfdb_energy_reduziert"

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        val = self._entry.data.get(CONF_ENERGY_REDUZIERT, DEFAULT_ENERGY_REDUZIERT)
        self._state = round(val, 2)


# ------------------------------------------------------------------------------
# (2) HEUTE / MORGEN / SUN RISING / SUN SETTING
# ------------------------------------------------------------------------------
class SfdbPowerHighestPeakTimeTodaySUMDaySensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_highest_peak_time_today_SUM_day"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        iso_ts = timestamp_state(self.hass, "sensor.date_time_iso") or 0.0
        iso_hours_int = int(iso_ts / 3600)
        midnight_hours_int = int(midnight_timestamp() / 3600)
        value = 24 - (iso_hours_int - midnight_hours_int)
        self._state = round(value, 1)


class SfdbPowerHighestPeakTimeTodaySUMDifSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_highest_peak_time_today_SUM_dif"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        now_ts = now_timestamp()
        total = 0
        for hour in ["", 2, 3, 4, 5]:
            ent = f"sensor.power_highest_peak_time_today_{hour}"
            ts = timestamp_state(self.hass, ent)
            if ts is not None:
                diff_hours = (now_ts - ts) / 3600.0 * -1
                total += int(diff_hours)
        val = total / 5
        self._state = round(val, 1)


        # Durchschnitt (durch 5) und round auf 1 Nachkommastelle
        avg = total / 5.0
        self._state = round(avg, 1)


class SfdbPowerHighestPeakTimeTodaySUMSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_highest_peak_time_today_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        total = 0
        count = 0
        for hour in ["", 2, 3, 4, 5]:
            ts = timestamp_state(self.hass, f"sensor.power_highest_peak_time_today_{hour}")
            if ts is not None:
                hours_int = int(ts / 3600)
                total += hours_int
                count += 1
        if count > 0:
            val = total / count
        else:
            val = 0
        self._state = round(val, 1)


class SfdbEnergyTimedifTodaySensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_today"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        peak_sum = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum")
        mid_hours = int(midnight_timestamp() / 3600)
        val = 24 - (peak_sum - mid_hours - 2)
        self._state = round(val, 1)


class SfdbPowerHighestPeakTimeTomorrowSUMDifSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_highest_peak_time_tomorrow_SUM_dif"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        now_ts = now_timestamp()
        total = 0
        for hour in ["", 2, 3, 4, 5]:
            ent = f"sensor.power_highest_peak_time_tomorrow_{hour}"
            ts = timestamp_state(self.hass, ent)
            if ts is not None:
                diff_hours = (now_ts - ts) / 3600.0 * -1
                total += int(diff_hours)
        val = total / 5
        self._state = round(val, 1)


class SfdbPowerHighestPeakTimeTomorrowSUMSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_highest_peak_time_tomorrow_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        total = 0
        count = 0
        for hour in ["", 2, 3, 4, 5]:
            ts = timestamp_state(self.hass, f"sensor.power_highest_peak_time_tomorrow_{hour}")
            if ts is not None:
                total += int(ts / 3600)
                count += 1
        if count > 0:
            val = total / count
        else:
            val = 0
        self._state = round(val, 1)


class SfdbEnergyTimedifTomorrowSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_tomorrow"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        peak_sum = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_tomorrow_sum")
        mid_hours = int(midnight_timestamp() / 3600)
        val = 48 - (peak_sum - mid_hours - 2)
        self._state = round(val, 1)


class SfdbPowerSunRisingTimeTodaySUMSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_sun_rising_time_today_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        ts = timestamp_state(self.hass, "sensor.sun_next_rising") or 0.0
        val = int(ts / 3600)
        self._state = round(val, 1)



class SfdbPowerSunRisingTimeTodaySUMDifZSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_sun_rising_time_today_SUM_dif_z"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        from datetime import datetime
        return {
            "attribute": datetime.now().minute
        }

    async def async_update(self):
        peak = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum")
        rising = float_state(self.hass, "sensor.sfdb_power_sun_rising_time_today_sum")
        val = peak - rising
        self._state = round(val, 1)


class SfdbPowerSunRisingTimeTodaySUMDifSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_sun_rising_time_today_SUM_dif"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        from datetime import datetime
        return {
            "attribute": datetime.now().minute
        }

    async def async_update(self):
        z = float_state(self.hass, "sensor.sfdb_power_sun_rising_time_today_sum_dif_z")
        if z < 0:
            val = (z + 24) / 2.0
        else:
            val = z / 2.0

        self._state = round(val, 1)



class SfdbPowerSunSettingTimeTodaySUMSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_sun_setting_time_today_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        ts = timestamp_state(self.hass, "sensor.sun_next_setting") or 0.0
        val = int(ts / 3600)
        self._state = round(val, 1)


class SfdbPowerSunSettingTimeTodaySUMDifZSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_sun_setting_time_today_SUM_dif_z"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        from datetime import datetime
        return {
            "attribute": datetime.now().minute
        }


    async def async_update(self):
        setting = float_state(self.hass, "sensor.sfdb_power_sun_setting_time_today_sum")
        peak = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum")
        val = setting - peak
        self._state = round(val, 1)



class SfdbPowerSunSettingTimeTodaySUMDifSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_power_sun_setting_time_today_SUM_dif"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state


    @property
    def extra_state_attributes(self):
        from datetime import datetime
        return {
            "attribute": datetime.now().minute
        }


    async def async_update(self):
        z = float_state(self.hass, "sensor.sfdb_power_sun_setting_time_today_sum_dif_z")
        if z > 24:
            val = (z - 24) / 2.0
        else:
            val = z / 2.0
        self._state = round(val, 1)


# ------------------------------------------------------------------------------
# (3) TIME-DIFF-KLASSEN (01h..24h) + Extra 1..4
# ------------------------------------------------------------------------------


class SfdbEnergyTimedif02hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_02h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 2
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif03hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_03h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 3
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif04hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_04h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 4
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif06hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_06h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 6
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif09hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_09h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 9
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif12hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_12h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 12
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif15hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_15h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 15
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif18hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_18h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 18
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif21hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_21h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 21
        if base < 0:
            base += 24
        self._state = round(base, 2)

class SfdbEnergyTimedif24hSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_24h"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        day_val = float_state(self.hass, "sensor.sfdb_power_highest_peak_time_today_sum_day")
        base = day_val - 24
        if base < 0:
            base += 24
        self._state = round(base, 2)


# Zusätzliche TimeDiff-Klassen 1..4
class SfdbEnergyTimedif1Sensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_1"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        timedif = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        rising = float_state(self.hass, "sensor.sfdb_power_sun_rising_time_today_sum_dif")
        val = timedif + rising + rising
        self._state = round(val, 1)

class SfdbEnergyTimedif2Sensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_2"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        timedif = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        rising = float_state(self.hass, "sensor.sfdb_power_sun_rising_time_today_sum_dif")
        val = timedif + rising
        self._state = round(val, 1)

class SfdbEnergyTimedif3Sensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_3"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        timedif = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        setting = float_state(self.hass, "sensor.sfdb_power_sun_setting_time_today_sum_dif")
        val = timedif - setting
        self._state = round(val, 1)

class SfdbEnergyTimedif4Sensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_timedif_4"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        timedif = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        setting = float_state(self.hass, "sensor.sfdb_power_sun_setting_time_today_sum_dif")
        val = timedif - setting - setting
        self._state = round(val, 1)


# ------------------------------------------------------------------------------
# (4) energy_reduziert_01_sum .. 04_sum
# ------------------------------------------------------------------------------
class SfdbEnergyReduziert01(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_reduziert_01_sum"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        r = float_state(self.hass, "sensor.sfdb_power_sun_rising_time_today_sum_dif")
        s = float_state(self.hass, "sensor.sfdb_power_sun_setting_time_today_sum_dif")
        total = (r + r + s + s)
        energy_red = float_state(self.hass, "sensor.sfdb_energy_reduziert")
        if r == 0 or total == 0:
            val = 0
        else:
            part = (r / total) * energy_red
            val = part / r
        self._state = round(val, 2)

class SfdbEnergyReduziert02(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_reduziert_02_sum"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        r = float_state(self.hass, "sensor.sfdb_power_sun_rising_time_today_sum_dif")
        s = float_state(self.hass, "sensor.sfdb_power_sun_setting_time_today_sum_dif")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")
        denom = (r + s)
        if r == 0 or denom == 0:
            val = 0
        else:
            val = ((r / denom) - red01) / r
        self._state = round(val, 2)

class SfdbEnergyReduziert03(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_reduziert_03_sum"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        s = float_state(self.hass, "sensor.sfdb_power_sun_setting_time_today_sum_dif")
        r = float_state(self.hass, "sensor.sfdb_power_sun_rising_time_today_sum_dif")
        val_04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        denom = (s + r)
        if s == 0 or denom == 0:
            val = 0
        else:
            val = ((s / denom) - val_04) / s
        self._state = round(val, 2)

class SfdbEnergyReduziert04(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_reduziert_04_sum"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state
    async def async_update(self):
        s = float_state(self.hass, "sensor.sfdb_power_sun_setting_time_today_sum_dif")
        r = float_state(self.hass, "sensor.sfdb_power_sun_rising_time_today_sum_dif")
        energy_red = float_state(self.hass, "sensor.sfdb_energy_reduziert")
        total = (r + r + s + s)
        if s == 0 or total == 0:
            val = 0
        else:
            part = (s / total) * energy_red
            val = part / s
        self._state = round(val, 2)


# ------------------------------------------------------------------------------
# (5) Production SUM
# ------------------------------------------------------------------------------


# sensor.energy_current_hour_SUM

class SfdbEnergyProductionCurrentHourSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_current_hour_SUM"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state

    async def async_update(self):

        Sensor1 = float_state(self.hass, "sensor.energy_current_hour")
        Sensor2 = float_state(self.hass, "sensor.energy_current_hour_2")
        Sensor3 = float_state(self.hass, "sensor.energy_current_hour_3")
        Sensor4 = float_state(self.hass, "sensor.energy_current_hour_4")
        Sensor5 = float_state(self.hass, "sensor.energy_current_hour_5")
        base = Sensor1 + Sensor2 + Sensor3 + Sensor4 + Sensor5
        if base < 0:
            base = 0
        self._state = round(base, 2)


# sensor.energy_production_next_hour_SUM

class SfdbEnergyProductionNextHourSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_next_hour_SUM"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state

    async def async_update(self):

        Sensor1 = float_state(self.hass, "sensor.energy_next_hour")
        Sensor2 = float_state(self.hass, "sensor.energy_next_hour_2")
        Sensor3 = float_state(self.hass, "sensor.energy_next_hour_3")
        Sensor4 = float_state(self.hass, "sensor.energy_next_hour_4")
        Sensor5 = float_state(self.hass, "sensor.energy_next_hour_5")
        base = Sensor1 + Sensor2 + Sensor3 + Sensor4 + Sensor5
        if base < 0:
            base = 0
        self._state = round(base, 2)


# sensor.energy_production_today_remaining_SUM

class SfdbEnergyProductionTodayRemainingSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_production_today_remaining_SUM"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state

    async def async_update(self):

        Sensor1 = float_state(self.hass, "sensor.energy_production_today_remaining")
        Sensor2 = float_state(self.hass, "sensor.energy_production_today_remaining_2")
        Sensor3 = float_state(self.hass, "sensor.energy_production_today_remaining_3")
        Sensor4 = float_state(self.hass, "sensor.energy_production_today_remaining_4")
        Sensor5 = float_state(self.hass, "sensor.energy_production_today_remaining_5")
        base = Sensor1 + Sensor2 + Sensor3 + Sensor4 + Sensor5
        if base < 0:
            base = 0
        self._state = round(base, 2)



# sensor.energy_production_today_SUM

class SfdbEnergyProductionTodaySensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_production_today_SUM"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state

    async def async_update(self):

        Sensor1 = float_state(self.hass, "sensor.energy_production_today")
        Sensor2 = float_state(self.hass, "sensor.energy_production_today_2")
        Sensor3 = float_state(self.hass, "sensor.energy_production_today_3")
        Sensor4 = float_state(self.hass, "sensor.energy_production_today_4")
        Sensor5 = float_state(self.hass, "sensor.energy_production_today_5")
        base = Sensor1 + Sensor2 + Sensor3 + Sensor4 + Sensor5
        if base < 0:
            base = 0
        self._state = round(base, 2)

# sensor.energy_production_tomorrow_SUM

class SfdbEnergyProductionTomorrowSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_production_tomorrow_SUM"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state

    async def async_update(self):

        Sensor1 = float_state(self.hass, "sensor.energy_production_tomorrow")
        Sensor2 = float_state(self.hass, "sensor.energy_production_tomorrow_2")
        Sensor3 = float_state(self.hass, "sensor.energy_production_tomorrow_3")
        Sensor4 = float_state(self.hass, "sensor.energy_production_tomorrow_4")
        Sensor5 = float_state(self.hass, "sensor.energy_production_tomorrow_5")
        base = Sensor1 + Sensor2 + Sensor3 + Sensor4 + Sensor5
        if base < 0:
            base = 0
        self._state = round(base, 2)


# sensor.energy_production_d2_SUM

class SfdbEnergyProductionD2Sensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_production_d2_SUM"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state

    async def async_update(self):

        Sensor1 = float_state(self.hass, "sensor.energy_production_d2")
        Sensor2 = float_state(self.hass, "sensor.energy_production_d2_2")
        Sensor3 = float_state(self.hass, "sensor.energy_production_d2_3")
        Sensor4 = float_state(self.hass, "sensor.energy_production_d2_4")
        Sensor5 = float_state(self.hass, "sensor.energy_production_d2_5")
        base = Sensor1 + Sensor2 + Sensor3 + Sensor4 + Sensor5
        if base < 0:
            base = 0
        self._state = round(base, 2)


# sensor.energy_production_d3_SUM

class SfdbEnergyProductionD3Sensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_production_d3_SUM"
        self._state = None
    @property
    def name(self):
        return self._attr_name
    @property
    def state(self):
        return self._state

    async def async_update(self):

        Sensor1 = float_state(self.hass, "sensor.energy_production_d3")
        Sensor2 = float_state(self.hass, "sensor.energy_production_d3_2")
        Sensor3 = float_state(self.hass, "sensor.energy_production_d3_3")
        Sensor4 = float_state(self.hass, "sensor.energy_production_d3_4")
        Sensor5 = float_state(self.hass, "sensor.energy_production_d3_5")
        base = Sensor1 + Sensor2 + Sensor3 + Sensor4 + Sensor5
        if base < 0:
            base = 0
        self._state = round(base, 2)



# ------------------------------------------------------------------------------
# (6) Energy Production Today Remaining => parametrisierte
# ------------------------------------------------------------------------------

class SfdbEnergyProductionTodayRemainingSUMDifSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_production_today_remaining_SUM_dif"
        self._state = None

    @property
    def name(self):
        return self._attr_name
    
    @property
    def state(self):
        return self._state

    async def async_update(self):
        total = 0.0
        # z.B. [1,2,3,4,6,9,12,15,18,21,24]
        for hour in [1,2,3,4,6,9,12,15,18,21,24]:
            rem = float_state(self.hass, f"sensor.energy_production_today_remaining_{hour}")
            nex = float_state(self.hass, f"sensor.energy_next_hour_{hour}")
            total += (rem - nex)
        self._state = round(total, 1)


# ------------------------------------------------------------------------------
# (7a) Today Forecast-Klasse => parametrisierte is_z
# ------------------------------------------------------------------------------


class SfdbEnergyForecastSensor02hToday(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_02h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_02h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_today_remaining_sum")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor03hToday(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_03h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_03h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_today_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor04hToday(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_04h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_04h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_today_remaining_sum")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor06hToday(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_06h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_06h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_today_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor09hToday(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_09h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_09h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_today_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor12hToday(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_12h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_12h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_today")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_today_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


# ------------------------------------------------------------------------------
# (7b) Tomorrow Forecast-Klasse => parametrisierte is_z
# ------------------------------------------------------------------------------


class SfdbEnergyForecastSensor15hTomorrow(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_15h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_15h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor18hTomorrow(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_18h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_18h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor21hTomorrow(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_21h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_21h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor24hTomorrow(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_24h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_24h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor27hTomorrow(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_27h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_03h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor30hTomorrow(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_30h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_06h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor33hTomorrow(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_33h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_09h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor36hTomorrow(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_36h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_12h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)



# ------------------------------------------------------------------------------
# (7c) D2 Forecast-Klasse => parametrisierte is_z
# ------------------------------------------------------------------------------

class SfdbEnergyForecastSensor39hD2(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_39h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_15h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d2_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor42hD2(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_42h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_18h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d2_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor45hD2(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_45h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_21h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d2_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)



class SfdbEnergyForecastSensor48hD2(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_48h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_24h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d2_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor51hD2(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_51h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_03h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d2_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor54hD2(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_54h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_06h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d2_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor57hD2(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_57h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_09h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d2_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor60hD2(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_60h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_12h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d2_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)




# ------------------------------------------------------------------------------
# (7d) D3 Forecast-Klasse => parametrisierte is_z
# ------------------------------------------------------------------------------

class SfdbEnergyForecastSensor63hD3(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_63h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_15h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d3_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor66hD3(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_66h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_18h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d3_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)



class SfdbEnergyForecastSensor69hD3(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_69h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_21h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d3_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor72hD3(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_72h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_24h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_d3_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor75hD3(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_75h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_03h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor78hD3(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_78h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_06h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor81hD3(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_81h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_09h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)


class SfdbEnergyForecastSensor84hD3(Entity):

    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_energy_84h_SUM"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Die Forecast-Logik, die in den alten _z und _SUM-Klassen stand:
        # Ein Beispiel (du kannst den Code anpassen):
        tX = float_state(self.hass, f"sensor.sfdb_energy_timedif_12h")

        t4 = float_state(self.hass, "sensor.sfdb_energy_timedif_4")
        t3 = float_state(self.hass, "sensor.sfdb_energy_timedif_3")
        t0 = float_state(self.hass, "sensor.sfdb_energy_timedif_tomorrow")
        t2 = float_state(self.hass, "sensor.sfdb_energy_timedif_2")
        t1 = float_state(self.hass, "sensor.sfdb_energy_timedif_1")

        prod_remain = float_state(self.hass, "sensor.sfdb_energy_production_tomorrow_SUM")
        red04 = float_state(self.hass, "sensor.sfdb_energy_reduziert_04_sum")
        red03 = float_state(self.hass, "sensor.sfdb_energy_reduziert_03_sum")
        red02 = float_state(self.hass, "sensor.sfdb_energy_reduziert_02_sum")
        red01 = float_state(self.hass, "sensor.sfdb_energy_reduziert_01_sum")

        # Vereinfacht: Dieselbe Abfrage wie in "SfdbEnergy2hSUMZSensor" usw.
        if tX < t4:
            val = 0
        else:
            if tX < t3:
                val = prod_remain * red04
            else:
                if tX < t0:
                    val = prod_remain * red03
                else:
                    if tX < t2:
                        val = prod_remain * red02
                    else:
                        if tX < t1:
                            val = prod_remain * red01
                        else:
                            if tX > t1:
                                val = 0
                            else:
                                val = 0

        self._state = round(val, 1)



# ------------------------------------------------------------------------------
# (8) ProdRemain
# ------------------------------------------------------------------------------
class SfdbProdRemainSensor(Entity):
    def __init__(self, hass):
        self.hass = hass
        self._attr_name = "sfdb_prod_remain"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        val = float_state(self.hass, "sensor.energy_production_today_remaining_p8", 0.0)
        self._state = round(val, 2)
