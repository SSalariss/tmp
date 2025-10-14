import tkinter as tk

from PIL.Image import Image

from custom_data_type.gifcanvas import GifCanvas
from custom_data_type.canvasitem import AdaptCanvasItem, AdaptCanvasGIF
from utils.resize import Resize


class LoadingMenu:
    """ 
    Classe per la gestione del Menu di caricamento.
    
    Questa classe rappresenta il menu di caricamento
    del progetto.
    """
    # Class costants
    _BACKGROUND_PATH: str = "resources\\menus\\loading_menu\\background.png"
    _GIF_PATH: str = "resources\\menus\\loading_menu\\loading.gif"
    
    # Class attributes
    _master: tk.Widget
    _background: GifCanvas


    def __init__(self, master: tk.Widget):
        """ Inizializza il Menu di caricamento. """
        self._master = master
        
        # Inizializzo il background
        self.__init_background__(master)

        # Creo un immagine di background
        self._background.add_image(self._BACKGROUND_PATH, resize_func=Resize.resize)

        # Creo una GIF
        self._background.add_gif(self._GIF_PATH, resize_func=self.__gif_resize__, anchor="se")

        # Aggiungo il background al master
        self._background.pack(expand=True, fill="both")
        

    def __init_background__(self, master: tk.Widget):
        """ Inizializza il background. """
        # Inizializzo un GIFCanvas
        self._background = GifCanvas(master)
        
    # ! Funzione non generica:
    # ! funziona soltanto con la GIF del loading
    # ! dato che MARGIN e COORDS sono fisse.
    # ! Non e' un problema in questo caso ma
    # ! a livello di codice fa schifo.
    def __gif_resize__(self, acg: AdaptCanvasGIF, size: tuple[int, int]):
        """ Ridimensiona le GIF """
        # Estraggo le dimensioni x ed y
        # del widget master.
        x, y = size

        # Proporzioni
        X_PROP = 0.125
        Y_PROP = 0.25

        # Margine in base al valore
        # attuale di x
        MARGIN = x / 20

        # Calcolo le nuove dimensioni della GIF.
        new_size = (int(x * X_PROP), int(y * Y_PROP))
        
        # Ottengo una copia dell'immagine
        # della GIF ridimensionata
        current_image: Image = acg.current_frame()
        Resize.resize_image(current_image, acg, new_size)

        # Aggiorno le coordinate della GIF
        self._background.coords(acg.id(), x-MARGIN, y)

