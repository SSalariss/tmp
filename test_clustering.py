import cv2
from color_clustering.clustering import cluster_players

def test_clustering():
    image_path = "data/test_image.jpg"
    image = cv2.imread(image_path)
    if image is None:
        print("Immagine non trovata")
        return

    # Aggiungi boxes e classes di esempio o usa quelli reali del detector se preferisci
    # Qui metti un esempio manuale:
    boxes = [[50, 50, 100, 150], [120, 60, 170, 160], [200, 80, 250, 180]]
    classes = [0, 0, 0]

    teams = cluster_players(boxes, classes, image)
    print("Team 0:", teams[0])
    print("Team 1:", teams[1])

    assert 0 in teams and 1 in teams, "I team non sono stati creati correttamente"
    assert len(teams[0]) + len(teams[1]) == 3, "Alcuni giocatori persi nella clusterizzazione"

if __name__ == "__main__":
    test_clustering()
