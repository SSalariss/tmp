import cv2
import torch
import numpy as np
import os
from offside.homography import convertPoint3Dto2D, convertPoint2Dto3D

def putPng(image, tag, position) -> None:
    """Sovrappone un'immagine PNG con trasparenza su un'altra immagine."""
    if tag.shape[2] == 4:
        b, g, r, a = cv2.split(tag)
        maschera = cv2.merge([a, a, a])
        maschera_inversa = cv2.bitwise_not(maschera)
        
        altezza_sovrapposta, larghezza_sovrapposta = tag.shape[:2]
        x, y = position[0], position[1]
        
        roi = image[y:y+altezza_sovrapposta, x:x+larghezza_sovrapposta]
        sfondo_bg = cv2.bitwise_and(roi, roi, mask=maschera_inversa[:, :, 0])
        sovrapposta_fg = cv2.bitwise_and(tag[:, :, :3], tag[:, :, :3], mask=maschera[:, :, 0])
        combinata = cv2.add(sfondo_bg, sovrapposta_fg)
        image[y:y+altezza_sovrapposta, x:x+larghezza_sovrapposta] = combinata

def extend_line_to_image_borders(p1, p2, image_shape):
    h_img, w_img = image_shape[:2]
    x1, y1 = p1
    x2, y2 = p2

    if abs(x2 - x1) < 1e-6:
        # Linea verticale, traccia da top a bottom con x costante
        x = int(round(x1))
        return (x, 0), (x, h_img - 1)

    m = (y2 - y1) / (x2 - x1)
    q = y1 - m * x1

    y_left = q
    y_right = m * (w_img - 1) + q

    # Clip y values all’interno dell’immagine
    y_left_clipped = max(0, min(h_img - 1, int(round(y_left))))
    y_right_clipped = max(0, min(h_img - 1, int(round(y_right))))

    point_left = (0, y_left_clipped)
    point_right = (w_img - 1, y_right_clipped)

    return point_left, point_right


