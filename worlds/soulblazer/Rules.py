from typing import Callable, TYPE_CHECKING

from enum import IntEnum, auto
from BaseClasses import CollectionState
from .Names import ItemName, ItemID, LairName, LairID, ChestName, ChestID, NPCRewardName, NPCRewardID, NPCName
from .Items import emblems_table, swords_table

if TYPE_CHECKING:
    from . import SoulBlazerWorld


class RuleFlag(IntEnum):
    NONE = 0
    """No special requirement preventing access."""
    CAN_CUT_METAL = auto()
    """Requires a way to damage metal enemies (Zantestu Sword|Soul Blade)."""
    CAN_CUT_SPIRIT = auto()
    """Requires a way to damage metal enemies (Spirit Sword|Soul Blade)."""
    HAS_THUNDER = auto()
    """
    Requires a way to damage metal enemies in the presence of a thunder pyramids
    (Thunder Ring|Zantestu Sword|Soul Blade).
    """
    HAS_MAGIC = auto()
    """Requires a way to damage enemies outside of sword range."""
    HAS_SWORD = auto()
    """
    Requires any sword. Only used as a sanity check at the start of the game
    since we prefill the first chest with a sword.
    """


metal_items = [ItemName.ZANTETSUSWORD, ItemName.SOULBLADE]
spirit_items = [ItemName.SPIRITSWORD, ItemName.SOULBLADE]
thunder_items = [ItemName.THUNDERRING, *metal_items]
magic_items = [
    ItemName.FLAMEBALL,
    ItemName.LIGHTARROW,
    ItemName.MAGICFLARE,
    ItemName.ROTATOR,
    ItemName.SPARKBOMB,
    ItemName.FLAMEPILLAR,
    ItemName.TORNADO,
]
sword_items = [*swords_table.keys()]


def no_requirement(state: CollectionState, player: int) -> bool:
    return True


def can_cut_metal(state: CollectionState, player: int) -> bool:
    return state.has_any(metal_items, player)


def can_cut_spirit(state: CollectionState, player: int) -> bool:
    return state.has_any(spirit_items, player)


def has_thunder(state: CollectionState, player: int) -> bool:
    return state.has_any(thunder_items, player)


def has_magic(state: CollectionState, player: int) -> bool:
    return state.has_any(magic_items, player)


def has_sword(state: CollectionState, player: int) -> bool:
    return state.has_any(sword_items, player)


rule_for_flag = {
    RuleFlag.NONE: no_requirement,
    RuleFlag.CAN_CUT_METAL: can_cut_metal,
    RuleFlag.CAN_CUT_SPIRIT: can_cut_spirit,
    RuleFlag.HAS_THUNDER: has_thunder,
    RuleFlag.HAS_MAGIC: has_magic,
    RuleFlag.HAS_SWORD: has_sword,
}

