"""
Generated file.
"""
from enum import Enum


class States(Enum):
    NonZero = '!ZER'
    ACQU = 'ACQU'
    Active = 'ACTV'
    AILogicState1 = 'AIS1'
    AILogicState2 = 'AIS2'
    AILogicState3 = 'AIS3'
    AnimOver = 'ANMO'
    AnimStart = 'ANMS'
    Approach = 'APRC'
    Arrived = 'ARRV'
    AttachedCollisionObject = 'ATCL'
    AttachedAnimatedObject = 'ATOB'
    ATPA = 'ATPA'
    Attack = 'ATTK'
    BEZR = 'BEZR'
    BallIceXDamage = 'BIDG'
    BeginScan = 'BSCN'
    BSPL = 'BSPL'
    BallXDamage = 'BXDG'
    CINT = 'CINT'
    Closed = 'CLOS'
    Connect = 'CONN'
    CameraPath = 'CPTH'
    CROM = 'CROM'
    CameraTarget = 'CTGT'
    CameraTime = 'CTIM'
    Damage = 'DAMG'
    DBMB = 'DBMB'
    Dead = 'DEAD'
    DeGenerate = 'DGNR'
    Down = 'DOWN'
    DarkXDamage = 'DRKX'
    Entered = 'ENTR'
    EndScan = 'ESCN'
    Exited = 'EXIT'
    Footstep = 'FOOT'
    FOVP = 'FOVP'
    Freeze = 'FREZ'
    GRN0 = 'GRN0'
    GRN1 = 'GRN1'
    Generate = 'GRNT'
    InheritBounds = 'IBND'
    Inactive = 'ICTV'
    IceXDamage = 'IDMG'
    Inside = 'INSD'
    InternalState0 = 'IS00'
    InternalState1 = 'IS01'
    InternalState2 = 'IS02'
    InternalState3 = 'IS03'
    InternalState4 = 'IS04'
    InternalState5 = 'IS05'
    InternalState6 = 'IS06'
    InternalState7 = 'IS07'
    InternalState8 = 'IS08'
    InternalState9 = 'IS09'
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
    IS20 = 'IS20'
    IS21 = 'IS21'
    IS22 = 'IS22'
    IS23 = 'IS23'
    IS24 = 'IS24'
    IS25 = 'IS25'
    IS26 = 'IS26'
    IS27 = 'IS27'
    IS28 = 'IS28'
    IS29 = 'IS29'
    IS30 = 'IS30'
    IS31 = 'IS31'
    IS32 = 'IS32'
    IS33 = 'IS33'
    IS34 = 'IS34'
    IS35 = 'IS35'
    IS36 = 'IS36'
    IS37 = 'IS37'
    IS38 = 'IS38'
    IS39 = 'IS39'
    IS40 = 'IS40'
    IS41 = 'IS41'
    IS44 = 'IS44'
    IS45 = 'IS45'
    IS46 = 'IS46'
    IS47 = 'IS47'
    IS48 = 'IS48'
    DrawAfter = 'LDWA'
    DrawBefore = 'LDWB'
    Left = 'LEFT'
    LINR = 'LINR'
    Locked = 'LOCK'
    ThinkAfter = 'LTKA'
    ThinkBefore = 'LTKB'
    MaxReached = 'MAXR'
    Modify = 'MDFY'
    MOTP = 'MOTP'
    MOTS = 'MOTS'
    NEXT = 'NEXT'
    Open = 'OPEN'
    ORBO = 'ORBO'
    Play = 'PLAY'
    PLRP = 'PLRP'
    PressA = 'PRSA'
    PressB = 'PRSB'
    PressStart = 'PRST'
    PressX = 'PRSX'
    PressY = 'PRSY'
    PressZ = 'PRSZ'
    Patrol = 'PTRL'
    DeathRattle = 'RATL'
    RCRM = 'RCRM'
    SpawnResidue = 'RDUE'
    ReflectedDamage = 'REFD'
    ResistedDamage = 'RESD'
    Right = 'RGHT'
    Relay = 'RLAY'
    RotationOver = 'ROTO'
    RotationStart = 'ROTS'
    Retreat = 'RTRT'
    ScanDone = 'SCND'
    ScanSource = 'SCNS'
    SE01 = 'SE01'
    SE02 = 'SE02'
    SE03 = 'SE03'
    Slave = 'SLAV'
    SpawnLargeCreatures = 'SLCR'
    SpawnMediumCreatures = 'SMCR'
    Sequence = 'SQNC'
    SpawnSmallCreatures = 'SSCR'
    TGTO = 'TGTO'
    TGTP = 'TGTP'
    TGTS = 'TGTS'
    UnFreeze = 'UFRZ'
    Unlocked = 'ULCK'
    Up = 'UP  '
    WLTE = 'WLTE'
    BackToFront = 'XB2F'
    XDamage = 'XDMG'
    FrontToBack = 'XF2B'
    InBack = 'XINB'
    InFront = 'XINF'
    Outside = 'XOUT'
    Zero = 'ZERO'


