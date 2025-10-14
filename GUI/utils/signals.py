from enum import StrEnum

class Signals(StrEnum):
    MAIN_MENU_SIG = "<<SIGMain>>"
    LOADING_MENU_SIG = "<<SIGLoading>>"
    CHOOSE_MENU_SIG = "<<SIGChoosing>>"
    FINAL_MENU_SIG = "<<SIGFinal>>"