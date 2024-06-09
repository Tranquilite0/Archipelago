from dataclasses import dataclass, replace
from BaseClasses import Region, Location, Entrance, Item, ItemClassification as IC
from typing import Optional, TYPE_CHECKING, List, Dict
from .Names import ItemID, ItemName, LairID, NPCName
from .Names.ArchipelagoID import BASE_ID, LAIR_ID_OFFSET, SOUL_OFFSET
from .Util import int_to_bcd

if TYPE_CHECKING:
    from . import SoulBlazerWorld


@dataclass(frozen=True)
class ItemData:
    id: int
    """Internal item ID"""

    operand: int
    """Either Gems/Exp Quantity or Lair ID"""

    classification: IC

    def duplicate(self, **changes) -> "ItemData":
        """Returns a copy of this ItemData with the specified changes."""
        return replace(self, **changes)

    @property
    def code(self) -> int:
        """The unique ID used by archipelago for this item"""

        if self.id == ItemID.LAIR_RELEASE:
            return BASE_ID + LAIR_ID_OFFSET + self.operand
        elif self.id == ItemID.SOUL:
            return BASE_ID + SOUL_OFFSET + self.operand
        return BASE_ID + self.id

    @property
    def operand_bcd(self) -> int:
        return int_to_bcd(self.operand)

    @property
    def operand_for_id(self) -> int:
        if self.id == ItemID.GEMS or self.id == ItemID.EXP:
            return self.operand_bcd
        return self.operand


class SoulBlazerItem(Item):
    game = "Soul Blazer"

    def __init__(self, name: str, player: int, itemData: ItemData):
        super().__init__(name, itemData.classification, itemData.code, player)
        self._itemData = itemData

    def set_operand(self, value: int) -> "SoulBlazerItem":
        self._itemData = self._itemData.duplicate(operand=value)
        return self

    @property
    def id(self) -> int:
        return self._itemData.id

    @property
    def operand(self) -> int:
        return self._itemData.operand

    @operand.setter
    def operand(self, value: int):
        self._itemData.operand = value

    @property
    def operand_bcd(self) -> int:
        return self._itemData.operand_bcd

    @operand_bcd.setter
    def operand_bcd(self, bcd: int):
        self._itemData.operand_bcd = bcd

    @property
    def operand_for_id(self) -> int:
        return self._itemData.operand_for_id


herb_count = 20
"""Number of Herbs in vanilla item pool"""

bottle_count = 7
"""Number of Strange Bottles in vanilla item pool"""

nothing_count = 3
"""Number of 'Nothing' rewards in vanilla item pool"""

gem_values_vanilla = [1, 12, 40, 50, 50, 50, 50, 50, 60, 60, 80, 80, 80, 80, 80, 100, 100, 100, 100, 150, 200]
"""Gem reward values in vanilla item pool"""

exp_values_vanilla = [1, 30, 80, 150, 180, 200, 250, 300, 300, 300, 300, 300, 400]
"""Exp reward values in vanilla item pool"""


def create_gem_pool(world: "SoulBlazerWorld") -> List[int]:
    if world.options.gem_exp_pool == "random_range":
        return [world.random.randint(1, 999) for _ in range(len(gem_values_vanilla))]
    if world.options.gem_exp_pool == "improved":
        return [gem * 2 for gem in gem_values_vanilla]

    return gem_values_vanilla[:]


def create_exp_pool(world: "SoulBlazerWorld") -> List[int]:
    if world.options.gem_exp_pool == "random_range":
        return [world.random.randint(1, 9999) for _ in range(len(exp_values_vanilla))]
    if world.options.gem_exp_pool == "improved":
        return [exp * 10 for exp in exp_values_vanilla]

    return exp_values_vanilla[:]


def create_itempool(world: "SoulBlazerWorld") -> List[SoulBlazerItem]:
    itempool = [SoulBlazerItem(name, world.player, itemData) for (name, itemData) in unique_items_table.items()]
    itempool += [
        SoulBlazerItem(ItemName.MEDICALHERB, world.player, repeatable_items_table[ItemName.MEDICALHERB])
        for _ in range(herb_count)
    ]
    itempool += [
        SoulBlazerItem(ItemName.STRANGEBOTTLE, world.player, repeatable_items_table[ItemName.STRANGEBOTTLE])
        for _ in range(bottle_count)
    ]
    # TODO: Add option to replace nothings with... something?
    itempool += [
        SoulBlazerItem(ItemName.NOTHING, world.player, repeatable_items_table[ItemName.NOTHING])
        for _ in range(nothing_count)
    ]
    world.gem_items = [world.create_item(ItemName.GEMS).set_operand(value) for value in create_gem_pool(world)]
    itempool += world.gem_items
    world.exp_items = [world.create_item(ItemName.EXP).set_operand(value) for value in create_exp_pool(world)]
    itempool += world.exp_items

    return itempool