class Messages(Enum):
    Action = 'ACTN'
    Activate = 'ACTV'
    Alert = 'ALRT'
    ARRV = 'ARRV'
    Attach = 'ATCH'
    AttachInstance = 'ATCI'
    Close = 'CLOS'
    ClearOriginator = 'CORG'
    Deactivate = 'DCTV'
    Decrement = 'DECR'
    Down = 'DOWN'
    Escape = 'ESCP'
    FadeIn = 'FADI'
    FadeOut = 'FADO'
    Follow = 'FOLW'
    InternalMessage0 = 'IM00'
    InternalMessage1 = 'IM01'
    InternalMessage2 = 'IM02'
    InternalMessage3 = 'IM03'
    InternalMessage4 = 'IM04'
    InternalMessage5 = 'IM05'
    InternalMessage6 = 'IM06'
    InternalMessage7 = 'IM07'
    InternalMessage8 = 'IM08'
    InternalMessage9 = 'IM09'
    InternalMessage10 = 'IM10'
    InternalMessage11 = 'IM11'
    InternalMessage12 = 'IM12'
    InternalMessage13 = 'IM13'
    InternalMessage14 = 'IM14'
    InternalMessage15 = 'IM15'
    InternalMessage16 = 'IM16'
    InternalMessage17 = 'IM17'
    InternalMessage18 = 'IM18'
    InternalMessage19 = 'IM19'
    IM20 = 'IM20'
    IM21 = 'IM21'
    IM22 = 'IM22'
    IM23 = 'IM23'
    IM24 = 'IM24'
    IM25 = 'IM25'
    IM26 = 'IM26'
    IM27 = 'IM27'
    IM28 = 'IM28'
    IM42 = 'IM42'
    IM43 = 'IM43'
    Increment = 'INCR'
    Kill = 'KILL'
    Left = 'LEFT'
    Load = 'LOAD'
    Lock = 'LOCK'
    Next = 'NEXT'
    _None = 'NONE'
    OFF = 'OFF '
    ON = 'ON  '
    OPEN = 'OPEN'
    PLAY = 'PLAY'
    Right = 'RGHT'
    RMOV = 'RMOV'
    RSAN = 'RSAN'
    Reset = 'RSET'
    RSTP = 'RSTP'
    ResetAndStart = 'RSTS'
    StopAllSounds = 'SALL'
    StopAllLoopedSounds = 'SALP'
    SetToMax = 'SMAX'
    SetOriginator = 'SORG'
    Stop = 'STOP'
    StopAndReset = 'STPR'
    Start = 'STRT'
    ToggleActive = 'TCTV'
    ToggleOpen = 'TOPN'
    Unlock = 'ULCK'
    Unload = 'ULOD'
    Up = 'UP  '
    AreaLoaded = 'XALD'
    AcidOnVisor = 'XAOV'
    AIUpdateDisabled = 'XAUD'
    AreaUnloading = 'XAUL'
    Clear = 'XCLR'
    Create = 'XCRT'
    Delete = 'XDEL'
    XDMG = 'XDMG'
    EnteredFluid = 'XENF'
    XENT = 'XENT'
    EnteredPhazonPool = 'XEPZ'
    ExitedFluid = 'XEXF'
    Falling = 'XFAL'
    HitObject = 'XHIT'
    InsideFluid = 'XINF'
    InShrubbery = 'XINS'
    InsidePhazonPool = 'XIPZ'
    Launching = 'XLAU'
    Landed = 'XLND'
    LandedOnStaticGround = 'XLSG'
    OffGround = 'XOFF'
    OnDirt = 'XOND'
    OnIce = 'XONI'
    OnOrganic = 'XONO'
    OnPlatform = 'XONP'
    XRDG = 'XRDG'
    WorldLoaded = 'XWLD'
    XXDG = 'XXDG'
    ExitedPhazonPool = 'XXPZ'
    SetToZero = 'ZERO'


