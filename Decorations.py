StrToNum={
    'r' : 0,
    'o' : 1,
    'y' : 2,
    'g' : 3,
    'b' : 4,
    'm' : 5
}

class Typo:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INVERT = '\033[7m'


    BLACK = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[98m'
    ORANGE = '\033[38;2;255;165;0m'


    #BOLD
    BBLACK = '\033[1;30m'
    BRED = '\033[1;31m'
    BGREEN = '\033[1;32m'
    BYELLOW = '\033[1;33m'
    BBLUE = '\033[1;34m'
    BWHITE = '\033[1;37m'
    BMAGENTA = '\[\033[1;35m'

    #UNDERLINE
    UBLACK="\033[4;30m"
    URED="\033[4;31m"
    #UORANGE NOT WORKING
    UGREEN="\033[4;32m"
    UYELLOW="\033[4;33m"
    UBLUE="\033[4;34m"
    UMAGENTA="\033[4;35m"
    UWHITE="\033[4;37m"

    #BACKGROUND
    ONBLACK="\033[40m"
    ONRED="\033[41m"
    ONGREEN="\033[42m"
    ONYELLOW="\033[43m"
    ONBLUE="\033[44m"
    ONMAGENTA="\033[45m"
    ONCYAN="\033[46m"
    ONWHITE="\033[47m"

NumToDisp={
    0 : Typo.RED,
    1 : Typo.ORANGE,
    2 : Typo.YELLOW,
    3 : Typo.GREEN,
    4 : Typo.BLUE,
    5 : Typo.MAGENTA
}

NumToUnderline={
    0 : Typo.URED,
    1 : Typo.UNDERLINE,
    2 : Typo.UYELLOW,
    3 : Typo.UGREEN,
    4 : Typo.UBLUE,
    5 : Typo.UMAGENTA
}