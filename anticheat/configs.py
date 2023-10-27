"""MTA Client Anticheat Configs"""

from enum import Enum


class AntiCheatConfigs(Enum):
    """MTA:SA Client Anticheat Configurations"""

    class SpecialDetection(Enum):
        """MTA:SA Client Special Detection Anticheat (AKA: SD)"""

        NONE = 0
        DISALLLOW_D3D = 12
        DISALLLOW_VM = 14
        DISALLLOW_DISABLED_DRIVER_SIGN = 15
        DISALLOW_DISABLE_ANTICHEAT = 16
        DISALOW_NON_STANDARD_GTA3 = 20
        DISALLOW_RESOURCE_SCRIPT_DOWNLOAD_ERRORS = 22
        DISALLOW_RESOURCE_FILE_DOWNLOAD_ERRORS = 23
        DISALLOW_WINE = 28
        IGNORE_INJECTED_BY_KEYBOARD_INPUT = 31
        IGNORE_INJECTED_BY_MOUSE_INPUT = 32
        DISALLOW_NET_LIMITERS = 33
        DISALLOW_INTERNET_CAFE = 34
        DISALLOW_FPS_LOCKERS = 35
        DISALLOW_AUTOHOTKEY = 36

    class AllowGta3ImgMods(Enum):
        PEDS = 0
        NONE = 1

    class MTAAntiCheat(Enum):
        """MTA Client Anticheat Configurations (AKA: AC)"""

        NONE = 0
        HEALTH_ARMOUR_HACK_AC1 = 1
        CORRUPTED_DLL_AC2 = 2
        TRAINER_AC4 = 4
        TRAINER_AC5 = 5
        TRAINER_VF6 = 6
        TRAINER_VF7 = 7
        UNAUTHORIZED_MOD_VF8 = 8
        TRAINERS_AC11 = 11
        DATA_FILE_SD13 = 13
        SPEED_HACK_VF17 = 17
        TRAINER_AC21 = 21
        ANTICHEAT_BLOCK_SD26 = 26

    class DataFile(Enum):
        NONE = 0
        CAR_MODS_DAT = 0x01
        ANIM_GROUP_DAT = 0x02
        HANDLING_CFG = 0x04
        AR_STATS_DAT = 0x08
        MELEE_DAT = 0x10
        CLOTHES_DAT = 0x20
        OBJECT_DAT = 0x40
        DEFAULT_DAT = 0x80
        SURFACE_DAT = 0x100
        DEFAULT_IDE = 0x200
        GTA_DAT = 0x400
        SURFACE_INFO_DAT = 0x800
        PEDS_IDE = 0x1000
        VEHICLE_IDE = 0x2000
        PEDS_STATS_DAT = 0x4000
        WATER_DAT = 0x8000
        TXD_CUT_IDE = 0x10000
        WATER_1_DAT = 0x20000
        WEAPONS_COL = 0x40000
        WEAPONS_DAT = 0x80000
        PLANTS_DAT = 0x100000
        PED_IFP = 0x200000
        FURNITURE_DAT = 0x400000
        PROC_OBJ_DAT = 0x800000
        MAPS = 0x1000000
