import tkinter as tk

from custom_data_type.adaptcanvas import AdaptCanvas
from custom_data_type.borderbutton import BorderButton
from utils.resize import Resize
from utils.signals import Signals


class FinalMenu():

    _master: tk.Widget
    _background: AdaptCanvas
    _BACKGROUND_PATH: str = "GUI/resources/menus/final_menu/background.png"


    def __init__(self, master: tk.Widget):
        self._master = master
        self.__init_background__()

    def __init_background__(self):
        self._background = AdaptCanvas(self._master)
        self._background.add_image(self._BACKGROUND_PATH, resize_func=Resize.resize)
        self._background.pack(fill="both", expand=True)

        self._background.columnconfigure(0, weight=1)   # Spazio laterale
        self._background.columnconfigure(1, weight=4)   # Inizio immagine
        self._background.columnconfigure(2, weight=2)   # Pulsante
        self._background.columnconfigure(3, weight=4)   # Fine immagine
        self._background.columnconfigure(4, weight=1)   # Spazio laterale

        self._background.rowconfigure(0, weight=2)      # Spazio in alto
        self._background.rowconfigure(1, weight=20)     # Immagine
        self._background.rowconfigure(2, weight=1)      # Spazio centrale
        self._background.rowconfigure(3, weight=1)      # Pulsanti
        self._background.rowconfigure(4, weight=2)      # Spazio in basso

        immagine = tk.Frame(self._background, background="black")
        immagine.grid(column=1, columnspan=3, row=1, sticky="nswe")

        button = BorderButton(self._background, 1, "#23AECA", text="Riprova", font=("Aerial", 20), cursor="hand2")
        button.get_frame().grid(row=3, column=2, sticky="nswe")
        button.add_event_on_click(Signals.MAIN_MENU_SIG)