# Home Assistant Planviewer Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

This is a custom component for Home Assistant to scrape public announcements (like building permits) from the [Planviewer website](https://www.planviewer.nl/) for a specific Dutch municipality and expose them as sensor entities.

**Please Note:** This is a custom component and is not officially supported by Home Assistant or Planviewer.

## Features

* Scrapes the latest announcements for a configured municipality.
* Creates individual sensor entities for the most recent announcements (defaulting to the top 3).
* Each sensor provides details like the full announcement text (extracted from the link), start date, end date, and a direct link.
* Includes diagnostic sensors to monitor the integration's update status and errors.
* Configurable scan interval for checking for new announcements.

## Installation

### Via HACS (Recommended)

1.  Ensure you have [HACS](https://hacs.xyz/) installed and configured in your Home Assistant.
2.  In Home Assistant, go to **HACS** -> **Integrations**.
3.  Click the **'+ Explore & Download Repositories'** button in the bottom right.
4.  Search for "Planviewer" (or the name you give your repository).
5.  Click on the repository and then click **'Download'**.
6.  Restart your Home Assistant instance.

### Manual Installation

1.  Navigate to your Home Assistant configuration directory (where `configuration.yaml` is located).
2.  Create a `custom_components` folder if it doesn't exist.
3.  Inside the `custom_components` folder, create a new folder named `planviewer`.
4.  Copy all the files from this repository (`__init__.py`, `api.py`, `config_flow.py`, `const.py`, `coordinator.py`, `manifest.json`, `sensor.py`) into the `planviewer` folder.
5.  Restart your Home Assistant instance.

## Configuration

After installation and restarting Home Assistant, you can configure the Planviewer integration via the UI:

1.  In Home Assistant, go to **Settings** -> **Devices & Services**.
2.  Click the **'+ Add Integration'** button in the bottom right.
3.  Search for "Planviewer".
4.  Select the Planviewer integration.
5.  Enter the required information:
    * **Municipality:** The name of the municipality you want to scrape (e.g., `Heerlen`).
    * **Instance Name:** A unique name for this instance of the integration (e.g., `Heerlen Announcements`).

6.  Click **'Submit'**.

You can configure the update interval (how often the integration checks Planviewer for new data) by going to the integration in **Settings** -> **Devices & Services**, clicking **'Configure'**, and adjusting the 'Scan Interval' setting.

## Entities

This integration creates sensor entities for the scraped announcements and diagnostic information.

### Announcement Sensors

Sensor entities will be created for the most recent announcements (defaulting to the top 3 scraped).

* **Entity ID:** `sensor.planviewer_[municipality]_[index]` (e.g., `sensor.planviewer_heerlen_1`, `sensor.planviewer_heerlen_2`)
* **State:** The full announcement text.
* **Attributes:** Include `datum_start`, `datum_eind`, and `link` (the full URL).

### Diagnostic Sensors

Diagnostic sensors provide information about the integration's operation. These entities will be linked to the device created by the integration.

* **Coordinator Last Update:** Shows the timestamp of the last successful data update.
* **Last Update Status:** Indicates if the last update was successful ("OK") or resulted in an error ("Error").
* **Consecutive Update Errors:** Shows the count of consecutive failed update attempts.

## Development

If you wish to contribute or make changes, you can fork the repository and submit pull requests. Ensure you follow Home Assistant's custom component development practices.

## Acknowledgements

* Based on the Planviewer website structure.
* Inspired by other scraping-based Home Assistant integrations.

---
