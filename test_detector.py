from detection.detector import Detector

def test_detector():
    model_path = "model/teamClassification/weights/best.pt"
    image_path = "data/test_image.jpg"

    detector = Detector(model_path)
    boxes, classes = detector.detect(image_path)

    print("Boxes:", boxes)
    print("Classes:", classes)

    assert len(boxes) == len(classes), "Numero box e classi non corrispondono"
    assert len(boxes) > 0, "Nessun oggetto rilevato"

if __name__ == "__main__":
    test_detector()
