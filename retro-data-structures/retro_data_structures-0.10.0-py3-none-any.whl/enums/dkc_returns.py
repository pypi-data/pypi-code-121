"""
Generated file.
"""
from enum import Enum


class States(Enum):
    NonZero = '!ZER'
    ACQU = 'ACQU'
    Active = 'ACTV'
    AnimOver = 'ANMO'
    AnimStart = 'ANMS'
    Approach = 'APRC'
    Arrived = 'ARRV'
    CINT = 'CINT'
    Closed = 'CLOS'
    Connect = 'CONN'
    CameraPath = 'CPTH'
    CameraTarget = 'CTGT'
    Damage = 'DAMG'
    DBNH = 'DBNH'
    Dead = 'DEAD'
    DSPN = 'DSPN'
    Entered = 'ENTR'
    Exited = 'EXIT'
    FOVP = 'FOVP'
    GIBB = 'GIBB'
    GRN0 = 'GRN0'
    GRN1 = 'GRN1'
    Generate = 'GRNT'
    Inactive = 'ICTV'
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
    InternalState20 = 'IS20'
    InternalState21 = 'IS21'
    InternalState22 = 'IS22'
    InternalState23 = 'IS23'
    InternalState24 = 'IS24'
    InternalState25 = 'IS25'
    InternalState26 = 'IS26'
    InternalState27 = 'IS27'
    InternalState28 = 'IS28'
    InternalState29 = 'IS29'
    InternalState30 = 'IS30'
    InternalState31 = 'IS31'
    InternalState32 = 'IS32'
    InternalState33 = 'IS33'
    InternalState34 = 'IS34'
    InternalState35 = 'IS35'
    InternalState36 = 'IS36'
    InternalState37 = 'IS37'
    InternalState38 = 'IS38'
    InternalState39 = 'IS39'
    InternalState40 = 'IS40'
    InternalState41 = 'IS41'
    InternalState42 = 'IS42'
    InternalState43 = 'IS43'
    InternalState44 = 'IS44'
    InternalState45 = 'IS45'
    InternalState46 = 'IS46'
    InternalState47 = 'IS47'
    InternalState48 = 'IS48'
    InternalState49 = 'IS49'
    InternalState50 = 'IS50'
    InternalState51 = 'IS51'
    InternalState52 = 'IS52'
    InternalState53 = 'IS53'
    InternalState54 = 'IS54'
    InternalState55 = 'IS55'
    InternalState56 = 'IS56'
    InternalState57 = 'IS57'
    InternalState62 = 'IS62'
    InternalState65 = 'IS65'
    InternalState66 = 'IS66'
    InternalState67 = 'IS67'
    InternalState68 = 'IS68'
    InternalState70 = 'IS70'
    InternalState72 = 'IS72'
    InternalState73 = 'IS73'
    InternalState77 = 'IS77'
    InternalState78 = 'IS78'
    InternalState79 = 'IS79'
    KBDD = 'KBDD'
    KBDK = 'KBDK'
    DrawAfter = 'LDWA'
    DrawBefore = 'LDWB'
    ThinkAfter = 'LTKA'
    ThinkBefore = 'LTKB'
    MaxReached = 'MAXR'
    MOTP = 'MOTP'
    MOTS = 'MOTS'
    Next = 'NEXT'
    OBJP = 'OBJP'
    Open = 'OPEN'
    Play = 'PLAY'
    PLRP = 'PLRP'
    Previous = 'PREV'
    Patrol = 'PTRL'
    DeathRattle = 'RATL'
    Relay = 'RLAY'
    RotationOver = 'ROTO'
    RotationStart = 'ROTS'
    SE01 = 'SE01'
    SE02 = 'SE02'
    SE03 = 'SE03'
    SE05 = 'SE05'
    SE06 = 'SE06'
    SE07 = 'SE07'
    SE08 = 'SE08'
    SE09 = 'SE09'
    SE10 = 'SE10'
    Slave = 'SLAV'
    Sequence = 'SQNC'
    TGTO = 'TGTO'
    TGTP = 'TGTP'
    Unlocked = 'ULCK'
    Zero = 'ZERO'


class Messages(Enum):
    ACMT = 'ACMT'
    Action = 'ACTN'
    Activate = 'ACTV'
    Attach = 'ATCH'
    Close = 'CLOS'
    Deactivate = 'DCTV'
    Decrement = 'DECR'
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
    InternalMessage20 = 'IM20'
    InternalMessage21 = 'IM21'
    InternalMessage22 = 'IM22'
    InternalMessage23 = 'IM23'
    InternalMessage24 = 'IM24'
    InternalMessage25 = 'IM25'
    InternalMessage26 = 'IM26'
    InternalMessage27 = 'IM27'
    InternalMessage28 = 'IM28'
    InternalMessage29 = 'IM29'
    InternalMessage30 = 'IM30'
    InternalMessage31 = 'IM31'
    InternalMessage32 = 'IM32'
    InternalMessage33 = 'IM33'
    InternalMessage34 = 'IM34'
    InternalMessage35 = 'IM35'
    InternalMessage36 = 'IM36'
    InternalMessage37 = 'IM37'
    InternalMessage38 = 'IM38'
    InternalMessage39 = 'IM39'
    InternalMessage40 = 'IM40'
    InternalMessage41 = 'IM41'
    InternalMessage50 = 'IM50'
    Increment = 'INCR'
    Kill = 'KILL'
    Load = 'LOAD'
    Lock = 'LOCK'
    Next = 'NEXT'
    Off = 'OFF '
    On = 'ON  '
    Open = 'OPEN'
    Pause = 'PAUS'
    Play = 'PLAY'
    RCMT = 'RCMT'
    RMOV = 'RMOV'
    RSAN = 'RSAN'
    Reset = 'RSET'
    RSTP = 'RSTP'
    ResetAndStart = 'RSTS'
    SetToMax = 'SMAX'
    Stop = 'STOP'
    StopAndReset = 'STPR'
    Start = 'STRT'
    ToggleActive = 'TCTV'
    Unlock = 'ULCK'
    Unload = 'ULOD'
    Clear = 'XCLR'
    Delete = 'XDEL'
    SetToZero = 'ZERO'


