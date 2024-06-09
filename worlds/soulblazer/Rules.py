from typing import Dict, List, Callable, Optional, TYPE_CHECKING, Iterable
from dataclasses import dataclass, field
from enum import IntEnum, auto
from BaseClasses import CollectionState
from worlds.AutoWorld import World
from .Names import (
    ItemName,
    ItemID,
    LairName,
    LairID,
    ChestName,
    ChestID,
    NPCRewardName,
    NPCRewardID,
    NPCName,
    RegionName,
)
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
    Requires a way to damage metal enemies in the presence of thunder pyramids
    (Thunder Ring|Zantestu Sword|Soul Blade).
    """
    HAS_MAGIC = auto()
    """Requires a way to damage enemies outside of sword range."""
    HAS_SWORD = auto()
    """
    Requires any sword. Only used as a sanity check at the start of the game
    since we prefill the first chest with a sword.
    """
    HAS_STONES = auto()
    """Requires the necessary number of stones. Adjustable via option."""
    PHOENIX_CUTSCENE = auto()
    """
    Requires the Phoenix cutscene:
    Access to the Mountain King
    Both Dancing Grandmas
    The 3 Red-Hot Items
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


def no_requirement(state: CollectionState, player: Optional[int] = None) -> bool:
    return True


def can_cut_metal(state: CollectionState, player: int) -> bool:
    return state.has_any(metal_items, player)


def can_cut_spirit(state: CollectionState, player: int) -> bool:
    return state.has_any(spirit_items, player)


def has_thunder(state: CollectionState, player: int) -> bool:
    return state.has_any(thunder_items, player)


def has_magic(state: CollectionState, player: int) -> bool:
    return state.has(ItemName.SOUL_MAGICIAN, player) and state.has_any(magic_items, player)


def has_sword(state: CollectionState, player: int) -> bool:
    return state.has_any(sword_items, player)


def has_stones(state: CollectionState, player: int) -> bool:
    count: int = state.multiworld.worlds[player].options.stones_count.value
    return state.has_group("stones", player, count)


def has_phoenix_cutscene(state: CollectionState, player: int) -> bool:
    return state.can_reach_location(NPCRewardName.MOUNTAIN_KING, player)


rule_for_flag = {
    RuleFlag.NONE: no_requirement,
    RuleFlag.CAN_CUT_METAL: can_cut_metal,
    RuleFlag.CAN_CUT_SPIRIT: can_cut_spirit,
    RuleFlag.HAS_THUNDER: has_thunder,
    RuleFlag.HAS_MAGIC: has_magic,
    RuleFlag.HAS_SWORD: has_sword,
    RuleFlag.HAS_STONES: has_stones,
    RuleFlag.PHOENIX_CUTSCENE: has_phoenix_cutscene,
}


@dataclass(frozen=True)
class RuleData:
    """Baseclass used for defining location/exit access rules."""

    next: Optional["RuleData"] = None
    """Used for chaining rules together. Combined with logical and."""

    def get_rule(self, player: int) -> Callable[[CollectionState], bool]:
        """Returns the access rule defined by this RuleData."""
        if self.next is not None:
            next_rule = self.next.get_rule(player)

            def rule(state: CollectionState) -> bool:
                return True and next_rule(state)

        else:

            def rule(state: CollectionState) -> bool:
                return True

        return rule


@dataclass(frozen=True)
class FlagRuleData(RuleData):
    """Rule defined by a RuleFlag."""

    flag: RuleFlag = RuleFlag.NONE

    def get_rule(self, player: int) -> Callable[[CollectionState], bool]:
        """Returns the access rule defined by this RuleData."""
        flag_rule = rule_for_flag[self.flag]
        if self.next is not None:
            next_rule = self.next.get_rule(player)

            def rule(state: CollectionState) -> bool:
                return flag_rule(state, player) and next_rule(state)

        else:

            def rule(state: CollectionState) -> bool:
                return flag_rule(state, player)

        return rule


