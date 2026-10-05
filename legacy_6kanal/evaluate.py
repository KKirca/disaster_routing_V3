import torch
from models.unet import UNet
from utils import get_dataloaders, DiceScore, IoU

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load best model
model = UNet(in_channels=6, out_channels=1).to(DEVICE)
model.load_state_dict(torch.load("checkpoints/best_model.pth"))
model.eval()

# Load test data
_, _, test_loader = get_dataloaders(batch_size=8, num_workers=0)

# Metrics
criterion = torch.nn.BCEWithLogitsLoss()
dice = DiceScore()
iou = IoU()

test_loss = 0.0
test_dice = 0.0
test_iou = 0.0

print("Evaluating on test set...")
with torch.no_grad():
    for batch in test_loader:
        image = batch['image'].to(DEVICE)
        label = batch['label'].to(DEVICE)
        
        pred = model(image)
        loss = criterion(pred, label)
        d = dice(torch.sigmoid(pred), label)
        i = iou(torch.sigmoid(pred), label)
        
        test_loss += loss.item()
        test_dice += d.item()
        test_iou += i.item()

test_loss /= len(test_loader)
test_dice /= len(test_loader)
test_iou /= len(test_loader)

print(f"\n=== TEST SET RESULTS ===")
print(f"Loss:  {test_loss:.4f}")
print(f"Dice:  {test_dice:.4f}")
print(f"IoU:   {test_iou:.4f}")