class EffectType(Enum):
    Unknown1 = 365077733
    Unknown2 = 877767359
    Unknown3 = 354874423
    Unknown4 = 2774898446
    Unknown5 = 1013761716
    Unknown6 = 811586774
    Unknown7 = 2195128545
    Unknown8 = 1673905314
    Unknown9 = 2751469215
    Unknown10 = 1995589804
    Unknown11 = 2774749799
    Unknown12 = 181746950
    Unknown13 = 534950152
    Unknown14 = 852740438
    Unknown15 = 334990036
    Unknown16 = 288354812
    Unknown17 = 2284232774
    Unknown18 = 2047711026
    Unknown19 = 3808741000
    Unknown20 = 2443451219
    Unknown21 = 145574633
    Unknown22 = 2141878911
    Unknown23 = 1324882936
    Unknown24 = 3622914626
    Unknown25 = 458885336
    Unknown26 = 2186500450
    Unknown27 = 1431532452
    Unknown28 = 3428459038


class NodeType(Enum):
    Start = 196349534
    Stage = 619118187
    Boss = 4220375364
    Shop = 101436209
    Trophy = 3355872335
    Unknown = 2771737649
    Rocket = 211908608
    Temple = 2650564561


class Type(Enum):
    Unknown1 = 524714316
    Unknown2 = 3689524166


class CameraMode(Enum):
    Unknown1 = 2247187997
    Unknown2 = 2392533015


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
    Unknown6 = 2495447389
    Unknown7 = 2676901319


class Unknown(Enum):
    Unknown1 = 3630416747


class RenderOverride(Enum):
    Unknown1 = 2804367681
    Unknown2 = 3823735588
    Unknown3 = 3968027345


class AreaType(Enum):
    Unknown1 = 2647520736
    Unknown2 = 1289200119
    Unknown3 = 1232673568
    Unknown4 = 2061956760
    Unknown5 = 3385429830
    Unknown6 = 721080891
    Unknown7 = 2632766436
    Unknown8 = 1888564951
    Unknown9 = 1026962455


class Direction(Enum):
    Unknown1 = 3704572404
    Unknown2 = 1052123818


class CartType(Enum):
    Unknown1 = 2661054436
    Unknown2 = 2945132126
    Unknown3 = 1799167068


class ReviewStage(Enum):
    Unknown1 = 2968599450
    Unknown2 = 2894522719
    Unknown3 = 1514157935


class Effect(Enum):
    Unknown1 = 25619637
    Unknown2 = 877033987
    Unknown3 = 3158641977
    Unknown4 = 2738734088
    Unknown5 = 2903729899
    Unknown6 = 3410305576
    Unknown7 = 2826881432
    Unknown8 = 1571727289
    Unknown9 = 2024836402
    Unknown10 = 3564728217
    Unknown11 = 3615454347
    Unknown12 = 42137536
    Unknown13 = 2507138689
    Unknown14 = 1571697364
    Unknown15 = 1165023607
    Unknown16 = 413748726
    Unknown17 = 1278419307
    Unknown18 = 2847895704
    Unknown19 = 1082469433
    Unknown20 = 2502135564
    Unknown21 = 1965778313
    Unknown22 = 3520554973
    Unknown23 = 777332222
    Unknown24 = 1037380491
    Unknown25 = 706577130
    Unknown26 = 2699379773


class SurfaceType(Enum):
    Unknown1 = 4034626066
    Unknown2 = 2580263885
    Unknown3 = 653395187
    Unknown4 = 1331085964
    Unknown5 = 1691976390