swords_table = {
    ItemName.LIFESWORD: ItemData(ItemID.LIFESWORD, 0x00, IC.progression),
    ItemName.PSYCHOSWORD: ItemData(ItemID.PSYCHOSWORD, 0x00, IC.progression),
    ItemName.CRITICALSWORD: ItemData(ItemID.CRITICALSWORD, 0x00, IC.progression),
    ItemName.LUCKYBLADE: ItemData(ItemID.LUCKYBLADE, 0x00, IC.progression),
    ItemName.ZANTETSUSWORD: ItemData(ItemID.ZANTETSUSWORD, 0x00, IC.progression),
    ItemName.SPIRITSWORD: ItemData(ItemID.SPIRITSWORD, 0x00, IC.progression),
    ItemName.RECOVERYSWORD: ItemData(ItemID.RECOVERYSWORD, 0x00, IC.progression),
    ItemName.SOULBLADE: ItemData(ItemID.SOULBLADE, 0x00, IC.progression),
}

armors_table = {
    ItemName.IRONARMOR: ItemData(ItemID.IRONARMOR, 0x00, IC.useful),
    ItemName.ICEARMOR: ItemData(ItemID.ICEARMOR, 0x00, IC.progression),
    ItemName.BUBBLEARMOR: ItemData(ItemID.BUBBLEARMOR, 0x00, IC.progression),
    ItemName.MAGICARMOR: ItemData(ItemID.MAGICARMOR, 0x00, IC.useful),
    ItemName.MYSTICARMOR: ItemData(ItemID.MYSTICARMOR, 0x00, IC.useful),
    ItemName.LIGHTARMOR: ItemData(ItemID.LIGHTARMOR, 0x00, IC.useful),
    ItemName.ELEMENTALARMOR: ItemData(ItemID.ELEMENTALARMOR, 0x00, IC.useful),
    ItemName.SOULARMOR: ItemData(ItemID.SOULARMOR, 0x00, IC.progression),
}

castable_magic_table = {
    ItemName.FLAMEBALL: ItemData(ItemID.FLAMEBALL, 0x00, IC.progression),
    ItemName.LIGHTARROW: ItemData(ItemID.LIGHTARROW, 0x00, IC.progression),
    ItemName.MAGICFLARE: ItemData(ItemID.MAGICFLARE, 0x00, IC.progression),
    ItemName.ROTATOR: ItemData(ItemID.ROTATOR, 0x00, IC.progression),
    ItemName.SPARKBOMB: ItemData(ItemID.SPARKBOMB, 0x00, IC.progression),
    ItemName.FLAMEPILLAR: ItemData(ItemID.FLAMEPILLAR, 0x00, IC.progression),
    ItemName.TORNADO: ItemData(ItemID.TORNADO, 0x00, IC.progression),
}

magic_table = {
    **castable_magic_table,
    ItemName.PHOENIX: ItemData(ItemID.PHOENIX, 0x00, IC.progression),
}

emblems_table = {
    ItemName.EMBLEMA: ItemData(ItemID.EMBLEMA, 0x00, IC.progression),
    ItemName.EMBLEMB: ItemData(ItemID.EMBLEMB, 0x00, IC.progression),
    ItemName.EMBLEMC: ItemData(ItemID.EMBLEMC, 0x00, IC.progression),
    ItemName.EMBLEMD: ItemData(ItemID.EMBLEMD, 0x00, IC.progression),
    ItemName.EMBLEME: ItemData(ItemID.EMBLEME, 0x00, IC.progression),
    ItemName.EMBLEMF: ItemData(ItemID.EMBLEMF, 0x00, IC.progression),
    ItemName.EMBLEMG: ItemData(ItemID.EMBLEMG, 0x00, IC.progression),
    ItemName.EMBLEMH: ItemData(ItemID.EMBLEMH, 0x00, IC.progression),
}

redhots_table = {
    ItemName.REDHOTMIRROR: ItemData(ItemID.REDHOTMIRROR, 0x00, IC.progression),
    ItemName.REDHOTBALL: ItemData(ItemID.REDHOTBALL, 0x00, IC.progression),
    ItemName.REDHOTSTICK: ItemData(ItemID.REDHOTSTICK, 0x00, IC.progression),
}

