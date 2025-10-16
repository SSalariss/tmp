import os
import cv2
import numpy as np

def predictTeamAttacking(players_classification, img):

    def getAreas(coordinates_team_1, coordinates_team_2):
        """
        Calcola l'area formata dai giocatori più esterni di tutte le due squadre.
        """
        height, width, channels = img.shape
        img_empty = np.zeros((height, width, channels), dtype=np.uint8)

        # Disegno i punti in una immagine vuota
        for center in coordinates_team_1:
            cv2.circle(img_empty, center, 5, (0, 0, 255), -1)
        for center in coordinates_team_2:
            cv2.circle(img_empty, center, 5, (255, 0, 0), -1)
        for center in coordinates_goalkeeper:
            cv2.circle(img_empty, center, 5, (0,255,0), -1)
        
        # calcolo il convex hull per i punti delle due squadre per trovare i giocatori più esterni
        hull_points_team_1 = cv2.convexHull(coordinates_team_1)
        hull_points_team_2 = cv2.convexHull(coordinates_team_2)

        # disegno le linee sull'immagine vuota per rappresentare l'area dei giocatori
        cv2.polylines(img_empty, [hull_points_team_1], isClosed=True, color=(0,0,255), thickness=1)
        cv2.polylines(img_empty, [hull_points_team_2], isClosed=True, color=(255,0,0), thickness=1)

        def calculate_area(points):
            n = len(points)
            area = 0.0
            for i in range(n):
                j = (i + 1) % n
                area += points[i][0] * points[j][1]
                area -= points[j][0] * points[i][1]
            area = abs(area) / 2.0
            return area
        
        if not os.path.exists("results"):
            os.makedirs("results")
        cv2.imwrite(os.path.join("results", "PolygonsPlayerPoints.png"), img_empty)

        area_points_team_1 = calculate_area(hull_points_team_1.squeeze())
        area_points_team_2 = calculate_area(hull_points_team_2.squeeze())

        return area_points_team_1, area_points_team_2
    
    def getPlayerCloserToGoalkeeper(coordinates_team_1, coordinates_team_2, coordinates_goalkeeper):
        counter_team_1 = 0
        counter_team_2 = 0
        max_players_near_goalkeeper = 0
        if existGoalkeeper:
            distances = []

            # compute distance from goalkeeper for each player
            for coordinate_1 in coordinates_team_1:
                distance_1 = cv2.norm(coordinate_1, coordinates_goalkeeper[0])
                distances.append((distance_1, 'team1'))
            for coordinate_2 in coordinates_team_2:
                distance_2 = cv2.norm(coordinate_2, coordinates_goalkeeper[0])
                distances.append((distance_2, 'team2'))

            distances_sorted = sorted(distances, key=lambda x: (x[0]))
            max_players_near_goalkeeper = len(distances) // 2
            for i in range(max_players_near_goalkeeper):
                if distances_sorted[i][1] == 'team1':
                    counter_team_1 += 1
                else:
                    counter_team_2 += 1
        return counter_team_1, counter_team_2, max_players_near_goalkeeper
    
    def getTeamCloserToBall(coordinates_team_1, coordinates_team_2, coordinates_ball):
        team_closer_to_ball = ""
        if existBall:
            distances_ball = []

            #compute distance from ball for each player
            for coordinate_1 in coordinates_team_1:
                distance_1 = cv2.norm(coordinate_1, coordinates_ball[0])
                distances_ball.append((distance_1, 'team1'))
            for coordinate_2 in coordinates_team_2:
                distance_2 = cv2.norm(coordinate_2, coordinates_ball[0])
                distances_ball.append((distance_2, 'team2'))
            
            team_closer_to_ball = sorted(distances_ball, key=lambda x: (x[0]))[0][1]
            
        return team_closer_to_ball  
    
    def getPercentages(area_points_team_1, area_points_team_2, n_players_team_1, n_players_team_2, max_players_near_goalkeeper, counter_team_1, counter_team_2, team_closer_to_ball):
        max_area = max(area_points_team_1, area_points_team_2)
        max_n_players = max(n_players_team_1, n_players_team_2)
        
        # Controllo divisione per zero
        if max_area == 0:
            norm_area_team_1 = 0
            norm_area_team_2 = 0
        else:
            norm_area_team_1 = area_points_team_1 / max_area
            norm_area_team_2 = area_points_team_2 / max_area
            
        norm_n_players_team_1 = 1- (n_players_team_1 / max_n_players )
        norm_n_players_team_2 = 1 - (n_players_team_2 / max_n_players )
        w_ball = 0
        w_distance = 0
        w_area = 0
        w_n_players = 0

        # imposto i pesi dati ad ogni parametro a seconda della presenza o meno di portiere e/o palla
        if max_players_near_goalkeeper > 0 and team_closer_to_ball != "":
            _case = "gb" #goalkeeper & ball
            w_ball = 0.4
            w_distance = 0.3
            w_area = 0.2
            w_n_players = 0.1
        elif max_players_near_goalkeeper == 0 and team_closer_to_ball != "":
            _case = "b" # ball
            w_ball = 0.45
            w_area = 0.35
            w_n_players = 0.2
        elif max_players_near_goalkeeper > 0 and team_closer_to_ball == "":
            _case = "g" # goalkeeper
            w_distance = 0.4
            w_area = 0.4
            w_n_players = 0.2
        else:
            _case = "None" # !goalkeeper & !ball
            w_area = 0.7
            w_n_players = 0.3

        # Sostituisco match con if-elif-else per compatibilità
        if _case == "gb":
            norm_distance_team_1 = 1 - (counter_team_1 / max_players_near_goalkeeper)
            norm_distance_team_2 = 1 - (counter_team_2 / max_players_near_goalkeeper)
            players_closer_to_ball_team1 = 1 if team_closer_to_ball == 'team1' else 0
            players_closer_to_ball_team2 = 1 if team_closer_to_ball == 'team2' else 0
            norm_ball_team1 = players_closer_to_ball_team1 / 1 
            norm_ball_team2 = players_closer_to_ball_team2 / 1
            score_team_1 = (w_ball * norm_ball_team1) + (w_area * norm_area_team_1) + (w_distance * norm_distance_team_1) + (w_n_players * norm_n_players_team_1)
            score_team_2 = (w_ball * norm_ball_team2) + (w_area * norm_area_team_2) + (w_distance * norm_distance_team_2) + (w_n_players * norm_n_players_team_2)
            total_score = score_team_1 + score_team_2
            percent_1 = (score_team_1/total_score) * 100
            percent_2 = (score_team_2/total_score) * 100
        elif _case == "b":
            players_closer_to_ball_team1 = 1 if team_closer_to_ball == 'team1' else 0
            players_closer_to_ball_team2 = 1 if team_closer_to_ball == 'team2' else 0
            norm_ball_team1 = players_closer_to_ball_team1 / 1 
            norm_ball_team2 = players_closer_to_ball_team2 / 1
            score_team_1 = (w_ball * norm_ball_team1) + (w_area * norm_area_team_1)  + (w_n_players * norm_n_players_team_1)
            score_team_2 = (w_ball * norm_ball_team2) + (w_area * norm_area_team_2)  + (w_n_players * norm_n_players_team_2)
            total_score = score_team_1 + score_team_2
            percent_1 = (score_team_1/total_score) * 100
            percent_2 = (score_team_2/total_score) * 100
        elif _case == "g":
            norm_distance_team_1 = 1 - (counter_team_1 / max_players_near_goalkeeper)
            norm_distance_team_2 = 1 - (counter_team_2 / max_players_near_goalkeeper)
            score_team_1 = (w_area * norm_area_team_1) + (w_distance * norm_distance_team_1) + (w_n_players * norm_n_players_team_1)
            score_team_2 = (w_area * norm_area_team_2) + (w_distance * norm_distance_team_2) + (w_n_players * norm_n_players_team_2)
            total_score = score_team_1 + score_team_2
            percent_1 = (score_team_1/total_score) * 100
            percent_2 = (score_team_2/total_score) * 100
        else:  # case "None"
            score_team_1 = (w_area * norm_area_team_1) + (w_n_players * norm_n_players_team_1)
            score_team_2 = (w_area * norm_area_team_2) + (w_n_players * norm_n_players_team_2)
            total_score = score_team_1 + score_team_2
            percent_1 = (score_team_1/total_score) * 100
            percent_2 = (score_team_2/total_score) * 100
            
        return percent_1, percent_2   

    """
    Calcolo coordinate di tutti i giocatori, portiere e palla (se esistono)
    come tuple (x1,y1)
    """
    existGoalkeeper = False
    existBall = False
    coordinates_team_1 = []
    coordinates_team_2 = []
    coordinates_goalkeeper = []
    coordinates_ball = []
    for key,value in players_classification.items():
        for box in value:
            x1,y1,x2,y2 = box
            center = (int((x1+x2)//2), int((y1+y2)//2))
            if key == 0:
                coordinates_team_1.append(center)
            elif key == 1:
                coordinates_team_2.append(center)
            elif key == 'goalkeeper':
                existGoalkeeper = True
                coordinates_goalkeeper.append(center)
            elif key == 'ball':
                existBall = True
                coordinates_ball.append(center)

    """
    Converto tutto in np array
    """
    coordinates_team_1 = np.array(coordinates_team_1)
    coordinates_team_2 = np.array(coordinates_team_2)
    coordinates_goalkeeper = np.array(coordinates_goalkeeper)
    coordinates_ball = np.array(coordinates_ball)

    # ottiene aree giocatori delle due squadre
    area_points_team_1, area_points_team_2 = getAreas(coordinates_team_1, coordinates_team_2)

    #ottieni numero giocatori più vicini al portiere delle due squadre
    counter_team_1, counter_team_2, max_players_near_goalkeeper = getPlayerCloserToGoalkeeper(coordinates_team_1, coordinates_team_2, coordinates_goalkeeper)

    """
    Calcolo numero giocatori
    """
    n_players_team_1 = len(players_classification[0])
    n_players_team_2 = len(players_classification[1])

    # ottieni la squadra più vicina alla palla
    team_closer_to_ball = getTeamCloserToBall(coordinates_team_1, coordinates_team_2, coordinates_ball)

    #calcola le percentuali di attacco delle due squadre
    percent_team_1, percent_team_2 = getPercentages(area_points_team_1, area_points_team_2, n_players_team_1, n_players_team_2, max_players_near_goalkeeper, counter_team_1, counter_team_2, team_closer_to_ball)

    return percent_team_1, percent_team_2
