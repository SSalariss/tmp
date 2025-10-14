# tkinter
import tkinter as tk
from tkinter import filedialog

# ABC
from abc import ABC
from abc import abstractmethod

# typing
from typing import Optional, IO, Any

# playsound
from playsound import playsound


class FileChooser(ABC):
    """ 
    Classe di supporto cui scopo e' quello di assicurarsi che, 
    il widget che la estende, implementi i metodi `file` e `__choose_file__` 
    allo scopo di scegliere ed ottenere il file scelto dall'utente.
    """

    @abstractmethod
    def file(self) -> IO[Any] | None: ...

    @abstractmethod
    def __choose_file__(self) -> None: ...


class BorderButtonABC(tk.Button, ABC):
    """
    Classe astratta per la gestione di `tk.Button` con bordo

    La classe crea le basi per la costruzione di un `tk.Button` contenuto da
    un `tk.Frame` per la simulazione di un bordo.

    La classe implementa gli eventi `<Enter>` e `<Leave>` configurabili
    dai metodi `btn_bd_on_leave`, `btn_bd_on_enter`, 
    `btn_bg_on_leave`, `btn_bg_on_enter`, `on_enter` ed infine, `on_leave`.

    Nota: la classe non e' un `AdaptCanvasItem`, in quanto si puo' utilizzare
    la funzione `grid` presente in ogni `tk.Widget` che si occupa del ridimensionamento
    in modo automatico.
    """

    # Frame attributes
    _outline: tk.Frame
    
    # Button attributes
    _button_color_on_enter: str
    _button_color_on_leave: str


    # Border attributes
    _border_color_on_enter: str
    _border_color_on_leave: str

    def __init__(self, master: tk.Widget=None, bd_width: Optional[int] = 1, bd_color: Optional[str] = "#FFFFFF", cnf={}, **kw) -> None:
        """
        Inizializza la classe

        A differenza del normale `tk.Button`, questa classe possiede un bordo, bisogna
        quindi specificarne la dimensione `bd_width` e il colore `bd_color`, e'
        modificare qualsiasi altro parametro presente nella classe `tk.Button`.

        Parameters
        --------------
        master : `tk.Widget` | None
            Il widget nel quale verra' inserito il `tk.Frame` che contiene il `tk.Button`

        bd_width : `int` | `None`
            Spessore del bordo

        bd_color : `str` | `None`
            Colore del bordo, sono accettati colori come "red" o "#FF0000"

        cnf : `dict[str, Any]` | None
            Dizionario utilizzato per compatibilita', vedi `tk.Button`

        **kw : `dict[str, Any] | None`
            Dizionario standard utilizzato per la configurazione della classe, vedi `tk.Button`
        """
        # Inizializzo  e configuro il frame nel quale verra'
        # inserito il `tk.Button`
        self._outline = tk.Frame(master, padx=bd_width, pady=bd_width, background=bd_color)

        # Obbligo la grandezza del bordo del pulsante a 0
        # e la funzione associata a `command`
        kw["borderwidth"] = kw.get("borderwidth", 0)
        kw["command"] = kw.get("command", self.__on_click__)

        # Supercostruttore
        super().__init__(self._outline, cnf, **kw)

        # Configuro il colore standard del bordo
        # durante gli eventi <Enter> e <Leave>
        self._border_color_on_enter = bd_color
        self._border_color_on_leave = bd_color

        # Configuro il colore standard del background
        # del pulsante durante gli eventi <Enter> e <Leave>
        self._button_color_on_enter = self.cget("bg")
        self._button_color_on_leave = self.cget("bg")

        # Eseguo un binding per gli eventi
        # <Enter> e <Leave>
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Inserisco il pulsante nel frame
        self.pack(expand=True, fill="both")

    def get_frame(self) -> tk.Frame:
        """
        Ritorna il frame

        Returns
        ----------
        frame : `tk.Frame`
            Ritorna il frame nel quale e' contenuto il `tk.Button`
        """
        return self._outline
    
    def _on_enter(self, _) -> None:
        """
        Effettua le modifiche di `background` e `bordo`
        quando si verifica l'evento `<Enter>`
        """
        # Configuro il backgroun del pulsante
        self.config(background=self._button_color_on_enter)
        # Configuro il bordo del pulsante
        self._outline.config(background=self._border_color_on_enter)

    def _on_leave(self, _) -> None:
        """
        Effettua le modifiche di `background` e `bordo`
        quando si verifica l'evento `<Leave>`
        """
        # Configuro il backgroun del pulsante
        self.config(background=self._button_color_on_leave)
        # Configuro il bordo del pulsante
        self._outline.config(background=self._border_color_on_leave)
    
    def btn_bd_on_enter(self, color: str) -> None:
        """ Modifica il colore del `bordo` quando si verifica l'evento `<Enter>` """
        self._border_color_on_enter = color

    def btn_bd_on_leave(self, color: str) -> None:
        """ Modifica il colore del `bordo` quando si verifica l'evento `<Leave>` """
        self._border_color_on_leave = color
    
    def btn_bg_on_enter(self, color: str) -> None:
        """ Modifica il colore del `background` quando si verifica l'evento `<Enter>` """
        self._button_color_on_enter = color

    def btn_bg_on_leave(self, color: str) -> None:
        """ Modifica il colore del `background` quando si verifica l'evento `<Leave>` """
        self._button_color_on_leave = color

    
    