class Function(Enum):
    What = 2563092183
    Function1 = 1025145004
    Function2 = 326062726
    BossEnergyBar = 923750542
    CinematicSkip = 696482924
    Function5 = 1225168693
    Function6 = 347364662
    Function7 = 1986974736
    EndGame = 2114084116
    GameEndChoice = 2285426762
    ExtraRenderClipPlane = 749815580
    Function12 = 3486029411
    Function13 = 3631301918
    GameStateEnvVar = 1713293792
    HUDTarget = 478141611
    Function16 = 3778572771
    LaunchPlayer = 2416123537
    InventoryThing1 = 2527813936
    ModifyInventory = 1770695450
    PermanentHypermode = 2206760967
    Function21 = 387758027
    Function22 = 3243946594
    ObjectFollowSomething = 100545803
    ObjectFollowLocator = 2552906403
    ObjectFollowObject = 1937834755
    Function26 = 3761260266
    OcclusionRelay = 2662250874
    PlayerFollowLocator = 4285373414
    PlayerInArea = 4265730537
    Function30 = 3635227978
    SetSuitType = 2401398557
    InventoryThing2 = 2471085421
    Function33 = 1142615654
    Function34 = 3847325796
    TinCanScore = 1345026962
    Function36 = 2209351239
    Function37 = 2131551016
    RotateSkybox = 1875478250
    StaticWorldRenderController = 2123107635
    SunGenerator = 3621975599
    Function41 = 3756334726
    DisableInTimeAttack = 1309154554
    Function43 = 3865323319
    ViewFrustumTester = 312252864
    Function45 = 4260548972
    DisableInMirrorMode = 267618072
    Function47 = 1221679289
    Function48 = 3446751535
    Function49 = 3663394547


class TransitionType(Enum):
    Unknown1 = 1258787890
    Unknown2 = 1947803303
    Unknown3 = 3610919462


class AnimEnum(Enum):
    Unknown1 = 2336065244
    Unknown2 = 4036350261
    Unknown3 = 4009782535


class Looping(Enum):
    Unknown1 = 3792794551
    Unknown2 = 581778936


class LogicType(Enum):
    Unknown1 = 3612469255
    Unknown2 = 1211310109
    Unknown3 = 1923348685
    Unknown4 = 3247196617


class Mode(Enum):
    Unknown1 = 1686810489
    Unknown2 = 4081997130


class Mode(Enum):
    Unknown1 = 188856672
    Unknown2 = 3652747271


class Curvature(Enum):
    Unknown1 = 3115803663
    Unknown2 = 1176110616
    Unknown3 = 3253497337
    Unknown4 = 2350587168
    Unknown5 = 3709664811
    Unknown6 = 1108898616
    Unknown7 = 1705490000


class BarrelCannonEnum(Enum):
    Unknown1 = 421781424
    Unknown2 = 2786346475
    Unknown3 = 483670039
    Unknown4 = 653957


class BehaviorType(Enum):
    Unknown1 = 651229050
    Unknown2 = 3443358897
    Unknown3 = 3314362031
    Unknown4 = 2708990775
    Unknown5 = 3309059797
    Unknown6 = 3708344331
    Unknown7 = 2820249117
    Unknown8 = 47626247
    Unknown9 = 3399735524
    Unknown10 = 3752877664
    Unknown11 = 3053812380
    Unknown12 = 2237940384
    Unknown13 = 2567970925
    Unknown14 = 3310592071
    Unknown15 = 3693111366
    Unknown16 = 3241016097
    Unknown17 = 4183697310
    Unknown18 = 369334039
    Unknown19 = 568094509
    Unknown20 = 3309243184
    Unknown21 = 465503771
    Unknown22 = 3442537170
    Unknown23 = 2730845027
    Unknown24 = 4168950681
    Unknown25 = 3225767448
    Unknown26 = 3646119199
    Unknown27 = 1498413248
    Unknown28 = 936938260
    Unknown29 = 3836342357
    Unknown30 = 3767012416
    Unknown31 = 3090833062
    Unknown32 = 3381701864
    Unknown33 = 2718967993
    Unknown34 = 3191238241
    Unknown35 = 1809622
    Unknown36 = 3154163507
    Unknown37 = 2477618090
    Unknown38 = 2028993550
    Unknown39 = 870560094


class BopJumpType(Enum):
    Unknown1 = 2006721511
    Unknown2 = 97615829
    Unknown3 = 603977818


class DirectionControl(Enum):
    Unknown1 = 2694600724
    Unknown2 = 1727638800
    Unknown3 = 3667328710
    Unknown4 = 1352585780


class CableEnum(Enum):
    Unknown1 = 2161975732
    Unknown2 = 617560305
    Unknown3 = 590757843


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


class MotionType(Enum):
    Unknown1 = 888911163
    Unknown2 = 1792774118


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
    Unknown1 = 2482478106
    Unknown2 = 1505753942
    Unknown3 = 279679312
    Unknown4 = 330387643
    Unknown5 = 2897552223
    Unknown6 = 1124668811


class ShakeShape(Enum):
    Unknown1 = 1492241241
    Unknown2 = 1817964322


class TrackingType(Enum):
    Unknown1 = 758527785
    Unknown2 = 1656925141


class TrackingAxis(Enum):
    Unknown1 = 2939766238
    Unknown2 = 1031446477
    Unknown3 = 1297260238
    Unknown4 = 2822079787


class GlueType(Enum):
    Unknown1 = 3572058615
    Unknown2 = 764328608
    Unknown3 = 20267210
    Unknown4 = 2414461515


class UseFixedLateralJump(Enum):
    Unknown1 = 720232196
    Unknown2 = 3450764681
    Unknown3 = 1952429158


