import torch
from pathlib import Path
from torch.utils.data import DataLoader
from data import KATECDDataset
from models.unet import UNet

ROOT = Path(__file__).resolve().parent
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = UNet(in_channels=6, out_channels=1).to(DEVICE)
state = torch.load(ROOT / "checkpoints" / "best_model.pth", map_location=DEVICE, weights_only=True)
model.load_state_dict(state)
model.eval()

loader = DataLoader(KATECDDataset("test"), batch_size=8, shuffle=False)

batch_dice = []
inter_total = 0.0
sum_total = 0.0
with torch.no_grad():
    for batch in loader:
        x = batch["image"].to(DEVICE)
        y = batch["label"].to(DEVICE)
        pred = (torch.sigmoid(model(x)) > 0.5).float()
        inter = (pred * y).sum().item()
        s = pred.sum().item() + y.sum().item()
        batch_dice.append(2 * inter / (s + 1e-6))
        inter_total += inter
        sum_total += s

print("Batch ortalamasi Dice:", sum(batch_dice) / len(batch_dice))
print("Global Dice          :", 2 * inter_total / (sum_total + 1e-6))