class Achievement(Enum):
    Unknown1 = 1290095210
    Unknown2 = 1741167017
    Unknown3 = 1941731395
    Unknown4 = 1847676886
    Unknown5 = 42311112
    Unknown6 = 2302821108
    Unknown7 = 3685060452
    Unknown8 = 2575337497
    Unknown9 = 977778753
    Unknown10 = 1741569191
    Unknown11 = 3796894174
    Unknown12 = 2288784460
    Unknown13 = 2046095677
    Unknown14 = 3347275427
    Unknown15 = 1815168570
    Unknown16 = 1015929027
    Unknown17 = 105107473
    Unknown18 = 80518716
    Unknown19 = 1831985480
    Unknown20 = 1831093832
    Unknown21 = 4096595954
    Unknown22 = 2200577892
    Unknown23 = 1437187765
    Unknown24 = 291959200
    Unknown25 = 3841084878
    Unknown26 = 3936228971
    Unknown27 = 246361685
    Unknown28 = 761891303
    Unknown29 = 3831947482
    Unknown30 = 1643699619
    Unknown31 = 1845492504
    Unknown32 = 3065393673
    Unknown33 = 2316897795
    Unknown34 = 3682273482
    Unknown35 = 2320145227
    Unknown36 = 2373462654
    Unknown37 = 2327213834
    Unknown38 = 3078454223
    Unknown39 = 923107635
    Unknown40 = 964468362
    Unknown41 = 3917812391
    Unknown42 = 3278886900
    Unknown43 = 1516668494
    Unknown44 = 761378520
    Unknown45 = 3986936146
    Unknown46 = 311100150
    Unknown47 = 1276826815
    Unknown48 = 3582734640
    Unknown49 = 159852610
    Unknown50 = 3670289904
    Unknown51 = 3035079377
    Unknown52 = 2621245633
    Unknown53 = 87316859
    Unknown54 = 1915972077
    Unknown55 = 3965189198
    Unknown56 = 675653541
    Unknown57 = 1583013528
    Unknown58 = 3845519601
    Unknown59 = 1020841902
    Unknown60 = 2754677268
    Unknown61 = 2238270125
    Unknown62 = 2159809142
    Unknown63 = 3026027834
    Unknown64 = 1534640759
    Unknown65 = 260599856
    Unknown66 = 118390863
    Unknown67 = 1657177142
    Unknown68 = 1896894749
    Unknown69 = 3803117518
    Unknown70 = 1923499191
    Unknown71 = 2458173973
    Unknown72 = 335555508
    Unknown73 = 3394623414
    Unknown74 = 800279568
    Unknown75 = 392796523
    Unknown76 = 3511454777
    Unknown77 = 1611981353
    Unknown78 = 1331676611
    Unknown79 = 4154542500
    Unknown80 = 3931564681
    Unknown81 = 380595334
    Unknown82 = 470973530
    Unknown83 = 2698926786
    Unknown84 = 2439373502


class AreaState(Enum):
    Unknown1 = 3421935818
    Unknown2 = 3169953884
    Unknown3 = 637073894
    Unknown4 = 1392494960
    Unknown5 = 3432733907
    Unknown6 = 3147590725
    Unknown7 = 580206079
    Unknown8 = 1435635049
    Unknown9 = 3308065016
    Unknown10 = 2989105262


class CameraMode(Enum):
    Unknown1 = 2247187997
    Unknown2 = 2392533015


class CinematicStartType(Enum):
    Unknown1 = 3248813110
    Unknown2 = 2415426910
    Unknown3 = 3516177437
    Unknown4 = 2852706775
    Unknown5 = 1552481122


class CinematicEndsType(Enum):
    Unknown1 = 1671241623
    Unknown2 = 3042939236
    Unknown3 = 1097122971
    Unknown4 = 4076161679


class Blend_Mode(Enum):
    Unknown1 = 3843753963
    Unknown2 = 4195520078
    Unknown3 = 2767891128
    Unknown4 = 3057539653
    Unknown5 = 3505979826
    Unknown6 = 188796281
    Unknown7 = 2832859382
    Unknown8 = 843861036
    Unknown9 = 144217437
    Unknown10 = 2495447389
    Unknown11 = 2676901319


class RotationBlendMode(Enum):
    Unknown1 = 3792314206
    Unknown2 = 687395058


class Mode(Enum):
    Unknown1 = 1123045001
    Unknown2 = 2484558442
    Unknown3 = 3387220509


class ControllerType(Enum):
    Unknown1 = 3024507316
    Unknown2 = 268540483
    Unknown3 = 1722423905


class ReticuleType(Enum):
    Unknown1 = 1652108937
    Unknown2 = 1286894661
    Unknown3 = 3349492343
    Unknown4 = 1604604469
    Unknown5 = 2885722417


class Unknown(Enum):
    Unknown1 = 3630416747
    Unknown2 = 2705574041


class DefaultSelection(Enum):
    Unknown1 = 703550369
    Unknown2 = 3553383554
    Unknown3 = 2736090902


class Unknown(Enum):
    Unknown1 = 3257279650
    Unknown2 = 3130803243
    Unknown3 = 3689862982


class MessageType(Enum):
    Unknown1 = 903903793
    Unknown2 = 20004303
    Unknown3 = 353225947
    Unknown4 = 3457428906


class PathCurveType(Enum):
    Unknown1 = 4117718896
    Unknown2 = 2494257178


class ProxyType(Enum):
    Unknown1 = 3560604011
    Unknown2 = 3638325778
    Unknown3 = 2293645153
    Unknown4 = 2459374031
    Unknown5 = 2561452093
    Unknown6 = 3823934638
    Unknown7 = 1939145129
    Unknown8 = 1377309871
    Unknown9 = 2544156382


