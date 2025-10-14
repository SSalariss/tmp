import cv2
import numpy as np
from sklearn.cluster import KMeans
import math

def compute_distance(color1, color2):
    """Calcola distanza euclidea tra due colori """
    return math.sqrt((color2[0]-color1[0])**2 + (color2[1]-color1[1])**2 + (color2[2]-color1[2])**2)

def extract_mean_color(bounding_box_player):
    
    # mask green
    bounding_box_hsv = cv2.cvtColor(bounding_box_player, cv2.COLOR_BGR2HSV)
    mask_green = cv2.inRange(bounding_box_hsv, (36,25,25), (70,255,255))
    
    mask_green_inv = cv2.bitwise_not(mask_green)
    result = cv2.bitwise_and(bounding_box_player, bounding_box_player, mask=mask_green_inv)
    # extract mean color
    mean_color = np.array(cv2.mean(bounding_box_player, mask=mask_green_inv))
    return mean_color[:3]

def get_dominant_colors(team_colors):
    colors_kmeans = KMeans(n_clusters=2)
    colors_kmeans.fit(team_colors)
    return colors_kmeans

def team_classification_complete(boxes, classes, image):
    
    # Estrai box per tipo 
    players_boxes = []
    goalkeeper_box = []
    team_colors = []
    ball_box = []
    
    for box, cls in zip(boxes, classes):
        if round(cls) == 0:  # classe 0 = player
            x1, y1, x2, y2 = map(int, box)
            players_boxes.append([x1, y1, x2, y2])
            player = image[y1:y2, x1:x2]  # RITAGLIO DELL'IMMAGINE
            color = extract_mean_color(player)  # Passa il ritaglio, non le coordinate
            team_colors.append(color)
        if round(cls) == 1:  # classe 1 = goalkeeper
            x1, y1, x2, y2 = map(int, box)
            goalkeeper_box.append([x1, y1, x2, y2])
        if round(cls) == 2:  # classe 2 = ball
            x1, y1, x2, y2 = map(int, box)
            ball_box.append([x1, y1, x2, y2])
    
    # KMeans sui colori 
    kmeans_colors = get_dominant_colors(team_colors)
    dominant_colors = kmeans_colors.cluster_centers_.astype(int)
    
    # Crea classificazione colori 
    color_classification = dict()
    team_1 = 0
    team_2 = 1
    goalkeeper = 'goalkeeper'
    ball = 'ball'
    
    for color in dominant_colors:
        if team_1 in color_classification:
            color_classification[team_2] = color
        else:
            color_classification[team_1] = color
    
    # Crea classificazione giocatori 
    players_classification = dict()
    players_classification[team_1] = []
    players_classification[team_2] = []
    if len(goalkeeper_box) > 0: 
        players_classification[goalkeeper] = goalkeeper_box
    if len(ball_box) > 0: 
        players_classification[ball] = ball_box
    
    # Assegna ogni giocatore alla squadra più vicina per colore 
    for i, color in enumerate(team_colors):
        distance_team_1 = compute_distance(color, color_classification[team_1])
        distance_team_2 = compute_distance(color, color_classification[team_2])
        if distance_team_1 < distance_team_2:
            players_classification[team_1].append(players_boxes[i])
        else:
            players_classification[team_2].append(players_boxes[i])
    
    return players_classification, color_classification