class Command(Enum):
    Unknown1 = 294842833
    Unknown2 = 1731350687
    Unknown3 = 27928524
    Unknown4 = 3070767272
    Unknown5 = 3699295922
    Unknown6 = 3980574952
    Unknown7 = 603446828
    Unknown8 = 1792278569
    Unknown9 = 3766654650
    Unknown10 = 1593615534
    Unknown11 = 79330256
    Unknown12 = 2511457494
    Unknown13 = 3385778078
    Unknown14 = 1873330588
    Unknown15 = 652527973
    Unknown16 = 989914839
    Unknown17 = 3839893830
    Unknown18 = 3756092388
    Unknown19 = 3111722167
    Unknown20 = 1885817639
    Unknown21 = 3321121544
    Unknown22 = 4107107956
    Unknown23 = 2604151700
    Unknown24 = 2828409898
    Unknown25 = 2228281338
    Unknown26 = 2868300621
    Unknown27 = 40450620
    Unknown28 = 616130584
    Unknown29 = 907377519
    Unknown30 = 3461520912
    Unknown31 = 534585026
    Unknown32 = 757208159
    Unknown33 = 811143585
    Unknown34 = 2144357321
    Unknown35 = 2192590330
    Unknown36 = 4102438678
    Invalid1 = 2505253282
    Invalid2 = 1598017240


class ConvergenceType(Enum):
    Unknown1 = 197952338
    Unknown2 = 10840534
    Unknown3 = 2916633979
    Unknown4 = 1845080979
    Unknown5 = 2654787412


class DI_DamageType(Enum):
    Unknown1 = 2457839363
    Unknown2 = 108355935
    Unknown3 = 1964652169
    Unknown4 = 705998558
    Unknown5 = 1586925222
    Unknown6 = 3355677312
    Unknown7 = 3734585837
    Unknown8 = 186355273
    Unknown9 = 3408073298
    Unknown10 = 2980905407
    Unknown11 = 161144709
    Unknown12 = 2834463468
    Unknown13 = 2736388683
    Unknown14 = 2395290967
    Unknown15 = 1353201790
    Unknown16 = 4121220510
    Unknown17 = 3250838969
    Unknown18 = 2351451823
    Unknown19 = 76321066
    Unknown20 = 1951014678
    Unknown21 = 1797603540


class DI_DefaultContactRule(Enum):
    Unknown1 = 243796686
    Unknown2 = 1415073108
    Unknown3 = 1917094689


class DamageableTriggerEnum(Enum):
    Unknown1 = 498294111
    Unknown2 = 1637064024
    Unknown3 = 945710146
    Unknown4 = 210876390


class DeathType(Enum):
    Unknown1 = 3565058401
    Unknown2 = 967851539
    Unknown3 = 3601684009


class Orientation(Enum):
    Unknown1 = 1990589437
    Unknown2 = 2503861812
    Unknown3 = 2707747667


class ScreenPlanes(Enum):
    Unknown1 = 2778280081
    Unknown2 = 1490620993
    Unknown3 = 3754614706


class FOVType(Enum):
    Unknown1 = 706440702
    Unknown2 = 1282771462
    Unknown3 = 2230438793


class MovementType(Enum):
    Unknown1 = 232480577
    Unknown2 = 805157494
    Unknown3 = 1382900452
    Unknown4 = 4009117944


class GenerationFacing(Enum):
    Unknown1 = 442941233
    Unknown2 = 2471859191
    Unknown3 = 3476423831


class Message(Enum):
    Unknown1 = 1951457447
    Unknown2 = 119650083
    Unknown3 = 257136971
    Unknown4 = 2379267438
    Unknown5 = 133622155
    Unknown6 = 1384500342
    Unknown7 = 3597341515
    Unknown8 = 2515933776
    Unknown9 = 3824535783
    Unknown10 = 2683235161
    Unknown11 = 115849955
    Unknown12 = 1910540917
    Unknown13 = 4018413526
    Unknown14 = 2558734144
    Unknown15 = 25853690
    Unknown16 = 1988972140
    Unknown17 = 3862057981
    Unknown18 = 2436195179
    Unknown19 = 138162897
    Unknown20 = 2134573639
    Unknown21 = 3781138404
    Unknown22 = 2522392434
    Unknown23 = 257029832
    Unknown24 = 2018952798
    Unknown25 = 4116630443
    Unknown26 = 2186935101
    Unknown27 = 458271367
    Unknown28 = 1817680401
    Unknown29 = 4063432626
    Unknown30 = 2234793764
    Unknown31 = 473788062
    Unknown32 = 1798987272
    Unknown33 = 4219814809
    Unknown34 = 2357359375
    Unknown35 = 361439925


class Behavior(Enum):
    Unknown1 = 3738736864
    Unknown2 = 700247869


class Set(Enum):
    Unknown1 = 1418502131
    Unknown2 = 3448098377
    Unknown3 = 3129147103
    Unknown4 = 619080572


class GrabPlayerType(Enum):
    Unknown1 = 3939312889
    Unknown2 = 1728348075


class IdleType(Enum):
    Unknown1 = 2507882204
    Unknown2 = 1516576467
    Unknown3 = 778879064


class InterpolationControlType(Enum):
    Unknown1 = 1464541212
    Unknown2 = 3715904643
    Unknown3 = 3342922233
    Unknown4 = 4055225324
    Unknown5 = 3980215693
    Unknown6 = 1935003390
    Unknown7 = 881774861
    Unknown8 = 2599754889