@dataclass(frozen=True)
class HasAnyRuleData(RuleData):
    """Access rule for if you have any of a given list of items."""

    items: Iterable[str] = field(default_factory=list)
    """Must have at least one of items collected for rule to return true."""

    def get_rule(self, player: int) -> Callable[[CollectionState], bool]:
        """Returns the access rule defined by this RuleData."""
        if self.next is not None:
            next_rule = self.next.get_rule(player)

            def rule(state: CollectionState) -> bool:
                return state.has_any(self.items, player) and next_rule(state)

        else:

            def rule(state: CollectionState) -> bool:
                return state.has_any(self.items, player)

        return rule


@dataclass(frozen=True)
class HasAllRuleData(RuleData):
    """Access rule for if you have all of a given list of items."""

    items: Iterable[str] = field(default_factory=list)
    """Must have all items collected for rule to return true."""

    def get_rule(self, player: int) -> Callable[[CollectionState], bool]:
        """Returns the access rule defined by this RuleData."""
        if self.next is not None:
            next_rule = self.next.get_rule(player)

            def rule(state: CollectionState) -> bool:
                return state.has_all(self.items, player) and next_rule(state)

        else:

            def rule(state: CollectionState) -> bool:
                return state.has_all(self.items, player)

        return rule


@dataclass(frozen=True)
class CanReachLocationRuleData(RuleData):
    """Access rule for if you can reach a given location."""

    spot: str = ""
    """Location name to reach."""

    def get_rule(self, player: int) -> Callable[[CollectionState], bool]:
        """Returns the access rule defined by this RuleData."""

        if self.next is not None:
            next_rule = self.next.get_rule(player)

            def rule(state: CollectionState) -> bool:
                return state.can_reach_location(self.spot, player) and next_rule(state)

        else:

            def rule(state: CollectionState) -> bool:
                return state.can_reach_location(self.spot, player)

        return rule


@dataclass(frozen=True)
class CanReachRegionRule(RuleData):
    """Access rule for if you can reach a given region."""

    spot: str = ""
    """Region name to reach."""

    def get_rule(self, player: int) -> Callable[[CollectionState], bool]:
        """Returns the access rule defined by this RuleData."""

        if self.next is not None:
            next_rule = self.next.get_rule(player)

            def rule(state: CollectionState) -> bool:
                return state.can_reach_region(self.spot, player) and next_rule(state)

        else:

            def rule(state: CollectionState) -> bool:
                return state.can_reach_region(self.spot, player)

        return rule


