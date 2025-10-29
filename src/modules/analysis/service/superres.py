import torch
from realesrgan import RealESRGANer

_sr_model = None

def get_sr_model():
    global _sr_model
    if _sr_model is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        weight_path = "weights/RealESRGAN_x4plus.pth"

        # inicializa o modelo diretamente, sem load_state_dict
        _sr_model = RealESRGANer(
            scale=4,
            model_path=weight_path,  # obrigatório em v0.3.0
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=True if device=='cuda' else False,
            device=device
        )
    return _sr_model

def enhance(frame):
    return frame