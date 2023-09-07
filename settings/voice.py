from typing import TypedDict


class VoiceSettings(TypedDict):
    enabled: bool
    voice_samplerate: int
    voice_quality: int
