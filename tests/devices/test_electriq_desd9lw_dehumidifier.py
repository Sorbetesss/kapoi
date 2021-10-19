from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_HUMIDITY,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import STATE_UNAVAILABLE

from ..const import ELECTRIQ_DESD9LW_DEHUMIDIFIER_PAYLOAD
from ..helpers import assert_device_properties_set
from .base_device_tests import TuyaDeviceTestCase

POWER_DPS = "1"
HUMIDITY_DPS = "2"
FAN_DPS = "4"
HVACMODE_DPS = "5"
CURRENTHUM_DPS = "6"
CURRENTTEMP_DPS = "7"
SWING_DPS = "10"
SWITCH_DPS = "12"
LIGHT_DPS = "15"
TEMPERATURE_DPS = "101"


class TestElectriqDESD9LWDehumidifier(TuyaDeviceTestCase):
    __test__ = True

    def setUp(self):
        self.setUpForConfig(
            "electriq_desd9lw_dehumidifier.yaml",
            ELECTRIQ_DESD9LW_DEHUMIDIFIER_PAYLOAD,
        )
        self.subject = self.entities.get("climate")
        self.light = self.entities.get("light_uv_sterilization")
        self.switch = self.entities.get("switch_ionizer")

    def test_supported_features(self):
        self.assertEqual(
            self.subject.supported_features,
            SUPPORT_FAN_MODE
            | SUPPORT_SWING_MODE
            | SUPPORT_TARGET_HUMIDITY
            | SUPPORT_TARGET_TEMPERATURE,
        )

    def test_icon(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "Auto"
        self.assertEqual(self.subject.icon, "mdi:air-humidifier")
        self.dps[HVACMODE_DPS] = "Dehumidity"
        self.assertEqual(self.subject.icon, "mdi:water")
        self.dps[HVACMODE_DPS] = "Heater"
        self.assertEqual(self.subject.icon, "mdi:fire")
        self.dps[HVACMODE_DPS] = "Fan"
        self.assertEqual(self.subject.icon, "mdi:fan")
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.icon, "mdi:air-humidifier-off")

    def test_temperature_unit_returns_device_temperature_unit(self):
        self.assertEqual(
            self.subject.temperature_unit, self.subject._device.temperature_unit
        )

    def test_target_temperature(self):
        self.dps[TEMPERATURE_DPS] = 24
        self.assertEqual(self.subject.target_temperature, 24)

    def test_target_temperature_step(self):
        self.assertEqual(self.subject.target_temperature_step, 1)

    def test_minimum_target_temperature(self):
        self.assertEqual(self.subject.min_temp, 16)

    def test_maximum_target_temperature(self):
        self.assertEqual(self.subject.max_temp, 30)

    async def test_legacy_set_temperature_with_temperature(self):
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 22}
        ):
            await self.subject.async_set_temperature(temperature=22)

    async def test_legacy_set_temperature_with_no_valid_properties(self):
        await self.subject.async_set_temperature(something="else")
        self.subject._device.async_set_property.assert_not_called()

    async def test_set_target_temperature_rounds_value_to_closest_integer(self):
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 23}
        ):
            await self.subject.async_set_target_temperature(22.6)

    async def test_set_target_temperature_fails_outside_valid_range(self):
        with self.assertRaisesRegex(
            ValueError, "temperature \\(15\\) must be between 16 and 30"
        ):
            await self.subject.async_set_target_temperature(15)

        with self.assertRaisesRegex(
            ValueError, "temperature \\(31\\) must be between 16 and 30"
        ):
            await self.subject.async_set_target_temperature(31)

    def test_current_temperature(self):
        self.dps[CURRENTTEMP_DPS] = 21
        self.assertEqual(self.subject.current_temperature, 21)

    def test_current_humidity(self):
        self.dps[CURRENTHUM_DPS] = 60
        self.assertEqual(self.subject.current_humidity, 60)

    def test_min_target_humidity(self):
        self.assertEqual(self.subject.min_humidity, 35)

    def test_max_target_humidity(self):
        self.assertEqual(self.subject.max_humidity, 80)

    def test_target_humidity(self):
        self.dps[HUMIDITY_DPS] = 45
        self.assertEqual(self.subject.target_humidity, 45)

    async def test_set_target_humidity_rounds_to_5_percent(self):
        async with assert_device_properties_set(
            self.subject._device,
            {HUMIDITY_DPS: 55},
        ):
            await self.subject.async_set_humidity(53)

        async with assert_device_properties_set(
            self.subject._device,
            {HUMIDITY_DPS: 45},
        ):
            await self.subject.async_set_humidity(47)

    def test_hvac_mode(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "Heater"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_HEAT)

        self.dps[HVACMODE_DPS] = "Dehumidity"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_DRY)

        self.dps[HVACMODE_DPS] = "Fan"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_FAN_ONLY)

        self.dps[HVACMODE_DPS] = "Auto"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_AUTO)

        self.dps[HVACMODE_DPS] = None
        self.assertEqual(self.subject.hvac_mode, STATE_UNAVAILABLE)

        self.dps[HVACMODE_DPS] = "Auto"
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_OFF)

    def test_hvac_modes(self):
        self.assertCountEqual(
            self.subject.hvac_modes,
            [
                HVAC_MODE_AUTO,
                HVAC_MODE_DRY,
                HVAC_MODE_FAN_ONLY,
                HVAC_MODE_HEAT,
                HVAC_MODE_OFF,
            ],
        )

    async def test_turn_on(self):
        self.dps[HVACMODE_DPS] = "Auto"
        self.dps[POWER_DPS] = False

        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: True, HVACMODE_DPS: "Heater"}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_HEAT)

    async def test_turn_off(self):
        self.dps[HVACMODE_DPS] = "Auto"
        self.dps[POWER_DPS] = True

        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: False}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_OFF)

    async def test_set_mode_to_heater(self):
        self.dps[HVACMODE_DPS] = "Auto"
        self.dps[POWER_DPS] = True

        async with assert_device_properties_set(
            self.subject._device, {HVACMODE_DPS: "Heater", POWER_DPS: True}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_HEAT)

    async def test_set_mode_to_dehumidity(self):
        self.dps[HVACMODE_DPS] = "Auto"
        self.dps[POWER_DPS] = True

        async with assert_device_properties_set(
            self.subject._device, {HVACMODE_DPS: "Dehumidity", POWER_DPS: True}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_DRY)

    async def test_set_mode_to_fan(self):
        self.dps[HVACMODE_DPS] = "Auto"
        self.dps[POWER_DPS] = True

        async with assert_device_properties_set(
            self.subject._device, {HVACMODE_DPS: "Fan", POWER_DPS: True}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_FAN_ONLY)

    async def test_set_mode_to_auto(self):
        self.dps[HVACMODE_DPS] = "Fan"
        self.dps[POWER_DPS] = True

        async with assert_device_properties_set(
            self.subject._device, {HVACMODE_DPS: "Auto", POWER_DPS: True}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_AUTO)

    def test_fan_mode(self):
        self.dps[FAN_DPS] = "Low"
        self.assertEqual(self.subject.fan_mode, "Low")
        self.dps[FAN_DPS] = "Medium"
        self.assertEqual(self.subject.fan_mode, "Medium")
        self.dps[FAN_DPS] = "High"
        self.assertEqual(self.subject.fan_mode, "High")

    def test_fan_mode_invalid_in_auto_hvac_mode(self):
        self.dps[HVACMODE_DPS] = "Auto"
        self.dps[FAN_DPS] = "Low"
        self.assertIs(self.subject.fan_mode, None)

    def test_fan_modes(self):
        self.assertCountEqual(
            self.subject.fan_modes,
            ["Low", "Medium", "High"],
        )

    async def test_set_fan_mode_to_low(self):
        async with assert_device_properties_set(self.subject._device, {FAN_DPS: "Low"}):
            await self.subject.async_set_fan_mode("Low")

    async def test_set_fan_mode_to_medium(self):
        async with assert_device_properties_set(
            self.subject._device, {FAN_DPS: "Medium"}
        ):
            await self.subject.async_set_fan_mode("Medium")

    async def test_set_fan_mode_to_high(self):
        async with assert_device_properties_set(
            self.subject._device, {FAN_DPS: "High"}
        ):
            await self.subject.async_set_fan_mode("High")

    def test_swing_modes(self):
        self.assertCountEqual(
            self.subject.swing_modes,
            ["off", "vertical"],
        )

    def test_swing_mode(self):
        self.dps[SWING_DPS] = False
        self.assertEqual(self.subject.swing_mode, "off")

        self.dps[SWING_DPS] = True
        self.assertEqual(self.subject.swing_mode, "vertical")

    async def test_set_swing_mode_to_vertical(self):
        async with assert_device_properties_set(
            self.subject._device,
            {SWING_DPS: True},
        ):
            await self.subject.async_set_swing_mode("vertical")

    async def test_set_swing_mode_to_off(self):
        async with assert_device_properties_set(
            self.subject._device,
            {SWING_DPS: False},
        ):
            await self.subject.async_set_swing_mode("off")

    def test_light_state_attributes(self):
        self.assertEqual(self.light.device_state_attributes, {})

    def test_light_is_on(self):
        self.dps[LIGHT_DPS] = True
        self.assertTrue(self.light.is_on)
        self.dps[LIGHT_DPS] = False
        self.assertFalse(self.light.is_on)

    async def test_light_turn_on(self):
        async with assert_device_properties_set(
            self.light._device,
            {LIGHT_DPS: True},
        ):
            await self.light.async_turn_on()

    async def test_light_turn_off(self):
        async with assert_device_properties_set(
            self.light._device,
            {LIGHT_DPS: False},
        ):
            await self.light.async_turn_off()

    async def test_toggle_turns_the_light_on_when_it_was_off(self):
        self.dps[LIGHT_DPS] = False

        async with assert_device_properties_set(self.light._device, {LIGHT_DPS: True}):
            await self.light.async_toggle()

    async def test_toggle_turns_the_light_off_when_it_was_on(self):
        self.dps[LIGHT_DPS] = True

        async with assert_device_properties_set(self.light._device, {LIGHT_DPS: False}):
            await self.light.async_toggle()

    def test_light_icon(self):
        self.assertEqual(self.light.icon, "mdi:solar-power")

    def test_switch_state_attributes(self):
        self.assertEqual(self.switch.device_state_attributes, {})

    def test_switch_is_on(self):
        self.dps[SWITCH_DPS] = True
        self.assertTrue(self.switch.is_on)
        self.dps[SWITCH_DPS] = False
        self.assertFalse(self.switch.is_on)

    async def test_switch_turn_on(self):
        async with assert_device_properties_set(
            self.switch._device,
            {SWITCH_DPS: True},
        ):
            await self.switch.async_turn_on()

    async def test_switch_turn_off(self):
        async with assert_device_properties_set(
            self.switch._device,
            {SWITCH_DPS: False},
        ):
            await self.switch.async_turn_off()

    async def test_toggle_turns_the_switch_on_when_it_was_off(self):
        self.dps[SWITCH_DPS] = False

        async with assert_device_properties_set(
            self.switch._device, {SWITCH_DPS: True}
        ):
            await self.switch.async_toggle()

    async def test_toggle_turns_the_switch_off_when_it_was_on(self):
        self.dps[SWITCH_DPS] = True

        async with assert_device_properties_set(
            self.switch._device, {SWITCH_DPS: False}
        ):
            await self.switch.async_toggle()

    def test_switch_icon(self):
        self.assertEqual(self.switch.icon, "mdi:atom-variant")