class EnvironmentEffects(Enum):
    Unknown1 = 4188577367
    Unknown2 = 2965060395
    Unknown3 = 829035573
    Unknown4 = 187254247
    Unknown5 = 1692838265
    Unknown6 = 2922967539


class PhazonDamage(Enum):
    Unknown1 = 4044895378
    Unknown2 = 278612995
    Unknown3 = 306082665


class Priority(Enum):
    Unknown1 = 477433555
    Unknown2 = 984224020
    Unknown3 = 3559813316
    Unknown4 = 464330772
    Unknown5 = 2642601662


class SurfaceType(Enum):
    Unknown1 = 4034626066
    Unknown2 = 2580263885
    Unknown3 = 653395187
    Unknown4 = 1331085964
    Unknown5 = 1691976390


class Unknown(Enum):
    Unknown1 = 2345054103
    Unknown2 = 1079738432
    Unknown3 = 238894302
    Unknown4 = 4050431932


class Function(Enum):
    What = 2563092183
    Function1Unused = 240618207
    Function2Unused = 1025145004
    Function3Unused = 326062726
    BossEnergyBar = 923750542
    CinematicSkip = 696482924
    Function6Unused = 1225168693
    Credits = 3035969
    CountdownTimer = 2662821358
    Function9Unused = 347364662
    Function10Unused = 1986974736
    Function11Unused = 3587238547
    EndGame = 2114084116
    GameEndChoice = 2285426762
    Function14Unused = 346273372
    Function15Unused = 3153780527
    ExtraRenderClipPlane = 749815580
    Function17Unused = 3486029411
    Function18Unused = 3631301918
    GameStateEnvVar = 1713293792
    HUDTarget = 478141611
    SimpleHint = 2830122522
    Function22Unused = 3778572771
    LaunchPlayer = 2416123537
    MapStation = 740148357
    Function25Unused = 3053209948
    Inventorything = 2471085421
    ModifyInventory = 1770695450
    PermanentHypermode = 2206760967
    Function29Unused = 3243946594
    ObjectFollowsomething = 100545803
    ObjectFollowLocator = 2552906403
    ObjectFollowObject = 1937834755
    OcclusionRelay = 2662250874
    CockpitLightsLinkToPlayerArm = 4135506313
    Function35Unused = 1854158585
    Function36Unused = 653498141
    PlayerFollowLocator = 4285373414
    PlayerInArea = 4265730537
    RadarRangeOverride = 1715427716
    Function40Unused = 2615468805
    CockpitDisplayHelmetOnMap = 2023938588
    SaveStationCheckpoint = 3039339760
    SetarmorformorphtoGhor = 1993807369
    SetSuitType = 2401398557
    Function46Unused = 1142615654
    Function47Unused = 3847325796
    TinCanScore = 1345026962
    Function49Unused = 2209351239
    Function50Unused = 2131551016
    RotateSkybox = 1875478250
    WaypointOverrider = 1385398492
    PhaazeHypermodeHUDSwitch = 1447080691
    StaticWorldRenderController = 2123107635
    SunGenerator = 3621975599
    Function56Unused = 3756334726
    ViewFrustumTester = 312252864
    VisorBlowout = 4147516617
    Function59Unused = 3504523875
    KillPlayer = 507958412
    Unknown = 387758027


class ExtraInfo(Enum):
    Unknown1 = 3424517365
    Unknown2 = 3314683043


class VolumeType(Enum):
    Unknown1 = 2487228356
    Unknown2 = 3796633071
    Unknown3 = 4268377914


class FilterShape(Enum):
    Unknown1 = 1454381642
    Unknown2 = 1825123770
    Unknown3 = 2968864876


class Type(Enum):
    Unknown1 = 4190668287
    Unknown2 = 3649059742
    Unknown3 = 2346587055
    Unknown4 = 3272497734
    Unknown5 = 4170916833


class Shape(Enum):
    Box = 2006824261
    Ellipsoid = 2207446500
    Cylinder = 971864974


class ActorMaterialType(Enum):
    kMT_Unknown = 3498468170
    kMT_Stone = 1104775585
    kMT_Metal = 2560325698
    kMT_Grass = 4042527608
    kMT_Ice = 173689903
    kMT_MetaGrating = 35715264
    kMT_Phazon = 687970960
    kMT_Dirt = 114101165
    kMT_SP_Metal = 520586891
    kMT_Glass = 1077031892
    kMT_Snow = 2821279656
    kMT_Shield = 3064176193
    kMT_Sand = 1053849610
    kMT_SeedOrganics = 3543027614
    kMT_Web = 3571249264
    kMT_Wood = 2721575702
    kMT_Organic = 1369290280
    kMT_Rubber = 316113227


class ActorCollisionResponse(Enum):
    kACR_Default = 3733775805
    Unknown2 = 652573799
    Unknown3 = 1071627662


class BerserkerEnum(Enum):
    Unknown1 = 2457151020
    Unknown2 = 2362448510
    Unknown3 = 2161792701
    Unknown4 = 4046075334


