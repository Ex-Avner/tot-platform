"""
Triaxial Orientation Theory — Geometric Engine
================================================
Mathematical core for computing positions, zones, captures, shape parameters,
stamp signatures, and asymmetric deformations within the octahedral interior.

Theory: Ross Erickson / Avner Media
Implementation: TOT Research Platform v1.0

All computations are derived from the formal definitions in:
  - Triaxial Orientation Theory (FINAL)
  - Structural Configurations
  - The Eight Configurations
  - The Twenty-Four Subtypes
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
import json


# =============================================================================
# CONSTANTS & DEFINITIONS
# =============================================================================

class Pole(Enum):
    OHN = "Ohn"           # Ground of Being (Vertical -)
    HOC = "Hoc"           # Present Moment / Surface (Vertical +)
    HIM = "Him"           # Singular Self (Horizontal -)
    ALLMEN = "Allmen"     # Collective Other (Horizontal +)
    WASONCE = "Wasonce"   # Ancestral Past (Temporal -)
    WILLBE = "Willbe"     # Unborn Future (Temporal +)

class Axis(Enum):
    VERTICAL = "Vertical (Depth)"
    HORIZONTAL = "Horizontal (Breath)"
    TEMPORAL = "Temporal (Obligation)"

class Zone(Enum):
    I = "Zone I: The Performer"
    II = "Zone II: The Crowd"
    III = "Zone III: The Mystic"
    IV = "Zone IV: The Congregation"
    V = "Zone V: The Archivist"
    VI = "Zone VI: The Tradition"
    VII = "Zone VII: The Prophet"
    VIII = "Zone VIII: The Somey"

class CaptureType(Enum):
    VERTEX = "Vertex Capture"
    EDGE = "Edge Capture"
    FACE = "Face Capture"
    NONE = "No Capture"

class StampType(Enum):
    SCARCITY = "Scarcity Stamp"
    DISPLACEMENT = "Displacement Stamp"
    VIOLENCE = "Violence Stamp"
    SILENCING = "Silencing Stamp"
    ABANDONMENT = "Abandonment Stamp"

class DeformationType(Enum):
    AXIAL_COMPRESSION = "Axial Compression"
    AXIAL_FRACTURE = "Axial Fracture"
    POLAR_INVERSION = "Polar Inversion"
    PLANAR_SKEW = "Planar Skew"
    VOLUMETRIC_COLLAPSE = "Volumetric Collapse"

# Octahedron vertices (unit distance from origin)
VERTICES = {
    Pole.OHN:     np.array([0, 0, -1], dtype=float),   # Depth (V-)
    Pole.HOC:     np.array([0, 0,  1], dtype=float),   # Surface (V+)
    Pole.HIM:     np.array([-1, 0, 0], dtype=float),   # Singular (H-)
    Pole.ALLMEN:  np.array([ 1, 0, 0], dtype=float),   # Plural (H+)
    Pole.WASONCE: np.array([0, -1, 0], dtype=float),   # Past (T-)
    Pole.WILLBE:  np.array([0,  1, 0], dtype=float),   # Future (T+)
}

# Octahedron edges: 12 edges connecting adjacent poles
EDGES = [
    # Temporal axis collapsed (4 edges)
    (Pole.OHN, Pole.HIM),      # Ground + Singular
    (Pole.OHN, Pole.ALLMEN),   # Ground + Collective
    (Pole.HOC, Pole.HIM),      # Surface + Singular
    (Pole.HOC, Pole.ALLMEN),   # Surface + Collective
    # Horizontal axis collapsed (4 edges)
    (Pole.OHN, Pole.WASONCE),  # Ground + Ancestral
    (Pole.OHN, Pole.WILLBE),   # Ground + Futural
    (Pole.HOC, Pole.WASONCE),  # Surface + Ancestral
    (Pole.HOC, Pole.WILLBE),   # Surface + Futural
    # Vertical axis collapsed (4 edges)
    (Pole.HIM, Pole.WASONCE),  # Singular + Ancestral
    (Pole.HIM, Pole.WILLBE),   # Singular + Futural
    (Pole.ALLMEN, Pole.WASONCE), # Collective + Ancestral
    (Pole.ALLMEN, Pole.WILLBE),  # Collective + Futural
]

# Edge descriptions from the Structural Configurations document
EDGE_DESCRIPTIONS = {
    (Pole.OHN, Pole.HIM): {
        "name": "The Consumed Contemplative",
        "character": "Deep isolated present. Profound depth coupled with total withdrawal, severed from time.",
        "collapsed_axis": Axis.TEMPORAL,
    },
    (Pole.OHN, Pole.ALLMEN): {
        "name": "The Ecstatic Gathering",
        "character": "Deep communal present. Depth shared with others but disconnected from the chain of time.",
        "collapsed_axis": Axis.TEMPORAL,
    },
    (Pole.HOC, Pole.HIM): {
        "name": "The High-Performing Loner",
        "character": "Flat isolated present. Maximum productivity with no depth, connection, or temporal orientation.",
        "collapsed_axis": Axis.TEMPORAL,
    },
    (Pole.HOC, Pole.ALLMEN): {
        "name": "The Scroll",
        "character": "Flat communal present. Connected and surface and now. Togetherness without depth or duration.",
        "collapsed_axis": Axis.TEMPORAL,
    },
    (Pole.OHN, Pole.WASONCE): {
        "name": "The Archival Mystic",
        "character": "Deep ancestral solitude. Keeper of inherited mysteries who cannot share them.",
        "collapsed_axis": Axis.HORIZONTAL,
    },
    (Pole.OHN, Pole.WILLBE): {
        "name": "The Visionary Prophet",
        "character": "Deep futural solitude. Can see what must be built; cannot find the hands to build it.",
        "collapsed_axis": Axis.HORIZONTAL,
    },
    (Pole.HOC, Pole.WASONCE): {
        "name": "The Nostalgist",
        "character": "Flat ancestral fixation. Historical nostalgia without depth or relational life.",
        "collapsed_axis": Axis.HORIZONTAL,
    },
    (Pole.HOC, Pole.WILLBE): {
        "name": "The Techno-Optimist",
        "character": "Flat futural fixation. Planning without depth or community.",
        "collapsed_axis": Axis.HORIZONTAL,
    },
    (Pole.HIM, Pole.WASONCE): {
        "name": "The Duty-Bound Loner",
        "character": "Individuated ancestral surface. Carries inherited obligation as duty rather than felt connection.",
        "collapsed_axis": Axis.VERTICAL,
    },
    (Pole.HIM, Pole.WILLBE): {
        "name": "The Absent Builder",
        "character": "Individuated futural surface. Building for the future alone, with nothing underneath.",
        "collapsed_axis": Axis.VERTICAL,
    },
    (Pole.ALLMEN, Pole.WASONCE): {
        "name": "The Empty Ceremony",
        "character": "Communal ancestral surface. Cultural tradition without depth. Ritual as routine.",
        "collapsed_axis": Axis.VERTICAL,
    },
    (Pole.ALLMEN, Pole.WILLBE): {
        "name": "The Hollow Movement",
        "character": "Communal futural surface. Organized, collective, building together. But hollow.",
        "collapsed_axis": Axis.VERTICAL,
    },
}

# Zone definitions: (V_sign, H_sign, T_active)
# V: negative = deep (Ohn), positive = surface (Hoc)
# H: negative = singular (Him), positive = plural (Allmen)
# T: False = present-only (collapsed), True = temporally full
ZONE_DEFINITIONS = {
    Zone.I:    {"v": "surface", "h": "singular", "t": "collapsed",
                "name": "The Performer", "character": "Isolated, high-function, meaningless."},
    Zone.II:   {"v": "surface", "h": "plural",   "t": "collapsed",
                "name": "The Crowd", "character": "Diffuse, socially active, rootless."},
    Zone.III:  {"v": "deep",    "h": "singular", "t": "collapsed",
                "name": "The Mystic", "character": "Deep source contact without social integration or temporal obligation."},
    Zone.IV:   {"v": "deep",    "h": "plural",   "t": "collapsed",
                "name": "The Congregation", "character": "Religious community without historical grounding."},
    Zone.V:    {"v": "surface", "h": "singular", "t": "active",
                "name": "The Archivist", "character": "Historical individualism. The lone ancestor-bearer."},
    Zone.VI:   {"v": "surface", "h": "plural",   "t": "active",
                "name": "The Tradition", "character": "Cultural tradition without depth."},
    Zone.VII:  {"v": "deep",    "h": "singular", "t": "active",
                "name": "The Prophet", "character": "Prophetic isolation. Depth, obligation, but no community."},
    Zone.VIII: {"v": "deep",    "h": "plural",   "t": "active",
                "name": "The Somey", "character": "Full integration. Contact with source, with others, with time."},
}

# 24 Subtypes: 3 per zone
SUBTYPES = {
    Zone.I: [
        {"name": "The Optimizer", "description": "Peak performance as purpose replacement.",
         "bias": np.array([0.0, 0.0, 0.5])},  # Leans toward Hoc strongly
        {"name": "The Ghost", "description": "Functional dissociation. Present in the room, absent from experience.",
         "bias": np.array([0.0, -0.3, 0.3])},  # Moderate surface, more singular
        {"name": "The Competitor", "description": "Identity through opposition. The self exists only against something.",
         "bias": np.array([0.0, -0.5, 0.2])},  # Strong singular lean
    ],
    Zone.II: [
        {"name": "The Mirror", "description": "Identity shifts to match whoever is in the room.",
         "bias": np.array([0.0, 0.5, 0.3])},
        {"name": "The Influencer", "description": "Social presence as substitute for self. Audience as identity.",
         "bias": np.array([0.0, 0.3, 0.5])},
        {"name": "The Swarm", "description": "Group identity without individual moral discernment.",
         "bias": np.array([0.0, 0.5, 0.5])},
    ],
    Zone.III: [
        {"name": "The Hermit", "description": "Genuine depth contact, total withdrawal from the horizontal.",
         "bias": np.array([0.0, -0.5, -0.5])},
        {"name": "The Psychonaut", "description": "Depth through altered states. No integration.",
         "bias": np.array([0.0, -0.3, -0.3])},
        {"name": "The Sage Trap", "description": "Depth contact weaponized as superiority.",
         "bias": np.array([0.0, -0.5, -0.3])},
    ],
    Zone.IV: [
        {"name": "The Revival", "description": "Intense communal spiritual experience. No history. No tomorrow.",
         "bias": np.array([0.0, 0.5, -0.5])},
        {"name": "The Circle", "description": "Authentic community depth that reinvents the wheel every generation.",
         "bias": np.array([0.0, 0.3, -0.3])},
        {"name": "The Greenhouse", "description": "Genuine transformation in a sealed environment. No export.",
         "bias": np.array([0.0, 0.3, -0.5])},
    ],
    Zone.V: [
        {"name": "The Burden-Bearer", "description": "Carries generational weight alone. Cannot put it down.",
         "bias": np.array([-0.3, -0.3, 0.3])},
        {"name": "The Historian", "description": "Knows everything about what happened. Connects to nothing deeper.",
         "bias": np.array([0.0, -0.3, 0.5])},
        {"name": "The Sentinel", "description": "Watches the long-term consequences. Nobody is listening.",
         "bias": np.array([0.3, -0.3, 0.3])},
    ],
    Zone.VI: [
        {"name": "The Custodian", "description": "Maintains form after meaning has departed.",
         "bias": np.array([-0.3, 0.3, 0.3])},
        {"name": "The Monument", "description": "Collective identity through heritage performance rather than living practice.",
         "bias": np.array([0.0, 0.5, 0.3])},
        {"name": "The Institution", "description": "Organizational memory without living purpose.",
         "bias": np.array([0.0, 0.3, 0.5])},
    ],
    Zone.VII: [
        {"name": "The Visionary", "description": "Genuine sight. Genuine isolation. The framework without the room.",
         "bias": np.array([0.0, -0.5, -0.3])},
        {"name": "The Martyr", "description": "Depth and obligation without community. Sacrificial by structure.",
         "bias": np.array([-0.3, -0.5, -0.3])},
        {"name": "The Builder", "description": "Creates the architecture nobody has been invited into.",
         "bias": np.array([0.3, -0.3, -0.5])},
    ],
    Zone.VIII: [
        {"name": "The Moment", "description": "Temporary full orientation. Cannot be held. Can be recognized.",
         "bias": np.array([0.0, 0.0, 0.0])},
        {"name": "The Elder", "description": "Sustained practice across all three axes. Never permanent. Always returning.",
         "bias": np.array([0.0, 0.0, -0.2])},
        {"name": "The Bridge", "description": "Connects shards. Facilitates the assembly without directing it.",
         "bias": np.array([0.0, 0.2, 0.0])},
    ],
}

# Stamp signature profiles
STAMP_PROFILES = {
    StampType.SCARCITY: {
        "description": "Famine, poverty, resource deprivation sustained across generations.",
        "signature": {
            "v_bias": "surface",    # Depth is luxury scarcity doesn't permit
            "h_bias": "singular",   # Trust is expensive; must hoard
            "t_bias": "past",       # Inherited experience of loss dominates
            "shape_effect": "compression",  # Tight angular octahedron
        },
        "detection_weights": np.array([0.2, 0.8, -0.6, -0.2, -0.5, 0.1]),
        # [ohn, hoc, him, allmen, wasonce, willbe] — high surface, high singular, high past
    },
    StampType.DISPLACEMENT: {
        "description": "Forced migration, exile, cultural severance sustained across generations.",
        "signature": {
            "v_bias": "surface",     # Survival mode
            "h_bias": "plural",      # Cling to displaced community
            "t_bias": "collapsed",   # Severed on both ends
            "shape_effect": "compression",
        },
        "detection_weights": np.array([0.1, 0.7, -0.3, 0.6, -0.1, -0.1]),
    },
    StampType.VIOLENCE: {
        "description": "Sustained exposure to violence across generations.",
        "signature": {
            "v_bias": "surface",     # Dissociation from depth
            "h_bias": "fractured",   # Axis is broken, not collapsed
            "t_bias": "past",        # Hypervigilance monitoring past
            "shape_effect": "fracture",
        },
        "detection_weights": np.array([0.1, 0.6, -0.1, -0.1, -0.6, 0.0]),
    },
    StampType.SILENCING: {
        "description": "Sustained suppression of voice, truth, identity, or expression.",
        "signature": {
            "v_bias": "inverted",    # Depth present but toxic
            "h_bias": "performative", # Oscillation works but with false self
            "t_bias": "neutral",
            "shape_effect": "inversion",
        },
        "detection_weights": np.array([-0.4, 0.3, -0.2, 0.2, -0.1, 0.0]),
    },
    StampType.ABANDONMENT: {
        "description": "Parental absence, repeated relational severing across generations.",
        "signature": {
            "v_bias": "unfunded",   # Depth accessible but unshared
            "h_bias": "singular",   # Recoil from connection
            "t_bias": "future",     # Always looking for next thing
            "shape_effect": "compression",
        },
        "detection_weights": np.array([0.2, 0.2, -0.6, -0.3, 0.0, 0.5]),
    },
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PoleScores:
    """Raw orientation scores for each of the six poles (0.0 to 1.0)."""
    ohn: float = 0.0       # Ground of Being / Depth
    hoc: float = 0.0       # Present Moment / Surface
    him: float = 0.0       # Singular Self
    allmen: float = 0.0    # Collective Other
    wasonce: float = 0.0   # Ancestral Past
    willbe: float = 0.0    # Unborn Future

    def to_array(self) -> np.ndarray:
        return np.array([self.ohn, self.hoc, self.him, self.allmen, self.wasonce, self.willbe])

    def to_dict(self) -> dict:
        return {
            "Ohn (Depth)": self.ohn, "Hoc (Surface)": self.hoc,
            "Him (Singular)": self.him, "Allmen (Plural)": self.allmen,
            "Wasonce (Past)": self.wasonce, "Willbe (Future)": self.willbe,
        }


@dataclass
class AxisScores:
    """Computed axis scores derived from pole scores."""
    vertical: float = 0.0     # Negative = deep (Ohn), Positive = surface (Hoc)
    horizontal: float = 0.0   # Negative = singular (Him), Positive = plural (Allmen)
    temporal_extension: float = 0.0  # 0 = collapsed, 1 = fully extended
    temporal_balance: float = 0.0    # Negative = past-oriented, Positive = future-oriented

    def position_vector(self) -> np.ndarray:
        """Return 3D position in octahedral space: (H, T_ext, V)"""
        return np.array([self.horizontal, self.temporal_balance, self.vertical])


@dataclass
class CaptureAnalysis:
    """Results of capture proximity analysis."""
    capture_type: CaptureType = CaptureType.NONE
    primary_capture: str = "None"
    vertex_proximities: Dict[str, float] = field(default_factory=dict)
    edge_proximities: Dict[str, float] = field(default_factory=dict)
    face_proximities: Dict[str, float] = field(default_factory=dict)
    capture_intensity: float = 0.0  # 0-1 scale


@dataclass
class StampAnalysis:
    """Results of stamp signature detection."""
    detected_stamps: List[Tuple[StampType, float]] = field(default_factory=list)
    primary_stamp: Optional[StampType] = None
    stamp_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class SubtypeMatch:
    """Subtype matching result."""
    zone: Zone = Zone.I
    primary_subtype: str = ""
    primary_description: str = ""
    subtype_distances: List[Tuple[str, float]] = field(default_factory=list)


@dataclass
class AsymmetricGeometry:
    """
    Per-axis deformation data describing the actual interior geometry.

    The theory (Part V: Asymmetric Deformation) states that real interior
    spaces are rarely uniform. The shape parameter varies by axis. This
    dataclass captures those asymmetries.
    """
    # Per-axis health scores (0 = collapsed, 1 = fully active)
    vertical_health: float = 0.5
    horizontal_health: float = 0.5
    temporal_health: float = 0.5

    # Per-axis scale factors (how far the boundary extends along each axis)
    # 1.0 = normal, <1.0 = compressed, >1.0 = extended
    vertical_scale: float = 1.0
    horizontal_scale: float = 1.0
    temporal_scale: float = 1.0

    # Per-axis-pair shape parameters (exchange rate between specific axis pairs)
    p_vh: float = 1.0   # Vertical-Horizontal exchange rate
    p_vt: float = 1.0   # Vertical-Temporal exchange rate
    p_ht: float = 1.0   # Horizontal-Temporal exchange rate

    # Global shape parameter (integration of all three)
    p_global: float = 1.0
    p_empirical: float = 1.0  # Estimated from pole score distribution
    p_self_report: float = 1.0  # From integration items

    # Detected deformation types
    deformations: List[str] = field(default_factory=list)

    # Axis-specific diagnostics
    weakest_axis: str = ""
    strongest_axis: str = ""
    axis_imbalance: float = 0.0  # 0 = symmetric, 1 = maximally asymmetric


@dataclass
class TOTProfile:
    """Complete TOT analysis result for a single participant."""
    participant_id: str = ""
    pole_scores: PoleScores = field(default_factory=PoleScores)
    axis_scores: AxisScores = field(default_factory=AxisScores)
    zone: Zone = Zone.I
    zone_confidence: float = 0.0
    subtype: SubtypeMatch = field(default_factory=SubtypeMatch)
    shape_parameter: float = 1.0
    shape_name: str = "Octahedron"
    capture: CaptureAnalysis = field(default_factory=CaptureAnalysis)
    stamps: StampAnalysis = field(default_factory=StampAnalysis)
    geometry: AsymmetricGeometry = field(default_factory=AsymmetricGeometry)
    interior_volume: float = 0.0
    distance_from_center: float = 0.0
    distance_from_boundary: float = 0.0
    hall_of_mirrors: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "participant_id": self.participant_id,
            "pole_scores": self.pole_scores.to_dict(),
            "axis_scores": {
                "vertical": self.axis_scores.vertical,
                "horizontal": self.axis_scores.horizontal,
                "temporal_extension": self.axis_scores.temporal_extension,
                "temporal_balance": self.axis_scores.temporal_balance,
            },
            "zone": self.zone.value,
            "zone_confidence": round(self.zone_confidence, 3),
            "primary_subtype": self.subtype.primary_subtype,
            "subtype_description": self.subtype.primary_description,
            "shape_parameter": round(self.shape_parameter, 3),
            "shape_name": self.shape_name,
            "geometry": {
                "p_global": round(self.geometry.p_global, 3),
                "p_empirical": round(self.geometry.p_empirical, 3),
                "p_self_report": round(self.geometry.p_self_report, 3),
                "p_vh": round(self.geometry.p_vh, 3),
                "p_vt": round(self.geometry.p_vt, 3),
                "p_ht": round(self.geometry.p_ht, 3),
                "vertical_health": round(self.geometry.vertical_health, 3),
                "horizontal_health": round(self.geometry.horizontal_health, 3),
                "temporal_health": round(self.geometry.temporal_health, 3),
                "vertical_scale": round(self.geometry.vertical_scale, 3),
                "horizontal_scale": round(self.geometry.horizontal_scale, 3),
                "temporal_scale": round(self.geometry.temporal_scale, 3),
                "weakest_axis": self.geometry.weakest_axis,
                "strongest_axis": self.geometry.strongest_axis,
                "axis_imbalance": round(self.geometry.axis_imbalance, 3),
                "deformations": self.geometry.deformations,
            },
            "capture_type": self.capture.capture_type.value,
            "capture_primary": self.capture.primary_capture,
            "capture_intensity": round(self.capture.capture_intensity, 3),
            "primary_stamp": self.stamps.primary_stamp.value if self.stamps.primary_stamp else "None",
            "stamp_scores": {k: round(v, 3) for k, v in self.stamps.stamp_scores.items()},
            "interior_volume": round(self.interior_volume, 4),
            "distance_from_center": round(self.distance_from_center, 4),
            "distance_from_boundary": round(self.distance_from_boundary, 4),
            "hall_of_mirrors": self.hall_of_mirrors,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# =============================================================================
# GEOMETRIC ENGINE
# =============================================================================

class TOTEngine:
    """
    Core geometric engine for Triaxial Orientation Theory.

    Takes pole scores and integration cost scores as input.
    Produces a complete TOT profile including zone, subtype, shape parameter,
    capture analysis, and stamp detection.
    """

    # Thresholds
    TEMPORAL_EXTENSION_THRESHOLD = 0.35  # Below this = "present only"
    CAPTURE_VERTEX_THRESHOLD = 0.25      # Proximity to vertex for capture detection
    CAPTURE_EDGE_THRESHOLD = 0.20        # Proximity to edge
    STAMP_DETECTION_THRESHOLD = 0.40     # Minimum score for stamp detection
    HALL_OF_MIRRORS_THRESHOLD = 0.58     # Composite score to flag HoM

    def compute_axis_scores(self, poles: PoleScores) -> AxisScores:
        """Compute axis scores from raw pole scores."""
        scores = AxisScores()

        # Vertical: positive = surface (Hoc), negative = deep (Ohn)
        scores.vertical = poles.hoc - poles.ohn

        # Horizontal: positive = plural (Allmen), negative = singular (Him)
        scores.horizontal = poles.allmen - poles.him

        # Temporal extension: average of both temporal orientations
        # High = temporally active, Low = present-locked
        scores.temporal_extension = (poles.wasonce + poles.willbe) / 2.0

        # Temporal balance: future vs past orientation
        scores.temporal_balance = poles.willbe - poles.wasonce

        return scores

    def classify_zone(self, axes: AxisScores) -> Tuple[Zone, float]:
        """
        Classify into one of eight zones based on axis scores.
        Returns zone and confidence (distance from zone boundaries).
        """
        is_deep = axes.vertical < 0
        is_plural = axes.horizontal > 0
        is_temporal = axes.temporal_extension > self.TEMPORAL_EXTENSION_THRESHOLD

        # Confidence: minimum distance from any decision boundary
        v_dist = abs(axes.vertical)
        h_dist = abs(axes.horizontal)
        t_dist = abs(axes.temporal_extension - self.TEMPORAL_EXTENSION_THRESHOLD)
        confidence = min(v_dist, h_dist, t_dist)

        if is_deep and is_plural and is_temporal:
            return Zone.VIII, confidence
        elif is_deep and not is_plural and is_temporal:
            return Zone.VII, confidence
        elif not is_deep and is_plural and is_temporal:
            return Zone.VI, confidence
        elif not is_deep and not is_plural and is_temporal:
            return Zone.V, confidence
        elif is_deep and is_plural and not is_temporal:
            return Zone.IV, confidence
        elif is_deep and not is_plural and not is_temporal:
            return Zone.III, confidence
        elif not is_deep and is_plural and not is_temporal:
            return Zone.II, confidence
        else:
            return Zone.I, confidence

    def match_subtype(self, zone: Zone, axes: AxisScores) -> SubtypeMatch:
        """Match to the closest subtype within the classified zone."""
        result = SubtypeMatch(zone=zone)
        subtypes = SUBTYPES.get(zone, [])

        pos = np.array([axes.horizontal, axes.temporal_balance, axes.vertical])
        distances = []

        for sub in subtypes:
            # Compute zone center based on zone definition
            zdef = ZONE_DEFINITIONS[zone]
            center = np.array([
                0.5 if zdef["h"] == "plural" else -0.5,
                0.0,
                0.5 if zdef["v"] == "surface" else -0.5,
            ])
            subtype_pos = center + sub["bias"]
            dist = np.linalg.norm(pos - subtype_pos)
            distances.append((sub["name"], sub["description"], dist))

        distances.sort(key=lambda x: x[2])
        result.subtype_distances = [(d[0], round(d[2], 4)) for d in distances]

        if distances:
            result.primary_subtype = distances[0][0]
            result.primary_description = distances[0][1]

        return result

    def estimate_shape_parameter(self, integration_scores: List[float]) -> float:
        """
        Estimate the Lp shape parameter from integration cost items.

        Integration scores measure how expensive it is to hold multiple axes.
        Higher scores = easier integration = higher p (rounder shape).

        Returns p value:
          p < 1.0: Suboctahedron (crisis geometry)
          p = 1.0: Octahedron (linear tradeoffs)
          1.0 < p < 2.0: Rounded octahedron
          p = 2.0: Sphere (balanced tradeoffs)
          p > 2.0: Hyperround (integration surplus)
        """
        if not integration_scores:
            return 1.0

        # Mean integration capacity (0-1 scale after Likert normalization)
        mean_integration = np.mean(integration_scores)

        # Map [0, 1] integration capacity to shape parameter
        # 0.0 -> p = 0.5 (severe suboctahedron)
        # 0.25 -> p = 0.75
        # 0.5 -> p = 1.0 (octahedron)
        # 0.625 -> p = 1.5 (rounded)
        # 0.75 -> p = 2.0 (sphere)
        # 0.875 -> p = 3.0 (hyperround)
        # 1.0 -> p = 4.0 (extreme hyperround)

        if mean_integration <= 0.5:
            # Suboctahedron to octahedron: [0.5, 1.0]
            p = 0.5 + mean_integration
        elif mean_integration <= 0.75:
            # Octahedron to sphere: [1.0, 2.0]
            p = 1.0 + (mean_integration - 0.5) * 4.0
        else:
            # Sphere to hyperround: [2.0, 4.0]
            p = 2.0 + (mean_integration - 0.75) * 8.0

        return round(np.clip(p, 0.3, 5.0), 3)

    def estimate_shape_empirical(self, poles: PoleScores) -> float:
        """
        Estimate shape parameter empirically from pole score distribution.

        If a person scores high on multiple poles simultaneously, they are
        demonstrating higher integrative capacity than someone who scores
        high on only one. This is observable evidence of shape parameter
        independent of self-report.

        Method: Compute the "multi-axis load" — how many poles carry
        significant orientation. Map this to a shape parameter.
        """
        arr = poles.to_array()

        # How many poles exceed threshold for "active orientation"
        active_count = np.sum(arr > 0.5)

        # Mean of active poles (how high they go when active)
        active_mean = np.mean(arr[arr > 0.5]) if active_count > 0 else 0.0

        # Entropy of pole distribution (more uniform = higher integrative capacity)
        # Normalize to probability distribution
        total = np.sum(arr) + 1e-10
        probs = arr / total
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        max_entropy = np.log(6)  # Maximum entropy for 6 poles
        normalized_entropy = entropy / max_entropy

        # Combined integrative signal:
        # Weight: 40% active count, 30% active mean, 30% entropy
        count_signal = active_count / 6.0
        integrative_signal = 0.4 * count_signal + 0.3 * active_mean + 0.3 * normalized_entropy

        # Map to shape parameter using same curve as self-report
        if integrative_signal <= 0.5:
            p = 0.5 + integrative_signal
        elif integrative_signal <= 0.75:
            p = 1.0 + (integrative_signal - 0.5) * 4.0
        else:
            p = 2.0 + (integrative_signal - 0.75) * 8.0

        return round(np.clip(p, 0.3, 5.0), 3)

    def compute_asymmetric_geometry(self, poles: PoleScores, axes: AxisScores,
                                     p_self_report: float,
                                     stamps: 'StampAnalysis') -> AsymmetricGeometry:
        """
        Compute the full asymmetric interior geometry.

        Per Part V of Structural Configurations: "The true interior space
        of a human being is not a regular geometric solid. It is an
        irregular one. The shape parameter varies by axis."

        This method computes per-axis health, scale, pair-wise shape
        parameters, and detects specific deformation types.
        """
        geom = AsymmetricGeometry()

        # ── Per-axis health ──
        # Health = how active/functional each axis is (0-1).
        # A healthy axis has at least one pole strongly active.
        # A collapsed axis has BOTH poles low (axis forgotten entirely).
        # A directional axis (one pole high, other low) is active, not collapsed.
        # Bonus for oscillation (both poles active = capacity for movement).

        def axis_health(pole_a: float, pole_b: float) -> float:
            peak = max(pole_a, pole_b)           # Is the axis reaching anywhere?
            floor = min(pole_a, pole_b)           # Is the other pole accessible?
            activation = peak                     # Primary signal: peak orientation
            oscillation = floor * 0.5             # Bonus: other pole is also reachable
            # A collapsed axis has low peak (neither pole active)
            # A directional axis has high peak, low floor (active but one-sided)
            # A oscillating axis has high peak, decent floor (active and mobile)
            return np.clip(activation * 0.7 + oscillation * 0.3 + floor * 0.1, 0, 1)

        geom.vertical_health = round(axis_health(poles.ohn, poles.hoc), 3)
        geom.horizontal_health = round(axis_health(poles.him, poles.allmen), 3)
        geom.temporal_health = round(axis_health(poles.wasonce, poles.willbe), 3)

        # ── Per-axis scale factors ──
        # Scale = how far the boundary extends along each axis.
        # Collapsed axis = boundary compressed toward zero on that dimension.
        # Healthy axis = boundary extends to full unit distance.
        geom.vertical_scale = round(0.3 + 0.7 * geom.vertical_health, 3)
        geom.horizontal_scale = round(0.3 + 0.7 * geom.horizontal_health, 3)
        geom.temporal_scale = round(0.3 + 0.7 * geom.temporal_health, 3)

        # ── Per-axis-pair shape parameters ──
        # The exchange rate between two axes is cheaper when both are healthy.
        # When one is weak, the pair has a lower p (more angular exchange).
        p_base = self.estimate_shape_empirical(poles)

        geom.p_vh = round(p_base * (geom.vertical_health * geom.horizontal_health) ** 0.3, 3)
        geom.p_vt = round(p_base * (geom.vertical_health * geom.temporal_health) ** 0.3, 3)
        geom.p_ht = round(p_base * (geom.horizontal_health * geom.temporal_health) ** 0.3, 3)

        # ── Global shape parameter ──
        # Combine self-report and empirical estimates (weighted average)
        geom.p_self_report = p_self_report
        geom.p_empirical = p_base
        # Empirical gets 60% weight because it's derived from demonstrated capacity
        geom.p_global = round(0.4 * p_self_report + 0.6 * p_base, 3)

        # ── Axis diagnostics ──
        healths = {
            "Vertical (Depth)": geom.vertical_health,
            "Horizontal (Breath)": geom.horizontal_health,
            "Temporal (Obligation)": geom.temporal_health,
        }
        geom.weakest_axis = min(healths, key=healths.get)
        geom.strongest_axis = max(healths, key=healths.get)

        health_vals = list(healths.values())
        geom.axis_imbalance = round(max(health_vals) - min(health_vals), 3)

        # ── Deformation detection ──
        deformations = []

        # Axial Compression: one axis much weaker than the other two
        if geom.axis_imbalance > 0.25:
            deformations.append(f"Axial Compression ({geom.weakest_axis.split('(')[0].strip()} compressed)")

        # Check for fracture indicators from stamps
        if stamps and stamps.primary_stamp:
            stamp_sig = STAMP_PROFILES.get(stamps.primary_stamp, {}).get("signature", {})
            if stamp_sig.get("shape_effect") == "fracture":
                deformations.append(f"Axial Fracture ({stamp_sig.get('h_bias', 'horizontal')} axis)")
            if stamp_sig.get("shape_effect") == "inversion":
                deformations.append(f"Polar Inversion ({stamp_sig.get('v_bias', 'vertical')} axis)")

        # Volumetric Collapse: all three health scores are low
        mean_health = np.mean(health_vals)
        if mean_health < 0.4:
            deformations.append("Volumetric Collapse (global shrinkage)")

        # Planar Skew: check if the strongest axis is much stronger than the other two combined
        if max(health_vals) > 0.8 and min(health_vals) < 0.4:
            deformations.append("Planar Skew (asymmetric distortion)")

        geom.deformations = deformations

        return geom

    def shape_name(self, p: float) -> str:
        """Return the named shape for a given shape parameter."""
        if p < 0.8:
            return "Suboctahedron (Crisis)"
        elif p < 1.2:
            return "Octahedron (Constrained)"
        elif p < 1.8:
            return "Rounded Octahedron (Functional)"
        elif p < 2.3:
            return "Sphere (Integrated)"
        else:
            return "Hyperround (Generative)"

    def compute_lp_boundary(self, p: float, point: np.ndarray) -> float:
        """
        Compute the Lp norm of a point. The boundary is where this equals 1.
        |x|^p + |y|^p + |z|^p = 1
        """
        return np.sum(np.abs(point) ** p)

    def compute_interior_volume(self, p: float) -> float:
        """
        Compute the volume of the Lp unit ball in 3D.
        V_p = 8 * Gamma(1 + 1/p)^3 / Gamma(1 + 3/p)
        """
        from math import gamma
        try:
            vol = 8.0 * (gamma(1.0 + 1.0/p) ** 3) / gamma(1.0 + 3.0/p)
            return round(vol, 4)
        except (ValueError, ZeroDivisionError, OverflowError):
            return 0.0

    def distance_from_boundary(self, p: float, point: np.ndarray) -> float:
        """
        Compute approximate distance from point to the Lp boundary surface.
        Positive = inside, Negative = outside.
        """
        norm_val = self.compute_lp_boundary(p, point)
        if norm_val < 1e-10:
            return 1.0  # At center
        # Approximate distance using the norm value
        # Scale factor to convert norm units to Euclidean distance
        pt_dist = np.linalg.norm(point)
        if pt_dist < 1e-10:
            return 1.0
        boundary_dist = pt_dist * (1.0 - norm_val ** (1.0/p))
        return round(boundary_dist, 4)

    def detect_hall_of_mirrors(self, poles: PoleScores, axes: AxisScores,
                                p_self_report: float, p_empirical: float,
                                hom_scores: Optional[List[float]] = None) -> dict:
        """
        Detect Hall of Mirrors: self-referential recursive epistemic trap.

        Geometrically distinct from all eight zones: position collapses toward
        center not through genuine multi-axis integration (Zone VIII) but through
        pole undifferentiation — no axis achieves real contact. The person
        references all orientations without being genuinely captured by any.

        Key diagnostic: self-reported integration capacity (p_self_report)
        significantly exceeds empirically demonstrated capacity (p_empirical).
        In genuine Zone VIII, both are high. In HoM, self-report is high but
        empirical shape is flat — the person believes they hold everything
        simultaneously because they reference everything through one recursive loop.

        Components:
          pole_undifferentiation: all poles near mid-range (0.5), no genuine contact
          center_proximity: position vector near origin (not through balance but flatness)
          integration_divergence: self-report p >> empirical p
          epistemic_subscale: score on M01-M06 subscale (if provided)
        """
        pole_arr = poles.to_array()

        # 1. Pole undifferentiation: are all poles mid-range?
        # Formula: for each pole, score is 1.0 if pole=0.5, 0.0 if pole=0.0 or 1.0
        mid_range = np.clip(1.0 - 2.0 * np.abs(pole_arr - 0.5), 0.0, 1.0)
        undifferentiation = float(np.mean(mid_range))

        # 2. Center proximity: position vector near origin
        pos = axes.position_vector()
        distance = float(np.linalg.norm(pos))
        center_score = float(np.clip(1.0 - distance / 0.30, 0.0, 1.0))

        # 3. Integration divergence: self-report meaningfully exceeds empirical
        divergence = p_self_report - p_empirical
        divergence_score = float(np.clip(divergence / 0.80, 0.0, 1.0))

        # 4. Epistemic subscale (M01-M06): direct self-report of self-referential closure
        subscale_score = 0.50  # neutral prior when not provided
        if hom_scores:
            subscale_score = float(np.mean(hom_scores))

        # Weighted composite — subscale gets highest weight when available
        if hom_scores:
            composite = (
                0.20 * undifferentiation +
                0.20 * center_score +
                0.20 * divergence_score +
                0.40 * subscale_score
            )
        else:
            composite = (
                0.40 * undifferentiation +
                0.30 * center_score +
                0.30 * divergence_score
            )

        detected = composite > self.HALL_OF_MIRRORS_THRESHOLD

        return {
            "detected": detected,
            "score": round(float(composite), 3),
            "components": {
                "pole_undifferentiation": round(float(undifferentiation), 3),
                "center_proximity": round(float(center_score), 3),
                "integration_divergence": round(float(divergence_score), 3),
                "epistemic_subscale": round(float(subscale_score), 3),
            },
            "active_pole_count": int(np.sum(pole_arr > 0.60)),
            "description": (
                "Hall of Mirrors pattern detected. The position profile shows "
                "epistemic self-enclosure: no axis achieves genuine pole contact, "
                "yet integration is self-reported as high. This pattern reflects "
                "orientation through recursive self-reference rather than direct "
                "contact with depth, community, or temporal obligation."
                if detected else
                "Hall of Mirrors pattern not detected at current threshold."
            ),
        }

    def analyze_captures(self, poles: PoleScores, axes: AxisScores) -> CaptureAnalysis:
        """
        Analyze proximity to all 26 capture configurations:
        6 vertex captures, 12 edge captures, 8 face captures.
        """
        result = CaptureAnalysis()
        pole_arr = poles.to_array()  # [ohn, hoc, him, allmen, wasonce, willbe]

        # --- Vertex capture analysis ---
        pole_names = [Pole.OHN, Pole.HOC, Pole.HIM, Pole.ALLMEN, Pole.WASONCE, Pole.WILLBE]
        vertex_names = {
            Pole.OHN: "Ground (Consumed Mystic)",
            Pole.HOC: "Surface (Flat Performer)",
            Pole.HIM: "Singular (Sealed Self)",
            Pole.ALLMEN: "Collective (Dissolved)",
            Pole.WASONCE: "Ancestral (Haunted)",
            Pole.WILLBE: "Futural (Ungrounded Visionary)",
        }

        max_vertex_score = 0
        max_vertex_name = ""
        for i, pole in enumerate(pole_names):
            # Vertex capture = high score on one pole, low on all others
            this_score = pole_arr[i]
            other_scores = np.delete(pole_arr, i)
            # Dominance: how much this pole exceeds the average of others
            dominance = this_score - np.mean(other_scores)
            proximity = np.clip(dominance, 0, 1)
            name = vertex_names[pole]
            result.vertex_proximities[name] = round(proximity, 3)
            if proximity > max_vertex_score:
                max_vertex_score = proximity
                max_vertex_name = name

        # --- Edge capture analysis ---
        pole_index = {Pole.OHN: 0, Pole.HOC: 1, Pole.HIM: 2,
                      Pole.ALLMEN: 3, Pole.WASONCE: 4, Pole.WILLBE: 5}

        max_edge_score = 0
        max_edge_name = ""
        for edge in EDGES:
            desc = EDGE_DESCRIPTIONS.get(edge, EDGE_DESCRIPTIONS.get((edge[1], edge[0]), {}))
            name = desc.get("name", f"{edge[0].value}-{edge[1].value}")

            i1, i2 = pole_index[edge[0]], pole_index[edge[1]]
            pair_score = (pole_arr[i1] + pole_arr[i2]) / 2.0
            others = np.delete(pole_arr, [i1, i2])
            other_mean = np.mean(others)
            dominance = pair_score - other_mean
            proximity = np.clip(dominance, 0, 1)
            result.edge_proximities[name] = round(proximity, 3)
            if proximity > max_edge_score:
                max_edge_score = proximity
                max_edge_name = name

        # --- Face capture: use zone strength ---
        for zone in Zone:
            zdef = ZONE_DEFINITIONS[zone]
            # Compute how strongly the person matches this zone
            v_match = (1 - axes.vertical) / 2 if zdef["v"] == "deep" else (1 + axes.vertical) / 2
            h_match = (1 + axes.horizontal) / 2 if zdef["h"] == "plural" else (1 - axes.horizontal) / 2
            if zdef["t"] == "active":
                t_match = axes.temporal_extension
            else:
                t_match = 1.0 - axes.temporal_extension
            face_score = (v_match + h_match + t_match) / 3.0
            result.face_proximities[zone.value] = round(face_score, 3)

        # --- Determine capture type ---
        if max_vertex_score > 0.6:
            result.capture_type = CaptureType.VERTEX
            result.primary_capture = max_vertex_name
            result.capture_intensity = max_vertex_score
        elif max_edge_score > 0.5:
            result.capture_type = CaptureType.EDGE
            result.primary_capture = max_edge_name
            result.capture_intensity = max_edge_score
        elif max(result.face_proximities.values()) > 0.7:
            result.capture_type = CaptureType.FACE
            best_face = max(result.face_proximities, key=result.face_proximities.get)
            result.primary_capture = best_face
            result.capture_intensity = result.face_proximities[best_face]
        else:
            result.capture_type = CaptureType.NONE
            result.capture_intensity = 0.0

        return result

    def detect_stamps(self, poles: PoleScores) -> StampAnalysis:
        """
        Detect stamp signatures by correlating pole scores with known stamp profiles.
        """
        result = StampAnalysis()
        pole_arr = poles.to_array()

        scores = {}
        for stamp_type, profile in STAMP_PROFILES.items():
            weights = profile["detection_weights"]
            # Dot product correlation
            raw_score = np.dot(pole_arr, weights)
            # Normalize to 0-1 range
            max_possible = np.sum(np.abs(weights))
            if max_possible > 0:
                normalized = (raw_score + max_possible) / (2 * max_possible)
            else:
                normalized = 0.5
            scores[stamp_type.value] = round(normalized, 3)

        result.stamp_scores = scores

        # Detect stamps above threshold
        detected = [(st, scores[st.value]) for st in StampType
                     if scores[st.value] > self.STAMP_DETECTION_THRESHOLD]
        detected.sort(key=lambda x: x[1], reverse=True)
        result.detected_stamps = detected

        if detected:
            result.primary_stamp = detected[0][0]

        return result

    def compute_profile(self, poles: PoleScores,
                        integration_scores: Optional[List[float]] = None,
                        hom_scores: Optional[List[float]] = None,
                        participant_id: str = "") -> TOTProfile:
        """
        Compute a complete TOT profile from pole scores and integration scores.
        This is the main entry point for the engine.
        """
        profile = TOTProfile(participant_id=participant_id)
        profile.pole_scores = poles

        # Axis scores
        profile.axis_scores = self.compute_axis_scores(poles)

        # Zone classification
        profile.zone, profile.zone_confidence = self.classify_zone(profile.axis_scores)

        # Subtype matching
        profile.subtype = self.match_subtype(profile.zone, profile.axis_scores)

        # Shape parameter — self-report
        p_self_report = 1.0
        if integration_scores:
            p_self_report = self.estimate_shape_parameter(integration_scores)

        # Stamp detection (needed before geometry computation)
        profile.stamps = self.detect_stamps(poles)

        # Asymmetric geometry (produces the combined shape parameter)
        profile.geometry = self.compute_asymmetric_geometry(
            poles, profile.axis_scores, p_self_report, profile.stamps
        )

        # Use the combined global shape parameter
        profile.shape_parameter = profile.geometry.p_global
        profile.shape_name = self.shape_name(profile.shape_parameter)

        # Interior volume at the global shape parameter
        profile.interior_volume = self.compute_interior_volume(profile.shape_parameter)

        # Position metrics
        pos = profile.axis_scores.position_vector()
        profile.distance_from_center = round(float(np.linalg.norm(pos)), 4)
        profile.distance_from_boundary = self.distance_from_boundary(
            profile.shape_parameter, pos
        )

        # Capture analysis
        profile.capture = self.analyze_captures(poles, profile.axis_scores)

        # Hall of Mirrors detection
        profile.hall_of_mirrors = self.detect_hall_of_mirrors(
            poles, profile.axis_scores,
            p_self_report=p_self_report,
            p_empirical=profile.geometry.p_empirical,
            hom_scores=hom_scores,
        )

        return profile

    # --- Geometric surface generation for visualization ---

    @staticmethod
    def generate_lp_surface(p: float, resolution: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate the Lp unit ball surface for 3D visualization.
        Returns X, Y, Z meshgrid arrays.
        """
        u = np.linspace(0, 2 * np.pi, resolution)
        v = np.linspace(-np.pi / 2, np.pi / 2, resolution)
        U, V = np.meshgrid(u, v)

        # Parametric Lp surface (superellipsoid)
        cos_v = np.cos(V)
        sin_v = np.sin(V)
        cos_u = np.cos(U)
        sin_u = np.sin(U)

        exp = 2.0 / p

        X = np.sign(cos_v) * np.abs(cos_v) ** exp * np.sign(cos_u) * np.abs(cos_u) ** exp
        Y = np.sign(cos_v) * np.abs(cos_v) ** exp * np.sign(sin_u) * np.abs(sin_u) ** exp
        Z = np.sign(sin_v) * np.abs(sin_v) ** exp

        return X, Y, Z

    @staticmethod
    def generate_asymmetric_surface(geometry: 'AsymmetricGeometry',
                                     resolution: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate an asymmetric Lp surface that deforms per-axis based on
        the actual interior geometry. This is the visualization that shows
        collapsed axes, compressed dimensions, and stamp deformations.

        The surface uses per-axis scale factors and a global shape parameter.
        Collapsed axes produce visible flattening of the boundary.
        """
        u = np.linspace(0, 2 * np.pi, resolution)
        v = np.linspace(-np.pi / 2, np.pi / 2, resolution)
        U, V = np.meshgrid(u, v)

        p = geometry.p_global
        exp = 2.0 / max(p, 0.3)

        cos_v = np.cos(V)
        sin_v = np.sin(V)
        cos_u = np.cos(U)
        sin_u = np.sin(U)

        # Base superellipsoid
        X = np.sign(cos_v) * np.abs(cos_v) ** exp * np.sign(cos_u) * np.abs(cos_u) ** exp
        Y = np.sign(cos_v) * np.abs(cos_v) ** exp * np.sign(sin_u) * np.abs(sin_u) ** exp
        Z = np.sign(sin_v) * np.abs(sin_v) ** exp

        # Apply per-axis scaling (the deformation)
        # X = Horizontal, Y = Temporal, Z = Vertical
        X *= geometry.horizontal_scale
        Y *= geometry.temporal_scale
        Z *= geometry.vertical_scale

        return X, Y, Z

    @staticmethod
    def generate_deformed_wireframe(geometry: 'AsymmetricGeometry') -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate wireframe for a deformed octahedron where each axis
        is scaled by its health-derived scale factor.

        This is the key visualization: a collapsed axis visibly
        shrinks the octahedron along that dimension.
        """
        # Scale the vertices by per-axis factors
        scale = np.array([
            geometry.horizontal_scale,  # X axis
            geometry.temporal_scale,    # Y axis
            geometry.vertical_scale,    # Z axis
        ])

        scaled_vertices = {}
        for pole, vert in VERTICES.items():
            scaled_vertices[pole] = vert * scale

        lines = []
        verts = list(scaled_vertices.values())
        for i in range(6):
            for j in range(i + 1, 6):
                v1, v2 = verts[i], verts[j]
                # Skip opposite poles
                orig1 = list(VERTICES.values())[i]
                orig2 = list(VERTICES.values())[j]
                if np.dot(orig1, orig2) < -0.99:
                    continue
                lines.append((v1, v2))
        return lines, scaled_vertices

    @staticmethod
    def generate_octahedron_wireframe() -> List[Tuple[np.ndarray, np.ndarray]]:
        """Generate line segments for octahedron wireframe visualization."""
        lines = []
        verts = list(VERTICES.values())
        # Connect each vertex to all non-opposite vertices
        for i in range(6):
            for j in range(i + 1, 6):
                v1, v2 = verts[i], verts[j]
                # Skip opposite poles (they share an axis)
                if np.dot(v1, v2) < -0.99:
                    continue
                lines.append((v1, v2))
        return lines


# =============================================================================
# SCORING ENGINE
# =============================================================================

class TOTScorer:
    """
    Scores raw questionnaire responses into pole scores and integration scores.
    """

    def score_likert_responses(self, responses: Dict[str, int],
                                item_pole_map: Dict[str, str],
                                likert_max: int = 7) -> PoleScores:
        """
        Score Likert-scale responses into pole scores.

        Parameters:
            responses: {item_id: response_value} (1 to likert_max)
            item_pole_map: {item_id: pole_name} mapping items to poles
            likert_max: maximum Likert scale value
        """
        pole_totals = {p.value: [] for p in Pole}

        for item_id, response in responses.items():
            pole_name = item_pole_map.get(item_id)
            if pole_name and pole_name in pole_totals:
                # Normalize to 0-1
                normalized = (response - 1) / (likert_max - 1)
                pole_totals[pole_name].append(normalized)

        poles = PoleScores()
        poles.ohn = np.mean(pole_totals["Ohn"]) if pole_totals["Ohn"] else 0.5
        poles.hoc = np.mean(pole_totals["Hoc"]) if pole_totals["Hoc"] else 0.5
        poles.him = np.mean(pole_totals["Him"]) if pole_totals["Him"] else 0.5
        poles.allmen = np.mean(pole_totals["Allmen"]) if pole_totals["Allmen"] else 0.5
        poles.wasonce = np.mean(pole_totals["Wasonce"]) if pole_totals["Wasonce"] else 0.5
        poles.willbe = np.mean(pole_totals["Willbe"]) if pole_totals["Willbe"] else 0.5

        return poles

    def score_integration_items(self, responses: Dict[str, int],
                                 integration_item_ids: List[str],
                                 reverse_coded: List[str],
                                 likert_max: int = 7) -> List[float]:
        """
        Score integration cost items. Reverse-coded items are flipped.
        Returns list of normalized scores (0-1) where higher = better integration.
        """
        scores = []
        for item_id in integration_item_ids:
            if item_id in responses:
                val = responses[item_id]
                if item_id in reverse_coded:
                    val = likert_max + 1 - val
                scores.append((val - 1) / (likert_max - 1))
        return scores


# =============================================================================
# STATISTICAL ANALYSIS
# =============================================================================

class TOTAnalyzer:
    """Statistical analysis tools for TOT research data."""

    @staticmethod
    def descriptive_stats(profiles: List[TOTProfile]) -> dict:
        """Compute descriptive statistics for a collection of profiles."""
        if not profiles:
            return {}

        axes_v = [p.axis_scores.vertical for p in profiles]
        axes_h = [p.axis_scores.horizontal for p in profiles]
        axes_t = [p.axis_scores.temporal_extension for p in profiles]
        shapes = [p.shape_parameter for p in profiles]

        def stats(arr):
            a = np.array(arr)
            return {
                "mean": round(float(np.mean(a)), 4),
                "std": round(float(np.std(a)), 4),
                "min": round(float(np.min(a)), 4),
                "max": round(float(np.max(a)), 4),
                "median": round(float(np.median(a)), 4),
            }

        return {
            "n": len(profiles),
            "vertical_axis": stats(axes_v),
            "horizontal_axis": stats(axes_h),
            "temporal_extension": stats(axes_t),
            "shape_parameter": stats(shapes),
            "zone_distribution": TOTAnalyzer._zone_distribution(profiles),
        }

    @staticmethod
    def _zone_distribution(profiles: List[TOTProfile]) -> dict:
        """Count participants per zone."""
        counts = {z.value: 0 for z in Zone}
        for p in profiles:
            counts[p.zone.value] += 1
        return counts

    @staticmethod
    def cronbach_alpha(item_scores: np.ndarray) -> float:
        """
        Compute Cronbach's alpha for internal consistency.
        item_scores: 2D array (participants x items)
        """
        n_items = item_scores.shape[1]
        if n_items < 2:
            return 0.0

        item_vars = np.var(item_scores, axis=0, ddof=1)
        total_var = np.var(np.sum(item_scores, axis=1), ddof=1)

        if total_var == 0:
            return 0.0

        alpha = (n_items / (n_items - 1)) * (1 - np.sum(item_vars) / total_var)
        return round(float(alpha), 4)

    @staticmethod
    def test_retest_icc(scores1: np.ndarray, scores2: np.ndarray) -> float:
        """
        Compute Intraclass Correlation Coefficient (ICC 3,1) for test-retest reliability.
        """
        n = len(scores1)
        if n < 3:
            return 0.0

        grand_mean = np.mean(np.concatenate([scores1, scores2]))
        subject_means = (scores1 + scores2) / 2.0
        bms = 2.0 * np.sum((subject_means - grand_mean) ** 2) / (n - 1)  # Between MS
        wms = np.sum((scores1 - scores2) ** 2) / (2.0 * n)  # Within MS (error)

        if (bms + wms) == 0:
            return 0.0

        icc = (bms - wms) / (bms + wms)
        return round(float(icc), 4)
