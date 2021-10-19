"""
Setup for different kinds of Tuya switch devices
"""
import logging

from . import DOMAIN
from .const import (
    CONF_DEVICE_ID,
    CONF_TYPE,
)
from .generic.switch import TuyaLocalSwitch
from .helpers.device_config import get_config

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the switch device according to its type."""
    data = hass.data[DOMAIN][discovery_info[CONF_DEVICE_ID]]
    device = data["device"]
    switches = []

    cfg = get_config(discovery_info[CONF_TYPE])
    if cfg is None:
        raise ValueError(f"No device config found for {discovery_info}")
    ecfg = cfg.primary_entity
    if ecfg.entity == "switch" and discovery_info.get(ecfg.config_id, False):
        data[ecfg.config_id] = TuyaLocalSwitch(device, ecfg)
        switches.append(data[ecfg.config_id])
        if ecfg.deprecated:
            _LOGGER.warning(ecfg.deprecation_message)
        _LOGGER.debug(f"Adding switch for {discovery_info[ecfg.config_id]}")

    for ecfg in cfg.secondary_entities():
        if ecfg.entity == "switch" and discovery_info.get(ecfg.config_id, False):
            data[ecfg.config_id] = TuyaLocalSwitch(device, ecfg)
            switches.append(data[ecfg.config_id])
            if ecfg.deprecated:
                _LOGGER.warning(ecfg.deprecation_message)
            _LOGGER.debug(f"Adding switch for {discovery_info[ecfg.config_id]}")

    if not switches:
        raise ValueError(f"{device.name} does not support use as a switch device.")

    async_add_entities(switches)


async def async_setup_entry(hass, config_entry, async_add_entities):
    config = {**config_entry.data, **config_entry.options}
    await async_setup_platform(hass, {}, async_add_entities, config)