class Unknown(Enum):
    Unknown1 = 2473440237
    Unknown2 = 4176174928
    Unknown3 = 1533397409
    Unknown4 = 2158070624
    Unknown5 = 3388425333
    Unknown6 = 3591303767
    Unknown7 = 2817662562


class WorldLightingOptions(Enum):
    Unknown1 = 0
    NormalWorldLighting = 1
    Unknown2 = 2
    DisableWorldLighting = 3


class LocomotionContext(Enum):
    Unknown1 = 1217500904
    Unknown2 = 1659886973
    Unknown3 = 3043946116
    Unknown4 = 3717702700


class SplineInput(Enum):
    Unknown1 = 1306613276
    Unknown2 = 3510421530


class MotionType(Enum):
    Unknown1 = 2003923368
    Unknown2 = 1102650983
    Unknown3 = 62257768
    Unknown4 = 4043791539
    Unknown5 = 359230179
    Unknown6 = 2542029021
    Unknown7 = 3469981234


class MusicEnumA(Enum):
    Unknown1 = 2667448087
    Unknown2 = 685090775
    Unknown3 = 3600967174


class MusicEnumB(Enum):
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


class ModelSelect(Enum):
    Unknown1 = 747529578
    Unknown2 = 25649140
    Unknown3 = 1988128610
    Unknown4 = 4018749144
    Unknown5 = 2559446606
    Unknown6 = 116038637


class SoundSelect(Enum):
    Unknown1 = 743666217
    Unknown2 = 2920611314
    Unknown3 = 3586792535
    Unknown4 = 245357536


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
    Unknown6 = 2842420594
    Unknown7 = 3406290353


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
    Unknown5 = 1606438391


class InitialPosition(Enum):
    Unknown1 = 3529489810
    Unknown2 = 3079009261
    Unknown3 = 2952273734
    Unknown4 = 237832937
    Unknown5 = 635227635


class PhysicalControl(Enum):
    Unknown1 = 538784560
    Unknown2 = 1257927101
    Unknown3 = 2527082480
    Unknown4 = 262760010
    Unknown5 = 1605113718
    Unknown6 = 3332720332
    Unknown7 = 3241795345
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
    Unknown21 = 482737692
    Unknown22 = 2024691420
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
    Unknown35 = 448542600
    Unknown36 = 1204478533
    Unknown37 = 589982697
    Unknown38 = 2118965801
    Unknown39 = 1296341802
    Unknown40 = 4264401241
    Unknown41 = 2501073051
    Unknown42 = 416591226
    Unknown43 = 2126425707
    Unknown44 = 153831471
    Unknown45 = 2382561797
    Unknown46 = 2194421220
    Unknown47 = 3830782992
    Unknown48 = 948457836
    Unknown49 = 1882875513
    Unknown50 = 3830727351
    Unknown51 = 3065589481
    Unknown52 = 1723958282
    Unknown53 = 5895001
    Unknown54 = 929866935
    Unknown55 = 1376095990
    Unknown56 = 3406618444
    Unknown57 = 1097406112
    Unknown58 = 913188406
    Unknown59 = 750056011
    Unknown60 = 3602632488
    Unknown61 = 2194707590
    Unknown62 = 2027923941
    Unknown63 = 3932661243
    Unknown64 = 1443881457
    Unknown65 = 3073052112
    Unknown66 = 3776455486
    Unknown67 = 2014409348
    Unknown68 = 2238942206
    Unknown69 = 4067736424
    Unknown70 = 2195767795
    Unknown71 = 1803414226
    Unknown72 = 2678677379
    Unknown73 = 1705403104
    Unknown74 = 1923125713
    Unknown75 = 438438636
    Unknown76 = 713052917
    Unknown77 = 1276650918
    Unknown78 = 4150513473
    Unknown79 = 620168925
    Unknown80 = 3133194335
    Unknown81 = 2481737266
    Unknown82 = 530264547
    Unknown83 = 4118034785
    Unknown84 = 3915798836
    Unknown85 = 2620818456
    Unknown86 = 3291423487
    Unknown87 = 4205769547
    Unknown88 = 4018211503
    Unknown89 = 4242657632
    Unknown90 = 2593197220
    Unknown91 = 2591663667
    Unknown92 = 391300525
    Unknown93 = 1938441096
    Unknown94 = 1047334326


class PhysicalControlBoolean(Enum):
    Unknown1 = 3437305164
    Unknown2 = 1743300625
    Unknown3 = 3272702804


class HurlDirection(Enum):
    Unknown1 = 1649245644
    Unknown2 = 2152107551


