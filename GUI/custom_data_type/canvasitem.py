# tkinter
import tkinter as tk
from tkinter import PhotoImage


# PIL
from PIL import Image as ImageFactory, ImageSequence
from PIL.Image import Image

# typing
from typing import Callable, Self


class CanvasItem():
    """
    Questa classe rappresenta un Widget contenente un immagine.

    Questa classe rappresenta un tipo di dato composto utile per la gestione
    di immagini all'interno dei Canvas, specialmente per la classe `AdaptCanvas`.

    Lo scopo della classe e' salvare in un unica struttura, tutte le informazioni
    utili per la gestione di immagini contenute in un canvas.
    """
    # Canvas attributes
    _master: tk.Canvas
    _path: str
    _image: Image
    _current_pi: PhotoImage
    _id: int


    def __init__(self, master: tk.Canvas, path: str, image: Image, current_pi: PhotoImage, id: int) -> None:
        """
        Inizializza un `CanvasItem`

        Parameters
        ------------
        path : `str`
            Percorso dell'immagine contenuta nel `tk.Canvas`
        
        image :  `Image`
            `Image` dell'immagine contenuta nel `tk.Canvas`

        current_pi : `PhotoImage`
            `PhotoImage` di `Image`, questo attributo la `PhotoImage` attualmente
            mostrata dal `tk.Canvas`.

        id : `int`
            Id ritornato dalla funzione `tk.Canvas.create_image`
        """
        # Inizializzo i vari attributi
        self._path = path
        self._master = master
        self._image = image
        self.set_current_pi(current_pi)
        self._id = id


    def path(self):
        """ Ritorna il percorso dell'immagine. """
        return self._path

    def image(self):
        """ Ritorna l'immagine originale del Canvas. """
        return self._image
    
    def current_pi(self):
        """ Ritorna la `PhotoImage` attualmente mostrata dal Canvas. """
        return self._current_pi
    
    def id(self):
        """ Ritorna l'id unico del Canvas """
        return self._id
    
    def set_current_pi(self, pi: PhotoImage):
        """ Imposta la nuova `PhotoImage` """
        self._current_pi = pi

    def master(self) -> tk.Canvas:
        return self._master
    
    def __repr__(self):
        """ Stringa rappresentate l'oggetto """
        return f"image: {self._path}, id: {self._id}"
    

class AdaptCanvasItem(CanvasItem):
    """
    Questa classe nasce come estensione di `CanvasItem` ma con
    l'aggiunta di una funzione `resize` che ridimensiona il widget stesso.
    
    NOTA: la funzione `resize` non deve essere chiamata dall'utente
    ma deve essere evocata dopo un evento `<Configure>`.
    """
    _resize_func: Callable[[tuple[int, int]], Image]

    def __init__(self, master: tk.Canvas, path: str, image: Image, current_pi: PhotoImage, id: int, resize_func: Callable[[Self, tuple[int, int]], None]):
        """
        Inizializza un `AdaptCanvasItem`

        Parameters
        ------------
        path : `str`
            Percorso dell'immagine contenuta nel `tk.Canvas`
        
        image :  `Image`
            `Image` dell'immagine contenuta nel `tk.Canvas`

        current_pi : `PhotoImage`
            `PhotoImage` di `Image`, questo attributo la `PhotoImage` attualmente
            mostrata dal `tk.Canvas`.

        id : `int`
            Id ritornato dalla funzione `tk.Canvas.create_image`

        resize_func: `Callable[[Self, tuple[int, int ]], None]`
            Funzione di resize passata dall'utente, questa funzione:
            dato un oggetto `AdaptCanvasItem` e le dimensioni del widget master,
            esegue un resize del widget cui `id` combacia con l'`id` di questa classe.
            Lo scopo e' permettere a qualsiasi AdaptCanvasItem di avere una `propria` funzione
            di `resize` in base al suo utilizzo e scopo.
            """
        # Inizializzo la superclasse
        super().__init__(master, path, image, current_pi, id)

        # Configuro  la funzione di resize
        self._resize_func = resize_func

    def resize(self, size: tuple[int, int]) -> None:
        """
        Chiama la funzione `resize` dell'utente. 
        
        La funzione esegue soltanto una chiamata alla funzione
        `resize`, cio' significa che non implementa essa stessa
        il resize o il suo stesso aggiornamento, tocca quindi all'utente
        implementarlo.

        Lo scopo di questa funzione e' essere chiamata quando si verifica
        l'evento `<Configure>` dal widget padre che la contiene, affinche' ogni
        suo widget possa ridimensionarsi in base alla propria funzione `resize`, ma cio'
        non significa che non possa essere chiamata altrove, tocca all'utente
        utilizzarla in modo consapevole in base alla funzione `resize` da lui
        dichiarata.
        """
        self._resize_func(self, size)



class AdaptCanvasGIF(AdaptCanvasItem):
    """
    Estensione della classe `AdaptCanvasItem`

    Questa classe nasce come estensione di un `AdaptCanvasItem` ma con
    la gestione di `GIF`.
    """

    # Animation attributes
    _frame_list: list[Image]
    _counter: int

    def __init__(self, master: tk.Widget, path: str, image: Image, current_pi: PhotoImage, id: int, resize_func: Callable[[Self, tuple[int, int]], None]):
        """
        Inizializza una classe

        La classe inizializza un `AdaptCanvasItem` ed, internamente,
        inizializza la lista di frames contenuta dalla GIF.

        Per info sui parametri vedi `AdaptCanvasItem`
        """
        # Inizializzo il supercostruttore
        super().__init__(master, path, image, current_pi, id, resize_func)
        
        # Inizializzo la frame list
        self.__init_frame_list__()

        # Inizializzo e configuro i frame
        self.__load_frames__()

    def __init_frame_list__(self):
        """
        Inizializza la lista di frame della GIF.
        """
        # Imposta il contatore a 0
        self._counter = 0

        # Inizializza la lista di frame
        self._frame_list = list()

        # Carica e configura i frame.
        self.__load_frames__()

    def __load_frames__(self) -> list[Image]:
        """
        Carica i frame

        La funzione estrae tutti i frame dalla GIF e
        ne preserva l'eventuale trasparenza, ed infine,
        li aggiunge alla lista di frame.
        """
        # Apri la GIF indicata dal path
        with ImageFactory.open(self._path) as im:

            # Per ogni frame presente nella GIF
            for frame in ImageSequence.Iterator(im):

                # Converti il frame al formato RGBA
                f = frame.convert("RGBA")
                
                # Crea un canvas trasparente grande quanto l'immagine
                new_frame = ImageFactory.new("RGBA", im.size, (0, 0, 0, 0))
                
                # Incolla sopra il frame (per preseravare il canale alpha)
                new_frame.paste(f, (0, 0), f)
                
                # Aggiungi il frame alla frame list
                self._frame_list.append(new_frame)
            
            # Chiudi il puntatore al file
            im.close()

    def next_frame(self):
        """ Ritorna il prossimo frame della GIF. """

        # Estraggo il frame puntato dal contatore.
        # Cio' fa si che il frame 0 sia
        # il primo frame che viene mostrato.
        frame = self.current_frame()

        # Incremento in contatore
        self._counter = (self._counter + 1) % len(self._frame_list)
        return frame
    
    def current_frame(self) -> Image:
        """ Ritorna il frame attuale della GIF. """
        return self._frame_list[self._counter]



    