class BonusCredit(Enum):
    Unknown1 = 3550818934
    Unknown2 = 725797134
    Unknown3 = 828710715
    Unknown4 = 3149230457
    Unknown5 = 3214133816


class CableEnum(Enum):
    Unknown1 = 2161975732
    Unknown2 = 617560305
    Unknown3 = 590757843


class CableBloom(Enum):
    Unknown1 = 1131364394
    Unknown2 = 3535683408
    Unknown3 = 3476137679
    Unknown4 = 1255115501
    Unknown5 = 176197152


class CableLighting(Enum):
    Unknown1 = 746881774
    Unknown2 = 596484757
    Unknown3 = 654430001


class CableType(Enum):
    Unknown1 = 2487912838
    Unknown2 = 3596787146


class SplineType(Enum):
    Unknown1 = 3115803663
    Unknown2 = 3253497337
    Unknown3 = 3709664811


class ImpulseLocation(Enum):
    Unknown1 = 2161975732
    Unknown2 = 590757843


class FOVType(Enum):
    Unknown1 = 2839405128
    Unknown2 = 2549691886
    Unknown3 = 974872831


class FOVPathObject(Enum):
    Unknown1 = 221052433
    Unknown2 = 3545934728
    Unknown3 = 2921949809


class CollisionType(Enum):
    Unknown1 = 2969932169
    Unknown2 = 889975228
    Unknown3 = 101998339


class OrientationType(Enum):
    Unknown1 = 1973921119
    Unknown2 = 688861620
    Unknown3 = 648890987
    Unknown4 = 1486504153
    Unknown5 = 3322825525
    Unknown6 = 3306457822
    Unknown7 = 1814657251


class LookAtType(Enum):
    Unknown1 = 869408558
    Unknown2 = 3208351709
    Unknown3 = 3923417272
    Unknown4 = 1224849172
    Unknown5 = 3331078636
    Unknown6 = 4226777021


class DistanceDirectionMethod(Enum):
    Unknown1 = 1531303199
    Unknown2 = 3341593124
    Unknown3 = 4205502699
    Unknown4 = 3784644380


class PositionType(Enum):
    Unknown1 = 3258570459
    Unknown2 = 700093416
    Unknown3 = 2482478106
    Unknown4 = 1505753942
    Unknown5 = 279679312
    Unknown6 = 330387643
    Unknown7 = 2897552223


class ShakeShape(Enum):
    Unknown1 = 1492241241
    Unknown2 = 1817964322


class ColliderPositionType(Enum):
    Unknown1 = 3074795145


class Command(Enum):
    Unknown1 = 3901647376
    Unknown2 = 2581939688
    Unknown3 = 2750450586
    Unknown4 = 899849925
    Unknown5 = 109932284
    Unknown6 = 2446731085
    Unknown7 = 3803725138
    Unknown8 = 2690424049
    Unknown9 = 3699295922
    Unknown10 = 3996274175
    Unknown11 = 137873876
    Unknown12 = 2167747411
    Unknown13 = 1231245019
    Unknown14 = 726214613
    Unknown15 = 1423451252
    Unknown16 = 3416415133
    Unknown17 = 4079415854
    Unknown18 = 55864240
    Unknown19 = 3156750812
    Unknown20 = 1848293130
    Unknown21 = 1773328712
    Unknown22 = 4121744237
    Unknown23 = 541928560
    Unknown24 = 1699049272
    Unknown25 = 1875089819
    Unknown26 = 785211435
    Unknown27 = 1067837646
    Unknown28 = 3534481192
    Unknown29 = 1362252510
    Unknown30 = 1135613235
    Unknown31 = 1130843359
    Unknown32 = 1387487870
    Unknown33 = 2991816435
    Unknown34 = 1198525559
    Unknown35 = 994331281
    Unknown36 = 1292212532
    Unknown37 = 3991851469
    Unknown38 = 1233152379
    Unknown39 = 3553892191
    Unknown40 = 2579448604
    Unknown41 = 2930622747
    Unknown42 = 2686272281
    Unknown43 = 4237958029
    Unknown44 = 4155323971
    Unknown45 = 1805149946
    Unknown46 = 3844960534
    Unknown47 = 3521809460
    Unknown48 = 4101879789
    Unknown49 = 2528966795
    Unknown50 = 980624810
    Unknown51 = 343759879
    Unknown52 = 4223842739
    Unknown53 = 283049438
    Unknown54 = 3520575665
    Unknown55 = 600453719
    Unknown56 = 1968064456
    Unknown57 = 3727723490
    Unknown58 = 3098082481
    Unknown59 = 2567258098
    Unknown60 = 2867761147
    Unknown61 = 3479224811
    Unknown62 = 534585026
    Unknown63 = 2992259733
    Unknown64 = 637210426
    Unknown65 = 2159907274
    Unknown66 = 3861243545
    Unknown67 = 2901285394
    Unknown68 = 2051261897
    Unknown69 = 1719198263
    Unknown70 = 340038035
    Unknown71 = 1288278651
    Unknown72 = 3321121544
    Unknown73 = 4107107956
    Unknown74 = 2877067267
    Unknown75 = 652527973
    Unknown76 = 3415844723
    Unknown77 = 1461157841
    Unknown78 = 1789003583
    Unknown79 = 3521624545
    Unknown80 = 3228790715
    Unknown81 = 2800425192
    Unknown82 = 2967516577
    Unknown83 = 996654954
    Unknown84 = 1684683972
    Unknown85 = 1520854483
    Unknown86 = 2724605556
    Unknown87 = 3305003303
    Unknown88 = 2148884262
    Unknown89 = 1360235495
    Unknown90 = 714095169
    Unknown91 = 2053486089
    Unknown92 = 315811492
    Unknown93 = 984481977
    Unknown94 = 3923398827
    Unknown95 = 322153173
    Unknown96 = 764797371
    Unknown97 = 3425615115
    Unknown98 = 3298385702
    Unknown99 = 2228281338
    Invalid1 = 2151003287
    Invalid2 = 156891041
    Invalid3 = 2599178616
    Invalid4 = 3674132153
    Invalid5 = 1530671344
    Invalid6 = 1448630541
    Invalid7 = 1820496063
    Invalid8 = 818144998
    Invalid9 = 3113676861
    Invalid10 = 3808326893
    Invalid11 = 2983710080
    Invalid12 = 3568842610
    Invalid13 = 1948874982
    Invalid14 = 179696054
    Invalid15 = 1301198552
    Invalid16 = 722911627
    Invalid17 = 1603950717
    Invalid18 = 2910162076
    Invalid19 = 1019209684
    Invalid20 = 2248942576
    Invalid21 = 3594513416
    Invalid22 = 177089843
    Invalid23 = 1225243796
    Invalid24 = 794959369
    Invalid25 = 4221452702


