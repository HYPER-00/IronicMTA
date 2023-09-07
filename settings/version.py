from typing import TypedDict


class VersionSettings(TypedDict):
    minclientversion: str
    minclientversion_auto_update: int
    recommendedclientversion: str
    
    