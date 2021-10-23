"""
Platform to control tuya fan devices.
"""
import logging

from homeassistant.components.fan import (
    FanEntity,
    SUPPORT_DIRECTION,
    SUPPORT_OSCILLATE,
    SUPPORT_PRESET_MODE,
    SUPPORT_SET_SPEED,
)

from homeassistant.const import (
    STATE_UNAVAILABLE,
)

from ..device import TuyaLocalDevice
from ..helpers.device_config import TuyaEntityConfig

_LOGGER = logging.getLogger(__name__)


class TuyaLocalFan(FanEntity):
    """Representation of a Tuya Fan entity."""

    def __init__(self, device: TuyaLocalDevice, config: TuyaEntityConfig):
        """
        Initialise the fan device.
        Args:
           device (TuyaLocalDevice): The device API instance.
           config (TuyaEntityConfig): The entity config.
        """
        self._device = device
        self._config = config
        self._support_flags = 0
        self._attr_dps = []
        dps_map = {c.name: c for c in config.dps()}
        self._switch_dps = dps_map.pop("switch", None)
        self._preset_dps = dps_map.pop("preset_mode", None)
        self._speed_dps = dps_map.pop("speed", None)
        self._oscillate_dps = dps_map.pop("oscillate", None)
        self._direction_dps = dps_map.pop("direction", None)

        for d in dps_map.values():
            if not d.hidden:
                self._attr_dps.append(d)

        if self._preset_dps:
            self._support_flags |= SUPPORT_PRESET_MODE
        if self._speed_dps:
            self._support_flags |= SUPPORT_SET_SPEED
        if self._oscillate_dps:
            self._support_flags |= SUPPORT_OSCILLATE
        if self._direction_dps:
            self._support_flags |= SUPPORT_DIRECTION

    @property
    def supported_features(self):
        """Return the features supported by this climate device."""
        return self._support_flags

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the friendly name of the entity for the UI."""
        return self._config.name(self._device.name)

    @property
    def unique_id(self):
        """Return the unique id for this climate device."""
        return self._config.unique_id(self._device.unique_id)

    @property
    def device_info(self):
        """Return device information about this heater."""
        return self._device.device_info

    @property
    def icon(self):
        """Return the icon to use in the frontend for this device."""
        icon = self._config.icon(self._device)
        if icon:
            return icon
        else:
            return super().icon

    @property
    def is_on(self):
        """Return whether the switch is on or not."""
        # If there is no switch, it is always on
        if self._switch_dps is None:
            return True
        is_switched_on = self._switch_dps.get_value(self._device)

        if is_switched_on is None:
            return STATE_UNAVAILABLE
        else:
            return bool(is_switched_on)

    async def async_turn_on(self, **kwargs):
        """Turn the switch on"""
        if self._switch_dps is None:
            raise NotImplementedError()
        await self._switch_dps.async_set_value(self._device, True)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off"""
        if self._switch_dps is None:
            raise NotImplementedError
        await self._switch_dps.async_set_value(self._device, False)

    @property
    def percentage(self):
        """Return the currently set percentage."""
        if self._speed_dps is None:
            return None
        return self._speed_dps.get_value(self._device)

    @property
    def percentage_step(self):
        """Return the step for percentage."""
        if self._speed_dps is None:
            return None
        if self._speed_dps.values(self._device) is None:
            return self._speed_dps.step(self._device)
        else:
            return 100 / len(self._speed_dps.values(self._device))

    @property
    def speed_count(self):
        """Return the number of speeds supported by the fan."""
        if self._speed_dps is None:
            return 0
        if self._speed_dps.values(self._device) is not None:
            return len(self._speed_dps.values(self._device))
        return int(round(100 / self.percentage_step))

    async def async_set_percentage(self, percentage):
        """Set the fan speed as a percentage."""
        if self._speed_dps is None:
            return None
        # If there is a fixed list of values, snap to the closest one
        if self._speed_dps.values(self._device) is not None:
            percentage = min(
                self._speed_dps.values(self._device), key=lambda x: abs(x - percentage)
            )

        await self._speed_dps.async_set_value(self._device, percentage)

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        if self._preset_dps is None:
            return None
        return self._preset_dps.get_value(self._device)

    @property
    def preset_modes(self):
        """Return the list of presets that this device supports."""
        if self._preset_dps is None:
            return []
        return self._preset_dps.values(self._device)

    async def async_set_preset_mode(self, preset_mode):
        """Set the preset mode."""
        if self._preset_dps is None:
            raise NotImplementedError()
        await self._preset_dps.async_set_value(self._device, preset_mode)

    @property
    def current_direction(self):
        """Return the current direction [forward or reverse]."""
        if self._direction_dps is None:
            return None
        return self._direction_dps.get_value(self._device)

    async def async_set_direction(self, direction):
        """Set the direction of the fan."""
        if self._direction_dps is None:
            raise NotImplementedError()
        await self._direction_dps.async_set_value(self._device, direction)

    @property
    def oscillating(self):
        """Return whether or not the fan is oscillating."""
        if self._oscillate_dps is None:
            return None
        return self._oscillate_dps.get_value(self._device)

    async def async_oscillate(self, oscillating):
        """Oscillate the fan."""
        if self._oscillate_dps is None:
            raise NotImplementedError()
        await self._oscillate_dps.async_set_value(self._device, oscillating)

    @property
    def device_state_attributes(self):
        """Get additional attributes that the integration itself does not support."""
        attr = {}
        for a in self._attr_dps:
            attr[a.name] = a.get_value(self._device)
        return attr

    async def async_update(self):
        await self._device.async_refresh()