class ConvergenceType(Enum):
    Unknown1 = 197952338
    Unknown2 = 10840534
    Unknown3 = 2916633979
    Unknown4 = 1845080979
    Unknown5 = 2654787412


class DI_WeaponType(Enum):
    Power = 2410944582
    Plasma = 1118216892
    Nova = 2134273114
    Phazon = 444481760
    Missile = 17740316
    ScrewAttack = 2604127627
    AI = 3161493559
    Friendly = 3441875184
    UnknownSource = 1243625939
    Electric = 4160790275
    PoisonWater = 3877195498


class DamageableTriggerEnum(Enum):
    Unknown1 = 498294111
    Unknown2 = 1637064024
    Unknown3 = 945710146
    Unknown4 = 210876390


class FOVType(Enum):
    Unknown1 = 706440702
    Unknown2 = 1282771462
    Unknown3 = 2230438793


class FluidType(Enum):
    Unknown1 = 1425213472
    Unknown2 = 230544723
    Unknown3 = 1204522302


class Bloom(Enum):
    Unknown1 = 1222417634
    Unknown2 = 759120936
    Unknown3 = 413038581
    Unknown4 = 3476137679
    Unknown5 = 1255115501
    Unknown6 = 131148223
    Unknown7 = 176197152


class Unknown(Enum):
    Unknown1 = 3516796033
    Unknown2 = 3364175296


class HyperModeType(Enum):
    Unknown1 = 2781966248
    Unknown2 = 440171881
    Unknown3 = 4246244689


class InterpolationControlType(Enum):
    Unknown1 = 1464541212
    Unknown2 = 3715904643
    Unknown3 = 3342922233
    Unknown4 = 4055225324
    Unknown5 = 3980215693
    Unknown6 = 1935003390
    Unknown7 = 881774861


class MotionType(Enum):
    Unknown1 = 864275068
    Unknown2 = 4166922378
    Unknown3 = 3471808923
    Unknown4 = 1896907209


class WorldLightingOptions(Enum):
    Unknown1 = 0
    NormalWorldLighting = 1
    Unknown2 = 2
    DisableWorldLighting = 3


class MiscControls_UnknownEnum1(Enum):
    Unknown1 = 3138569503
    Unknown2 = 3604958465
    Unknown3 = 1504980732
    Unknown4 = 3891005505
    Unknown5 = 4199960577


class MotionType(Enum):
    Unknown1 = 2003923368
    Unknown2 = 1102650983
    Unknown3 = 62257768


class OffsetType(Enum):
    Unknown1 = 2512106878
    Unknown2 = 142006047
    Unknown3 = 3952570983
    Unknown4 = 3725467126
    Unknown5 = 1409063055


class OrientationType(Enum):
    Unknown1 = 894727893
    Unknown2 = 1703284864
    Unknown3 = 2424825473
    Unknown4 = 293088044
    Unknown5 = 1061457362


