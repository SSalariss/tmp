import cv2

def draw_boxes(image, boxes, classes, players_classification=None):
    """
    Disegna bounding box su immagine con colori e etichette per squadre, portiere, arbitro e pallone.
    """
    annotated_image = image.copy()
    
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        cls = int(classes[i])
        
        # Determina colore e etichetta
        if cls == 0:  # Player
            # Trova a quale team appartiene questo box
            team_label = "Player"
            color = (128, 128, 128)  # Grigio di default
            
            if players_classification:
                # Cerca in Team A
                if 'Team A' in players_classification:
                    for team_box in players_classification['Team A']:
                        if team_box == [x1, y1, x2, y2]:
                            team_label = "Team A"
                            color = (0, 0, 255)  # Rosso
                            break
                
                # Cerca in Team B
                if 'Team B' in players_classification:
                    for team_box in players_classification['Team B']:
                        if team_box == [x1, y1, x2, y2]:
                            team_label = "Team B"
                            color = (255, 0, 0)  # Blu
                            break
                            
        elif cls == 1:  # Goalkeeper
            team_label = "GK"
            color = (0, 0, 0)  # Nero
        elif cls == 2:  # Ball
            team_label = "Ball"
            color = (0, 255, 255)  # Giallo
        else:  # Altri (referee, etc.)
            team_label = f"Class {cls}"
            color = (128, 128, 128)  # Grigio
        
        # Disegna rettangolo e testo
        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated_image, team_label, (x1, y1-10), 
                    cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)
    
    return annotated_image

def save_image(image, path):
    """Salva immagine su disco."""
    cv2.imwrite(path, image)