stones_table = {
    ItemName.BROWNSTONE: ItemData(ItemID.BROWNSTONE, 0x00, IC.progression),
    ItemName.GREENSTONE: ItemData(ItemID.GREENSTONE, 0x00, IC.progression),
    ItemName.BLUESTONE: ItemData(ItemID.BLUESTONE, 0x00, IC.progression),
    ItemName.SILVERSTONE: ItemData(ItemID.SILVERSTONE, 0x00, IC.progression),
    ItemName.PURPLESTONE: ItemData(ItemID.PURPLESTONE, 0x00, IC.progression),
    ItemName.BLACKSTONE: ItemData(ItemID.BLACKSTONE, 0x00, IC.progression),
}

inventory_items_table = {
    ItemName.GOATSFOOD: ItemData(ItemID.GOATSFOOD, 0x00, IC.useful),
    ItemName.HARPSTRING: ItemData(ItemID.HARPSTRING, 0x00, IC.progression),
    ItemName.APASS: ItemData(ItemID.APASS, 0x00, IC.progression),
    ItemName.DREAMROD: ItemData(ItemID.DREAMROD, 0x00, IC.progression),
    ItemName.LEOSBRUSH: ItemData(ItemID.LEOSBRUSH, 0x00, IC.progression),
    ItemName.TURBOSLEAVES: ItemData(ItemID.TURBOSLEAVES, 0x00, IC.progression),
    ItemName.MOLESRIBBON: ItemData(ItemID.MOLESRIBBON, 0x00, IC.progression),
    ItemName.BIGPEARL: ItemData(ItemID.BIGPEARL, 0x00, IC.progression),
    ItemName.MERMAIDSTEARS: ItemData(ItemID.MERMAIDSTEARS, 0x00, IC.progression),
    ItemName.MUSHROOMSHOES: ItemData(ItemID.MUSHROOMSHOES, 0x00, IC.progression),
    ItemName.AIRSHIPKEY: ItemData(ItemID.AIRSHIPKEY, 0x00, IC.progression),
    ItemName.THUNDERRING: ItemData(ItemID.THUNDERRING, 0x00, IC.progression),
    ItemName.DELICIOUSSEEDS: ItemData(ItemID.DELICIOUSSEEDS, 0x00, IC.progression),
    ItemName.ACTINIDIALEAVES: ItemData(ItemID.ACTINIDIALEAVES, 0x00, IC.progression),
    ItemName.DOORKEY: ItemData(ItemID.DOORKEY, 0x00, IC.progression),
    ItemName.PLATINUMCARD: ItemData(ItemID.PLATINUMCARD, 0x00, IC.progression),
    ItemName.VIPCARD: ItemData(ItemID.VIPCARD, 0x00, IC.progression),
    **emblems_table,
    **redhots_table,
    ItemName.POWERBRACELET: ItemData(ItemID.POWERBRACELET, 0x00, IC.useful),
    ItemName.SHIELDBRACELET: ItemData(ItemID.SHIELDBRACELET, 0x00, IC.useful),
    ItemName.SUPERBRACELET: ItemData(ItemID.SUPERBRACELET, 0x00, IC.useful),
    ItemName.MEDICALHERB: ItemData(ItemID.MEDICALHERB, 0x00, IC.filler),
    ItemName.STRANGEBOTTLE: ItemData(ItemID.STRANGEBOTTLE, 0x00, IC.filler),
    **stones_table,
    ItemName.MAGICBELL: ItemData(ItemID.MAGICBELL, 0x00, IC.useful),
}


misc_table = {
    ItemName.NOTHING: ItemData(ItemID.NOTHING, 0x00, IC.filler),
    ItemName.GEMS: ItemData(ItemID.GEMS, 100, IC.filler),
    ItemName.EXP: ItemData(ItemID.EXP, 250, IC.filler),
}

repeatable_items_table = {
    ItemName.MEDICALHERB: inventory_items_table[ItemName.MEDICALHERB],
    ItemName.STRANGEBOTTLE: inventory_items_table[ItemName.STRANGEBOTTLE],
    **misc_table,
}

items_table = {
    **swords_table,
    **armors_table,
    **magic_table,
    **inventory_items_table,
}