class PIDType(Enum):
    Unknown1 = 1220683900
    Unknown2 = 1517782930


class PathLinkType(Enum):
    Unknown1 = 3955847150
    Unknown2 = 3844849857
    Unknown3 = 1461363479
    Unknown4 = 3983564465


class PathDeterminationMethod(Enum):
    Unknown1 = 368071499
    Unknown2 = 866990353
    Unknown3 = 1330523455
    Unknown4 = 1762871141


class InitialPosition(Enum):
    Unknown1 = 3529489810
    Unknown2 = 3079009261
    Unknown3 = 2952273734
    Unknown4 = 237832937
    Unknown5 = 635227635


class Curvature(Enum):
    Unknown1 = 3115803663
    Unknown2 = 1176110616
    Unknown3 = 3253497337
    Unknown4 = 2350587168
    Unknown5 = 3709664811
    Unknown6 = 1108898616
    Unknown7 = 1705490000


class PhysicalControl(Enum):
    Unknown1 = 538784560
    Unknown2 = 3795023653
    Unknown3 = 2527082480
    Unknown4 = 262760010
    Unknown5 = 1706296828
    Unknown6 = 4240266310
    Unknown7 = 3978335045
    Unknown8 = 371522223
    Unknown9 = 1096604377
    Unknown10 = 680639111
    Unknown11 = 667200906
    Unknown12 = 2697488232
    Unknown13 = 1761263604
    Unknown14 = 2435665866
    Unknown15 = 1593512693
    Unknown16 = 514168199
    Unknown17 = 1496847900
    Unknown18 = 830697549
    Unknown19 = 2753380155
    Unknown20 = 2017321684
    Unknown21 = 1170446731
    Unknown22 = 3704277041
    Unknown23 = 3114222144
    Unknown24 = 1405012678
    Unknown25 = 2759137981
    Unknown26 = 2577594915
    Unknown27 = 1462419467
    Unknown28 = 1295727496
    Unknown29 = 888257540
    Unknown30 = 732122331
    Unknown31 = 1712867438
    Unknown32 = 2411151363
    Unknown33 = 1133573905
    Unknown34 = 1168863462
    Unknown35 = 3776455486
    Unknown36 = 2014409348
    Unknown37 = 2238942206
    Unknown38 = 4067736424
    Unknown39 = 2195767795
    Unknown40 = 1803414226
    Unknown41 = 2678677379
    Unknown42 = 1705403104
    Unknown43 = 1923125713
    Unknown44 = 438438636
    Unknown45 = 713052917
    Unknown46 = 1276650918
    Unknown47 = 4150513473
    Unknown48 = 620168925
    Unknown49 = 3133194335
    Unknown50 = 2481737266
    Unknown51 = 530264547
    Unknown52 = 4118034785
    Unknown53 = 3915798836
    Unknown54 = 2620818456
    Unknown55 = 3291423487
    Unknown56 = 4205769547
    Unknown57 = 4018211503
    Unknown58 = 4242657632
    Unknown59 = 2593197220
    Unknown60 = 2591663667
    Unknown61 = 391300525
    Unknown62 = 1938441096
    Unknown63 = 1047334326


class PhysicalControlBoolean(Enum):
    Unknown1 = 3437305164
    Unknown2 = 1743300625
    Unknown3 = 3272702804


class PlayerItem(Enum):
    PowerBeam = 4218679992
    PlasmaBeam = 2477616633
    NovaBeam = 1352706725
    ChargeUpgrade = 893945120
    Missile = 2452465320
    IceMissile = 2431700692
    SeekerMissile = 3086280557
    GrappleBeamPull = 1906007133
    GrappleBeamSwing = 522801372
    GrappleBeamVoltage = 536233745
    Bomb = 3112660177
    CombatVisor = 2523287191
    ScanVisor = 3016416327
    CommandVisor = 1943434474
    XRayVisor = 1714103130
    DoubleJump = 2512389418
    ScrewAttack = 3654131422
    SuitType = 3492481752
    Energy = 649447109
    HypermodeEnergy = 496397544
    EnergyTank = 3010129117
    ItemPercentage = 1347001155
    Fuses = 2881244206
    Fuse1 = 862874770
    Fuse2 = 2858892584
    Fuse3 = 3714059710
    Fuse4 = 1124374557
    Fuse5 = 872654987
    Fuse6 = 2903177521
    Fuse7 = 3658336679
    Fuse8 = 1253233718
    Fuse9 = 1035330720
    MorphBall = 1211073077
    BoostBall = 2988161223
    SpiderBall = 1296127826
    HyperModeTank = 1432926409
    HyperModeBeam = 1239982508
    HyperModeMissile = 1364547232
    HyperModeBall = 2353547179
    HyperModeGrapple = 2270562373
    HyperModePermanent = 2414588173
    HyperModePhaaze = 4110398365
    HyperModeOriginal = 3854177617
    ShipGrapple = 1470237978
    ShipMissile = 2174833663
    FaceCorruptionLevel = 2109957860
    PhazonBall = 1373743611
    CannonBall = 2070581050
    ActivateMorphballBoost = 3022734302
    HyperShot = 2307731988
    CommandVisorJammed = 1065514078
    Stat_EnemiesKilled = 3227265003
    Stat_ShotsFired = 2966561623
    Stat_DamageReceived = 3809976091
    Stat_DataSaves = 4187912088
    Stat_HypermodeUses = 1141429883
    Stat_CommandoKills = 1206369514
    Stat_TinCanHighScore = 574164774
    Stat_TinCanCurrentScore = 951995458


