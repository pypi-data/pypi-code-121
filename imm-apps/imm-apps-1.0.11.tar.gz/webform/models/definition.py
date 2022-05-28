from enum import Enum


class Action(Enum):
    Radio_Yes_No = "Radio_Yes_No"
    Radio_Yes_No_Null = "Radio_Yes_No_Null"
    Checkbox = "Checkbox"
    Input = "Input"
    Areatext = "Areatext"
    Select = "Select"
    Radio = "Radio"
    Button = "Button"
    Turnpage = "Turnpage"
    Wait4Element = "Wait4Elment"
    RepeatSection = "RepeatSection"
    DependantSelect = "DependantSelect"
    SelectPopup = "SelectPopup"
    SelectPopup2 = "SelectPopup2"
    GotoPage = "GotoPage"
    WebPage = "WebPage"
    Login = "Login"
    Security = "Security"
    Upload = "Upload"
    Pdf = "Pdf"
    PrPortalPick = "PrPortalPick"
    Wait = "Wait"
    Continue = "Continue"


class Role(Enum):
    PA = "Principal Applicant"
    SP = "Spouse"
    DP = "Dependant"
