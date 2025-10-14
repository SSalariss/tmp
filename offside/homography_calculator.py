import os
import numpy as np
import torch
import imageio
from PIL import Image

from sportsfield_release.utils import util
from sportsfield_release.utils import image_utils, constant_var
from sportsfield_release.models import end_2_end_optimization
from sportsfield_release.options import fake_options


def calculateOptimHomography(imagePath: str) -> torch.Tensor:
    """
    Calcola la matrice di omografia ottimale per un'immagine di campo da calcio.
    
    Args:
        imagePath (str): Percorso dell'immagine del campo
        
    Returns:
        torch.Tensor: Matrice di omografia ottimizzata
    """
    # Configurazione GPU/CPU
    constant_var.USE_CUDA = False
    util.fix_randomness()
    torch.backends.cudnn.enabled = True

    # Configurazione opzioni
    opt = fake_options.FakeOptions()
    opt.batch_size = 1
    opt.coord_conv_template = True
    opt.error_model = 'loss_surface'
    opt.error_target = 'iou_whole'
    opt.goal_image_path = imagePath
    opt.guess_model = 'init_guess'
    opt.homo_param_method = 'deep_homography'
    opt.load_weights_error_model = 'pretrained_loss_surface'
    opt.load_weights_upstream = 'pretrained_init_guess'
    opt.lr_optim = 1e-5
    opt.need_single_image_normalization = True
    opt.need_spectral_norm_error_model = True
    opt.need_spectral_norm_upstream = False
    opt.optim_criterion = 'l1loss'
    opt.optim_iters = 200
    opt.optim_method = 'stn'
    opt.optim_type = 'adam'
    opt.out_dir = 'sportsfield_release/out'
    opt.prevent_neg = 'sigmoid'
    opt.template_path = 'sportsfield_release/data/world_cup_template.png'
    opt.warp_dim = 8
    opt.warp_type = 'homography'

    # Carica e preprocessa immagine obiettivo
    goal_image = imageio.imread(opt.goal_image_path, pilmode='RGB')
    
    # Ridimensiona a 256x256 e normalizza
    pil_image = Image.fromarray(np.uint8(goal_image))
    pil_image = pil_image.resize([256, 256], resample=Image.NEAREST)
    goal_image = np.array(pil_image)
    
    # Converte a tensor PyTorch e normalizza
    goal_image = util.np_img_to_torch_img(goal_image)
    if opt.need_single_image_normalization:
        goal_image = image_utils.normalize_single_image(goal_image)
    
    print(f'Goal image - Mean: {goal_image.mean():.4f}, Std: {goal_image.std():.4f}')

    # Carica e preprocessa template
    template_image = imageio.imread(opt.template_path, pilmode='RGB')
    template_image = template_image / 255.0
    if opt.coord_conv_template:
        template_image = image_utils.rgb_template_to_coord_conv_template(template_image)
    
    template_image = util.np_img_to_torch_img(template_image)
    if opt.need_single_image_normalization:
        template_image = image_utils.normalize_single_image(template_image)

    # Inizializza e esegue ottimizzazione end-to-end
    e2e = end_2_end_optimization.End2EndOptimFactory.get_end_2_end_optimization_model(opt)
    orig_homography, optim_homography = e2e.optim(goal_image[None], template_image)
    
    print("Omografia calcolata con successo!")
    return optim_homography

def save_homography(homography: torch.Tensor, save_path: str):
    """Salva la matrice di omografia su disco."""
    torch.save(homography, save_path)
    print(f"Omografia salvata in: {save_path}")

def load_homography(load_path: str) -> torch.Tensor:
    """Carica la matrice di omografia da disco."""
    homography = torch.load(load_path)
    print(f"Omografia caricata da: {load_path}")
    return homography
