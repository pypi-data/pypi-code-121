import argparse, random, os

def is_posix():
    if os.name == "posix":
        return True

    return False

# Styles

BOLD                =   "\e[1m"
REG                 =   "\e[0m"

# Colors (Simple)

C_RED               =   "\e[;31m"
C_GREEN             =   "\e[;32m"
C_YELLOW            =   "\e[;33m"
C_BLUE              =   "\e[;34m"
C_MAGENTA           =   "\e[;35m"
C_CYAN              =   "\e[;36m"
C_WHITE             =   "\e[;37m"

# Colors (Advanced)

C_REPLY_HAZY        =   "\e[38;2;245;28;106m"
C_EXCELLENT_LUCK    =   "\e[38;2;253;77;50m"
C_GOOD_LUCK         =   "\e[38;2;231;137;12m"
C_AVERAGE_LUCK      =   "\e[38;2;186;194;0m"
C_BAD_LUCK          =   "\e[38;2;127;236;17m"
C_GOOD_NEWS         =   "\e[38;2;67;253;59m"
C_AWARE_RAAN        =   "\e[38;2;22;241;116m"
C_KITA_TORI         =   "\e[38;2;0;203;176m"
C_HANDSOME_STRANGER =   "\e[38;2;8;147;225m"
C_BETTER_NOT        =   "\e[38;2;42;86;251m"
C_OUTLOOK_GOOD      =   "\e[38;2;96;35;248m"
C_VERY_BAD          =   "\e[38;2;157;5;218m"
C_GODLY_LUCK        =   "\e[38;2;211;2;167m"
C_LE_EBIN           =   "\e[38;2;38;0;208m"
C_GET_DICK          =   "\e[38;2;42;86;251m"
C_AYY_LMAO          =   "\e[38;2;233;65;227m"
C_BANNED            =   "\e[38;2;255;0;0m"
C_GET_SHREKT        =   "\e[38;2;104;146;58m"
C_THE_GAME          =   "\e[38;2;140;140;140m"
C_SENPAI_BAKA       =   "\e[38;2;136;28;202m"

# Fortunes

REPLY_HAZY          =   "Reply hazy, try again"
EXCELLENT_LUCK      =   "Excellent Luck"
GOOD_LUCK           =   "Good Luck"
AVERAGE_LUCK        =   "Average Luck"
BAD_LUCK            =   "Bad Luck"
GOOD_NEWS           =   "Good news will come to you by mail"
AWARE_RAAN          =   "（　´_ゝ\\`）ﾌｰﾝ"
KITA_TORI           =   "ｷﾀ━━━━━━(ﾟ∀ﾟ)━━━━━━ \\!\\!\\!\\!"
HANDSOME_STRANGER   =   "You will meet a dark handsome stranger"
BETTER_NOT          =   "Better not tell you now"
OUTLOOK_GOOD        =   "Outlook good"
VERY_BAD            =   "Very Bad Luck"
GODLY_LUCK          =   "Godly Luck"
LE_EBIN             =   "le ebin dubs xDDDDDDDDDDDD"
GET_DICK            =   "you gon' get some dick"
AYY_LMAO            =   "ayy lmao"
BANNED              =   "(YOU ARE BANNED)"
GET_SHREKT          =   "Get Shrekt"
THE_GAME            =   "YOU JUST LOST THE GAME"
SENPAI_BAKA         =   "NOT SO SENPAI BAKA~KUN"

# Your fortune

YOUR_FORTUNE = "Your fortune: "

# Fortune List
FORCHANS = [
    REPLY_HAZY,
    EXCELLENT_LUCK,
    GOOD_LUCK,
    AVERAGE_LUCK,
    BAD_LUCK,
    GOOD_NEWS,
    AWARE_RAAN,
    KITA_TORI,
    HANDSOME_STRANGER,
    BETTER_NOT,
    OUTLOOK_GOOD,
    VERY_BAD,
    GODLY_LUCK
]

# Fortune Dictionary

