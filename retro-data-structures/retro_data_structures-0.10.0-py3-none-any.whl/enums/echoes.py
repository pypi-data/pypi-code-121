"""
Generated file.
"""
from enum import Enum


class States(Enum):
    NonZero = '!ZER'
    Active = 'ACTV'
    AILogicState1 = 'AIS1'
    AILogicState2 = 'AIS2'
    AILogicState3 = 'AIS3'
    Approach = 'APRC'
    Arrived = 'ARRV'
    AttachedCollisionObject = 'ATCL'
    AttachedAnimatedObject = 'ATOB'
    Attack = 'ATTK'
    BallIceXDamage = 'BIDG'
    BallXDamage = 'BXDG'
    Closed = 'CLOS'
    Connect = 'CONN'
    CPLR = 'CPLR'
    CameraPath = 'CPTH'
    CameraTarget = 'CTGT'
    CameraTime = 'CTIM'
    Damage = 'DAMG'
    DamageAnnihilator = 'DANN'
    DBAI = 'DBAI'
    DBAL = 'DBAL'
    DBMB = 'DBMB'
    DCAN = 'DCAN'
    DamageDark = 'DDRK'
    Dead = 'DEAD'
    DFST = 'DFST'
    DeGenerate = 'DGNR'
    DamageLight = 'DLGT'
    DMIS = 'DMIS'
    DPBM = 'DPBM'
    DPHZ = 'DPHZ'
    DamagePower = 'DPWR'
    DarkXDamage = 'DRKX'
    DSCW = 'DSCW'
    Entered = 'ENTR'
    Exited = 'EXIT'
    Footstep = 'FOOT'
    Freeze = 'FREZ'
    Generate = 'GRNT'
    InheritBounds = 'IBND'
    Inactive = 'ICTV'
    IceXDamage = 'IDMG'
    Inside = 'INSD'
    InternalState00 = 'IS00'
    InternalState01 = 'IS01'
    InternalState02 = 'IS02'
    InternalState03 = 'IS03'
    InternalState04 = 'IS04'
    InternalState05 = 'IS05'
    InternalState06 = 'IS06'
    InternalState07 = 'IS07'
    InternalState08 = 'IS08'
    InternalState09 = 'IS09'
    InternalState10 = 'IS10'
    InternalState11 = 'IS11'
    InternalState12 = 'IS12'
    InternalState13 = 'IS13'
    InternalState14 = 'IS14'
    InternalState15 = 'IS15'
    InternalState16 = 'IS16'
    InternalState17 = 'IS17'
    InternalState18 = 'IS18'
    InternalState19 = 'IS19'
    Left = 'LEFT'
    MaxReached = 'MAXR'
    Modify = 'MDFY'
    Open = 'OPEN'
    Play = 'PLAY'
    PressA = 'PRSA'
    PressB = 'PRSB'
    PressStart = 'PRST'
    PressX = 'PRSX'
    PressY = 'PRSY'
    PressZ = 'PRSZ'
    Patrol = 'PTRL'
    DeathRattle = 'RATL'
    SpawnResidue = 'RDUE'
    ReflectedDamage = 'REFD'
    ResistedDamage = 'RESD'
    Right = 'RGHT'
    Retreat = 'RTRT'
    ScanDone = 'SCND'
    ScanSource = 'SCNS'
    Sequence = 'SQNC'
    UnFreeze = 'UFRZ'
    Up = 'UP  '
    XDamage = 'XDMG'
    InBack = 'XINB'
    InFront = 'XINF'
    Zero = 'ZERO'


