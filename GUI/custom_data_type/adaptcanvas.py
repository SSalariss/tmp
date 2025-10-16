# tkinter
import tkinter as tk
from tkinter import PhotoImage, Event

# PIL
from PIL import Image as ImageFactory, ImageTk
from PIL.Image import Image, Resampling

# ABC
from abc import ABC
from abc import abstractmethod

# typing
from typing import Optional, Callable, Literal

# os
import os

# Custom classes
from GUI.custom_data_type.canvasitem import AdaptCanvasItem

class AdaptCanvasABC(tk.Canvas, ABC):
    """
    Classe astratta estensione di `tk.Canvas`.

    Questa classe ha lo scopo di gestire in modo autonomo
    il `resize` di ogni `child` al suo interno in base
    alla loro stessa funzione `resize`. In modo piu' specifico:
    E' possibile aggiugere alla classe dei `AdaptCanvasItem` chiamati `childs`
    tramite la funzione `add_child` che, ad ogni evento `<Configure>`, 
    vengono chiamati e ridimensionati tramite la loro funzione di `resize`.
    """
    # Widget attributes
    _master: tk.Widget

    # childs
    _childs: list[AdaptCanvasItem]


    def __init__(self, master: tk.Widget, thickness: Optional[int] = 0) -> None:
        """
        Inizializza la classe.

        La classe esegue un binding verso la funzione `on_configure`
        quando si verifica l'evento `<Configure>

        Parameters
        --------------
        master : `tk.Widget`
            Finestra master del widget.

        thickness : int | None
            Imposta lo spessore del bordo del widget (default=0).
        """
        super().__init__(master, highlightthickness=thickness)

        # Configura la classe master in cui si trova
        self._master = master
        self._childs = list()

        # Esegue il bind all'evento <Configure>
        self.bind("<Configure>", self.on_configure)
    
    def add_image(self, image_path: str,
                    *,
                    resize_func: Callable[[AdaptCanvasItem, tuple[int,int]], None],
                    pos_x: Optional[int] = 0,
                    pos_y: Optional[int] = 0,
                    anchor: Optional[Literal['nw', 'n', 'ne', 'w', 'center', 'e', 'sw', 's', 'se']] = "nw") -> None:
        """
        Aggiungi un immagine al Canvas.

        La funzione inizializza e configura, in base ai parametri passati,
        un `AdaptCanvasItem` contenente un'immagine.

        Parameters
        ------------
        image_path: `str`
            percorso dell'immagine

        resize_func: `Callable[[AdaptCanvasItem, Tuple[int, int]], None]`
            funzione che gestisce il `resize` del widget che si sta creando.
            La dichiarazione della funzione e' obbligatoria in quanto, ogni
            child di questa classe, deve implementare il ridimensionamento.

        pos_x: `int` | `None`
            coordinata x in cui deve essere posizionato l'`AdaptCanvasItem`
            alla sua creazione (default=0)

        pos_y: `int` | `None`
            coordinata y in cui deve essere posizionato l'`AdaptCanvasItem`
            alla sua creazione (default=0)

        anchor: `Literal['nw', 'ne','center', 'sw', 'se']` | `None`
            a quale angolo e' associata la coordinata
        """
        # Apro e salvo l'immagine puntata dal path
        image: Image = self.__open_image__(image_path)

        # Converto l'Image in PhotoImage
        photo_image: PhotoImage = ImageTk.PhotoImage(image)

        # Creo un immagine nel Canvas e salvo l'id
        id = self.create_image(pos_x, pos_y, image=photo_image, anchor=anchor)

        # Creo un nuovo oggetto AdaptCanvasItem
        new_child = AdaptCanvasItem(self, image_path, image, photo_image, id, resize_func)

        # Lo aggiungo tra i figli del Canvas.
        self.__add_child__(new_child)

    def __add_child__(self, aci: AdaptCanvasItem):
        """ Aggiunge un `AdaptCanvasItem` come child alla classe. """
        if aci in self._childs: return
        self._childs.append(aci)

    @abstractmethod
    def on_configure(self, event: Event) -> None: ...

    def __open_image__(self, path: str) -> Image:
        """
        Apre l'immagine indicata dal path

        Parameters
        --------------
        path : str
            Percorso valido ad un immagine

        Returns
        -------------
        una variabile `Image` contenente l'immagine
        indicata dal `path`

        Raises
        ------------
        AttributeError
            se il path non indica alcun file oppure se il file
            non ha un estensione valida.
        """
        # Se il percorso non rappresenta un file
        # solleva un eccezione.
        if not os.path.isfile(path) :
            raise AttributeError(f"Il file {path} non e' valido.")
        
        # Genero l'Image tramite il path
        return ImageFactory.open(path)


class AdaptCanvas(AdaptCanvasABC):
    """
    Questa classe implementa tutti i metodi richiesti da `AdaptCanvasABC`

    Questa classe gestire la funzione `on_configure` richiesta
    dalla superclasse `AdaptCanvasABC`.
    """

    # @overload
    def on_configure(self, event):
        """
        Gestisce l'evento `<Configure>`

        Quando la label `master` subisce un ridimensionamento
        essa chiamera' questa funzione che, a sua volta, per ogni `child` della classe,
        verra' chiamta al funzione `child.resize` passando la nuova dimensione della label master
        come argomento.
        Cio' e' possibile in quanto ogni `child` presente e' di tipo
        `AdaptCanvasItem` che possiede un metodo `resize`.
        """
        # Estra la nuova dimensione del widget master
        new_size: tuple[int, int] = (event.width, event.height)

        # Per ogni figlio:
        for child in self._childs:
            # Effettua il resize
            child.resize(new_size)


