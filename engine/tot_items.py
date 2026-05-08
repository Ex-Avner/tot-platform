"""
Triaxial Orientation Theory — Assessment Item Bank v2.0
========================================================
54 axis orientation items (9 per pole) + 12 integration cost items.
OVERHAULED from v1.0 based on full validity audit.

Changes from v1.0:
  - 4 broken items replaced (V13, H01, H04, H15)
  - Him subscale rebuilt (6 of 9 items rewritten to fix social desirability)
  - 20 gray-zone items reworded to eliminate cross-axis loading
  - Integration positive-coded items rewritten as observable/behavioral
  - All items now target ORIENTATION (what you do/experience) not
    ASPIRATION (what you wish were true about yourself)

Likert scale: 1 (Strongly Disagree) to 7 (Strongly Agree)
Theory: Ross Erickson / Avner Media
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class AssessmentItem:
    id: str
    text: str
    pole: str
    axis: str
    reverse_coded: bool = False

OHN_ITEMS = [
    AssessmentItem("V01", "I sometimes feel contact with something foundational that underlies everyday experience.", "Ohn", "Vertical"),
    AssessmentItem("V02", "There are moments when everyday experience opens into something that feels deeper or more real.", "Ohn", "Vertical"),
    AssessmentItem("V03", "Questions about the nature of existence feel personally urgent to me, not just intellectually interesting.", "Ohn", "Vertical"),
    AssessmentItem("V04", "Silence and stillness feel nourishing rather than empty to me.", "Ohn", "Vertical"),
    AssessmentItem("V05", "I have had experiences of unusual depth or clarity that revealed something about the nature of reality itself.", "Ohn", "Vertical"),
    AssessmentItem("V06", "The word 'sacred' has personal meaning to me, whether or not I am religious.", "Ohn", "Vertical"),
    AssessmentItem("V07", "There is a ground or foundation beneath the surface of ordinary experience that I return to directly, not just as an idea.", "Ohn", "Vertical"),
    AssessmentItem("V08", "Art, music, or the natural world can produce in me a feeling of contact with something that underlies all experience.", "Ohn", "Vertical"),
    AssessmentItem("V09", "I have direct experiences of meaningfulness that feel discovered rather than chosen, as if the meaning was already there.", "Ohn", "Vertical"),
]

HOC_ITEMS = [
    AssessmentItem("V10", "I feel most grounded when dealing with concrete, immediate tasks rather than abstract or existential questions.", "Hoc", "Vertical"),
    AssessmentItem("V11", "I prefer practical solutions to philosophical questions.", "Hoc", "Vertical"),
    AssessmentItem("V12", "The tangible and measurable feel more real to me than the abstract.", "Hoc", "Vertical"),
    AssessmentItem("V13", "Doing and producing feel more real and satisfying to me than reflecting or contemplating.", "Hoc", "Vertical"),
    AssessmentItem("V14", "I do not spend much time looking for deeper significance in everyday experiences.", "Hoc", "Vertical"),
    AssessmentItem("V15", "Efficiency and results matter more to me than process or depth.", "Hoc", "Vertical"),
    AssessmentItem("V16", "When something meaningful happens, I am more interested in what to do about it than what it means.", "Hoc", "Vertical"),
    AssessmentItem("V17", "I feel uncomfortable when conversations become too abstract or existential.", "Hoc", "Vertical"),
    AssessmentItem("V18", "I trust concrete results more than abstract principles.", "Hoc", "Vertical"),
]

HIM_ITEMS = [
    AssessmentItem("H01", "I usually already know my position on something before hearing anyone else's view.", "Him", "Horizontal"),
    AssessmentItem("H02", "When my view conflicts with the people closest to me, I usually hold my position rather than adjusting.", "Him", "Horizontal"),
    AssessmentItem("H03", "My sense of what is true about something does not depend on reaching agreement with others.", "Him", "Horizontal"),
    AssessmentItem("H04", "I notice that other people's opinions rarely change what I actually think, even when I understand their reasoning.", "Him", "Horizontal"),
    AssessmentItem("H05", "I would rather be right alone than wrong with the group.", "Him", "Horizontal"),
    AssessmentItem("H06", "When the people around me converge on a conclusion I disagree with, I hold my own position rather than moving toward theirs.", "Him", "Horizontal"),
    AssessmentItem("H07", "My most important work happens in solitude.", "Him", "Horizontal"),
    AssessmentItem("H08", "In group settings, I often hold positions I do not share because the group would not understand them.", "Him", "Horizontal"),
    AssessmentItem("H09", "There is a way I see things that remains consistent regardless of who I am around.", "Him", "Horizontal"),
]

ALLMEN_ITEMS = [
    AssessmentItem("H10", "I feel most alive in genuine conversation with another person.", "Allmen", "Horizontal"),
    AssessmentItem("H11", "Other people's experiences and perspectives genuinely change how I see things.", "Allmen", "Horizontal"),
    AssessmentItem("H12", "I am drawn to community and collaborative work.", "Allmen", "Horizontal"),
    AssessmentItem("H13", "I genuinely need other people's perspectives to understand my own experience fully.", "Allmen", "Horizontal"),
    AssessmentItem("H14", "Being in relationship with others is essential to who I am.", "Allmen", "Horizontal"),
    AssessmentItem("H15", "I actively seek out people who see the world differently than I do.", "Allmen", "Horizontal"),
    AssessmentItem("H16", "I feel genuinely affected by the struggles of people I have never met.", "Allmen", "Horizontal"),
    AssessmentItem("H17", "I learn more from dialogue than from solitary reflection.", "Allmen", "Horizontal"),
    AssessmentItem("H18", "The boundary between self and other sometimes feels less fixed than I expect.", "Allmen", "Horizontal"),
]

WASONCE_ITEMS = [
    AssessmentItem("T01", "I feel a genuine connection to those who came before me.", "Wasonce", "Temporal"),
    AssessmentItem("T02", "The choices made by previous generations still shape my life in specific ways I can identify.", "Wasonce", "Temporal"),
    AssessmentItem("T03", "I am shaped by obligations I inherited rather than chose.", "Wasonce", "Temporal"),
    AssessmentItem("T04", "Understanding where I come from is essential to understanding who I am.", "Wasonce", "Temporal"),
    AssessmentItem("T05", "I sometimes feel the weight of inherited patterns I did not create.", "Wasonce", "Temporal"),
    AssessmentItem("T06", "Honoring the dead feels like a real responsibility, not just a ritual.", "Wasonce", "Temporal"),
    AssessmentItem("T07", "Historical events that happened before I was born feel personally relevant to me.", "Wasonce", "Temporal"),
    AssessmentItem("T08", "I regularly think about specific people in my past whose sacrifices I am still living inside of.", "Wasonce", "Temporal"),
    AssessmentItem("T09", "Patterns from my family history show up in my choices in ways I can recognize.", "Wasonce", "Temporal"),
]

WILLBE_ITEMS = [
    AssessmentItem("T10", "I think regularly about how my decisions will affect people not yet born.", "Willbe", "Temporal"),
    AssessmentItem("T11", "I feel responsible to future generations I will never meet.", "Willbe", "Temporal"),
    AssessmentItem("T12", "I make present-day sacrifices specifically because of how things will be for people living decades from now.", "Willbe", "Temporal"),
    AssessmentItem("T13", "I orient my work toward what will be needed after I am gone.", "Willbe", "Temporal"),
    AssessmentItem("T14", "When I make decisions today, I find myself factoring in what conditions I am handing to people who will be alive after I am gone.", "Willbe", "Temporal"),
    AssessmentItem("T15", "I plan beyond my own lifespan.", "Willbe", "Temporal"),
    AssessmentItem("T16", "What I am leaving behind motivates my choices today.", "Willbe", "Temporal"),
    AssessmentItem("T17", "I feel genuine obligation, not just concern, about problems that will mostly affect people who come after me.", "Willbe", "Temporal"),
    AssessmentItem("T18", "Building something that outlasts me feels like a genuine obligation, not just ambition.", "Willbe", "Temporal"),
]

INTEGRATION_ITEMS = [
    AssessmentItem("I01", "When I focus deeply on one important thing, everything else in my life tends to fall apart.", "Integration", "Integration", reverse_coded=True),
    AssessmentItem("I02", "When someone I care about is in distress, I can stay emotionally present without losing my own stability.", "Integration", "Integration"),
    AssessmentItem("I03", "Attending to the past and the future makes it hard for me to be present.", "Integration", "Integration", reverse_coded=True),
    AssessmentItem("I04", "I remain present and available to the people I care about even when I am deep in demanding work.", "Integration", "Integration"),
    AssessmentItem("I05", "Pursuing depth in one area of my life requires me to sacrifice connection in another.", "Integration", "Integration", reverse_coded=True),
    AssessmentItem("I06", "Holding awareness of what matters most and handling daily logistics does not feel like it pulls me in two directions.", "Integration", "Integration"),
    AssessmentItem("I07", "Caring about the long term exhausts my capacity for dealing with the present.", "Integration", "Integration", reverse_coded=True),
    AssessmentItem("I08", "When I care deeply about something and am also holding relationships and thinking about the future, it feels sustainable rather than depleting.", "Integration", "Integration"),
    AssessmentItem("I09", "When one area of life demands my full attention, other areas necessarily collapse.", "Integration", "Integration", reverse_coded=True),
    AssessmentItem("I10", "I can be genuinely present to multiple significant commitments at the same time without feeling that attending to one requires abandoning the others.", "Integration", "Integration"),
    AssessmentItem("I11", "Trying to maintain orientation on too many things at once causes me to lose all of them.", "Integration", "Integration", reverse_coded=True),
    AssessmentItem("I12", "I experience periods where depth, connection, and purpose feel aligned without effort.", "Integration", "Integration"),
]

HOM_ITEMS = [
    AssessmentItem("M01", "My model of how I work tends to incorporate new experiences rather than being significantly changed by them.", "HallOfMirrors", "Epistemic"),
    AssessmentItem("M02", "When someone close to me describes my behavior in a way I disagree with, I typically have a more complete explanation of the situation already.", "HallOfMirrors", "Epistemic"),
    AssessmentItem("M03", "My understanding of my own psychology has remained fundamentally the same even through major life changes.", "HallOfMirrors", "Epistemic"),
    AssessmentItem("M04", "I can give a more accurate account of why I do what I do than most people around me can.", "HallOfMirrors", "Epistemic"),
    AssessmentItem("M05", "I rarely encounter an experience of myself that my existing self-understanding cannot account for.", "HallOfMirrors", "Epistemic"),
    AssessmentItem("M06", "The frameworks I use to understand my own experience tend to generate explanations for whatever I encounter.", "HallOfMirrors", "Epistemic"),
]

ALL_AXIS_ITEMS = OHN_ITEMS + HOC_ITEMS + HIM_ITEMS + ALLMEN_ITEMS + WASONCE_ITEMS + WILLBE_ITEMS
ALL_ITEMS = ALL_AXIS_ITEMS + INTEGRATION_ITEMS + HOM_ITEMS

def get_item_bank() -> List[AssessmentItem]: return ALL_ITEMS
def get_axis_items() -> List[AssessmentItem]: return ALL_AXIS_ITEMS
def get_integration_items() -> List[AssessmentItem]: return INTEGRATION_ITEMS
def get_hom_items() -> List[AssessmentItem]: return HOM_ITEMS
def get_item_pole_map() -> Dict[str, str]: return {item.id: item.pole for item in ALL_AXIS_ITEMS}
def get_integration_item_ids() -> List[str]: return [item.id for item in INTEGRATION_ITEMS]
def get_hom_item_ids() -> List[str]: return [item.id for item in HOM_ITEMS]
def get_reverse_coded_ids() -> List[str]: return [item.id for item in INTEGRATION_ITEMS if item.reverse_coded]
def get_randomized_order(seed=None) -> List[AssessmentItem]:
    import random
    items = list(ALL_ITEMS)
    if seed is not None: random.seed(seed)
    random.shuffle(items)
    return items
def get_axis_items_by_pole() -> Dict[str, List[AssessmentItem]]:
    grouped = {}
    for item in ALL_AXIS_ITEMS:
        grouped.setdefault(item.pole, []).append(item)
    return grouped

CODEBOOK = """
TRIAXIAL ORIENTATION THEORY — ASSESSMENT CODEBOOK v2.1
========================================================
INSTRUMENT: TOT Orientation Assessment v2.1 (72 items, 7-point Likert)
ADMIN TIME: 10-15 minutes
VERSION NOTES: v2.1 revisions from v2.0:
  - V01, V07: removed "cannot name/explain" qualifier (penalized articulable depth)
  - H03, H06, H09: replaced introversion-confounded items with epistemic independence items
  - T14: replaced political/legal language with behavioral future-orientation item
  - I04: replaced third-party inference with first-person behavioral item
  - I10: removed explicit axis terminology (theory contamination)
  - Added HOM subscale (M01-M06): 6-item Interpretive Orientation scale
    for Hall of Mirrors (9th formation) detection
SCORING: See tot_engine.py compute_profile() for full pipeline.
THEORY: Erickson, R. (2025). Triaxial Orientation Theory. Avner Media.
STATUS: Pre-validation research instrument.
"""
def get_codebook() -> str: return CODEBOOK