def drawOffside(pathImage: str, team: str, colors: dict, homography: torch.Tensor, 
                defender: list, attacker: list, goalkeeper: list = None) -> int:
    """
    Calcola e disegna il fuorigioco su immagine 2D e 3D.
    
    Args:
        pathImage: Path dell'immagine 3D
        team: Squadra che attacca ('Team A' o 'Team B')
        colors: Dizionario colori squadre
        homography: Matrice omografia
        defender: Lista posizioni difensori
        attacker: Lista posizioni attaccanti
        goalkeeper: Lista posizioni portiere
    
    Returns:
        int: Numero attaccanti in fuorigioco
    """
    image = cv2.imread(pathImage)
    pitch2D = cv2.imread("sportsfield_release/data/world_cup_template.png")
    
    # Carica tag fuorigioco (crea un'immagine di default se non esiste)
    try:
        offside_tag = cv2.imread('data/offside_tag.png', cv2.IMREAD_UNCHANGED)
    except:
        # Crea tag temporaneo se non esiste
        offside_tag = np.zeros((60, 130, 4), dtype=np.uint8)
        cv2.putText(offside_tag, "OFFSIDE", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255, 255), 2)
        offside_tag[:, :, 3] = 255  # Canale alfa
    
    w, h = len(image[0]), len(image)
    offside = []
    attacker2D = []
    defender2D = []
    
    # Determina colori squadre
    if team == 'Team A':
        c_def = colors.get('Team B', np.array([255, 0, 0])).tolist()
        c_att = colors.get('Team A', np.array([0, 0, 255])).tolist()
    else:
        c_def = colors.get('Team A', np.array([0, 0, 255])).tolist()
        c_att = colors.get('Team B', np.array([255, 0, 0])).tolist()
    
    # Converte posizioni a 2D
    for p in attacker:
        x_center = round((abs(p[0] + p[2]) / 2))
        p_att = convertPoint3Dto2D(homography, [x_center, p[3]], w, h)
        attacker2D.append(p_att)
        
    for p in defender:
        x_center = round((abs(p[0] + p[2]) / 2))
        p_def = convertPoint3Dto2D(homography, [x_center, p[3]], w, h)
        defender2D.append(p_def)
    
    # Determina lato di gioco
    side = 'left'
    if goalkeeper and len(goalkeeper) > 0:
        x_center = round((abs(goalkeeper[0][0] + goalkeeper[0][2]) / 2))
        p_gk = convertPoint3Dto2D(homography, [x_center, goalkeeper[0][3]], w, h)
        side = 'left' if p_gk[0] < 525 else 'right'  # 525 = 1050/2
        cv2.circle(pitch2D, (int(p_gk[0]), int(p_gk[1])), 10, c_def, -1)
    else:
        # Determina lato basandosi sulla distribuzione giocatori
        c_left = sum(1 for p in defender2D + attacker2D if p[0] < 525)
        c_right = len(defender2D + attacker2D) - c_left
        side = 'left' if c_left > c_right else 'right'
    
    # Calcola linea fuorigioco e rileva infrazioni
    if side == 'left':
        last_def = min(defender2D, key=lambda x: x[0])
        cv2.line(pitch2D, (int(last_def[0]), 0), (int(last_def[0]), 680), (0, 255, 255), 2)
        
        # Disegna linea su immagine 3D
        invex_homo = torch.inverse(homography)
        p1 = convertPoint2Dto3D(invex_homo, [last_def[0], 0], w, h)
        p2 = convertPoint2Dto3D(invex_homo, [last_def[0], 680], w, h)
        p1_ext, p2_ext = extend_line_to_image_borders(p1, p2, image.shape)
        cv2.line(image, p1_ext, p2_ext, (0, 255, 255), 3)
        #cv2.line(image, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (0, 255, 255), 3)
        
        for i, p in enumerate(attacker2D):
            if p[0] < last_def[0]:
                offside.append(p)
                mediax = round(((attacker[i][2] - attacker[i][0]) / 2) + attacker[i][0])
                putPng(image, offside_tag, [mediax - 65, attacker[i][1] - 30])
                
    else:  # side == 'right'
        last_def = max(defender2D, key=lambda x: x[0])
        cv2.line(pitch2D, (int(last_def[0]), 0), (int(last_def[0]), 680), (0, 255, 255), 2)
        
        invex_homo = torch.inverse(homography)
        p1 = convertPoint2Dto3D(invex_homo, [last_def[0], 0], w, h)
        p2 = convertPoint2Dto3D(invex_homo, [last_def[0], 680], w, h)
        p1_ext, p2_ext = extend_line_to_image_borders(p1, p2, image.shape)
        cv2.line(image, p1_ext, p2_ext, (0, 255, 255), 3)
        #cv2.line(image, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (0, 255, 255), 3)

        for i, p in enumerate(attacker2D):
            if p[0] > last_def[0]:
                offside.append(p)
                mediax = round(((attacker[i][2] - attacker[i][0]) / 2) + attacker[i][0])
                putPng(image, offside_tag, [mediax - 65, attacker[i][1] - 30])
    
    # Disegna giocatori su mappa 2D
    for p in attacker2D:
        if p in offside:
            cv2.circle(pitch2D, (int(p[0]), int(p[1])), 12, (0, 255, 255), -1)
        cv2.circle(pitch2D, (int(p[0]), int(p[1])), 10, c_att, -1)
    
    for p in defender2D:
        cv2.circle(pitch2D, (int(p[0]), int(p[1])), 10, c_def, -1)
    
    # Salva risultati
    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    cv2.imwrite(os.path.join(results_dir, 'offside_3D.jpg'), image)
    cv2.imwrite(os.path.join(results_dir, 'offside_2D.png'), pitch2D)
    
    return len(offside)