# Many locations depend on one or two NPC releases so rather than create regions to hold one location,
# we put these location-specific dependencies here.
location_dependencies: Dict[str, RuleData] = {
    # Act 1 - Grass Valley
    NPCRewardName.TOOL_SHOP_OWNER: HasAllRuleData(items=[NPCName.TOOL_SHOP_OWNER]),
    NPCRewardName.EMBLEM_A_TILE: HasAllRuleData(items=[NPCName.IVY, NPCName.IVY_EMBLEM_A]),
    NPCRewardName.GOAT_PEN_CORNER: HasAllRuleData(items=[NPCName.GOAT_HERB]),
    NPCRewardName.TEDDY: HasAllRuleData(items=[NPCName.TOOL_SHOP_OWNER, NPCName.TEDDY]),
    NPCRewardName.PASS_TILE: HasAllRuleData(items=[NPCName.IVY, NPCName.TULIP_PASS]),
    NPCRewardName.TILE_IN_CHILDS_SECRET_CAVE: HasAllRuleData(items=[NPCName.BOY_CAVE, ItemName.APASS]),
    NPCRewardName.RECOVERY_SWORD_CRYSTAL: HasAllRuleData(
        items=[NPCName.IVY_RECOVERY_SWORD, NPCName.BOY_CAVE, ItemName.APASS]
    ),
    NPCRewardName.VILLAGE_CHIEF: HasAllRuleData(items=[NPCName.VILLAGE_CHIEF, NPCName.OLD_WOMAN]),
    NPCRewardName.MAGICIAN: FlagRuleData(flag=RuleFlag.HAS_SWORD),
    NPCRewardName.MAGICIAN_SOUL: FlagRuleData(flag=RuleFlag.HAS_SWORD),
    LairName.OLD_MAN: HasAllRuleData(items=[NPCName.LISA, ItemName.DREAMROD]),
    LairName.IVY_EMBLEM_A: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.IVY_RECOVERY_SWORD: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    ChestName.UNDERGROUND_CASTLE_LEOS_BRUSH: HasAllRuleData(items=[NPCName.LISA, ItemName.DREAMROD]),
    ChestName.LEOS_PAINTING_TORNADO: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    # Act 2 - Greenwood
    NPCRewardName.REDHOT_MIRROR_BIRD: HasAllRuleData(items=[NPCName.BIRD_RED_HOT_MIRROR]),
    NPCRewardName.MAGIC_BELL_CRYSTAL: HasAllRuleData(
        items=[*emblems_table.keys(), NPCName.DEER_MAGIC_BELL, NPCName.CROCODILE3]
    ),
    NPCRewardName.WOODSTIN_TRIO: HasAllRuleData(items=[NPCName.DEER, NPCName.SQUIRREL3, NPCName.DOG3]),
    NPCRewardName.GREENWOOD_LEAVES_TILE: HasAllRuleData(
        items=[
            NPCName.MOLE_SOUL_OF_LIGHT,
            NPCName.CROCODILE,
            NPCName.CROCODILE2,
            NPCName.BIRD_GREENWOOD_LEAF,
            ItemName.DREAMROD,
        ]
    ),
    NPCRewardName.SHIELD_BRACELET_MOLE: HasAllRuleData(
        items=[NPCName.MOLE, NPCName.MOLE_SHIELD_BRACELET, ItemName.MOLESRIBBON]
    ),
    NPCRewardName.PSYCHO_SWORD_SQUIRREL: HasAllRuleData(items=[NPCName.SQUIRREL_PSYCHO_SWORD, ItemName.DELICIOUSSEEDS]),
    NPCRewardName.EMBLEM_C_SQUIRREL: HasAllRuleData(items=[NPCName.SQUIRREL_EMBLEM_C, NPCName.SQUIRREL_PSYCHO_SWORD]),
    NPCRewardName.GREENWOODS_GUARDIAN: HasAllRuleData(items=[NPCName.GREENWOODS_GUARDIAN]),
    NPCRewardName.FIRE_SHRINE_CRYSTAL: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    NPCRewardName.MOLE_SOUL_OF_LIGHT: HasAllRuleData(items=[NPCName.MOLE_SOUL_OF_LIGHT]),
    LairName.BIRD_RED_HOT_MIRROR: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.BIRD3: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    ChestName.GREENWOOD_ICE_ARMOR: HasAllRuleData(items=[NPCName.MOLE, NPCName.SQUIRREL_ICE_ARMOR, ItemName.DREAMROD]),
    ChestName.GREENWOOD_TUNNELS: HasAllRuleData(items=[NPCName.MONMO, NPCName.MOLE3]),
    ChestName.FIRE_SHRINE_2_SCORPION: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    ChestName.LIGHT_SHRINE: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    # Act 3 - St Elles
    NPCRewardName.NORTHEASTERN_MERMAID_HERB: HasAllRuleData(items=[NPCName.MERMAID, NPCName.DOLPHIN2]),
    NPCRewardName.MAGIC_FLARE_MERMAID: HasAllRuleData(
        items=[NPCName.MERMAID_MAGIC_FLARE, NPCName.MERMAID_BUBBLE_ARMOR]
    ),
    NPCRewardName.REDHOT_STICK_MERMAID: HasAllRuleData(items=[NPCName.MERMAID_RED_HOT_STICK]),
    NPCRewardName.LUE: HasAllRuleData(items=[NPCName.LUE, NPCName.DOLPHIN_SAVES_LUE, NPCName.MERMAID_PEARL]),
    NPCRewardName.MERMAID_QUEEN: HasAllRuleData(items=[NPCName.MERMAID_QUEEN]),
    NPCRewardName.ANGELFISH_SOUL_OF_SHIELD: HasAllRuleData(items=[NPCName.ANGELFISH_SOUL_OF_SHIELD]),
    LairName.MERMAID_RED_HOT_STICK: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.MERMAID3: HasAllRuleData(items=[ItemName.MERMAIDSTEARS]),
    LairName.MERMAID_STATUE_BLESTER: HasAllRuleData(items=[ItemName.MERMAIDSTEARS]),
    LairName.MERMAID_STATUE_GHOST_SHIP: FlagRuleData(flag=RuleFlag.HAS_THUNDER),
    ChestName.DUREAN_CRITICAL_SWORD: HasAllRuleData(items=[ItemName.MERMAIDSTEARS]),
    # Act 4 - Mountain of Souls
    NPCRewardName.MOUNTAIN_KING: HasAllRuleData(
        items=[
            NPCName.DANCING_GRANDMA,
            NPCName.DANCING_GRANDMA2,
            ItemName.REDHOTBALL,
            ItemName.REDHOTMIRROR,
            ItemName.REDHOTSTICK,
        ]
    ),
    NPCRewardName.MUSHROOM_SHOES_BOY: HasAllRuleData(items=[NPCName.BOY_MUSHROOM_SHOES]),
    NPCRewardName.EMBLEM_E_SNAIL: HasAllRuleData(items=[NPCName.SNAIL_EMBLEM_E]),
    # Also includes path from lune to sleeping mushroom for the two locations locked behind mushroom's dream.
    NPCRewardName.EMBLEM_F_TILE: HasAllRuleData(
        items=[NPCName.MUSHROOM_EMBLEM_F, NPCName.GRANDPA5, NPCName.MUSHROOM2, ItemName.DREAMROD]
    ),
    LairName.SNAIL_EMBLEM_E: HasAllRuleData(
        items=[NPCName.MUSHROOM_EMBLEM_F, NPCName.GRANDPA5, NPCName.MUSHROOM2, ItemName.DREAMROD]
    ),
    # Act 5 - Leo's Lab
    NPCRewardName.EMBLEM_G_UNDER_CHEST_OF_DRAWERS: HasAllRuleData(
        items=[
            NPCName.CHEST_OF_DRAWERS_MYSTIC_ARMOR,
            NPCName.GREAT_DOOR,
            ItemName.DOORKEY,
        ]
    ),
    NPCRewardName.CHEST_OF_DRAWERS_MYSTIC_ARMOR: HasAllRuleData(
        items=[
            NPCName.CHEST_OF_DRAWERS_MYSTIC_ARMOR,
            NPCName.GREAT_DOOR,
            ItemName.DOORKEY,
        ]
    ),
    NPCRewardName.HERB_PLANT_IN_LEOS_LAB: HasAllRuleData(
        items=[
            NPCName.PLANT_HERB,
            NPCName.MOUSE,
            NPCName.CAT,
            NPCName.CAT2,
            ItemName.ACTINIDIALEAVES,
        ]
    ),
    NPCRewardName.SPARK_BOMB_MOUSE: HasAllRuleData(
        items=[
            NPCName.MOUSE_SPARK_BOMB,
            NPCName.MOUSE,
            NPCName.CAT,
            NPCName.CAT2,
            ItemName.ACTINIDIALEAVES,
        ]
    ),
    NPCRewardName.LEOS_CAT_DOOR_KEY: HasAllRuleData(items=[NPCName.CAT_DOOR_KEY, ItemName.DREAMROD]),
    NPCRewardName.ACTINIDIA_PLANT: HasAllRuleData(items=[NPCName.PLANT_ACTINIDIA_LEAVES]),
    NPCRewardName.CHEST_OF_DRAWERS_HERB: HasAllRuleData(items=[NPCName.CHEST_OF_DRAWERS2]),
    NPCRewardName.MARIE: HasAllRuleData(items=[NPCName.MARIE]),
    # Potentially optional icearmor requirement.
    NPCRewardName.POWER_PLANT_CRYSTAL: HasAllRuleData(
        items=[ItemName.ICEARMOR], next=FlagRuleData(flag=RuleFlag.CAN_CUT_METAL)
    ),
    NPCRewardName.GREAT_DOOR_SOUL_OF_DETECTION: HasAllRuleData(items=[NPCName.GREAT_DOOR_SOUL_OF_DETECTION]),
    LairName.PLANT_HERB: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.CHEST_OF_DRAWERS_MYSTIC_ARMOR: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.CAT2: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.GREAT_DOOR: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.GREAT_DOOR_MODEL_TOWNS: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.STEPS_UPSTAIRS: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.MOUSE: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    LairName.DOLL: HasAllRuleData(items=[ItemName.ICEARMOR], next=FlagRuleData(flag=RuleFlag.CAN_CUT_METAL)),
    LairName.MARIE: HasAllRuleData(items=[ItemName.ICEARMOR], next=FlagRuleData(flag=RuleFlag.CAN_CUT_METAL)),
    LairName.MOUSE_SPARK_BOMB: FlagRuleData(flag=RuleFlag.HAS_MAGIC),
    LairName.MOUSE3: FlagRuleData(flag=RuleFlag.HAS_MAGIC),
    LairName.MODEL_TOWN2: FlagRuleData(flag=RuleFlag.HAS_MAGIC),
    LairName.MOUSE4: FlagRuleData(flag=RuleFlag.HAS_MAGIC),
    LairName.STEPS_MARIE: FlagRuleData(flag=RuleFlag.HAS_MAGIC),
    ChestName.POWER_PLANT_LIGHT_ARMOR: FlagRuleData(flag=RuleFlag.CAN_CUT_METAL),
    # Act 6 - Magridd Castle
    NPCRewardName.ELEMENTAL_MAIL_SOLDIER: HasAllRuleData(items=[NPCName.SOLDIER_ELEMENTAL_MAIL, ItemName.DREAMROD]),
    NPCRewardName.SUPER_BRACELET_TILE: HasAllRuleData(
        items=[
            NPCName.DR_LEO,
            NPCName.SOLDIER_WITH_LEO,
            NPCName.SOLDIER_DOK,
            NPCName.QUEEN_MAGRIDD,
        ]
    ),
    NPCRewardName.QUEEN_MAGRIDD_VIP_CARD: HasAllRuleData(items=[NPCName.QUEEN_MAGRIDD]),
    NPCRewardName.PLATINUM_CARD_SOLDIER: HasAllRuleData(
        items=[
            NPCName.SOLDIER_PLATINUM_CARD,
            NPCName.SINGER_CONCERT_HALL,
            ItemName.HARPSTRING,
        ]
    ),
    NPCRewardName.MAID_HERB: HasAllRuleData(items=[NPCName.MAID_HERB]),
    NPCRewardName.EMBLEM_H_TILE: HasAllRuleData(items=[NPCName.SOLDIER_CASTLE]),
    NPCRewardName.KING_MAGRIDD: HasAllRuleData(items=[NPCName.KING_MAGRIDD, NPCName.SOLDIER_CASTLE]),
    NPCRewardName.SOLDIER_SOUL_OF_REALITY: HasAllRuleData(items=[NPCName.SOLDIER_SOUL_OF_REALITY]),
    LairName.SOLDIER2: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.SOLDIER3: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.SOLDIER_ELEMENTAL_MAIL: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.SOLDIER4: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.SINGER_CONCERT_HALL: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.MAID: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.SOLDIER_PLATINUM_CARD: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.SINGER: FlagRuleData(flag=RuleFlag.CAN_CUT_SPIRIT),
    LairName.KING_MAGRIDD: HasAllRuleData(items=[ItemName.AIRSHIPKEY]),
    # Act 7 - World of Evil
    ChestName.WOE_1_SE: FlagRuleData(flag=RuleFlag.HAS_MAGIC),
    ChestName.WOE_1_SW: FlagRuleData(flag=RuleFlag.HAS_MAGIC),
    ChestName.WOE_1_REDHOT_BALL: FlagRuleData(flag=RuleFlag.HAS_MAGIC),
    ChestName.DAZZLING_SPACE_SE: HasAllRuleData(items=[ItemName.SOULARMOR]),
    ChestName.DAZZLING_SPACE_SW: HasAllRuleData(items=[ItemName.SOULARMOR]),
}


def get_rule_for_location(name: str, player: int) -> Callable[[CollectionState], bool]:
    """Returns the access rule for the given location."""

    return location_dependencies.get(name, RuleData()).get_rule(player)


# def set_rules(world: "SoulBlazerWorld") -> None:
#    # TODO: Cant create locations during rule generation.
#    # AssertionError: 295 != 296 : Soul Blazer modified locations count during rule creation
#    region = world.multiworld.get_region(RegionName.DEATHTOLL, world.player)
#    region.locations.append(world.create_victory_event(region))
#    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)