# Many locations depend on one or two NPC releases so rather than create regions to hold one location,
# we put these location-specific dependencies here.
# TODO: Add chests dependencies too
location_dependencies = {
    # Act 1 - Grass Valley
    NPCRewardName.TOOL_SHOP_OWNER: [NPCName.TOOL_SHOP_OWNER],
    # TODO: figure out if we can patch it to make emblem A tile activatable without turning the water wheel
    NPCRewardName.EMBLEM_A_TILE: [NPCName.IVY, NPCName.IVY_EMBLEM_A, NPCName.WATER_MILL],
    NPCRewardName.GOAT_PEN_CORNER: [NPCName.GOAT_HERB],
    NPCRewardName.TEDDY: [NPCName.TOOL_SHOP_OWNER, NPCName.TEDDY],
    NPCRewardName.PASS_TILE: [NPCName.IVY, NPCName.TULIP_PASS],
    # TODO: put these two in a region?
    NPCRewardName.TILE_IN_CHILDS_SECRET_CAVE: [NPCName.BOY_CAVE, ItemName.APASS],
    NPCRewardName.RECOVERY_SWORD_CRYSTAL: [NPCName.IVY_RECOVERY_SWORD, NPCName.BOY_CAVE, ItemName.APASS],
    NPCRewardName.VILLAGE_CHIEF: [NPCName.VILLAGE_CHIEF, NPCName.OLD_WOMAN],
    #NPCRewardName.MAGICIAN: [],  # TODO: delete
    # TODO: put this and two chests into region and delete.
    #NPCRewardName.GRASS_VALLEY_SECRET_ROOM_CRYSTAL: [NPCName.IVY_CHEST_ROOM],
    #NPCRewardName.UNDERGROUND_CASTLE_CRYSTAL: [],  # TODO: delete
    # Act 2 - Greenwood
    NPCRewardName.REDHOT_MIRROR_BIRD: [NPCName.BIRD_RED_HOT_MIRROR],
    NPCRewardName.MAGIC_BELL_CRYSTAL: [*emblems_table.keys(), NPCName.DEER_MAGIC_BELL, NPCName.CROCODILE3],
    NPCRewardName.WOODSTIN_TRIO: [NPCName.DEER, NPCName.SQUIRREL3, NPCName.DOG3],
    NPCRewardName.GREENWOODS_GUARDIAN: [],  # TODO: delete
    NPCRewardName.GREENWOOD_LEAVES_TILE: [
        NPCName.MOLE_SOUL_OF_LIGHT,
        NPCName.CROCODILE,
        NPCName.CROCODILE2,
        NPCName.BIRD_GREENWOOD_LEAF,
        ItemName.DREAMROD,
    ],
    NPCRewardName.SHIELD_BRACELET_MOLE: [NPCName.MOLE, NPCName.MOLE_SHIELD_BRACELET, ItemName.MOLESRIBBON],
    NPCRewardName.PSYCHO_SWORD_SQUIRREL: [NPCName.SQUIRREL_PSYCHO_SWORD, ItemName.DELICIOUSSEEDS],
    NPCRewardName.EMBLEM_C_SQUIRREL: [NPCName.SQUIRREL_EMBLEM_C, NPCName.SQUIRREL_PSYCHO_SWORD],
    NPCRewardName.WATER_SHRINE_TILE: [],  # TODO: delete
    NPCRewardName.LIGHT_ARROW_CRYSTAL: [],  # TODO: delete
    NPCRewardName.LOST_MARSH_CRYSTAL: [],  # TODO: delete
    NPCRewardName.WATER_SHRINE_CRYSTAL: [],  # TODO: delete
    NPCRewardName.FIRE_SHRINE_CRYSTAL: [],  # TODO: delete
    ChestName.GREENWOOD_ICE_ARMOR: [NPCName.MOLE, NPCName.SQUIRREL_ICE_ARMOR, ItemName.DREAMROD],
    # Act 3 - St Elles
    # Notes:
    # Mermaid 4: unlocks path to West Seabed Sanctuary (make region?)
    # Dolphin 2: unlocks path to east seabed sanctuary (make region?)
    # Bubble Armor mermaid: unlocks path to south seabed sanctuary
    NPCRewardName.NORTHEASTERN_MERMAID_HERB: [NPCName.MERMAID, NPCName.DOLPHIN2],
    NPCRewardName.BUBBLE_ARMOR_MERMAID: [],  # TODO: delete
    NPCRewardName.MAGIC_FLARE_MERMAID: [NPCName.MERMAID_MAGIC_FLARE, NPCName.MERMAID_BUBBLE_ARMOR],
    NPCRewardName.MERMAID_QUEEN: [],  # TODO: delete
    NPCRewardName.REDHOT_STICK_MERMAID: [NPCName.MERMAID_BUBBLE_ARMOR],
    # TODO: Lue also needs 1 of Bubble mermaid or Dolphin 4. gonna need regions for those
    # MERMAID_PEARL should probably be a region too. gonna need to to do a little mapping
    NPCRewardName.LUE: [NPCName.LUE, NPCName.DOLPHIN_SAVES_LUE, NPCName.MERMAID_PEARL],
    NPCRewardName.ROCKBIRD_CRYSTAL: [],
    NPCRewardName.SEABED_CRYSTAL_NEAR_BLESTER: [],
    NPCRewardName.SEABED_CRYSTAL_NEAR_DUREAN: [],
    # Act 4 - Mountain of Souls
    # TODO: Delete these once they are no longer useful.
    LairID.DOG3: [LairID.DEER],
    LairID.SQUIRREL3: [LairID.DEER],
    LairID.DOLPHIN: [LairID.MERMAID_NANA],
    LairID.ANGELFISH: [LairID.ANGELFISH_SOUL_OF_SHIELD],
    LairID.MERMAID2: [LairID.MERMAID4],
    LairID.MERMAID_RED_HOT_STICK: [LairID.MERMAID_BUBBLE_ARMOR],
    LairID.MERMAID6: [LairID.MERMAID4],
    LairID.MERMAID_TEARS: [LairID.MERMAID_BUBBLE_ARMOR],
    LairID.MERMAID_MAGIC_FLARE: [LairID.MERMAID_BUBBLE_ARMOR],
    LairID.ANGELFISH4: [LairID.MERMAID5],
    LairID.MERMAID8: [LairID.MERMAID_BUBBLE_ARMOR],
    LairID.MERMAID9: [LairID.MERMAID4],
    LairID.NOME: [LairID.GRANDPA5],
    LairID.BOY2: [LairID.GRANDPA5],
    LairID.MUSHROOM_EMBLEM_F: [LairID.GRANDPA5],
    LairID.GRANDMA: [LairID.GRANDPA2],
    LairID.GIRL2: [LairID.BOY],
    LairID.SNAIL: [LairID.BOY_MUSHROOM_SHOES],
    LairID.SNAIL2: [LairID.GRANDPA4],
    LairID.SOLDIER6: [LairID.SINGER_CONCERT_HALL],
    LairID.SOLDIER_PLATINUM_CARD: [LairID.SINGER_CONCERT_HALL],
    LairID.MAID2: [LairID.SINGER_CONCERT_HALL],
    LairID.SOLDIER7: [LairID.MAID],
    LairID.SOLDIER8: [LairID.SOLDIER_SOUL_OF_REALITY],
    LairID.SOLDIER10: [LairID.MAID_HERB],
    LairID.KING_MAGRIDD: [LairID.SOLDIER_CASTLE],
}


def get_rule_for_location(name: str, player: int, flag: RuleFlag) -> Callable[[CollectionState], bool]:
    """Returns the access rule for the given location."""

    def rule(state: CollectionState) -> bool:
        return rule_for_flag[flag](state, player) and state.has_all(location_dependencies.get(name, []), player)

    return rule


def set_rules(world: "SoulBlazerWorld") -> None:
    # TODO: Replace "Test" with Deathtoll's Palace Region name?
    world.multiworld.get_region("Test", world.player).locations += world.create_victory_event()
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)


# TODO: access rule for region/entrance