class BorderButton(BorderButtonABC):
    """
    Classe specifica di un `BorderButton`

    Questa classe rappresenta i pulsanti presenti nel progetto.
    """
    
    # On click events
    _on_click_events: set[str]

    # Last choosen file
    _file: IO[Any] | None

    def __init__(self, master: tk.Widget = None, bd_width: Optional[int] = 1, bd_color: Optional[str] = "#FFFFFF", cnf={}, **kw) -> None:
        """ Inizializza la classe. """
        # Supercostruttore
        super().__init__(master, bd_width, bd_color, cnf, **kw)

        # Set per la gestione di eventi
        self._on_click_events = set()
        self._file = None
    
    
    def add_event_on_click(self, virtual_event: str):
        """
        Aggiunge un evento virtuale da sollevare
        quando si clicca sul pulsante.
        """
        self._on_click_events.add(virtual_event)


    def __click_sound__(self):
        """ Riproduce il suono di un click. """
        # Riproduco il suono associato al pulsante.
        playsound("resources\\sounds\\effects\\mouse_click_effect.wav", False)


    def __on_click__(self):
        """
        Viene chiamata al click del pulsante.
        
        La funzione si occupa delle chiamate interne da effettuare
        dopo il click del pulsante, solo dopo aver raggiunto
        uno stato interno stabile solleva tutti gli eventi virtuali.

        Notare che la funzione potrebbe non sollevare alcun
        evento virtuale in quanto non si e' raggiunta al soddisfacibilita'
        durante la sua chiamata al metodo.
        """
        # Riproduco il suono di un click
        self.__click_sound__()
        
        # Altrimenti siamo arrivati ad uno stato
        # interno stabile: solleva gli eventi virtuali
        self.__raise_virtual_events__()


    def __raise_virtual_events__(self):
        """
        Solleva tutti gli eventi virtuali associati
        al pulsante.
        """
        # Per ogni evento virtuale salvato:
        for event in self._on_click_events:
           # Genera quell'evento
           self.event_generate(event)



class BorderButtonFileChooser(BorderButton, FileChooser):
    """
    Estensione della classe `BorderButton`,
    il click sul pulsante causera' l'apertura di un filedialog.
    """

    
    def __on_click__(self):

        self.__click_sound__()
        # Ottengo il file scelto dall'utente (solo immagini consentite).
        file = self.__choose_file__("Images", (".png", ".jpeg", ".jpg"))

        # Aggiorno l'ultimo file scelto.
        self._file = file

        # Se non abbiamo alcun file allora
        # l'utente ha annullato la scelta: return
        if not file: return

        self.__raise_virtual_events__()



    # @overload from FileChooser
    def __choose_file__(self, name: Optional[str] = "any", valid_types: Optional[set[str]] = "*.*"):
        """
        Apre un filedialog che permette la scelta
        di un file in base ai tipi di file concessi.

        Parameters
        --------------
        name : `str` | `None`
            Nome del tipo di file valido (es. Immagini, GIF, ...)

        valid_types : `set[str]` | `None`
            Tipi di file validi (default = any)
        
        Return
        --------
        File
            Il file scelto dall'utente
        """
        # Unisci tutti i tipi passati in una stringa
        types = " ".join(valid_types)

        # Apri il filedialog
        file = filedialog.askopenfile(mode="rb", initialdir="", title="Select an image", filetypes=[(name, types)])
        return file
    
    # @overload from FileChooser
    def file(self) -> IO[Any] | None:
        """ Ritorna l'ultimo file scelto dall'utente, se esiste. """
        return self._file


