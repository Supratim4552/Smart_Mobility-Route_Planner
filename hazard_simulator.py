"""
Hazard Simulator Module
Simulates real-time road hazards for smart mobility route planning.
"""

import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple
from datetime import datetime


@dataclass
class Hazard:
    """Represents a road hazard."""
    id: str
    name: str
    latitude: float
    longitude: float
    severity: str  # "low", "medium", "high", "critical"
    hazard_type: str
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    radius_m: float = 100.0  # affected radius in meters

    @property
    def severity_color(self) -> str:
        colors = {
            "low": "#2ecc71",
            "medium": "#f39c12",
            "high": "#e74c3c",
            "critical": "#8e44ad",
        }
        return colors.get(self.severity, "#95a5a6")

    @property
    def severity_score(self) -> int:
        scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return scores.get(self.severity, 0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "severity": self.severity,
            "hazard_type": self.hazard_type,
            "description": self.description,
            "timestamp": self.timestamp,
            "radius_m": self.radius_m,
            "severity_color": self.severity_color,
            "severity_score": self.severity_score,
        }


HAZARD_TEMPLATES = [
    {
        "name": "Pothole Cluster",
        "hazard_type": "Road Damage",
        "description": "Multiple deep potholes across lanes",
        "severity": "high",
        "icon": "⚠️",
    },
    {
        "name": "Waterlogging",
        "hazard_type": "Flooding",
        "description": "Stagnant water accumulation due to poor drainage",
        "severity": "medium",
        "icon": "🌊",
    },
    {
        "name": "Accident Zone",
        "hazard_type": "Accident",
        "description": "Vehicle collision causing lane blockage",
        "severity": "critical",
        "icon": "🚨",
    },
    {
        "name": "Construction Site",
        "hazard_type": "Construction",
        "description": "Active road construction with lane closure",
        "severity": "medium",
        "icon": "🚧",
    },
    {
        "name": "Signal Malfunction",
        "hazard_type": "Infrastructure",
        "description": "Traffic signal not working properly",
        "severity": "high",
        "icon": "🚦",
    },
    {
        "name": "Fallen Tree",
        "hazard_type": "Natural",
        "description": "Tree obstruction blocking partial roadway",
        "severity": "high",
        "icon": "🌳",
    },
    {
        "name": "Oil Spill",
        "hazard_type": "Road Damage",
        "description": "Slippery road surface due to oil spillage",
        "severity": "medium",
        "icon": "🛢️",
    },
    {
        "name": "Heavy Fog Zone",
        "hazard_type": "Weather",
        "description": "Dense fog reducing visibility below 50m",
        "severity": "high",
        "icon": "🌫️",
    },
    {
        "name": "Landslide Risk",
        "hazard_type": "Natural",
        "description": "Loose debris and soil near hillside road",
        "severity": "critical",
        "icon": "⛰️",
    },
    {
        "name": "Speed Breaker (Unmarked)",
        "hazard_type": "Road Damage",
        "description": "Unmarked speed bump causing vehicle damage",
        "severity": "low",
        "icon": "🔶",
    },
]


class HazardSimulator:
    """Simulates hazards in a given geographical area."""

    def __init__(self, center_lat: float, center_lon: float, radius_km: float = 5.0):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_km = radius_km
        self.hazards: List[Hazard] = []
        self._counter = 0

    def _random_point_in_radius(self) -> Tuple[float, float]:
        """Generate a random lat/lon within the simulation radius."""
        # Convert km to approximate degrees
        lat_offset = self.radius_km / 111.0
        lon_offset = self.radius_km / (111.0 * np.cos(np.radians(self.center_lat)))

        lat = self.center_lat + random.uniform(-lat_offset, lat_offset)
        lon = self.center_lon + random.uniform(-lon_offset, lon_offset)
        return round(lat, 6), round(lon, 6)

    def generate_hazards(self, count: int = 8) -> List[Hazard]:
        """Generate a set of random hazards around the center point."""
        self.hazards = []
        templates = random.sample(HAZARD_TEMPLATES, min(count, len(HAZARD_TEMPLATES)))

        for template in templates:
            self._counter += 1
            lat, lon = self._random_point_in_radius()
            hazard = Hazard(
                id=f"HAZ-{self._counter:04d}",
                name=template["name"],
                latitude=lat,
                longitude=lon,
                severity=template["severity"],
                hazard_type=template["hazard_type"],
                description=template["description"],
                radius_m=random.uniform(50, 300),
            )
            self.hazards.append(hazard)

        return self.hazards

    def get_hazards_by_severity(self, severity: str) -> List[Hazard]:
        """Filter hazards by severity level."""
        return [h for h in self.hazards if h.severity == severity]

    def get_hazard_summary(self) -> dict:
        """Get a summary of current hazards."""
        summary = {"total": len(self.hazards), "by_severity": {}, "by_type": {}}
        for h in self.hazards:
            summary["by_severity"][h.severity] = summary["by_severity"].get(h.severity, 0) + 1
            summary["by_type"][h.hazard_type] = summary["by_type"].get(h.hazard_type, 0) + 1
        return summary

    def calculate_risk_score(self) -> float:
        """Calculate overall risk score for the area (0-100)."""
        if not self.hazards:
            return 0.0
        total_score = sum(h.severity_score for h in self.hazards)
        max_possible = len(self.hazards) * 4
        return round((total_score / max_possible) * 100, 1)
