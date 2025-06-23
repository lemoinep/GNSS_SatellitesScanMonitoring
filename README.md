This project provides a set of Python tools for scanning, monitoring, and analyzing GNSS (Global Navigation Satellite System) satellite signals. The programs enable real-time detection and tracking of multiple satellite constellations, collection of signal quality and status data, and visualization of satellite positions and signal metrics. These tools support monitoring GNSS performance, detecting anomalies or signal disruptions, and assisting in research or development related to satellite navigation and positioning systems.

Python Program Descriptions

- GNSS_SatellitesScanMonitoringLevel1.py: This script provides a foundational GNSS satellite scanning and monitoring system. It detects visible satellites from multiple GNSS constellations, measures their signal strengths, and continuously updates satellite status in real time. It is designed for basic monitoring tasks such as tracking satellite availability and signal quality, making it suitable for initial GNSS performance assessments.

- GPS_Yocto_Basis.py: This program interfaces directly with Yoctopuce GPS hardware modules to acquire raw GPS data streams. It processes satellite signals to extract accurate positioning, velocity, and timing information. The script serves as a hardware integration layer, enabling seamless communication with GPS devices and providing essential GPS data for further analysis or monitoring applications.

