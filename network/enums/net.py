class SpecialDetections:
    def __init__(self) -> None:
        self.DisallowD3d9 = 12
        self.DisallowVM = 14
        self.DisallowedDisabledDriverSign = 15
        self.DisasllowDisableAntiCheat = 16
        self.DisallowNonStandardGta3 = 20
        self.DisallowResourceScriptDownloadErrors = 22
        self.DisallowResourceFileDownloadErrors = 23
        self.DisallowWine = 28
        self.IgnoreInjectedKeyboardInput = 31
        self.IgnoreInjectedMouseInput = 32
        self.DisallowNetLimiters = 33
        self.DisallowInternetCafe = 34
        self.DisallowFpsLockers = 35
        self.DisallowAutoHotKey = 36

class WrapperErrors:
    def __init__(self) -> None:
        self.Success = 0
        self.UnableToLoadDll = -1001
        self.IncompatibilityCheckUnavailable = -1002
        self.IsIncompatible = -1003
        self.InterfaceUnavailable = -1004
        self.UnableToInit = -1005
        self.UnableToStart = -1006

class FileData:
    def __init__(self) -> None:
        self.Null = 0
        self.carmodsDat = 0x01
        self.animgrpDat = 0x02
        self.handlingCfg = 0x04
        self.ar_statsDat = 0x08
        self.meleeDat = 0x10
        self.clothesDat = 0x20
        self.objectDat = 0x40
        self.defaultDat = 0x80
        self.surfaceDat = 0x100
        self.defaultIde = 0x200
        self.gtaDat = 0x400
        self.surfinfoDat = 0x800
        self.pedsIde = 0x1000
        self.vehiclesIde = 0x2000
        self.pedstatsDat = 0x4000
        self.waterDat = 0x8000
        self.txdcutIde = 0x10000
        self.water1Dat = 0x20000
        self.weaponsCol = 0x40000
        self.weaponDat = 0x80000
        self.plantsDat = 0x100000
        self.pedIfp = 0x200000
        self.furniturDat = 0x400000
        self.procobjDat = 0x800000
        self.maps = 0x1000000
        self.timecycDat = 0x2000000

class AntiCheat:
    def __init__(self) -> None:
        self.Null = 0
        self.HealthArmourHackAC1 = 1
        self.CorruptedDllAC2 = 2
        self.TrainerAC4 = 4
        self.TrainerAC5 = 5
        self.TrainerVF6 = 6
        self.TrainerVF7 = 7
        self.UnauthorizedModVF8 = 8
        self.TrainersAC11 = 11
        self.DataFileSD13 = 13
        self.SpeedHackVF17 = 17
        self.TrainersAC21 = 21
        self.AntiCheatBlockSD26 = 26

class AllowGta3ImgMods:
    def __init__(self) -> None:
        self.Peds = 'Peds'
        self.Null = 'None'
