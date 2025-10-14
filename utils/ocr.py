from paddleocr import PaddleOCR

ocr_model = None
def get_ocr(lang='en'):
    global ocr_model
    if ocr_model is None:
        ocr_model = PaddleOCR(use_angle_cls=True, lang=lang)
    return ocr_model

def read_plate(image):
    ocr = get_ocr()
    result = ocr.ocr(image)
    texts = [line[1][0] for line in result[0]]
    return ''.join(texts)