class Messages(Enum):
    Action = 'ACTN'
    Activate = 'ACTV'
    Alert = 'ALRT'
    Arrive = 'ARRV'
    Attach = 'ATCH'
    Close = 'CLOS'
    ClearOriginator = 'CORG'
    Deactivate = 'DCTV'
    Decrement = 'DECR'
    Escape = 'ESCP'
    Follow = 'FOLW'
    InternalMessage00 = 'IM00'
    InternalMessage01 = 'IM01'
    InternalMessage02 = 'IM02'
    InternalMessage03 = 'IM03'
    InternalMessage04 = 'IM04'
    InternalMessage05 = 'IM05'
    InternalMessage06 = 'IM06'
    InternalMessage07 = 'IM07'
    InternalMessage08 = 'IM08'
    InternalMessage09 = 'IM09'
    InternalMessage10 = 'IM10'
    InternalMessage11 = 'IM11'
    InternalMessage12 = 'IM12'
    InternalMessage13 = 'IM13'
    InternalMessage14 = 'IM14'
    Increment = 'INCR'
    Kill = 'KILL'
    Left = 'LEFT'
    Load = 'LOAD'
    Lock = 'LOCK'
    Next = 'NEXT'
    Open = 'OPEN'
    Play = 'PLAY'
    Reset = 'RSET'
    ResetAndStart = 'RSTS'
    SetToMax = 'SMAX'
    SetOriginator = 'SORG'
    Stop = 'STOP'
    StopAndReset = 'STPR'
    Start = 'STRT'
    ToggleActive = 'TCTV'
    Unlock = 'ULCK'
    Unload = 'ULOD'
    Clear = 'XCLR'
    Delete = 'XDEL'
    XDamage = 'XDMG'
    SetToZero = 'ZERO'


class FilterShape(Enum):
    FullScreen = 0
    FullScreenHalvesLeftRight = 1
    FullScreenHalvesTopBottom = 2
    FullScreenQuarters = 3
    CinemaBars = 4
    ScanLinesEven = 5
    ScanLinesOdd = 6
    RandomStatic = 7
    DialogBox = 8
    CinematicPlaceholderLabel = 9
    CookieCutterDepthRandomStatic = 10


class EnvironmentEffects(Enum):
    _None = 0
    Snow = 1
    Rain = 2
    Bubbles = 3
    DarkWorld = 4
    Aerie = 5
    ElectricRain = 6


class PhazonDamage(Enum):
    _None = 0
    Blue = 1
    Orange = 2


class Function(Enum):
    What = 0
    PlayerFollowLocator = 1
    SpinnerControllerUnused = 2
    ObjectFollowLocator = 3
    Function4Unused = 4
    InventoryActivator = 5
    MapStation = 6
    SaveStationCheckpoint = 7
    IntroBossRingControllerUnused = 8
    ViewFrustumTester = 9
    ShotSpinnerControllerUnused = 10
    EscapeSequence = 11
    BossEnergyBar = 12
    EndGame = 13
    HUDFadeInUnused = 14
    CinematicSkip = 15
    ScriptLayerControllerUnused = 16
    RainSimulatorUnused = 17
    AreaDamageUnused = 18
    ObjectFollowObject = 19
    RedundantHintSystem = 20
    DropBombUnused = 21
    Function22Unused = 22
    MissileStationUnused = 23
    BillboardUnused = 24
    PlayerInAreaRelay = 25
    HUDTargetUnused = 26
    FogFader = 27
    EnterLogbookScreenUnused = 28
    PowerBombStationUnused = 29
    Ending = 30
    FusionRelayUnused = 31
    WeaponSwitchUnused = 32
    LaunchPlayer = 33
    Function34Unused = 34
    Darkworld = 35
    Function36Unused = 36
    Function37Unused = 37
    Function38Unused = 38
    Function39Unused = 39
    SetNumPlayers___RemoveHackedEffect = 40
    EnableCannonBallDamage = 41
    ModifyInventoryAmount = 42
    IncrementDecrementPlayersJoinedCount = 43
    InventoryThing1 = 44
    InventoryThing2 = 45
    Function46Unused = 46
    AutomaticSunPlacement = 47
    Function48Unused = 48
    WipeOnOff___ = 49
    Function50Unused = 50
    InventoryLost = 51
    Function52Unused = 52
    SunGeneratorTeleporter = 53
    SkyFader = 54
    OcclusionRelay = 55
    MultiplayerCountdown = 56
    ScaleSZ = 57
    Attach___ = 58
    Function59Unused = 59
    ExtraRenderClipPlane = 60
    VisorBlowout = 61
    AreaAutoLoadController = 62
    UnlockMultiplayerMusic = 63
    EnableDarkworldAutomapperbutton = 64
    PlaySelectedMusicMultiplayer = 65
    TranslatorDoorLocation = 66
    CinematicSkipSignal = 67
    RemoveRezbitVirus = 68
    Credits = 69


