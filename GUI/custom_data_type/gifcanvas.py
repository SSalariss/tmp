# tkinter
import tkinter as tk

# PIL
from PIL import ImageTk
from PIL.Image import Resampling

# ABC
from abc import ABC
from abc import abstractmethod

# Typing
from typing import Optional, Callable, Literal

# Custom classes
from custom_data_type.adaptcanvas import AdaptCanvas
from custom_data_type.canvasitem import AdaptCanvasItem, AdaptCanvasGIF
from resize import Resize




class GifCanvasABC(AdaptCanvas, ABC):
    """
    Questa classe astratta rappresenta un `AdaptCanvas` ma con
    gestione delle GIF.
    """

    def __init__(self, master: tk.Widget, thickness: Optional[int] = 0) -> None:
        # Supercostruttore
        super().__init__(master, thickness)

    def add_gif(self,
                gif_path: str,
                *,
                resize_func: Callable[[AdaptCanvasItem, tuple[int,int]], None],
                pos_x: Optional[int] = 0,
                pos_y: Optional[int] = 0,
                anchor: Optional[Literal['nw', 'n', 'ne', 'w', 'center', 'e', 'sw', 's', 'se']] = "nw",
                wait_time: Optional[int] = 40):
        """
        Aggiungi una GIF al Canvas.

        La funzione inizializza e configura, in base ai parametri passati,
        un `AdaptCanvasGIF` contenente una GIF.

        Parameters
        ------------
        image_path: `str`
            percorso dell'immagine

        resize_func: `Callable[[AdaptCanvasItem, Tuple[int, int]], None]`
            funzione che gestisce il `resize` del widget che si sta creando.
            La dichiarazione della funzione e' obbligatoria in quanto, ogni
            child di questa classe, deve implementare il ridimensionamento.

        pos_x: `int` | `None`
            coordinata x in cui deve essere posizionato l'`AdaptCanvasGIF`
            alla sua creazione (default=0)

        pos_y: `int` | `None`
            coordinata y in cui deve essere posizionato l'`AdaptCanvasGIF`
            alla sua creazione (default=0)

        anchor: `Literal['nw', 'ne','center', 'sw', 'se']` | `None`
            a quale angolo e' associata la coordinata

        wait_time: `int` | `None`
            tempo di attesa tra un frame e l'altro. (default=0)
        """
        # Apro l'immagine puntata dal path
        gif_image = self.__open_image__(gif_path)

        # Converto l'Image in PhotoImage
        gif_pi = ImageTk.PhotoImage(gif_image)

        # Ottengo l'id della GIF
        gif_id = self.create_image(pos_x, pos_y, image=gif_pi, anchor=anchor)

        # Creo un AdaptCanvasItem con le informazioni della GIF
        gif_child = AdaptCanvasGIF(self, gif_path, gif_image, gif_pi, gif_id, resize_func)

        # Lo aggiungo come figlio al Canvas
        self.__add_child__(gif_child)

        # Inizio l'animazione della GIF
        self.__animate__(gif_child, wait_time)

    @abstractmethod
    def __animate__(self, acg: AdaptCanvasGIF, wait_time: int): ...


class GifCanvas(GifCanvasABC):

    """ 
    Questa classe implementa tutte le funzioni richieste
    dalla superclasse `GifCanvasABC` per la gestione di GIF.
    """

    def __init__(self, master: tk.Widget, thickness: Optional[int] = 0):
        """ 
        Inizializza la calsse. 

        Per informazioni sui parametri vedi `AdaptCanvas`        
        """
        # Inizializza il supercostruttore
        super().__init__(master, thickness)

    # @overload from GifCanvasABC
    def __animate__(self, acg: AdaptCanvasGIF, wait_time: int):
        """ 
        Inizia l'animazione della GIF.
        
        Inizia e gestisce l'animazione della GIF
        ed eventuali ridimensionamenti.
        """
        # Ottengo il prossimo frame
        next_frame = acg.next_frame()
        
        # Estraggo la dimensione attuale della GIF
        size = (acg.current_pi().width(), acg.current_pi().height())

        # Eseguo un resize in quanto next_frame ritorna
        # soltanto l'immagine originale, dunque bisogna
        # eseguire un resize in caso l'immagine
        # fosse di dimensioni diverse.
        # Ricordiamo che la funzione salva tutto nel
        # AdaptCanvas passato.
        Resize.resize_image(next_frame, acg, size)

        # Configuro il timer
        self.after(wait_time, lambda: self.__animate__(acg, wait_time))
    
        