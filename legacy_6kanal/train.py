import torch
import torch.nn as nn
import torch.optim as optim
from models.unet import UNet
from utils import get_dataloaders, DiceScore, IoU
import os
from tqdm import tqdm

EPOCHS = 50
BATCH_SIZE = 8
LEARNING_RATE = 1e-4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Device:", DEVICE)
os.makedirs("checkpoints", exist_ok=True)

print("Loading KATE-CD...")
train_loader, val_loader, test_loader = get_dataloaders(batch_size=BATCH_SIZE, num_workers=0)
print(f"Train: {len(train_loader)} batches, Val: {len(val_loader)} batches")

model = UNet(in_channels=6, out_channels=1).to(DEVICE)
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
dice = DiceScore()

best_val_loss = float('inf')

for epoch in range(EPOCHS):
    model.train()
    train_loss = 0.0
    
    for batch in train_loader:
        image = batch['image'].to(DEVICE)
        label = batch['label'].to(DEVICE)
        
        optimizer.zero_grad()
        pred = model(image)
        loss = criterion(pred, label)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    
    train_loss /= len(train_loader)
    
    model.eval()
    val_loss = 0.0
    val_dice = 0.0
    
    with torch.no_grad():
        for batch in val_loader:
            image = batch['image'].to(DEVICE)
            label = batch['label'].to(DEVICE)
            pred = model(image)
            loss = criterion(pred, label)
            d = dice(torch.sigmoid(pred), label)
            val_loss += loss.item()
            val_dice += d.item()
    
    val_loss /= len(val_loader)
    val_dice /= len(val_loader)
    
    print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {train_loss:.4f} | Val: {val_loss:.4f} | Dice: {val_dice:.4f}")
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), "checkpoints/best_model.pth")
        print("  → Best checkpoint saved")

print(f"\nDone! Best val loss: {best_val_loss:.4f}")