class CollisionType(Enum):
    Unknown1 = 1750192226
    Unknown2 = 500705356
    Unknown3 = 2418955086


class RevolutionControlType(Enum):
    Unknown1 = 1989807457
    Unknown2 = 3492954719
    Unknown3 = 2606158878
    Unknown4 = 1231291285
    Unknown5 = 3555293293
    Unknown6 = 1272469130
    Unknown7 = 3663496210


class RevolutionControl_UnknownEnum1(Enum):
    Unknown1 = 2597642428
    Unknown2 = 1190654113
    Unknown3 = 2373762245
    Unknown4 = 2784335752
    Unknown5 = 1553256326
    Unknown6 = 3438239968
    Unknown7 = 2352913090
    Unknown8 = 4049356512
    Unknown9 = 3952457493
    Unknown10 = 3273432152
    Unknown11 = 2212135243
    Unknown12 = 329330221


class RevolutionControl_UnknownEnum2(Enum):
    Unknown1 = 1154737403
    Unknown2 = 967762110
    Unknown3 = 1744548478


class RevolutionVirtualControl(Enum):
    Unknown1 = 2997493716
    Unknown2 = 288465778
    Unknown3 = 4009748226
    Unknown4 = 3635765891
    Unknown5 = 891244416
    Unknown6 = 2689619302
    Unknown7 = 837808268
    Unknown8 = 21086754
    Unknown9 = 396303202
    Unknown10 = 3664856383
    Unknown11 = 3484034738
    Unknown12 = 733602211
    Unknown13 = 3559541428
    Unknown14 = 1097158738
    Unknown15 = 280637756
    Unknown16 = 3031673392


class ScanSpeed(Enum):
    Normal = 0
    Slow = 1


class ShadowProjection(Enum):
    Unknown1 = 2220656430
    Unknown2 = 2690336603
    Unknown3 = 1214374227
    Unknown4 = 4117616162
    Unknown5 = 3804557437
    Unknown6 = 193846629


class SaveGame(Enum):
    Unknown1 = 718950382
    Unknown2 = 769513116
    Unknown3 = 3263590420
    Unknown4 = 57119807
    Unknown5 = 3218965678
    Unknown6 = 634958821
    Unknown7 = 3878045253
    Unknown8 = 17817487
    Unknown9 = 1589020689


class InterpolantType(Enum):
    Unknown1 = 3466621951
    Unknown2 = 1314609833
    Unknown3 = 39922381
    Unknown4 = 175739832
    Unknown5 = 1623449729
    Unknown6 = 2401829323
    Unknown7 = 1873684334
    Unknown8 = 3103654610
    Unknown9 = 2842352988
    Unknown10 = 1923990691
    Unknown11 = 35890198


class StaticGeometryTest(Enum):
    Unknown1 = 996120112
    Unknown2 = 3961747340
    Unknown3 = 1419069414


class TeamAIState(Enum):
    Unknown1 = 4229634895
    Unknown2 = 2906748314
    Unknown3 = 210580899
    Unknown4 = 3276372239


class TweakGui_UnknownEnum1(Enum):
    Unknown1 = 4043628561
    Unknown2 = 1745727915
    Unknown3 = 520782141
    Unknown4 = 2171475102
    Unknown5 = 4134085640
    Unknown6 = 1868592562
    Unknown7 = 4292831267
    Unknown8 = 1285035198


class TweakPlayer_AimStuff_UnknownEnum1(Enum):
    Unknown1 = 3836570269
    Unknown2 = 3796405200
    Unknown3 = 4233376783


class TweakPlayer_AimStuff_UnknownEnum2(Enum):
    Unknown1 = 2531440486
    Unknown2 = 313036472
    Unknown3 = 576609856
    Unknown4 = 2183082095


class UnknownEnum1(Enum):
    Unknown1 = 1990589437
    Unknown2 = 2503861812
    Unknown3 = 2707747667


class Unknown(Enum):
    Unknown1 = 2868300453
    Unknown2 = 881720149
    Unknown3 = 1464639200


class ScriptWeaponType(Enum):
    Unknown1 = 2667276721


class CollisionChecks(Enum):
    Unknown1 = 2950079402
    Unknown2 = 3581750714
    Unknown3 = 2877254144
    Unknown4 = 731683444