class PlayerItem(Enum):
    Banana = 2989480091
    BananaCoin = 179769247
    Player1Dead = 2126962961
    Player2Dead = 1432650682
    Unknown1 = 683198367
    Unknown2 = 680401301
    _1UP = 541403960
    Unknown3 = 2693678525
    PuzzlePiece = 2466406539
    KONGK = 1648547163
    KONGO = 1697583426
    KONGN = 304619988
    KONGG = 1811192176
    SuperGuideAvailable = 1739429232
    Unknown4 = 2939645372
    Unknown5 = 3261153874
    Unknown6 = 3867676351
    Unknown7 = 1290288555
    Unknown8 = 825391244
    Unknown9 = 335133244
    Key1Jungle = 191335887
    Key2Beach = 2456738933
    Key3Ruins = 3848924387
    Key4Cave = 2064480576
    Key5Forest = 202000854
    Key6Cliff = 2500008044
    Key7Factory = 3791923450
    Key8Volcano = 1924871531
    FactoryKeyL5 = 1485020731
    FactoryKeyL6 = 3247099777
    FactoryKeyL7 = 3062759191
    Unknown10 = 1562155182
    Unknown11 = 3289762068
    Unknown12 = 3004365186
    Unknown13 = 762735649
    Unknown14 = 1517378743
    Unknown15 = 3279424781
    Unknown16 = 3028237723
    Unknown17 = 616570890
    Unknown18 = 4052900803
    Unknown19 = 3089971392
    Unknown20 = 15802396
    MirrorMode = 3808453171
    TikiTongAward = 3170261865
    Heart = 2139003975


class BlendMode(Enum):
    Unknown1 = 1325699157
    Unknown2 = 4033765706
    Unknown3 = 2234072790


class CharacterType(Enum):
    Unknown1 = 3498085335
    Unknown2 = 3500442295
    Unknown3 = 3196863511
    Unknown4 = 122254083
    Unknown5 = 1016091067
    Unknown6 = 487816011


class Mode(Enum):
    Unknown1 = 547879193
    Unknown2 = 1737019397
    Unknown3 = 3676988069
    Unknown4 = 2012074074


class CollisionType(Enum):
    Unknown1 = 988868003
    Unknown2 = 3290837091
    Unknown3 = 64195446
    Unknown4 = 406774627


class Orientation(Enum):
    Unknown1 = 1210096040
    Unknown2 = 3994269074
    Unknown3 = 4243498757


class MotionType(Enum):
    Unknown1 = 408845096
    Unknown2 = 892529961
    Unknown3 = 2699437848
    Unknown4 = 2881999260
    Unknown5 = 3150408382
    Unknown6 = 3935665287
    Unknown7 = 4016849840


class RenderingType(Enum):
    Unknown1 = 567642100
    Unknown2 = 2706276301
    Unknown3 = 3032625655


class CollisionType(Enum):
    Unknown1 = 1750192226
    Unknown2 = 500705356
    Unknown3 = 2418955086


class TriggeringBehavior(Enum):
    Unknown1 = 1646698372
    Unknown2 = 616771319
    Unknown3 = 3193573373
    Unknown4 = 855879045
    Unknown5 = 2101052759
    Unknown6 = 3222593132
    Unknown7 = 687212262
    Unknown8 = 2661042625


class RevolutionControlType(Enum):
    Unknown1 = 1989807457
    Unknown2 = 3492954719
    Unknown3 = 2606158878
    Unknown4 = 1231291285
    Unknown5 = 3555293293
    Unknown6 = 1272469130
    Unknown7 = 3663496210
    Unknown8 = 493907588


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
    Unknown9 = 3762479092
    Unknown10 = 396303202
    Unknown11 = 3664856383
    Unknown12 = 3484034738
    Unknown13 = 733602211
    Unknown14 = 3559541428
    Unknown15 = 1097158738
    Unknown16 = 280637756
    Unknown17 = 3031673392
    Unknown18 = 3975963313


class RobotChickenEnum(Enum):
    Unknown1 = 2355519386
    Unknown2 = 1585000868


class AttackType(Enum):
    Unknown1 = 3049474916
    Unknown2 = 1247556284
    Unknown3 = 3969890760
    Unknown4 = 4102395283
    Unknown5 = 3424416932
    Unknown6 = 604683877


class AttackType(Enum):
    Unknown1 = 3049474916
    Unknown2 = 3424416932
    Unknown3 = 3852875433
    Unknown4 = 3441388673
    Unknown5 = 2331366705
    Unknown6 = 3455670365
    Unknown7 = 3063280919
    Unknown8 = 2763651948
    Unknown9 = 1034988246
    Unknown10 = 1253546560
    Unknown11 = 3570601955
    Unknown12 = 2748596085
    Unknown13 = 987590351
    Unknown14 = 1306156633
    Unknown15 = 3714401224
    Unknown16 = 2858578782
    Unknown17 = 1652139044
    Unknown18 = 3001058877
    Unknown19 = 736745351
    Unknown20 = 1559160593
    Unknown21 = 3263853234
    Unknown22 = 3045933604
    Unknown23 = 746853278
    Unknown24 = 1535320840
    Unknown25 = 3409723033
    Unknown26 = 3157986831
    Unknown27 = 2114165819
    Unknown28 = 3332687925


class Mode(Enum):
    Unknown1 = 3821732504
    Unknown2 = 960210097


class EdgeAdjust(Enum):
    Unknown1 = 3052433601
    Unknown2 = 1732273257
    Unknown3 = 2165931078
    Unknown4 = 3175546924


class Shape(Enum):
    Box = 2006824261
    Ellipsoid = 2207446500
    Cylinder = 971864974


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


class SwingLineType(Enum):
    Unknown1 = 1785685439
    Unknown2 = 3603989999


