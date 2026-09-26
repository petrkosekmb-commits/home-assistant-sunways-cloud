# Sunways Cloud for Home Assistant

[Česky](README.cs.md) | English

Community Home Assistant integration for monitoring Sunways photovoltaic systems through the Sunways Portal cloud API.

## What it does

- connects to an existing Sunways Portal account;
- discovers stations and inverters linked to the account;
- exposes production, consumption, grid flow, battery and inverter values when supplied by the device;
- provides configurable polling and reauthentication;
- validates cloud values and avoids replacing unavailable measurements with false zeroes;
- redacts credentials, tokens and station identifiers from diagnostics.

This integration is read-only. It does not change inverter operating modes, export limits or other device settings.

## Installation

### HACS custom repository

1. In HACS, open **Integrations** and add this repository as a custom repository of type **Integration**.
2. Install **Sunways Cloud**.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and search for **Sunways**.

### Manual installation

Copy `custom_components/sunways` to `/config/custom_components/sunways`, restart Home Assistant and add the integration from the user interface.

## Configuration and privacy

The integration requires Sunways Portal credentials. Home Assistant stores configuration-entry data in its own protected configuration storage. Never publish diagnostics or configuration files without reviewing them first.

The Sunways Portal API is not a documented public contract and may change without notice. This project is not affiliated with or endorsed by Sunways Technologies.

## Credits and license

This project builds on the Apache-2.0 licensed [adamus-tork/home-assistant-sunways](https://github.com/adamus-tork/home-assistant-sunways) integration and includes subsequent community work. See [NOTICE](NOTICE) for attribution.

Licensed under the [Apache License 2.0](LICENSE).

## Support the project

If this integration helps you, you will be able to support its maintenance through the donation link published here after the support profile is activated.

