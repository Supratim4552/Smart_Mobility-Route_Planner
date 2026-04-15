"""
Route Planner Module
Provides route planning with hazard-aware pathfinding for smart mobility.
"""

import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from hazard_simulator import Hazard


@dataclass
class RoutePoint:
    """A point along a route."""
    latitude: float
    longitude: float
    label: str = ""


@dataclass
class Route:
    """Represents a planned route."""
    name: str
    points: List[RoutePoint]
    distance_km: float
    estimated_time_min: float
    hazard_count: int = 0
    risk_score: float = 0.0
    color: str = "#3498db"
    is_recommended: bool = False

    @property
    def avg_speed_kmh(self) -> float:
        if self.estimated_time_min == 0:
            return 0
        return round((self.distance_km / self.estimated_time_min) * 60, 1)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on Earth (km)."""
    R = 6371.0
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def _generate_intermediate_points(
    start: RoutePoint, end: RoutePoint, num_waypoints: int = 4, jitter: float = 0.008
) -> List[RoutePoint]:
    """Generate intermediate waypoints between start and end with random jitter."""
    points = [start]
    for i in range(1, num_waypoints + 1):
        frac = i / (num_waypoints + 1)
        lat = start.latitude + frac * (end.latitude - start.latitude) + random.uniform(-jitter, jitter)
        lon = start.longitude + frac * (end.longitude - start.longitude) + random.uniform(-jitter, jitter)
        points.append(RoutePoint(latitude=round(lat, 6), longitude=round(lon, 6), label=f"WP-{i}"))
    points.append(end)
    return points


def _count_nearby_hazards(route_points: List[RoutePoint], hazards: List[Hazard], threshold_km: float = 0.5) -> int:
    """Count hazards near any point on the route."""
    count = 0
    for hazard in hazards:
        for pt in route_points:
            dist = haversine_distance(pt.latitude, pt.longitude, hazard.latitude, hazard.longitude)
            if dist < threshold_km:
                count += 1
                break
    return count


def _calculate_route_risk(route_points: List[RoutePoint], hazards: List[Hazard], threshold_km: float = 0.5) -> float:
    """Calculate a risk score (0-100) for a route based on nearby hazards."""
    if not hazards:
        return 0.0

    total_risk = 0.0
    for hazard in hazards:
        min_dist = float("inf")
        for pt in route_points:
            dist = haversine_distance(pt.latitude, pt.longitude, hazard.latitude, hazard.longitude)
            min_dist = min(min_dist, dist)
        if min_dist < threshold_km:
            proximity_factor = 1.0 - (min_dist / threshold_km)
            total_risk += hazard.severity_score * proximity_factor

    max_possible = len(hazards) * 4
    return round(min((total_risk / max_possible) * 100, 100.0), 1)


def plan_routes(
    start: RoutePoint,
    end: RoutePoint,
    hazards: List[Hazard],
    num_routes: int = 3,
) -> List[Route]:
    """
    Plan multiple routes between start and end, evaluate against hazards.
    Returns routes sorted by recommendation (lowest risk first).
    """
    direct_dist = haversine_distance(start.latitude, start.longitude, end.latitude, end.longitude)
    routes: List[Route] = []

    route_configs = [
        {"name": "🛣️ Shortest Route", "jitter": 0.003, "speed_range": (35, 45), "color": "#e74c3c", "waypoints": 3},
        {"name": "🛡️ Safest Route", "jitter": 0.015, "speed_range": (25, 35), "color": "#2ecc71", "waypoints": 5},
        {"name": "⚡ Balanced Route", "jitter": 0.008, "speed_range": (30, 40), "color": "#3498db", "waypoints": 4},
    ]

    for i, config in enumerate(route_configs[:num_routes]):
        points = _generate_intermediate_points(start, end, num_waypoints=config["waypoints"], jitter=config["jitter"])

        # Calculate total distance along the route
        total_dist = 0.0
        for j in range(len(points) - 1):
            total_dist += haversine_distance(
                points[j].latitude, points[j].longitude,
                points[j + 1].latitude, points[j + 1].longitude,
            )

        avg_speed = random.uniform(*config["speed_range"])
        est_time = (total_dist / avg_speed) * 60  # minutes

        hazard_count = _count_nearby_hazards(points, hazards)
        risk_score = _calculate_route_risk(points, hazards)

        routes.append(
            Route(
                name=config["name"],
                points=points,
                distance_km=round(total_dist, 2),
                estimated_time_min=round(est_time, 1),
                hazard_count=hazard_count,
                risk_score=risk_score,
                color=config["color"],
            )
        )

    # Mark the route with the lowest risk as recommended
    if routes:
        best = min(routes, key=lambda r: r.risk_score)
        best.is_recommended = True

    return sorted(routes, key=lambda r: r.risk_score)