class DeathLineAction(Enum):
    Unknown1 = 3159497651
    Unknown2 = 3053783048
    Unknown3 = 1208586442


class RopeBlendMode(Enum):
    Unknown1 = 1971095211
    Unknown2 = 1461792423
    Unknown3 = 860542818


class TandemBeamType(Enum):
    Unknown1 = 2267357019
    Unknown2 = 198534853


class BeamScrollDirection(Enum):
    Unknown1 = 3222423752
    Unknown2 = 4162030962
    Unknown3 = 3320164207


class Mode(Enum):
    Unknown1 = 3319629014
    Unknown2 = 1638556020
    Unknown3 = 2397105244


class OffsetUsing(Enum):
    Unknown1 = 1852738074
    Unknown2 = 2734575865


class OffsetPlane(Enum):
    Unknown1 = 1504524536
    Unknown2 = 3232000322
    Unknown3 = 1085671865


class ScaleUsing(Enum):
    Unknown1 = 324142880
    Unknown2 = 2048101552


class ScalePlane(Enum):
    Unknown1 = 604405720
    Unknown2 = 1025330841
    Unknown3 = 3171888738


class AttackDirection(Enum):
    Unknown1 = 2480441985
    Unknown2 = 2997032087
    Unknown3 = 3930447781
    Unknown4 = 4038531701
    Unknown5 = 3178342758
    Unknown6 = 2173062009


class AxisRelationship(Enum):
    Unknown1 = 3967299408
    Unknown2 = 1098140846
    Unknown3 = 2944019842
    Unknown4 = 402777336


class TweakGraphicalTransitions_UnknownEnum1(Enum):
    Unknown1 = 281035013
    Unknown2 = 1664922133
    Unknown3 = 2494648407
    Unknown4 = 1406306775


class UnknownEnum1(Enum):
    Unknown1 = 3498468170
    Unknown2 = 2667496530
    Unknown3 = 2047403829
    Unknown4 = 1355285209
    Unknown5 = 4042527608
    Unknown6 = 2244757927
    Unknown7 = 4093280761
    Unknown8 = 316113227
    Unknown9 = 1053849610
    Unknown10 = 3540895599
    Unknown11 = 2940312393
    Unknown12 = 2747963473
    Unknown13 = 2216304526
    Unknown14 = 3733225391
    Unknown15 = 2710780938
    Unknown16 = 726080521
    Unknown17 = 2991476147
    Unknown18 = 2884392300
    Unknown19 = 2335322311
    Unknown20 = 2932947914
    Unknown21 = 1055885139
    Unknown22 = 3019595684
    Unknown23 = 3309813611
    Unknown24 = 301158827
    Unknown25 = 882394908
    Unknown26 = 3295058287
    Unknown27 = 4197224736
    Unknown28 = 1366861671
    Unknown29 = 118081788
    Unknown30 = 560552649
    Unknown31 = 3260680116
    Unknown32 = 2230153123
    Unknown33 = 226363571
    Unknown34 = 2288417301
    Unknown35 = 237661532
    Unknown36 = 3028341189
    Unknown37 = 1471384760
    Unknown38 = 3526156651
    Unknown39 = 73248019
    Unknown40 = 1823769759
    Unknown41 = 170955119
    Unknown42 = 6982693
    Unknown43 = 803838669
    Unknown44 = 3436890032
    Unknown45 = 3752155563
    Unknown46 = 169692266
    Unknown47 = 301636307
    Unknown48 = 1965544138
    Unknown49 = 1020242868
    Unknown50 = 2301287145
    Unknown51 = 1780058004
    Unknown52 = 2696026638
    Unknown53 = 918055931


class UnknownEnum2(Enum):
    Unknown1 = 4154998361
    Unknown2 = 43112267
    Unknown3 = 1001675783
    Unknown4 = 2125443110
    Unknown5 = 1762039417
    Unknown6 = 406308725


class UnknownEnum3(Enum):
    Unknown1 = 2193008170
    Unknown2 = 3466373042


class UnknownEnum4(Enum):
    Unknown1 = 623070171
    Unknown2 = 3156875873


class Unknown(Enum):
    Unknown1 = 3301645737
    Unknown2 = 1520862100
    Unknown3 = 1550664063
    Unknown4 = 1209216122
    Unknown5 = 1322839697
    Unknown6 = 4038019871
    Unknown7 = 4133784052
    Unknown8 = 1836610470


class FusedMode(Enum):
    Unknown1 = 15591780
    Unknown2 = 765067123
    Unknown3 = 3431676720
    Unknown4 = 3653023550
    Unknown5 = 561086974
    Unknown6 = 2644326084


class Unknown(Enum):
    Unknown1 = 2036438260
    Unknown2 = 3973515826


class OffsetMethod(Enum):
    Unknown1 = 4143668412
    Unknown2 = 2395860326
    Unknown3 = 3301486136


class Unknown(Enum):
    Unknown1 = 1570070236
    Unknown2 = 2893014572


class Unknown(Enum):
    Unknown1 = 1138461727
    Unknown2 = 423672500


class Transform(Enum):
    Unknown1 = 910385532
    Unknown2 = 4025702105


