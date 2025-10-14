import cv2
from analysis.attack_prediction import predictTeamAttacking

def test_attack_prediction():
    image_path = "data/test_image.jpg"
    image = cv2.imread(image_path)
    if image is None:
        print("Immagine non trovata")
        return

    # Esempio di players_classification con coordinate bounding box (x1,y1,x2,y2) per le squadre, portiere e palla
    players_classification = {
        0: [[100, 100, 140, 180], [150, 120, 190, 200]],    # Squadra 0
        1: [[300, 200, 340, 280], [350, 220, 390, 300]],    # Squadra 1
        'goalkeeper': [[30, 180, 70, 260]],                 # Portiere
        'ball': [[230, 160, 250, 180]]                       # Palla
    }

    percent_team_1, percent_team_2 = predictTeamAttacking(players_classification, image)

    print(f"Probabilità attacco Team 1: {percent_team_1:.2f}%")
    print(f"Probabilità attacco Team 2: {percent_team_2:.2f}%")

    assert 0 <= percent_team_1 <= 100, "Percentuale Team 1 fuori intervallo"
    assert 0 <= percent_team_2 <= 100, "Percentuale Team 2 fuori intervallo"

if __name__ == "__main__":
    test_attack_prediction()
