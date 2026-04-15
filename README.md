<div align="center">

# 🚗 Smart Mobility

### Hazard-Aware Route Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Folium](https://img.shields.io/badge/Folium-Maps-77B829?style=for-the-badge&logo=leaflet&logoColor=white)](https://python-visualization.github.io/folium/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> *AI-powered urban route planning with real-time hazard simulation, interactive dark-themed maps, and intelligent risk scoring — for safer, smarter commutes.*

---

<img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="status"/>
<img src="https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square" alt="version"/>

</div>

---

## ✨ Features

| Feature | Description |
|:--------|:------------|
| 🗺️ **Interactive Dark Map** | Live map powered by Folium with CartoDB dark tiles, route overlays, and hazard zones |
| ⚠️ **Hazard Simulation** | Randomly generated real-world hazards — potholes, flooding, accidents, construction & more |
| 🛣️ **Multi-Route Planning** | Compares **Shortest**, **Safest**, and **Balanced** routes side-by-side |
| 📊 **Risk Scoring** | Each route scored based on proximity to active road hazards |
| 📈 **Analytics Dashboard** | Bar charts for hazard distribution by severity & type, plus route comparison tables |
| 🏙️ **Multi-City Support** | Preset coordinates for **Kolkata, Mumbai, Delhi, Bangalore, Chennai, Hyderabad** |
| 🔄 **Live Simulation** | Re-generate hazards and re-plan routes on-the-fly with one click |

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|:------|:-----------|:--------|
| 🖥️ **Frontend** | Streamlit | Interactive dashboard UI |
| 🗺️ **Maps** | Folium + streamlit-folium | Geospatial visualization |
| 📊 **Data** | Pandas · NumPy | Data processing & analysis |
| 🐍 **Language** | Python 3.10+ | Core runtime |

</div>

---

## 🚀 Quick Start

### Prerequisites

- Python **3.10** or higher
- pip package manager

### Installation

```bash
# 1 · Clone the repository
git clone https://github.com/your-username/smart-mobility.git
cd smart-mobility

# 2 · Install dependencies
pip install -r requirements.txt

# 3 · Launch the dashboard
streamlit run app.py
# or if streamlit is not on PATH:
python -m streamlit run app.py
```

> 💡 The app will open automatically at **http://localhost:8501**

---

## 📁 Project Structure

```
smart-mobility/
│
├── 📄 app.py                  # Main Streamlit dashboard — UI, map, tabs, analytics
├── 📄 route_planner.py        # Route planning engine — multi-route generation & risk scoring
├── 📄 hazard_simulator.py     # Hazard simulation — random hazard generation & risk calculation
├── 📄 requirements.txt        # Python dependencies
└── 📄 README.md               # You are here
```

---

## 🧭 How It Works

```mermaid
graph LR
    A[🏙️ Select City] --> B[📍 Set Start & End Points]
    B --> C[⚙️ Configure Simulation]
    C --> D[🔄 Generate Hazards]
    D --> E[🛣️ Plan Routes]
    E --> F[🗺️ View Map & Analytics]
```

1. **Select a city** from the sidebar dropdown or enter custom coordinates
2. **Set start & end points** for your route
3. **Configure simulation** — number of hazards and radius
4. **Click "Simulate Hazards & Plan Routes"** to generate the scenario
5. **Explore the results** across four tabs:
   - 🗺️ **Live Map** — interactive dark-themed map with routes and hazard zones
   - 🛣️ **Routes** — detailed route cards with distance, time, and risk metrics
   - ⚠️ **Hazards** — sortable data table of all active hazards
   - 📊 **Analytics** — severity charts, type distribution, and route comparisons

---

## 📸 Dashboard Tabs

| Tab | What You'll See |
|:----|:----------------|
| **🗺️ Live Map** | Dark-themed Folium map with colored route lines, start/end markers, and hazard circles with severity-based coloring |
| **🛣️ Routes** | Styled route cards showing distance (km), estimated time (min), nearby hazards count, and risk score with color-coded badges |
| **⚠️ Hazards** | Interactive data table listing all simulated hazards with ID, type, severity, description, and coordinates |
| **📊 Analytics** | Bar charts (severity & type breakdown), route comparison table, and an overall area risk progress gauge |

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using Streamlit & Folium**

⭐ Star this repo if you found it useful!

</div>
