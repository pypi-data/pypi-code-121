from .enums import (
    CLIDatabaseEnum, CLIRunEnum, CLIHelperEnum, HTTPMethodEnum, TurboActionEnum
)

CLIModeEnumUnion = CLIDatabaseEnum | CLIRunEnum | CLIHelperEnum
