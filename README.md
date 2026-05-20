# Skylight Hyperspot Home Assistant Integration

Custom Home Assistant integration for Skylight Hyperspot aquarium lights.

## Features

- Local control
- Brightness control
- Color temperature / warm-white / cold-white mixing
- Auto mode button
- No cloud required

## Notes

This integration was currently only tested with:

- Skylight Hyperspot M AQCT-3

The internal channel scaling values may differ between Skylight models.

For the Hyperspot M AQCT-3 model:
- 0–10000 was used as the warm/cold channel range.

Other models may use:
- lower maximum values
- higher maximum values
- different scaling behavior

## Auto Mode

The current auto/schedule resume button is still experimental.

Known behavior:
- Works on the tested AQCT-3 model
- May not instantly apply the current schedule state
- Behavior may differ between firmware versions and Skylight models

The exact native app auto/schedule mechanism is still being reverse engineered.

## Installation

### HACS Custom Repository

Add this repository to HACS as a custom repository:

- HACS
- Custom repositories
- Add repository URL
- Category: Integration

Then install the integration and restart Home Assistant.

## Disclaimer

This project is not affiliated with Skylight.
