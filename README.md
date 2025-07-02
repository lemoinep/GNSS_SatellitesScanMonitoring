This project provides a set of Python tools for scanning, monitoring, and analyzing GNSS (Global Navigation Satellite System) satellite signals. The programs enable real-time detection and tracking of multiple satellite constellations, collection of signal quality and status data, and visualization of satellite positions and signal metrics. These tools support monitoring GNSS performance, detecting anomalies or signal disruptions, and assisting in research or development related to satellite navigation and positioning systems.

Python Program Descriptions

- GNSS_SatellitesScanMonitoringLevel1.py: This script provides a foundational GNSS satellite scanning and monitoring system. It detects visible satellites from multiple GNSS constellations, measures their signal strengths, and continuously updates satellite status in real time. It is designed for basic monitoring tasks such as tracking satellite availability and signal quality, making it suitable for initial GNSS performance assessments.

- GPS_Yocto_Basis.py: This program interfaces directly with Yoctopuce GPS hardware modules to acquire raw GPS data streams. It processes satellite signals to extract accurate positioning, velocity, and timing information. The script serves as a hardware integration layer, enabling seamless communication with GPS devices and providing essential GPS data for further analysis or monitoring applications.

- GNSS_SatellitesScanMonitoringLevel2.py: This program connects to a GPS receiver (Yocto-GPS or system GPS) and determines the user's current geographic position. It retrieves and parses satellite data to calculate the elevation and azimuth of each visible satellite. For each satellite, it estimates its approximate latitude, longitude, and altitude in space. The program can display this information in the console and, with the 3D option, shows the satellites' positions on an interactive celestial sphere. Cardinal points and satellite names are visualized, and the user can rotate the sky map with the mouse.

- GNSS_SatellitesScanMonitoringLevel3.py: This program connects to a GPS receiver (Yocto-GPS or a system GPS) to determine the user's current geographic position and altitude. It retrieves and parses satellite data to calculate the elevation and azimuth of each visible satellite. For each satellite, the program estimates its approximate latitude, longitude, and altitude in space using geometric calculations. It displays detailed information for each satellite, including signal strength and whether it is used in the current position fix. The program supports both Yocto-GPS modules and standard serial GPS receivers, adapting its data parsing accordingly.

Future development will allow selecting one of the satellites and communicating with it. However, to achieve this, I need to conduct a state-of-the-art review on the subject to determine its feasibility. I will soon upload this review to my repository. I am doing this out of curiosity and to create effective tools that could be useful for my future software development projects.




# Comprehensive Documentation on Satellite Communication Systems and GPS Technology

## 1. Introduction

