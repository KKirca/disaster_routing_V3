import torch
import numpy as np
import matplotlib.pyplot as plt
from models.unet import UNet
from utils import get_dataloaders
import os

os.makedirs("test_results", exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = UNet(in_channels=6, out_channels=1).to(DEVICE)
model.load_state_dict(torch.load("checkpoints/best_model.pth"))
model.eval()

# Load test data
_, _, test_loader = get_dataloaders(batch_size=1, num_workers=0)

# Take 10 samples
samples = list(test_loader)[:10]

print("Generating individual predictions...")
with torch.no_grad():
    for idx, batch in enumerate(samples):
        image = batch['image'].to(DEVICE)
        label = batch['label'].to(DEVICE)
        
        # Split pre/post
        pre = image[0, :3].cpu().numpy().transpose(1, 2, 0)
        post = image[0, 3:].cpu().numpy().transpose(1, 2, 0)
        gt = label[0, 0].cpu().numpy()
        
        # Model prediction
        pred = model(image)
        pred_viz = torch.sigmoid(pred)[0, 0].cpu().numpy()
        
        # Create figure with 4 subplots
        fig, axes = plt.subplots(1, 4, figsize=(16, 4))
        
        axes[0].imshow(pre)
        axes[0].set_title(f"Pre-Image #{idx}")
        axes[0].axis('off')
        
        axes[1].imshow(post)
        axes[1].set_title(f"Post-Image #{idx}")
        axes[1].axis('off')
        
        axes[2].imshow(gt, cmap='gray', vmin=0, vmax=1)
        axes[2].set_title(f"Ground Truth #{idx}")
        axes[2].axis('off')
        
        axes[3].imshow(pred_viz, cmap='gray', vmin=0, vmax=1)
        axes[3].set_title(f"Model Prediction #{idx}")
        axes[3].axis('off')
        
        plt.tight_layout()
        fname = f"test_results/sample_{idx:02d}.png"
        plt.savefig(fname, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"  ✓ {fname}")

print(f"\n10 sonuç kaydedildi: test_results/sample_00.png ... sample_09.png")
