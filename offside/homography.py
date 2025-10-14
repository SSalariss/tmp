import torch
import numpy as np

def convertPoint3Dto2D(homography: torch.Tensor, p: list[int], w: int, h: int) -> list[float]:
    """Converte un punto dall'immagine 3D al campo 2D usando omografia."""
    x = torch.tensor(p[0] / w - 0.5).float()
    y = torch.tensor(p[1] / h - 0.5).float()
    xy = torch.stack([x, y, torch.ones_like(x)])
    xy_warped = torch.matmul(homography.cpu(), xy)
    xy_warped, z_warped = xy_warped.split(2, dim=1)
    
    xy_warped = 2.0 * xy_warped / (z_warped + 1e-8)
    x_warped, y_warped = torch.unbind(xy_warped, dim=1)
    
    x_warped = (x_warped.item() * 0.5 + 0.5) * 1050
    y_warped = (y_warped.item() * 0.5 + 0.5) * 680
    
    return [x_warped, y_warped]

def convertPoint2Dto3D(homography: torch.Tensor, p: list[int], w: int, h: int) -> list[float]:
    """Converte un punto dal campo 2D all'immagine 3D usando omografia inversa."""
    x = torch.tensor(p[0] / 1050 - 0.5).float()
    y = torch.tensor(p[1] / 680 - 0.5).float()
    xy = torch.stack([x, y, torch.ones_like(x)])
    xy_warped = torch.matmul(homography.cpu(), xy)
    xy_warped, z_warped = xy_warped.split(2, dim=1)
    
    xy_warped = 2.0 * xy_warped / (z_warped + 1e-8)
    x_warped, y_warped = torch.unbind(xy_warped, dim=1)
    
    x_warped = (x_warped.item() * 0.5 + 0.5) * w
    y_warped = (y_warped.item() * 0.5 + 0.5) * h
    
    return [x_warped, y_warped]
