from .base_material import BaseMaterial
from .glass import Glass
from .masonry import Masonry
from .rc import ReinforcedConcrete
from .steel import Steel
from .uhpc import UHPC

# Registry mapping material profile names to their Python classes
MATERIAL_CLASS_MAP = {
    "Glass 6mm Monolithic": Glass,
    "Glass 12mm Laminated": Glass,
    "Brick Masonry Unreinforced": Masonry,
    "Reinforced Concrete M30": ReinforcedConcrete,
    "Ultra-High Performance Concrete (UHPC)": UHPC,
    "Structural Steel Grade 250": Steel
}
