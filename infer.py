import os
import numpy as np
import torch
from pathlib import Path
from models.unet import UNet

ROOT = Path(__file__).resolve().parent
# DEVICE=cpu ile disaridan zorlanabilir (ornegin GPU egitimle doluyken).
DEVICE = os.environ.get("DEVICE") or ("cuda" if torch.cuda.is_available() else "cpu")


def load_model(ckpt="checkpoints/post_best.pth", in_channels=3):
    model = UNet(in_channels=in_channels, out_channels=1).to(DEVICE)
    state = torch.load(ROOT / ckpt, map_location=DEVICE, weights_only=True)
    model.load_state_dict(state)
    return model.eval()


def tile_starts(length, tile, step):
    # Son karo goruntunun kenarina yaslanir: disarida piksel kalmaz, karo disari tasmaz.
    starts = list(range(0, max(length - tile, 0) + 1, step))
    if starts[-1] + tile < length:
        starts.append(length - tile)
    return starts


def predict_prob(model, image, tile=512, overlap=64):
    # image: H x W x 3, uint8 (0-255). Donus: H x W olasilik haritasi (0-1).
    H, W = image.shape[:2]
    img = np.pad(image, ((0, max(tile - H, 0)), (0, max(tile - W, 0)), (0, 0)), mode="reflect")
    Hp, Wp = img.shape[:2]
    x = torch.from_numpy(img.astype(np.float32) / 255.0).permute(2, 0, 1)
    prob_sum = np.zeros((Hp, Wp), dtype=np.float32)
    count = np.zeros((Hp, Wp), dtype=np.float32)
    step = tile - overlap
    with torch.no_grad():
        for r in tile_starts(Hp, tile, step):
            for c in tile_starts(Wp, tile, step):
                patch = x[:, r:r + tile, c:c + tile].unsqueeze(0).to(DEVICE)
                prob_sum[r:r + tile, c:c + tile] += torch.sigmoid(model(patch))[0, 0].cpu().numpy()
                count[r:r + tile, c:c + tile] += 1
    return (prob_sum / count)[:H, :W]