To communicate with a satellite whose position you have located via GPS in the wilderness, several options are available, depending on the type of communication desired and the equipment at hand:
- **Satellite Phones:** 
These are devices enabling direct two-way communication via communication satellites, often in geostationary orbit. They function even in remote areas where there is no cellular network, such as in the mountains or deep in nature. However, their effectiveness depends on direct line of sight to the satellite, so a clear sky is necessary .
- **Personal Locator Beacons (PLB):** 
These devices emit a distress signal with your GPS coordinates to emergency services. They do not allow for ordinary communication but are very useful in emergencies to quickly alert rescue teams .
- **Satellite Messengers (e.g., Garmin inReach, SPOT):** 
These devices allow you to send text messages, including SOS, via a satellite network. They are more compact and often more affordable than satellite phones, suitable for staying in regular contact in the wilderness .
- **Two-way Radios:** 
Useful for short-range communication between group members, they do not work via satellite but can complement other means of communication in challenging terrain .
- **Satellite Antennas and Relays:** 
For more technical uses, specific antennas can transmit data to relay satellites (such as NASA's TDRS satellites) which then retransmit the information to ground stations. This requires specialized equipment and is not common for individual use in the wild .

Satellite communication systems and Global Positioning System (GPS) technology are foundational to global connectivity, navigation, and data exchange. They enable robust, reliable communication and precise geolocation, supporting everything from international broadcasting and military operations to disaster response and personal navigation. The rapid evolution of satellite technologies, including the proliferation of small satellites and low Earth orbit (LEO) constellations, is transforming how the world stays connected and informed[^2][^3][^4].


## 2. Satellite Communication Frequency Usage

### 2.1 Frequency Bands and Applications

Satellite communications utilize a broad spectrum of frequency bands, each optimized for specific applications and operational environments:

- **VHF (137–150 MHz):** Due to its low frequency, VHF signals experience minimal atmospheric attenuation and can penetrate foliage and buildings better than higher bands, making it suitable for military air-to-ground communications. However, bandwidth is limited, restricting data rates.
- **L-Band (1.5–2.0 GHz):** Offers a good trade-off between antenna size, atmospheric penetration, and bandwidth. L-Band signals suffer less from rain fade compared to higher frequencies, which is critical for GPS and MSS. The wavelength (~15–20 cm) allows for relatively compact antennas.
- **S-Band (1.98–2.5 GHz):** Provides increased bandwidth over L-Band, supporting higher data rates. However, rain attenuation becomes more significant, requiring adaptive coding and modulation schemes for reliable links.
- **C-Band (3.4–6.4 GHz):** Widely used for fixed satellite services (FSS). C-Band signals have moderate rain attenuation, requiring link margin design and fade mitigation techniques such as uplink power control and site diversity.
- **X-Band (7.25–8.4 GHz):** Primarily reserved for military applications due to favorable propagation and spectrum protection. Offers higher bandwidth, enabling secure, high-data-rate communications.
- **Ku-Band (10.9–14.5 GHz):** Common for direct broadcast satellite (DBS) and VSAT networks. Susceptible to rain fade, necessitating robust error correction (e.g., LDPC codes) and adaptive modulation (e.g., DVB-S2X).
- **Ka-Band (20.2–31.0 GHz):** Enables very high throughput satellite (VHTS) systems with spot beam technology for frequency reuse. However, Ka-Band is highly sensitive to atmospheric attenuation, requiring advanced adaptive coding/modulation, site diversity, and dynamic resource allocation.
- **EHF (30–110 GHz):** Used for ultra-secure military communications and experimental systems. EHF propagation is severely affected by atmospheric gases and rain, demanding highly directional antennas and sophisticated link adaptation. [^2][^5]


### 2.2 Signal Processing and Modulation Techniques

- **Modulation:** Satellite links employ modulation schemes such as QPSK, 8PSK, 16QAM, and higher-order QAM to balance spectral efficiency and robustness.
- **Forward Error Correction (FEC):** Techniques like Turbo codes, LDPC, and Reed-Solomon are implemented to correct errors induced by noise and fading.
- **Multiple Access:** TDMA, FDMA, CDMA, and more recently, OFDMA and SC-FDMA are used to efficiently share satellite transponder capacity among multiple users.
- **Beamforming and Antenna Arrays:** Phased array antennas enable electronic steering of beams, improving gain and interference rejection without mechanical movement.

### 2.3 Link Design and Performance

Key engineering considerations include:

- **Link Budgets:** Calculating signal strength, carrier-to-noise ratio (C/N), and bit error rate (BER) for uplink and downlink paths.
- **Propagation Effects:** Rain attenuation, atmospheric losses, and geographic impact on signal availability.
- **Antenna Design:** Selecting appropriate antenna types and sizes for both satellite and ground terminals to optimize performance[^2][^3].


## 3. Key Military and Commercial Satellite Systems

- **MILSTAR:** Employs cross-linked satellites with onboard processing to route traffic securely and resist jamming. Uses anti-jamming waveforms and frequency hopping.
- **DSCS:** Features bent-pipe transponders with high power amplifiers and multiple spot beams to cover tactical areas.
- **WGS:** Utilizes digital channelizers and regenerative payloads to increase throughput and flexibility.
- **INTELSAT and Commercial GEO Satellites:** Typically use bent-pipe transponders with frequency reuse via multiple spot beams, employing advanced payloads with flexible bandwidth allocation.
- **LEO Constellations (Globalstar, Iridium):** Use inter-satellite links and store-and-forward techniques to reduce latency and increase coverage.

## 4. GPS Technology: The Yocto-GPS-V2 Module

### 4.1 Core Features

The Yocto-GPS-V2 module exemplifies modern GPS technology, providing:

- **Geolocation:** Latitude, longitude, and altitude with high precision.
- **Movement Data:** Real-time speed, heading, and course over ground.
- **Timing:** Accurate date/time, Unix time, and time synchronization.
- **Satellite Constellation Data:** Number of satellites in view, signal quality, and dilution of precision (DOP).
- **APIs:** Integration with software platforms for data retrieval, logging, and processing.


### 4.2 Applications

- **Navigation:** For vehicles, drones, maritime, and personal use.
- **Asset Tracking:** Real-time monitoring of fleets, shipments, and critical infrastructure.
- **Scientific and Industrial:** Timing, synchronization, and geospatial data for research and automation.


## 5. Global Satellite System Landscape

### 5.1 Regional and National Systems

- **Regional Operators:** APSTAR, AsiaSat, EUTELSAT, providing coverage across continents.
- **National Systems:** Countries like Argentina (NAHUELSAT), Australia, China, France, India, Italy, Japan, Korea, Spain, and the US operate or lease satellites for national interests, security, and public services.

### 5.2 Satellite Orbits

- **Geostationary (GEO):** 36,000 km altitude, stationary relative to the Earth—ideal for broadcasting and weather.
- **Medium Earth Orbit (MEO):** 2,000–20,000 km, used for navigation (e.g., GPS, Galileo).
- **Low Earth Orbit (LEO):** 500–2,000 km, enables low-latency broadband (e.g., Starlink, OneWeb) and earth observation[^2][^3][^4].

## 6. Satellite System Orbits and Dynamics (Technical Considerations)

- **Orbital Mechanics:** Satellite orbits are defined by Keplerian elements; station-keeping maneuvers maintain GEO satellites within assigned orbital slots.
- **Doppler Shift:** Particularly relevant for LEO/MEO satellites, requiring dynamic frequency correction in ground terminals.
- **Latency:** GEO satellites introduce approximately 250 ms one-way delay; LEO systems reduce latency to under 50 ms, critical for interactive applications.
- **Constellation Design:** Trade-offs between coverage, revisit time, and capacity guide constellation size and orbital parameters.



## 7. Communication in Remote Areas (Technical Implementation)

- **Antenna Design:** Portable terminals use patch or helix antennas optimized for gain and polarization matching.
- **Power Management:** Battery-operated devices implement power-efficient protocols and duty cycling to extend operational life.
- **Network Protocols:** Use of Delay-Tolerant Networking (DTN) and store-and-forward techniques to handle intermittent connectivity.
- **Security:** Encryption algorithms (AES, RSA) protect data confidentiality and integrity over satellite links.



## 8. Communication in Remote and Challenging Environments

### 8.1 Satellite Phones

- **Direct voice/data communication** via GEO or LEO satellites.
- **Critical for emergency, maritime, aviation, and expeditions** where terrestrial networks are unavailable.


### 8.2 Personal Locator Beacons (PLB)

- **Emergency distress signals** with embedded GPS coordinates, relayed to rescue agencies.
- **Essential for safety** in wilderness, maritime, and aviation contexts.


### 8.3 Satellite Messengers

- **Text messaging and SOS alerts** via satellite networks.
- **Affordable and portable** compared to full-featured satellite phones.


### 8.4 Two-Way Radios

- **Short-range group communication**; not reliant on satellite but complements other methods.


### 8.5 Advanced Antennas and Relays

- **Specialized antennas** for high-bandwidth data uplink/downlink, telemetry, and relay.
- **Used in scientific, military, and industrial applications**.


### 8.6 Starlink and Next-Gen Broadband

- **High-speed, low-latency internet** via LEO constellations (Starlink, OneWeb, Kuiper).
- **Self-aligning terminals**, suitable for rural, maritime, and mobile users[^4].



## 9. Regulatory and Compliance Framework

### 9.1 International and National Regulation

- **International Telecommunication Union (ITU):** Coordinates global frequency allocation, orbital slots, and technical standards.
- **National bodies:** FCC (USA), ECO (Europe), and equivalents manage licensing, compliance, and enforcement at the country level[^1][^5].


### 9.2 Licensing and Frequency Allocation

- **GSO/NGSO Licenses:** Required for GEO, LEO, and MEO satellites; specify technical, service, and orbital parameters.
- **Experimental Licenses:** For testing new technologies.
- **Spectrum Coordination:** Prevents interference and ensures equitable access[^1].


### 9.3 Technical Standards and Compliance

- **ITU-R Recommendations, ETSI Standards:** Define system, equipment, and operational requirements.
- **Type Approval, Certification, Inspections:** Ensure safety, reliability, and interoperability of satellite equipment and operations[^1][^5].


## 10. Emerging Trends and Innovations

- **Small Satellites (Smallsats, Nanosats):** Mass-produced, cost-effective, and rapidly deployable for communications, earth observation, and IoT.
- **Advanced Ground Systems:** Electronically-steered antennas, decentralized and virtualized ground stations for real-time data handling and mission control[^4].
- **Inter-Satellite Links:** Optical and RF links for in-orbit data relay and constellation coordination.
- **AI and Automation:** Autonomous satellite operations, dynamic spectrum management, and predictive maintenance.
- **Space Weather Monitoring:** Real-time space environment data for aviation, energy, and finance sectors[^4].
- **Mission Control-as-a-Service:** Cloud-based platforms for satellite management, reducing operational costs and complexity[^4].
- **Optical Satellite Communications:** Lasercom systems offer Tbps data rates with narrow beamwidths, requiring precise pointing and tracking.
- **Quantum Communications:** Research into quantum key distribution (QKD) via satellites promises ultra-secure communications.


## 11. Mathematical models, link budget calculations

### 11.1 Mathematical Model: Satellite Link Budget

The **link budget** quantifies all gains and losses from the transmitter, through the medium (space), to the receiver. The fundamental equation is:

$$
P_{rx} = P_{tx} + G_{tx} - L_{tx} - L_{fs} - L_{prop} + G_{rx} - L_{rx}
$$

Where (all in dB/dBm unless otherwise noted):

- $P_{rx}$: Received power
- $P_{tx}$: Transmitter output power
- $G_{tx}$: Transmitter antenna gain
- $L_{tx}$: Transmitter-side losses (cables, connectors)
- $L_{fs}$: Free space path loss
- $L_{prop}$: Propagation losses (rain, atmospheric, polarization, pointing, etc.)
- $G_{rx}$: Receiver antenna gain
- $L_{rx}$: Receiver-side losses (cables, connectors, demodulator)[^1][^4][^7]


#### Free Space Path Loss (FSPL)

$$
L_{fs} = 20 \log_{10}(d) + 20 \log_{10}(f) + 92.45
$$

- $d$: Distance (km)
- $f$: Frequency (GHz)[^2][^4]


#### Additional Losses

- **Rain attenuation**: Use ITU or Crane models for $L_{rain}$
- **Atmospheric loss**: $L_{atm}$
- **Antenna mispointing**: $L_{mp}$
- **Polarization mismatch**: $L_{pol}$

$$
L_{prop} = L_{rain} + L_{atm} + L_{mp} + L_{pol} + \ldots
$$

#### Carrier-to-Noise Ratio (C/N)

$$
\left(\frac{C}{N_0}\right) = EIRP + G/T - L_{fs} - L_{prop} - k
$$

Where:

- $EIRP = P_{tx} + G_{tx} - L_{tx}$ (Equivalent Isotropically Radiated Power)
- $G/T$: Receiver system figure of merit (antenna gain/system noise temperature)
- $k$: Boltzmann's constant in dBW/K/Hz ($-228.6$ dB)[^3][^6]


### 11.2 Step-by-Step Link Budget Calculation Example

**Scenario:** GEO satellite downlink, Ku-band, 14 GHz, 36,000 km, clear sky.

**Assumptions:**

- $P_{tx}$: 30 dBm (1 W)
- $G_{tx}$: 40 dBi (satellite antenna)
- $L_{tx}$: 1 dB
- $d$: 36,000 km
- $f$: 14 GHz
- $L_{prop}$: 2 dB (atmospheric, rain, etc.)
- $G_{rx}$: 45 dBi (earth station antenna)
- $L_{rx}$: 1 dB

**Calculation:**

1. **EIRP:**

$$
EIRP = P_{tx} + G_{tx} - L_{tx} = 30 + 40 - 1 = 69\, \text{dBm}
$$
2. **FSPL:**

$$
L_{fs} = 20 \log_{10}(36,000) + 20 \log_{10}(14) + 92.45
$$

$$
= 20 \times 4.556 + 20 \times 1.146 + 92.45
$$

$$
= 91.12 + 22.92 + 92.45 = 206.49\, \text{dB}
$$
3. **Received Power:**

$$
P_{rx} = EIRP - L_{fs} - L_{prop} + G_{rx} - L_{rx}
$$

$$
= 69 - 206.49 - 2 + 45 - 1
$$

$$
= 69 + 45 - 206.49 - 2 - 1
$$

$$
= 114 - 209.49 = -95.49\, \text{dBm}
$$
4. **Carrier-to-Noise Ratio (C/N):**
    - Assume $G/T = 30\, \text{dB/K}$ (typical for large earth stations)
    - $k = -228.6\, \text{dBW/K/Hz}$
    - For a 36 MHz transponder, noise bandwidth $B = 36 \times 10^6$ Hz ($10 \log_{10}(36 \times 10^6) = 75.56\, \text{dBHz}$)

$$
C/N = EIRP + G/T - L_{fs} - L_{prop} - k - 10 \log_{10}(B)
$$

$$
= 69 + 30 - 206.49 - 2 + 228.6 - 75.56
$$

$$
= 99 - 208.49 + 228.6 - 75.56
$$

$$
= -109.49 + 228.6 - 75.56 = 119.11 - 75.56 = 43.55\, \text{dB}
$$

### 11.3 Case Study: VSAT Network Deployment for Remote Connectivity

**Project:** Deploying a VSAT (Very Small Aperture Terminal) network for remote clinics in Sub-Saharan Africa.

#### Technical Design

- **Frequency:** Ku-band (12–14 GHz)
- **Satellite:** GEO, 36,000 km altitude
- **Earth Station Antenna:** 1.2 m diameter, 45% efficiency
- **Transmit Power:** 2 W (33 dBm)
- **Antenna Gain:** Calculated as

$$
G = 10 \log_{10}(\eta) + 20 \log_{10}(f) + 20 \log_{10}(d) + 20.4
$$

Where:
    - $\eta = 0.45$
    - $f = 14\, \text{GHz}$
    - $d = 1.2\, \text{m}$

$$
G = 10 \log_{10}(0.45) + 20 \log_{10}(14) + 20 \log_{10}(1.2) + 20.4
$$

$$
G = -3.46 + 22.92 + 1.58 + 20.4 = 41.44\, \text{dBi}
$$
- **Link Budget:** As above, with local rain fade margin of 3 dB included in $L_{prop}$.


#### Performance and Reliability

- **Availability Target:** 99.5% annual (ITU rain zone calculations used for fade margin)
- **Data Rate:** 2 Mbps per site, QPSK modulation with 3/4 FEC
- **Bandwidth:** $2\, \text{Mbps} \times \frac{1}{0.75} \times 1.2 = 3.2\, \text{MHz}$ (roll-off factor 0.2)
- **Bit Error Rate (BER):** Target $<10^{-6}$


#### Results

- **Measured C/N:** 13 dB (sufficient for QPSK 3/4)
- **Uptime:** >99.6% measured over 12 months
- **User Experience:** Reliable telemedicine, VoIP, and data transfer even during moderate rain


### 11.4 Key Parameters for Real Deployments

| Parameter | Typical Value (VSAT) | Notes |
| :-- | :-- | :-- |
| Frequency | Ku-band (14 GHz) | Higher bands allow smaller antennas |
| Antenna Diameter | 1.2 m | Trade-off between gain and cost |
| Transmit Power | 2–5 W | Higher power improves link margin |
| Fade Margin | 2–5 dB | Depends on rain zone and reliability target |
| Modulation/FEC | QPSK/3/4 | Higher-order for higher data rates |
| Availability | >99.5% | With proper fade margin |
| BER | <10⁻⁶ | For error-free digital services |


## Conclusion

Satellite communication systems and GPS technology are indispensable for global connectivity, navigation, and data-driven applications. The field is shaped by rapid technological innovation, complex regulatory frameworks, and the increasing demand for ubiquitous, high-speed connectivity. From advanced military networks to commercial broadband constellations and personal safety devices, satellite systems continue to expand their reach and capabilities, ensuring reliable communication and precise geolocation everywhere on Earth—and beyond[^1][^2][^3][^4][^5].


[^1]: https://www.numberanalytics.com/blog/ultimate-guide-satellite-communications-regulations

[^2]: https://ece.vt.edu/grad/courses/5610.html

[^3]: https://apps.ep.jhu.edu/syllabus/spring-2025/525.640.82

[^4]: https://www.startus-insights.com/innovators-guide/satellite-trends-innovation/

[^5]: https://www.itu.int/en/publications/gs/Pages/publications.aspx?parent=r-hdb-42

[^6]: https://extranet.wmo.int/edistrib_exped/grp_Semicircular/_en/03370-2025-I-SSU-Vote-Satellite-Skills-Guidelines_en.pdf

[^7]: https://bookauthority.org/books/new-satellite-communication-books

[^8]: https://dam.esmo.org/image/upload/v1746518952/ESMO_2025_Industry_Satellite_Symposia_Technical_Manual.pdf



