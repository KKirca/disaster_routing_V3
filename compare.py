import torch
from pathlib import Path
from torch.utils.data import DataLoader
from data import KATECDDataset
from models.unet import UNet

ROOT = Path(__file__).resolve().parent
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def evaluate(ckpt, mode, threshold=0.5):
    # Tum test seti uzerinde TP / FP / FN piksel sayilarini toplar (global).
    model = UNet(in_channels=6 if mode == "prepost" else 3, out_channels=1).to(DEVICE)
    state = torch.load(ROOT / "checkpoints" / ckpt, map_location=DEVICE, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    loader = DataLoader(KATECDDataset("test", mode=mode), batch_size=8, shuffle=False)
    tp = fp = fn = 0.0
    with torch.no_grad():
        for b in loader:
            y = b["label"].to(DEVICE)
            p = (torch.sigmoid(model(b["image"].to(DEVICE))) > threshold).float()
            tp += (p * y).sum().item()
            fp += (p * (1 - y)).sum().item()
            fn += ((1 - p) * y).sum().item()
    return tp, fp, fn


def metrics(tp, fp, fn, e=1e-6):
    return (2 * tp / (2 * tp + fp + fn + e), tp / (tp + fp + fn + e),
            tp / (tp + fp + e), tp / (tp + fn + e))


print("{:<9} {:>7} {:>7} {:>10} {:>7}".format("model", "dice", "iou", "precision", "recall"))
for name, ckpt, mode in (("6 kanal", "best_model.pth", "prepost"), ("3 kanal", "post_best.pth", "post")):
    d, i, p, r = metrics(*evaluate(ckpt, mode))
    print("{:<9} {:>7.4f} {:>7.4f} {:>10.4f} {:>7.4f}".format(name, d, i, p, r))