npc_release_table = {
    NPCName.OLD_WOMAN: ItemData(ItemID.LAIR_RELEASE, LairID.OLD_WOMAN, IC.progression),
    NPCName.TOOL_SHOP_OWNER: ItemData(ItemID.LAIR_RELEASE, LairID.TOOL_SHOP_OWNER, IC.progression),
    NPCName.TULIP: ItemData(ItemID.LAIR_RELEASE, LairID.TULIP, IC.filler),
    NPCName.BRIDGE_GUARD: ItemData(ItemID.LAIR_RELEASE, LairID.BRIDGE_GUARD, IC.progression),
    NPCName.VILLAGE_CHIEF: ItemData(ItemID.LAIR_RELEASE, LairID.VILLAGE_CHIEF, IC.progression),
    NPCName.IVY_CHEST_ROOM: ItemData(ItemID.LAIR_RELEASE, LairID.IVY_CHEST_ROOM, IC.progression),
    NPCName.WATER_MILL: ItemData(ItemID.LAIR_RELEASE, LairID.WATER_MILL, IC.progression),
    NPCName.GOAT_HERB: ItemData(ItemID.LAIR_RELEASE, LairID.GOAT_HERB, IC.progression),
    NPCName.LISA: ItemData(ItemID.LAIR_RELEASE, LairID.LISA, IC.progression),
    NPCName.TULIP2: ItemData(ItemID.LAIR_RELEASE, LairID.TULIP2, IC.filler),
    NPCName.ARCHITECT: ItemData(ItemID.LAIR_RELEASE, LairID.ARCHITECT, IC.progression),
    NPCName.IVY: ItemData(ItemID.LAIR_RELEASE, LairID.IVY, IC.progression),
    NPCName.GOAT: ItemData(ItemID.LAIR_RELEASE, LairID.GOAT, IC.progression),
    NPCName.TEDDY: ItemData(ItemID.LAIR_RELEASE, LairID.TEDDY, IC.progression),
    NPCName.TULIP3: ItemData(ItemID.LAIR_RELEASE, LairID.TULIP3, IC.filler),
    NPCName.LEOS_HOUSE: ItemData(ItemID.LAIR_RELEASE, LairID.LEOS_HOUSE, IC.progression),
    NPCName.LONELY_GOAT: ItemData(ItemID.LAIR_RELEASE, LairID.LONELY_GOAT, IC.filler),
    NPCName.TULIP_PASS: ItemData(ItemID.LAIR_RELEASE, LairID.TULIP_PASS, IC.progression),
    NPCName.BOY_CABIN: ItemData(ItemID.LAIR_RELEASE, LairID.BOY_CABIN, IC.filler),
    NPCName.BOY_CAVE: ItemData(ItemID.LAIR_RELEASE, LairID.BOY_CAVE, IC.progression),
    NPCName.OLD_MAN: ItemData(ItemID.LAIR_RELEASE, LairID.OLD_MAN, IC.filler),
    NPCName.OLD_MAN2: ItemData(ItemID.LAIR_RELEASE, LairID.OLD_MAN2, IC.filler),
    NPCName.IVY2: ItemData(ItemID.LAIR_RELEASE, LairID.IVY2, IC.filler),
    NPCName.IVY_EMBLEM_A: ItemData(ItemID.LAIR_RELEASE, LairID.IVY_EMBLEM_A, IC.progression),
    NPCName.IVY_RECOVERY_SWORD: ItemData(ItemID.LAIR_RELEASE, LairID.IVY_RECOVERY_SWORD, IC.progression),
    NPCName.TULIP4: ItemData(ItemID.LAIR_RELEASE, LairID.TULIP4, IC.filler),
    NPCName.GOAT2: ItemData(ItemID.LAIR_RELEASE, LairID.GOAT2, IC.filler),
    NPCName.BIRD_RED_HOT_MIRROR: ItemData(ItemID.LAIR_RELEASE, LairID.BIRD_RED_HOT_MIRROR, IC.progression),
    NPCName.BIRD: ItemData(ItemID.LAIR_RELEASE, LairID.BIRD, IC.filler),
    NPCName.DOG: ItemData(ItemID.LAIR_RELEASE, LairID.DOG, IC.filler),
    NPCName.DOG2: ItemData(ItemID.LAIR_RELEASE, LairID.DOG2, IC.filler),
    NPCName.DOG3: ItemData(ItemID.LAIR_RELEASE, LairID.DOG3, IC.progression),
    NPCName.MOLE_SHIELD_BRACELET: ItemData(ItemID.LAIR_RELEASE, LairID.MOLE_SHIELD_BRACELET, IC.progression),
    NPCName.SQUIRREL_EMBLEM_C: ItemData(ItemID.LAIR_RELEASE, LairID.SQUIRREL_EMBLEM_C, IC.progression),
    NPCName.SQUIRREL_PSYCHO_SWORD: ItemData(ItemID.LAIR_RELEASE, LairID.SQUIRREL_PSYCHO_SWORD, IC.progression),
    NPCName.BIRD2: ItemData(ItemID.LAIR_RELEASE, LairID.BIRD2, IC.filler),
    NPCName.MOLE_SOUL_OF_LIGHT: ItemData(ItemID.LAIR_RELEASE, LairID.MOLE_SOUL_OF_LIGHT, IC.progression),
    NPCName.DEER: ItemData(ItemID.LAIR_RELEASE, LairID.DEER, IC.progression),
    NPCName.CROCODILE: ItemData(ItemID.LAIR_RELEASE, LairID.CROCODILE, IC.progression),
    NPCName.SQUIRREL: ItemData(ItemID.LAIR_RELEASE, LairID.SQUIRREL, IC.filler),
    NPCName.GREENWOODS_GUARDIAN: ItemData(ItemID.LAIR_RELEASE, LairID.GREENWOODS_GUARDIAN, IC.progression),
    NPCName.MOLE: ItemData(ItemID.LAIR_RELEASE, LairID.MOLE, IC.progression),
    NPCName.DOG4: ItemData(ItemID.LAIR_RELEASE, LairID.DOG4, IC.filler),
    NPCName.SQUIRREL_ICE_ARMOR: ItemData(ItemID.LAIR_RELEASE, LairID.SQUIRREL_ICE_ARMOR, IC.progression),
    NPCName.SQUIRREL2: ItemData(ItemID.LAIR_RELEASE, LairID.SQUIRREL2, IC.filler),
    NPCName.DOG5: ItemData(ItemID.LAIR_RELEASE, LairID.DOG5, IC.filler),
    NPCName.CROCODILE2: ItemData(ItemID.LAIR_RELEASE, LairID.CROCODILE2, IC.progression),
    NPCName.MOLE2: ItemData(ItemID.LAIR_RELEASE, LairID.MOLE2, IC.filler),
    NPCName.SQUIRREL3: ItemData(ItemID.LAIR_RELEASE, LairID.SQUIRREL3, IC.progression),
    NPCName.BIRD_GREENWOOD_LEAF: ItemData(ItemID.LAIR_RELEASE, LairID.BIRD_GREENWOOD_LEAF, IC.progression),
    NPCName.MOLE3: ItemData(ItemID.LAIR_RELEASE, LairID.MOLE3, IC.progression),
    NPCName.DEER_MAGIC_BELL: ItemData(ItemID.LAIR_RELEASE, LairID.DEER_MAGIC_BELL, IC.progression),
    NPCName.BIRD3: ItemData(ItemID.LAIR_RELEASE, LairID.BIRD3, IC.filler),
    NPCName.CROCODILE3: ItemData(ItemID.LAIR_RELEASE, LairID.CROCODILE3, IC.progression),
    NPCName.MONMO: ItemData(ItemID.LAIR_RELEASE, LairID.MONMO, IC.progression),
    NPCName.DOLPHIN: ItemData(ItemID.LAIR_RELEASE, LairID.DOLPHIN, IC.filler),
    NPCName.ANGELFISH: ItemData(ItemID.LAIR_RELEASE, LairID.ANGELFISH, IC.filler),
    NPCName.MERMAID: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID, IC.progression),
    NPCName.ANGELFISH2: ItemData(ItemID.LAIR_RELEASE, LairID.ANGELFISH2, IC.filler),
    NPCName.MERMAID_PEARL: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_PEARL, IC.progression),
    NPCName.MERMAID2: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID2, IC.filler),
    NPCName.DOLPHIN_SAVES_LUE: ItemData(ItemID.LAIR_RELEASE, LairID.DOLPHIN_SAVES_LUE, IC.progression),
    NPCName.MERMAID_STATUE_BLESTER: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_STATUE_BLESTER, IC.progression),
    NPCName.MERMAID_RED_HOT_STICK: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_RED_HOT_STICK, IC.progression),
    NPCName.LUE: ItemData(ItemID.LAIR_RELEASE, LairID.LUE, IC.progression),
    NPCName.MERMAID3: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID3, IC.filler),
    NPCName.MERMAID_NANA: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_NANA, IC.filler),
    NPCName.MERMAID4: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID4, IC.filler),
    NPCName.DOLPHIN2: ItemData(ItemID.LAIR_RELEASE, LairID.DOLPHIN2, IC.progression),
    NPCName.MERMAID_STATUE_ROCKBIRD: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_STATUE_ROCKBIRD, IC.progression),
    NPCName.MERMAID_BUBBLE_ARMOR: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_BUBBLE_ARMOR, IC.progression),
    NPCName.MERMAID5: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID5, IC.filler),
    NPCName.MERMAID6: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID6, IC.filler),
    NPCName.MERMAID_TEARS: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_TEARS, IC.filler),
    NPCName.MERMAID_STATUE_DUREAN: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_STATUE_DUREAN, IC.progression),
    NPCName.ANGELFISH3: ItemData(ItemID.LAIR_RELEASE, LairID.ANGELFISH3, IC.filler),
    NPCName.ANGELFISH_SOUL_OF_SHIELD: ItemData(ItemID.LAIR_RELEASE, LairID.ANGELFISH_SOUL_OF_SHIELD, IC.progression),
    NPCName.MERMAID_MAGIC_FLARE: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_MAGIC_FLARE, IC.progression),
    NPCName.MERMAID_QUEEN: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_QUEEN, IC.progression),
    NPCName.MERMAID_STATUE_GHOST_SHIP: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID_STATUE_GHOST_SHIP, IC.progression),
    NPCName.DOLPHIN_SECRET_CAVE: ItemData(ItemID.LAIR_RELEASE, LairID.DOLPHIN_SECRET_CAVE, IC.progression),
    NPCName.MERMAID7: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID7, IC.filler),
    NPCName.ANGELFISH4: ItemData(ItemID.LAIR_RELEASE, LairID.ANGELFISH4, IC.filler),
    NPCName.MERMAID8: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID8, IC.filler),
    NPCName.DOLPHIN_PEARL: ItemData(ItemID.LAIR_RELEASE, LairID.DOLPHIN_PEARL, IC.progression),
    NPCName.MERMAID9: ItemData(ItemID.LAIR_RELEASE, LairID.MERMAID9, IC.filler),
    NPCName.GRANDPA: ItemData(ItemID.LAIR_RELEASE, LairID.GRANDPA, IC.progression),
    NPCName.GIRL: ItemData(ItemID.LAIR_RELEASE, LairID.GIRL, IC.filler),
    NPCName.MUSHROOM: ItemData(ItemID.LAIR_RELEASE, LairID.MUSHROOM, IC.filler),
    NPCName.BOY: ItemData(ItemID.LAIR_RELEASE, LairID.BOY, IC.progression),
    NPCName.GRANDPA2: ItemData(ItemID.LAIR_RELEASE, LairID.GRANDPA2, IC.filler),
    NPCName.SNAIL_JOCKEY: ItemData(ItemID.LAIR_RELEASE, LairID.SNAIL_JOCKEY, IC.filler),
    NPCName.NOME: ItemData(ItemID.LAIR_RELEASE, LairID.NOME, IC.progression),
    NPCName.BOY2: ItemData(ItemID.LAIR_RELEASE, LairID.BOY2, IC.filler),
    NPCName.MUSHROOM_EMBLEM_F: ItemData(ItemID.LAIR_RELEASE, LairID.MUSHROOM_EMBLEM_F, IC.progression),
    NPCName.DANCING_GRANDMA: ItemData(ItemID.LAIR_RELEASE, LairID.DANCING_GRANDMA, IC.progression),
    NPCName.DANCING_GRANDMA2: ItemData(ItemID.LAIR_RELEASE, LairID.DANCING_GRANDMA2, IC.progression),
    NPCName.SNAIL_EMBLEM_E: ItemData(ItemID.LAIR_RELEASE, LairID.SNAIL_EMBLEM_E, IC.progression),
    NPCName.BOY_MUSHROOM_SHOES: ItemData(ItemID.LAIR_RELEASE, LairID.BOY_MUSHROOM_SHOES, IC.progression),
    NPCName.GRANDMA: ItemData(ItemID.LAIR_RELEASE, LairID.GRANDMA, IC.filler),
    NPCName.GIRL2: ItemData(ItemID.LAIR_RELEASE, LairID.GIRL2, IC.filler),
    NPCName.MUSHROOM2: ItemData(ItemID.LAIR_RELEASE, LairID.MUSHROOM2, IC.progression),
    NPCName.SNAIL_RACER: ItemData(ItemID.LAIR_RELEASE, LairID.SNAIL_RACER, IC.filler),
    NPCName.SNAIL_RACER2: ItemData(ItemID.LAIR_RELEASE, LairID.SNAIL_RACER2, IC.filler),
    NPCName.GIRL3: ItemData(ItemID.LAIR_RELEASE, LairID.GIRL3, IC.progression),
    NPCName.MUSHROOM3: ItemData(ItemID.LAIR_RELEASE, LairID.MUSHROOM3, IC.filler),
    NPCName.SNAIL: ItemData(ItemID.LAIR_RELEASE, LairID.SNAIL, IC.filler),
    NPCName.GRANDPA3: ItemData(ItemID.LAIR_RELEASE, LairID.GRANDPA3, IC.progression),
    NPCName.SNAIL2: ItemData(ItemID.LAIR_RELEASE, LairID.SNAIL2, IC.filler),
    NPCName.GRANDPA4: ItemData(ItemID.LAIR_RELEASE, LairID.GRANDPA4, IC.progression),
    NPCName.GRANDPA_LUNE: ItemData(ItemID.LAIR_RELEASE, LairID.GRANDPA_LUNE, IC.progression),
    NPCName.GRANDPA5: ItemData(ItemID.LAIR_RELEASE, LairID.GRANDPA5, IC.progression),
    NPCName.MOUNTAIN_KING: ItemData(ItemID.LAIR_RELEASE, LairID.MOUNTAIN_KING, IC.progression),
    NPCName.PLANT_HERB: ItemData(ItemID.LAIR_RELEASE, LairID.PLANT_HERB, IC.progression),
    NPCName.PLANT: ItemData(ItemID.LAIR_RELEASE, LairID.PLANT, IC.filler),
    NPCName.CHEST_OF_DRAWERS_MYSTIC_ARMOR: ItemData(
        ItemID.LAIR_RELEASE, LairID.CHEST_OF_DRAWERS_MYSTIC_ARMOR, IC.progression
    ),
    NPCName.CAT: ItemData(ItemID.LAIR_RELEASE, LairID.CAT, IC.progression),
    NPCName.GREAT_DOOR_ZANTETSU_SWORD: ItemData(ItemID.LAIR_RELEASE, LairID.GREAT_DOOR_ZANTETSU_SWORD, IC.progression),
    NPCName.CAT2: ItemData(ItemID.LAIR_RELEASE, LairID.CAT2, IC.progression),
    NPCName.GREAT_DOOR: ItemData(ItemID.LAIR_RELEASE, LairID.GREAT_DOOR, IC.progression),
    NPCName.CAT3: ItemData(ItemID.LAIR_RELEASE, LairID.CAT3, IC.filler),
    NPCName.MODEL_TOWN1: ItemData(ItemID.LAIR_RELEASE, LairID.MODEL_TOWN1, IC.progression),
    NPCName.GREAT_DOOR_MODEL_TOWNS: ItemData(ItemID.LAIR_RELEASE, LairID.GREAT_DOOR_MODEL_TOWNS, IC.progression),
    NPCName.STEPS_UPSTAIRS: ItemData(ItemID.LAIR_RELEASE, LairID.STEPS_UPSTAIRS, IC.progression),
    NPCName.CAT_DOOR_KEY: ItemData(ItemID.LAIR_RELEASE, LairID.CAT_DOOR_KEY, IC.progression),
    NPCName.MOUSE: ItemData(ItemID.LAIR_RELEASE, LairID.MOUSE, IC.progression),
    NPCName.MARIE: ItemData(ItemID.LAIR_RELEASE, LairID.MARIE, IC.progression),
    NPCName.DOLL: ItemData(ItemID.LAIR_RELEASE, LairID.DOLL, IC.filler),
    NPCName.CHEST_OF_DRAWERS: ItemData(ItemID.LAIR_RELEASE, LairID.CHEST_OF_DRAWERS, IC.filler),
    NPCName.PLANT2: ItemData(ItemID.LAIR_RELEASE, LairID.PLANT2, IC.filler),
    NPCName.MOUSE2: ItemData(ItemID.LAIR_RELEASE, LairID.MOUSE2, IC.filler),
    NPCName.MOUSE_SPARK_BOMB: ItemData(ItemID.LAIR_RELEASE, LairID.MOUSE_SPARK_BOMB, IC.progression),
    NPCName.MOUSE3: ItemData(ItemID.LAIR_RELEASE, LairID.MOUSE3, IC.filler),
    NPCName.GREAT_DOOR_SOUL_OF_DETECTION: ItemData(
        ItemID.LAIR_RELEASE, LairID.GREAT_DOOR_SOUL_OF_DETECTION, IC.progression
    ),
    NPCName.MODEL_TOWN2: ItemData(ItemID.LAIR_RELEASE, LairID.MODEL_TOWN2, IC.progression),
    NPCName.MOUSE4: ItemData(ItemID.LAIR_RELEASE, LairID.MOUSE4, IC.filler),
    NPCName.STEPS_MARIE: ItemData(ItemID.LAIR_RELEASE, LairID.STEPS_MARIE, IC.progression),
    NPCName.CHEST_OF_DRAWERS2: ItemData(ItemID.LAIR_RELEASE, LairID.CHEST_OF_DRAWERS2, IC.progression),
    NPCName.PLANT_ACTINIDIA_LEAVES: ItemData(ItemID.LAIR_RELEASE, LairID.PLANT_ACTINIDIA_LEAVES, IC.progression),
    NPCName.MOUSE5: ItemData(ItemID.LAIR_RELEASE, LairID.MOUSE5, IC.filler),
    NPCName.CAT4: ItemData(ItemID.LAIR_RELEASE, LairID.CAT4, IC.filler),
    NPCName.STAIRS_POWER_PLANT: ItemData(ItemID.LAIR_RELEASE, LairID.STAIRS_POWER_PLANT, IC.progression),
    NPCName.SOLDIER: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER, IC.filler),
    NPCName.SOLDIER2: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER2, IC.filler),
    NPCName.SOLDIER3: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER3, IC.filler),
    NPCName.SOLDIER_ELEMENTAL_MAIL: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER_ELEMENTAL_MAIL, IC.progression),
    NPCName.SOLDIER4: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER4, IC.filler),
    NPCName.SOLDIER5: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER5, IC.filler),
    NPCName.SINGER_CONCERT_HALL: ItemData(ItemID.LAIR_RELEASE, LairID.SINGER_CONCERT_HALL, IC.progression),
    NPCName.SOLDIER6: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER6, IC.filler),
    NPCName.MAID: ItemData(ItemID.LAIR_RELEASE, LairID.MAID, IC.filler),
    NPCName.SOLDIER_LEFT_TOWER: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER_LEFT_TOWER, IC.progression),
    NPCName.SOLDIER_DOK: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER_DOK, IC.progression),
    NPCName.SOLDIER_PLATINUM_CARD: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER_PLATINUM_CARD, IC.progression),
    NPCName.SINGER: ItemData(ItemID.LAIR_RELEASE, LairID.SINGER, IC.filler),
    NPCName.SOLDIER_SOUL_OF_REALITY: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER_SOUL_OF_REALITY, IC.progression),
    NPCName.MAID2: ItemData(ItemID.LAIR_RELEASE, LairID.MAID2, IC.filler),
    NPCName.QUEEN_MAGRIDD: ItemData(ItemID.LAIR_RELEASE, LairID.QUEEN_MAGRIDD, IC.progression),
    NPCName.SOLDIER_WITH_LEO: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER_WITH_LEO, IC.progression),
    NPCName.SOLDIER_RIGHT_TOWER: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER_RIGHT_TOWER, IC.progression),
    NPCName.DR_LEO: ItemData(ItemID.LAIR_RELEASE, LairID.DR_LEO, IC.progression),
    NPCName.SOLDIER7: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER7, IC.filler),
    NPCName.SOLDIER8: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER8, IC.filler),
    NPCName.MAID_HERB: ItemData(ItemID.LAIR_RELEASE, LairID.MAID_HERB, IC.progression),
    NPCName.SOLDIER_CASTLE: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER_CASTLE, IC.progression),
    NPCName.SOLDIER9: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER9, IC.filler),
    NPCName.SOLDIER10: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER10, IC.filler),
    NPCName.SOLDIER11: ItemData(ItemID.LAIR_RELEASE, LairID.SOLDIER11, IC.filler),
    NPCName.KING_MAGRIDD: ItemData(ItemID.LAIR_RELEASE, LairID.KING_MAGRIDD, IC.progression),
}

souls_table = {
    ItemName.SOUL_MAGICIAN: ItemData(ItemID.SOUL, 0x00, IC.progression),
    ItemName.SOUL_LIGHT: ItemData(ItemID.SOUL, 0x01, IC.progression),
    ItemName.SOUL_SHIELD: ItemData(ItemID.SOUL, 0x02, IC.useful),
    ItemName.SOUL_DETECTION: ItemData(ItemID.SOUL, 0x03, IC.useful),
    ItemName.SOUL_REALITY: ItemData(ItemID.SOUL, 0x04, IC.progression),
}

special_table = {ItemName.VICTORY: ItemData(ItemID.VICTORY, 0x00, IC.progression)}

all_items_table = {
    **items_table,
    **misc_table,
    **npc_release_table,
    **souls_table,
    **special_table,
}

unique_items_table = {
    k: v for k, v in all_items_table.items() if k not in repeatable_items_table and k != ItemName.VICTORY
}

item_name_groups = {
    "swords": swords_table.keys(),
    "armors": armors_table.keys(),
    "magic": magic_table.keys(),
    "stones": stones_table.keys(),
    "emblems": emblems_table.keys(),
    "redhots": redhots_table.keys(),
    "souls": souls_table.keys(),
}
