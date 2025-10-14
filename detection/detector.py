from ultralytics import YOLO

class Detector:
    def __init__(self, model_path):
        """
        Inizializza il detector caricando il modello YOLO.

        Args:
            model_path (str): Percorso del file modello .pt
        """
        self.model = YOLO(model_path)

    def detect(self, image_path):
        """
        Esegue la detection sull'immagine data.

        Args:
            image_path (str): Percorso immagine su cui eseguire la detection.

        Returns:
            boxes (list of list): Lista di bounding box [x1, y1, x2, y2]
            classes (list of int): Lista delle classi corrispondenti alle box
        """
        results = self.model(image_path)
        boxes = results[0].boxes.xyxy.tolist()  # coordinate boxes
        classes = results[0].boxes.cls.tolist()  # classi associate
        return boxes, classes
