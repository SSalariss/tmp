import tkinter as tk
from GUI.custom_data_type.adaptcanvas import AdaptCanvas, AdaptCanvasItem
from GUI.custom_data_type.borderbutton import BorderButton

from typing import IO, Any
from GUI.utils.resize import Resize
from GUI.utils.signals import Signals


class ChoosingMenu():
    """ Questa classe rappresenta il menu di scelta del progetto."""


    # Class attributes
    _master: tk.Widget
    _file_path: str
    _background: AdaptCanvas
    _BACKGROUND_PATH: str = "GUI/resources/menus/choosing_menu/background.png"

    def __init__(self, master: tk.Widget, file_path: str) -> None:
        #! IN REALTA' NON MI SERVE IL FILE
        #! DEL PULSANTE MA IL FILE RISULTATO
        #! DELLA COMPUTAZIONE!
        self._master = master
        self._file_path = file_path
        self.__init_background__()



    def __init_background__(self):
        self._background = AdaptCanvas(self._master)
        self._background.add_image(self._BACKGROUND_PATH, resize_func=Resize.resize)
        self._background.pack(fill="both", expand=True)

        self._background.columnconfigure(0, weight=1)   # Spazio laterale
        self._background.columnconfigure(1, weight=1)   # Pulsante
        self._background.columnconfigure(2, weight=1)   # Pulsante
        self._background.columnconfigure(3, weight=7)   # Centro
        self._background.columnconfigure(4, weight=1)   # Pulsante
        self._background.columnconfigure(5, weight=1)   # Pulsante
        self._background.columnconfigure(6, weight=1)   # Spazio laterale

        self._background.rowconfigure(0, weight=2)      # Spazio in alto
        self._background.rowconfigure(1, weight=20)     # Immagine
        self._background.rowconfigure(2, weight=1)      # Spazio centrale
        self._background.rowconfigure(3, weight=1)      # Pulsanti
        self._background.rowconfigure(4, weight=2)      # Spazio in basso
        
        """
        frame0: tk.Frame = tk.Frame(self._background, background="red")
        frame1: tk.Frame = tk.Frame(self._background, background="yellow")
        frame11: tk.Frame = tk.Frame(self._background, background="black")
        frame2: tk.Frame = tk.Frame(self._background, background="cyan")
        frame33: tk.Frame = tk.Frame(self._background, background="black")
        frame3: tk.Frame = tk.Frame(self._background, background="yellow")
        frame4: tk.Frame = tk.Frame(self._background, background="red")
        frame0.grid(row=3, column=0, sticky="nswe")
        frame1.grid(row=3, column=1, sticky="nswe")
        frame11.grid(row=3, column=2, sticky="nswe")
        frame2.grid(row=3, column=3, sticky="nswe")
        frame33.grid(row=3, column=4, sticky="nswe")
        frame3.grid(row=3, column=5, sticky="nswe")
        frame4.grid(row=3, column=6, sticky="nswe")
        """
        

        image_frame = tk.Frame(self._background)
        image_frame.grid(column=2, columnspan=3, row=1, sticky="nswe")

        image_canvas = AdaptCanvas(image_frame)
        image_canvas.add_image(self._file_path, resize_func=Resize.resize)
        image_canvas.pack(fill="both", expand=True)

        teamA = BorderButton(self._background, 1, "#23AECA", text="Team A", font=("Aerial", 20), cursor="hand2")
        teamA.get_frame().grid(row=3, column=1, columnspan=2, sticky="nswe")
        teamA.add_event_on_click(Signals.LOADING_MENU_SIG)

        teamB = BorderButton(self._background, 1, "#23AECA", text="Team B", font=("Aerial", 20), cursor="hand2")
        teamB.get_frame().grid(row=3, column=4, columnspan=2, sticky="nswe")
        teamB.add_event_on_click(Signals.LOADING_MENU_SIG)


    def __background_resize__(self, aci: AdaptCanvasItem, size: tuple[int, int]) -> None:
        """
        Funzione di resize per `AdaptCanvasItem`

        La funzione ridimensiona l'`AdaptCanvasItem` affinche'
        occupi tutto il widget master.

        Vedi anche `custom_data_tyes.canvasitem.AdaptCanvasItem`
        """
        # Prendo una copia dell'immagine e la ridimensiono
        # in base alla nuova dimensione `size` passata alla funzione.
        Resize.resize(aci, size)
        aci.master().itemconfig(aci.id(), image=aci.current_pi())