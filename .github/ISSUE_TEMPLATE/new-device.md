---
name: New Device
about: Report an unsupported device.
title: Request support for [device description]
labels: new device
assignees: ''

---

<!--
Thank you for reporting a new device to add support for.  Please provide as much of the information requested below as you can.  Requests with all the information required will be prioritised over issues which are missing important information.
-->

# Log Message

<!--
Please paste the message from HA log that shows the **DPS** returned from the device.
-->

# Information about DPS mappings

<!--
If you have an iot.tuya.com account, please go to "Cloud" -> "API Explorer".  Under "Smart Home Device System"/"Device Control", select the last "Get Device Specification Attribute" function, check the server is set correctly, and enter your device ID.  Please post the output here.

If DPS are missing from the output above, go back to the IoT Platform "Cloud" main page and select your project.  Go to the "Devices" tab and select "Debug Device" next to your device.  Select "Device Logs" and open your browser's Developer Tools window on the Network tab.  For each function that has not yet been linked to a DPS, select the function from the "Select DP ID" dropdown and press "Search".  In the Developer Tools window, find the "list" request that was issued, and look in the Request Payload for a "code" parameter.  This is the DP id linked to that function, please add the remaining code and function name here.  If the function name is in Chinese, just paste it.

If you do not have access to iot.tuya.com, please try to identify as many DPs as possible, by experimenting with your device.  Please also note any ranges and scale factors for input numbers, and possible values and their meanings for any input strings (enums).
-->

# Product ID

<!--
If you have access to the IoT portal, please paste just the product_id line from API Explorer: General Device Capabilities" / "General Devices management" / "Get Device Information".  You will also find the local_key in here, please take care not to post that publicly.  If you do, then re-pairing the device with the mobile app will refresh the local key.

Although this information is optional and not required, it will be used in future to identify matching devices.
-->


# Information about how the device functions

<!--
If there is a manual or other explanation available online, please link to it (even if not in English)
Otherwise if it is not obvious what all the functions do, please give a brief description.
-->
