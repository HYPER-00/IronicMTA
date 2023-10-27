from typing import TypedDict, List


class AntiCheatSettings(TypedDict):
    disabled_ac: List[int]
    enabled_sd: List[int]
