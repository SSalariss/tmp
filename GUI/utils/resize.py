from PIL import ImageTk
from PIL.Image import Image, Resampling

from GUI.custom_data_type.canvasitem import AdaptCanvasItem

class Resize:

    @staticmethod
    def resize(aci: AdaptCanvasItem, size: tuple[int, int]) -> None:
        """
        Ridimensiona l'`AdaptCanvasItem`.

        Dato un `AdaptCanvasItem` ed una dimensione `size`,
        si ridimensiona l'`AdaptCanvasItem` alle dimensioni `size`.
        In modo piu' specifico: si estrae una copia dell'immagine originale
        dell'`AdaptCanvasItem`, si ridimensiona e si inizializza una nuova
        `PhotoImage` con l'immagine ridimensionata, infine, si aggiorna
        la `PhotoImage` dell'`AdaptCanvasItem`.
        """
        # Prendo una copia dell'immagine e la ridimensiono
        # in base alla nuova dimensione `size` passata alla funzione.
        Resize.resize_image(aci.image(), aci, size)


    @staticmethod
    def resize_image(image: Image, aci: AdaptCanvasItem, size: tuple[int, int]) -> None:
        """
        Ridimensiona l'immagine e la si inserisce nel'`AdaptCanvasItem`.

        Dato un `AdaptCanvasItem`, un'immagine `Image` ed una dimensione `size`,
        si ridimensiona l'immagine alle dimensioni `size`.
        In modo piu' specifico: si estrae una copia dell'immagine `Image`, 
        si ridimensiona e si inizializza una nuova `PhotoImage` con l'immagine ridimensionata, 
        infine, si aggiorna la `PhotoImage` dell'`AdaptCanvasItem`.
        """
        # Estraggo una copia dell'immagine ridimensionata.
        new_image = image.resize(size, Resampling.LANCZOS)

        # Converto l'immagine in PhotoImage.
        new_pi = ImageTk.PhotoImage(new_image)

        # La imposto PhotoImage corrente.
        aci.set_current_pi(new_pi)

        # Aggiorno l'item
        aci.master().itemconfig(aci.id(), image=aci.current_pi())