class Boolean(Enum):
    Unknown = 0
    And = 1
    Or = 2


class AmountOrCapacity(Enum):
    Amount = 0
    Capacity = 1


class Condition(Enum):
    EqualTo = 0
    NotEqualTo = 1
    GreaterThan = 2
    LessThan = 3
    GreaterThanorEqualTo = 4
    LessThanorEqualTo = 5
    Unknown = 6


class WorldLightingOptions(Enum):
    Unknown1 = 0
    NormalWorldLighting = 1
    Unknown2 = 2
    DisableWorldLighting = 3


class PlayerItem(Enum):
    PowerBeam = 0
    DarkBeam = 1
    LightBeam = 2
    AnnihilatorBeam = 3
    SuperMissile = 4
    Darkburst = 5
    Sunburst = 6
    SonicBoom = 7
    CombatVisor = 8
    ScanVisor = 9
    DarkVisor = 10
    EchoVisor = 11
    VariaSuit = 12
    DarkSuit = 13
    LightSuit = 14
    MorphBall = 15
    BoostBall = 16
    SpiderBall = 17
    MorphBallBomb = 18
    _EMPTY = 94
    ChargeBeam = 22
    GrappleBeam = 23
    SpaceJumpBoots = 24
    GravityBoost = 25
    SeekerLauncher = 26
    ScrewAttack = 27
    EnergyTransferModulePickup = 28
    SkyTempleKey1 = 29
    SkyTempleKey2 = 30
    SkyTempleKey3 = 31
    DarkAgonKey1 = 32
    DarkAgonKey2 = 33
    DarkAgonKey3 = 34
    DarkTorvusKey1 = 35
    DarkTorvusKey2 = 36
    DarkTorvusKey3 = 37
    IngHiveKey1 = 38
    IngHiveKey2 = 39
    IngHiveKey3 = 40
    HealthRefill = 41
    EnergyTank = 42
    PowerBomb = 43
    Missile = 44
    DarkAmmo = 45
    LightAmmo = 46
    ItemPercentage = 47
    NumPlayersJoined = 48
    NumPlayersInOptionsMenu = 49
    SwitchWeaponPower = 52
    SwitchWeaponDark = 53
    SwitchWeaponLight = 54
    SwitchWeaponAnnihilator = 55
    Invisibility = 57
    AmpDamage = 58
    Invincibility = 59
    SwitchVisorCombat = 75
    SwitchVisorScan = 76
    SwitchVisorDark = 77
    SwitchVisorEcho = 78
    Coin = 80
    UnlimitedMissiles = 81
    UnlimitedBeamAmmo = 82
    DarkShield = 83
    LightShield = 84
    AbsorbAttack = 85
    DeathBall = 86
    ScanVirus = 87
    DisableBeamAmmo = 89
    DisableMissiles = 90
    DisableUnmorphRemoveMorphBall = 91
    DisableBall = 92
    DisableSpaceJump = 93
    HackedEffect = 95
    CannonBall = 96
    VioletTranslator = 97
    AmberTranslator = 98
    EmeraldTranslator = 99
    CobaltTranslator = 100
    SkyTempleKey4 = 101
    SkyTempleKey5 = 102
    SkyTempleKey6 = 103
    SkyTempleKey7 = 104
    SkyTempleKey8 = 105
    SkyTempleKey9 = 106
    EnergyTransferModuleInventory = 107
    ChargeCombo = 108


class ScanSpeed(Enum):
    Normal = 0
    Slow = 1


class WeaponType(Enum):
    Power = 0
    Dark = 1
    Light = 2
    Annihilator = 3
    Bomb = 4
    PowerBomb = 5
    Missile = 6
    BoostBall = 7
    CannonBall = 8
    ScrewAttack = 9
    Phazon = 10
    AI = 11
    PoisonWater1 = 12
    PoisonWater2 = 13
    Lava = 14
    Hot = 15
    Cold = 16
    AreaDark = 17
    AreaLight = 18
    UnknownSource = 19
    SafeZone = 20


class Effect(Enum):
    Normal = 0
    Reflect = 1
    PassThru = 2
    Immune = 3
