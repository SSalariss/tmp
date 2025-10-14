import os
import cv2
from ultralytics import YOLO
from color_clustering.clustering import team_classification_complete
from analysis.attack_prediction import predictTeamAttacking
from visualization.visualize import draw_boxes, save_image

from offside.homography_calculator import calculateOptimHomography, save_homography, load_homography
from offside.offside_detection import drawOffside

def main():
    model_path = "model/teamClassification/weights/best.pt"
    model = YOLO(model_path)
    image_path = "data/test_image.jpg"
    results_dir = 'results'
    os.makedirs(results_dir, exist_ok=True)
    
    image = cv2.imread(image_path)
    if image is None:
        print("Immagine non trovata.")
        return

    print("Eseguendo detection YOLO...")
    results = model(image_path)
    boxes, classes = results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist()

    print("Classificando squadre...")
    players_classification, color_classification = team_classification_complete(boxes, classes, image)

    print("Analizzando percentuali di attacco...")
    percent_team_1, percent_team_2 = predictTeamAttacking(players_classification, image)

    # Assegna nomi Team A e Team B in base alla percentuale di attacco
    if percent_team_1 > percent_team_2:
        attacking_team_name = "Team A"
        defending_team_name = "Team B"
        players_classification['Team A'] = players_classification.pop(0)
        players_classification['Team B'] = players_classification.pop(1)
    else:
        attacking_team_name = "Team B"
        defending_team_name = "Team A"
        players_classification['Team B'] = players_classification.pop(0)
        players_classification['Team A'] = players_classification.pop(1)

    print(f"Squadra in attacco: {attacking_team_name}")

    # Calcolo o caricamento omografia
    homography_path = os.path.join(results_dir, 'homography.pt')
    if os.path.exists(homography_path):
        print("Caricando omografia esistente...")
        homography = load_homography(homography_path)
    else:
        print("Calcolando nuova omografia...")
        homography = calculateOptimHomography(image_path)
        save_homography(homography, homography_path)

    # Prepara dati per il rilevamento fuorigioco
    attacker_boxes = players_classification.get(attacking_team_name, [])
    defender_boxes = players_classification.get(defending_team_name, [])
    goalkeeper_boxes = players_classification.get('goalkeeper', [])

    print("Rilevando fuorigioco...")
    offside_count = drawOffside(image_path, attacking_team_name, color_classification, homography,
                                defender_boxes, attacker_boxes, goalkeeper_boxes)

    print(f"Numero di giocatori in fuorigioco: {offside_count}")

    # Salva immagine con le classificazioni
    annotated_image = draw_boxes(image, boxes, classes, players_classification)
    output_path = os.path.join(results_dir, 'final_annotated_result.jpg')
    save_image(annotated_image, output_path)

    print(f"Risultati salvati in: {results_dir}")

if __name__ == "__main__":
    main()