FORTUNES = {
    REPLY_HAZY          :   (C_REPLY_HAZY, C_RED),
    EXCELLENT_LUCK      :   (C_EXCELLENT_LUCK, C_RED),
    GOOD_LUCK           :   (C_GOOD_LUCK, C_YELLOW),
    AVERAGE_LUCK        :   (C_AVERAGE_LUCK, C_YELLOW),
    BAD_LUCK            :   (C_BAD_LUCK, C_GREEN),
    GOOD_NEWS           :   (C_GOOD_NEWS, C_GREEN),
    AWARE_RAAN          :   (C_AWARE_RAAN, C_GREEN),
    KITA_TORI           :   (C_KITA_TORI, C_CYAN),
    HANDSOME_STRANGER   :   (C_HANDSOME_STRANGER, C_BLUE),
    BETTER_NOT          :   (C_BETTER_NOT, C_BLUE),
    OUTLOOK_GOOD        :   (C_OUTLOOK_GOOD, C_MAGENTA),
    VERY_BAD            :   (C_VERY_BAD, C_MAGENTA),
    GODLY_LUCK          :   (C_GODLY_LUCK, C_MAGENTA),
    LE_EBIN             :   (C_LE_EBIN, C_BLUE),
    GET_DICK            :   (C_GET_DICK, C_BLUE),
    AYY_LMAO            :   (C_AYY_LMAO, C_MAGENTA),
    BANNED              :   (C_BANNED, C_RED),
    GET_SHREKT          :   (C_GET_SHREKT, C_GREEN),
    THE_GAME            :   (C_THE_GAME, C_WHITE),
    SENPAI_BAKA         :   (C_SENPAI_BAKA, C_MAGENTA)
}

def hex_to_rgb(hex):
    VALID_CHARS = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']

    if(len(hex) != 6):
        raise RuntimeError(f"The Hexadecimal string {hex} was not formatted correctly.")
    for ch in hex:
        if (ch.upper() not in VALID_CHARS):
            raise ValueError(f"The Value {ch} is not a hexadecimal number.")


    R = str(hex[0] + hex[1])
    G = str(hex[2] + hex[3])
    B = str(hex[4] + hex[5])

    return(int(R,16),int(G,16),int(B,16))

def main():
    parser = argparse.ArgumentParser(prog="forchan", description="Check you're fortune esfores style :^)")

    parser.add_argument("--compat_level", "-c", choices= ['0','1','2'], default='2', help="the level of terminal compatability for color output from lowest to highest")
    parser.add_argument("--spoof", "-s", default=None, help="spoof your own fortune text")
    parser.add_argument("--color", "-x", default=None, help="override your own hex value for fortune color output")

    args = parser.parse_args()

    COMPAT  = args.compat_level
    SPOOF   = args.spoof
    COLOR   = args.color
    ADVANCED = True if args.compat_level >= '1' else False
    COMPAT  = 0 if args.compat_level == '2' else 1

    fortune_text = None
    color = None

    random.seed()
    lucky_number = random.randint(0,len(FORCHANS) - 1)

    if (SPOOF != None):
        fortune_text = SPOOF
    else:
        fortune_text = FORCHANS[lucky_number]


    if ADVANCED:
        if (COLOR != None):
            r,g,b = None, None, None
            try:
                r,g,b = hex_to_rgb(COLOR)
            except RuntimeError as r:
                print(f"Error: The given value {COLOR} was not formatted correctly. Please input a six digit hexadecimal number.")
                exit(-1)
            except ValueError as v:
                print(f"Error: The given value {COLOR} contained characters that were not hexadecimal digits.")
                exit(-1)

            color = f"\e[38;2;{r};{g};{b}m"
        elif (SPOOF != None):
            if (SPOOF in FORTUNES):
                color = FORTUNES[SPOOF][COMPAT]
            else:
                color = FORTUNES[FORCHANS[lucky_number]][COMPAT]
        else:
            color = FORTUNES[FORCHANS[lucky_number]][COMPAT]

        fortune_text = f"{BOLD}{color}{YOUR_FORTUNE}{fortune_text}{REG}"
    else:
        fortune_text = f"{YOUR_FORTUNE}{fortune_text}"

    E = ""
    if is_posix():
        E = " -e"
    os.system(f"echo{E} \"{fortune_text}\"")

if __name__ == "__main__":
    main()
