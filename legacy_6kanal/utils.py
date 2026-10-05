import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset

class KATECDDataset(Dataset):
    def __init__(self, split="train", augment=False):
        self.dataset = load_dataset("CSCRS/kate-cd", split=split)
        self.augment = augment
    
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        sample = self.dataset[idx]
        pre = np.array(sample['pre_image'], dtype=np.float32) / 255.0
        post = np.array(sample['post_image'], dtype=np.float32) / 255.0
        label = np.array(sample['label'], dtype=np.float32) / 255.0
        
        pre = torch.from_numpy(pre).permute(2, 0, 1)
        post = torch.from_numpy(post).permute(2, 0, 1)
        label = torch.from_numpy(label).unsqueeze(0)
        
        image = torch.cat([pre, post], dim=0)
        return {'image': image, 'label': label}

def get_dataloaders(batch_size=8, num_workers=0):
    train_ds = KATECDDataset(split="train", augment=True)
    val_ds = KATECDDataset(split="validation", augment=False)
    test_ds = KATECDDataset(split="test", augment=False)
    
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    
    return train_loader, val_loader, test_loader

class DiceScore(torch.nn.Module):
    def forward(self, pred, target):
        pred = (pred > 0.5).float()
        intersection = (pred * target).sum()
        union = pred.sum() + target.sum()
        return 2.0 * intersection / (union + 1e-6)

class IoU(torch.nn.Module):
    def forward(self, pred, target):
        pred = (pred > 0.5).float()
        intersection = (pred * target).sum()
        union = (pred + target - pred * target).sum()
        return intersection / (union + 1e-6)