class LaunchDirection(Enum):
    Unknown1 = 2823948451
    Unknown2 = 3746904117
    Unknown3 = 1180461455
    Unknown4 = 575846200
    Unknown5 = 1431668654
    Unknown6 = 3428636180
    Unknown7 = 2018446428
    Unknown8 = 11462301


class PhysicsTargetType(Enum):
    Unknown1 = 851512901
    Unknown2 = 1115212370
    Unknown3 = 31413364


class Unknown(Enum):
    Unknown1 = 156009171
    Unknown2 = 1347574161
    Unknown3 = 3294124709


class SplineTargetType(Enum):
    Unknown1 = 650771470
    Unknown2 = 1139767447
    Unknown3 = 2114112772


class Unknown(Enum):
    Unknown1 = 1216708916
    Unknown2 = 1694551927


class BossType(Enum):
    Unknown1 = 1020568392
    Unknown2 = 750469656


class MoleType(Enum):
    Unknown1 = 1346330706
    Unknown2 = 234709402


class Priority(Enum):
    Unknown1 = 4007772996
    Unknown2 = 2137826916
    Unknown3 = 282277844
    Unknown4 = 378144275
    Unknown5 = 65721636
    Unknown6 = 3370441017
    Unknown7 = 3242266683


class Dominance(Enum):
    Unknown1 = 3983073400
    Unknown2 = 3128342963
    Unknown3 = 1997111451


class AccelerationFrame(Enum):
    Unknown1 = 3017233311
    Unknown2 = 1171803538


class SplineInput(Enum):
    Unknown1 = 802665130
    Unknown2 = 1596247140
    Unknown3 = 1675718848


class Mode(Enum):
    Unknown1 = 3935154705
    Unknown2 = 99213323
    Unknown3 = 2299600562
    Unknown4 = 3842212297
    Unknown5 = 3987018474


class RandomScheme(Enum):
    Unknown1 = 2880630628
    Unknown2 = 3234354105


class Location(Enum):
    Unknown1 = 283027849
    Unknown2 = 830478334
    Unknown3 = 1637896504


class BodyPart(Enum):
    Unknown1 = 2574655407
    Unknown2 = 3672585852
    Unknown3 = 2910815203


class RotatesAbout(Enum):
    Unknown1 = 861343981
    Unknown2 = 1592686023
    Unknown3 = 2733529863


class StartOrientation(Enum):
    Unknown1 = 1340586566
    Unknown2 = 1237959292
    Unknown3 = 2082595009


class IdleOrientation(Enum):
    Unknown1 = 2741072240
    Unknown2 = 4277815486
    Unknown3 = 3429082295
    Unknown4 = 1880248735
    Unknown5 = 1443833066


class AttackType(Enum):
    Unknown1 = 3049474916
    Unknown2 = 1247556284
    Unknown3 = 3969890760
    Unknown4 = 1784571755
    Unknown5 = 876917101
    Unknown6 = 4102395283


class ShadowProjection(Enum):
    Unknown1 = 2220656430
    Unknown2 = 2690336603
    Unknown3 = 1214374227
    Unknown4 = 4117616162
    Unknown5 = 3804557437
    Unknown6 = 193846629


class AttackType(Enum):
    Unknown1 = 3049474916
    Unknown2 = 4140404736
    Unknown3 = 1755930736
    Unknown4 = 3092218274
    Unknown5 = 929136215
    Unknown6 = 1737683946
    Unknown7 = 3302863318


class SwoopDirection(Enum):
    Unknown1 = 577560212
    Unknown2 = 3658389764
    Unknown3 = 689377491
    Unknown4 = 224659491


class EffectMode(Enum):
    Unknown1 = 192300787
    Unknown2 = 1867416351


class HorizontalType(Enum):
    Unknown1 = 3622626674
    Unknown2 = 1381776091
    Unknown3 = 845883630


class VerticalType(Enum):
    Unknown1 = 718348172
    Unknown2 = 1015257970
    Unknown3 = 3115917612
    Unknown4 = 2695442625
    Unknown5 = 3528244321


class CollisionType(Enum):
    Unknown1 = 2969932169
    Unknown2 = 889975228
    Unknown3 = 101998339


class AttackMode(Enum):
    Unknown1 = 3513386353
    Unknown2 = 787747780


class Limits(Enum):
    Unknown1 = 3849161731
    Unknown2 = 1441114211
    Unknown3 = 1893407381
    Unknown4 = 2781784261
    Unknown5 = 4257601293
    Unknown6 = 750989655


class LocomotionSpeed(Enum):
    Unknown1 = 2414343563
    Unknown2 = 2174636099
    Unknown3 = 2676411794


class AttackType(Enum):
    Unknown1 = 3049474916
    Unknown2 = 3654350753
    Unknown3 = 257472118
    Unknown4 = 788515472
    Unknown5 = 687224734
    Unknown6 = 1790335737
    Unknown7 = 480806635
    Unknown8 = 2107889035
    Unknown9 = 4198649417
    Unknown10 = 3547503450
    Unknown11 = 1410967332


class Unknown(Enum):
    Unknown1 = 2504930441
    Unknown2 = 2473440237
    Unknown3 = 562591724
    Unknown4 = 3095471702
    Unknown5 = 3481671360
    Unknown6 = 1373799267
    Unknown7 = 2817662562
