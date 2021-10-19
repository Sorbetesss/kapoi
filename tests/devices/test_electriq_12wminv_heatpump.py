from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.components.light import COLOR_MODE_ONOFF
from homeassistant.const import STATE_UNAVAILABLE

from ..const import ELECTRIQ_12WMINV_HEATPUMP_PAYLOAD
from ..helpers import assert_device_properties_set
from .base_device_tests import TuyaDeviceTestCase

POWER_DPS = "1"
TEMPERATURE_DPS = "2"
CURRENTTEMP_DPS = "3"
HVACMODE_DPS = "4"
FAN_DPS = "5"
UNKNOWN8_DPS = "8"
UNKNOWN12_DPS = "12"
SWITCH_DPS = "101"
UNKNOWN102_DPS = "102"
UNKNOWN103_DPS = "103"
LIGHT_DPS = "104"
VSWING_DPS = "106"
HSWING_DPS = "107"
UNKNOWN108_DPS = "108"
UNKNOWN109_DPS = "109"
UNKNOWN110_DPS = "110"


class TestElectriq12WMINVHeatpump(TuyaDeviceTestCase):
    __test__ = True

    def setUp(self):
        self.setUpForConfig(
            "electriq_12wminv_heatpump.yaml", ELECTRIQ_12WMINV_HEATPUMP_PAYLOAD
        )
        self.subject = self.entities.get("climate")
        self.light = self.entities.get("light_display")
        self.switch = self.entities.get("switch_sleep")

    def test_supported_features(self):
        self.assertEqual(
            self.subject.supported_features,
            SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE,
        )

    def test_icon(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "auto"
        self.assertEqual(self.subject.icon, "mdi:hvac")
        self.dps[HVACMODE_DPS] = "cold"
        self.assertEqual(self.subject.icon, "mdi:snowflake")
        self.dps[HVACMODE_DPS] = "hot"
        self.assertEqual(self.subject.icon, "mdi:fire")
        self.dps[HVACMODE_DPS] = "wet"
        self.assertEqual(self.subject.icon, "mdi:water")
        self.dps[HVACMODE_DPS] = "wind"
        self.assertEqual(self.subject.icon, "mdi:fan")
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.icon, "mdi:hvac-off")

    def test_temperature_unit_returns_device_temperature_unit(self):
        self.assertEqual(
            self.subject.temperature_unit, self.subject._device.temperature_unit
        )

    def test_target_temperature(self):
        self.dps[TEMPERATURE_DPS] = 25
        self.assertEqual(self.subject.target_temperature, 25)

    def test_target_temperature_step(self):
        self.assertEqual(self.subject.target_temperature_step, 1)

    def test_minimum_target_temperature(self):
        self.assertEqual(self.subject.min_temp, 16)

    def test_maximum_target_temperature(self):
        self.assertEqual(self.subject.max_temp, 32)

    async def test_legacy_set_temperature_with_temperature(self):
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 24}
        ):
            await self.subject.async_set_temperature(temperature=24)

    async def test_legacy_set_temperature_with_no_valid_properties(self):
        await self.subject.async_set_temperature(something="else")
        self.subject._device.async_set_property.assert_not_called()

    async def test_set_target_temperature_succeeds_within_valid_range(self):
        async with assert_device_properties_set(
            self.subject._device,
            {TEMPERATURE_DPS: 25},
        ):
            await self.subject.async_set_target_temperature(25)

    async def test_set_target_temperature_rounds_value_to_closest_integer(self):
        async with assert_device_properties_set(
            self.subject._device, {TEMPERATURE_DPS: 23}
        ):
            await self.subject.async_set_target_temperature(22.6)

    async def test_set_target_temperature_fails_outside_valid_range(self):
        with self.assertRaisesRegex(
            ValueError, "temperature \\(15\\) must be between 16 and 32"
        ):
            await self.subject.async_set_target_temperature(15)

        with self.assertRaisesRegex(
            ValueError, "temperature \\(33\\) must be between 16 and 32"
        ):
            await self.subject.async_set_target_temperature(33)

    def test_current_temperature(self):
        self.dps[CURRENTTEMP_DPS] = 25
        self.assertEqual(self.subject.current_temperature, 25)

    def test_hvac_mode(self):
        self.dps[POWER_DPS] = True
        self.dps[HVACMODE_DPS] = "hot"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_HEAT)

        self.dps[HVACMODE_DPS] = "cold"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_COOL)

        self.dps[HVACMODE_DPS] = "wet"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_DRY)

        self.dps[HVACMODE_DPS] = "wind"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_FAN_ONLY)

        self.dps[HVACMODE_DPS] = "auto"
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_HEAT_COOL)

        self.dps[HVACMODE_DPS] = None
        self.assertEqual(self.subject.hvac_mode, STATE_UNAVAILABLE)

        self.dps[HVACMODE_DPS] = "auto"
        self.dps[POWER_DPS] = False
        self.assertEqual(self.subject.hvac_mode, HVAC_MODE_OFF)

    def test_hvac_modes(self):
        self.assertCountEqual(
            self.subject.hvac_modes,
            [
                HVAC_MODE_OFF,
                HVAC_MODE_HEAT,
                HVAC_MODE_HEAT_COOL,
                HVAC_MODE_COOL,
                HVAC_MODE_DRY,
                HVAC_MODE_FAN_ONLY,
            ],
        )

    async def test_turn_on(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: True, HVACMODE_DPS: "hot"}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_HEAT)

    async def test_turn_off(self):
        async with assert_device_properties_set(
            self.subject._device, {POWER_DPS: False}
        ):
            await self.subject.async_set_hvac_mode(HVAC_MODE_OFF)

    def test_fan_mode(self):
        self.dps[FAN_DPS] = 1
        self.assertEqual(self.subject.fan_mode, "auto")
        self.dps[FAN_DPS] = 2
        self.assertEqual(self.subject.fan_mode, "Turbo")
        self.dps[FAN_DPS] = 3
        self.assertEqual(self.subject.fan_mode, "low")
        self.dps[FAN_DPS] = 4
        self.assertEqual(self.subject.fan_mode, "medium")
        self.dps[FAN_DPS] = 5
        self.assertEqual(self.subject.fan_mode, "high")

    def test_fan_mode_invalid_in_dry_hvac_mode(self):
        self.dps[HVACMODE_DPS] = "wet"
        self.dps[FAN_DPS] = 1
        self.assertIs(self.subject.fan_mode, None)

    def test_fan_modes(self):
        self.assertCountEqual(
            self.subject.fan_modes,
            [
                "auto",
                "Turbo",
                "low",
                "medium",
                "high",
            ],
        )

    async def test_set_fan_mode_to_auto(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: 1},
        ):
            await self.subject.async_set_fan_mode("auto")

    async def test_set_fan_mode_to_turbo(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: 2},
        ):
            await self.subject.async_set_fan_mode("Turbo")

    async def test_set_fan_mode_to_low(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: 3},
        ):
            await self.subject.async_set_fan_mode("low")

    async def test_set_fan_mode_to_medium(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: 4},
        ):
            await self.subject.async_set_fan_mode("medium")

    async def test_set_fan_mode_to_high(self):
        async with assert_device_properties_set(
            self.subject._device,
            {FAN_DPS: 5},
        ):
            await self.subject.async_set_fan_mode("high")

    def test_swing_modes(self):
        self.assertCountEqual(
            self.subject.swing_modes,
            ["off", "horizontal", "vertical", "both"],
        )

    def test_swing_mode(self):
        self.dps[VSWING_DPS] = False
        self.dps[HSWING_DPS] = False
        self.assertEqual(self.subject.swing_mode, "off")

        self.dps[VSWING_DPS] = True
        self.assertEqual(self.subject.swing_mode, "vertical")

        self.dps[HSWING_DPS] = True
        self.assertEqual(self.subject.swing_mode, "both")

        self.dps[VSWING_DPS] = False
        self.assertEqual(self.subject.swing_mode, "horizontal")

    async def test_set_swing_mode_to_both(self):
        async with assert_device_properties_set(
            self.subject._device,
            {HSWING_DPS: True, VSWING_DPS: True},
        ):
            await self.subject.async_set_swing_mode("both")

    async def test_set_swing_mode_to_horizontal(self):
        async with assert_device_properties_set(
            self.subject._device,
            {HSWING_DPS: True, VSWING_DPS: False},
        ):
            await self.subject.async_set_swing_mode("horizontal")

    async def test_set_swing_mode_to_off(self):
        async with assert_device_properties_set(
            self.subject._device,
            {HSWING_DPS: False, VSWING_DPS: False},
        ):
            await self.subject.async_set_swing_mode("off")

    async def test_set_swing_mode_to_vertical(self):
        async with assert_device_properties_set(
            self.subject._device,
            {HSWING_DPS: False, VSWING_DPS: True},
        ):
            await self.subject.async_set_swing_mode("vertical")

    def test_device_state_attribures(self):
        self.dps[UNKNOWN8_DPS] = True
        self.dps[UNKNOWN12_DPS] = False
        self.dps[UNKNOWN102_DPS] = True
        self.dps[UNKNOWN103_DPS] = False
        self.dps[UNKNOWN108_DPS] = 108
        self.dps[UNKNOWN109_DPS] = 109
        self.dps[UNKNOWN110_DPS] = 110
        self.assertDictEqual(
            self.subject.device_state_attributes,
            {
                "unknown_8": True,
                "unknown_12": False,
                "unknown_102": True,
                "unknown_103": False,
                "unknown_108": 108,
                "unknown_109": 109,
                "unknown_110": 110,
            },
        )

    def test_light_state_attributes(self):
        self.assertEqual(self.light.device_state_attributes, {})

    def test_light_supported_color_modes(self):
        self.assertCountEqual(
            self.light.supported_color_modes,
            [COLOR_MODE_ONOFF],
        )

    def test_light_color_mode(self):
        self.assertEqual(self.light.color_mode, COLOR_MODE_ONOFF)

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
        self.dps[LIGHT_DPS] = True
        self.assertEqual(self.light.icon, "mdi:led-on")

        self.dps[LIGHT_DPS] = False
        self.assertEqual(self.light.icon, "mdi:led-off")

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
        self.assertEqual(self.switch.icon, "mdi:power-sleep")
