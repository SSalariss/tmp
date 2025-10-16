import os
import cv2
from ultralytics import YOLO
from color_clustering.clustering import team_classification_complete
from analysis.attack_prediction import predictTeamAttacking
from visualization.visualize import draw_boxes, save_image
from offside.homography_calculator import calculateOptimHomography, load_homography, save_homography
from offside.offside_detection import drawOffside

import os
from io import BufferedReader
from numpy import frombuffer, uint8



class ModelManager: 

    _image_path: str
    _image: cv2.typing.MatLike

    _player_classification: dict
    _color_classification: dict
    _percent_team1: float
    _percent_team2: float

    def step_select_image(self, buffered_image: BufferedReader):
        """
        Questa funzione prende il percorso dell'immagine selezionata dalla GUI.
        Ritorna l'immagine caricata o None se impossibile caricarla.
        """
        image_data = buffered_image.read()
        np_arr = frombuffer(image_data, uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image is None:
            print("Immagine non trovata.")
            
        self._image_path = buffered_image.name
        self._image = image
        self._results_dir = 'results'
        os.makedirs(self._results_dir, exist_ok=True)


    def step_attack_prediction(self):
        """
        Esegue la detection e la classificazione dei giocatori,
        calcola le percentuali di attacco e ritorna la classificazione
        di giocatori, colori e le percentuali di attacco.
        """
        model_path = "model/teamClassification/weights/best.pt"
        model = YOLO(model_path)
        results = model(self._image_path)
        os.makedirs(self._results_dir, exist_ok=True)

        boxes, classes = results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist()

        self._players_classification, self._color_classification = team_classification_complete(boxes, classes, self._image)
        percent_team_1, percent_team_2 = predictTeamAttacking(self._players_classification, self._image)
        
        if percent_team_1 > percent_team_2:
            attacking_team_name = "Team A"
            defending_team_name = "Team B"
            self._players_classification['Team A'] = self._players_classification.pop(0)
            self._players_classification['Team B'] = self._players_classification.pop(1)
        else:
            attacking_team_name = "Team B"
            defending_team_name = "Team A"
            self._players_classification['Team B'] = self._players_classification.pop(0)
            self._players_classification['Team A'] = self._players_classification.pop(1)
        annotated_image = draw_boxes(self._image, boxes, classes, self._players_classification)
        save_image(annotated_image, os.path.join(self._results_dir, 'final_annotated_result.jpg'))

        return os.path.join(self._results_dir, 'final_annotated_result.jpg')

    def step_offside_detection(self, attacking_team_from_user):
        """
        Calcola o carica l'omografia, rileva il fuorigioco e salva l'immagine annotata.
        Ritorna il numero di giocatori in fuorigioco.
        """
        homography_path = os.path.join(self._results_dir, 'homography.pt')
        if os.path.exists(homography_path):
            print("Caricando omografia esistente...")
            homography = load_homography(homography_path)
        else:
            print("Calcolando nuova omografia...")
            homography = calculateOptimHomography(self._image_path)
            save_homography(homography, homography_path)

        attacking_team = "Team A" if attacking_team_from_user == "Team A" else "Team B"
        defending_team = "Team B" if attacking_team == "Team A" else "Team A"

        print(f"attacking: {attacking_team}, defending: {defending_team}")

        attacker_boxes = self._players_classification.get(attacking_team, [])
        defender_boxes = self._players_classification.get(defending_team, [])
        goalkeeper_boxes = self._players_classification.get('goalkeeper', [])

        offside_count = drawOffside(self._image_path, attacking_team, self._color_classification, homography,
                                defender_boxes, attacker_boxes, goalkeeper_boxes)

        print(f"Numero di giocatori in fuorigioco: {offside_count}")

        # Salva immagine annotata
        return os.path.join(self._results_dir, 'offside_3D.jpg')
