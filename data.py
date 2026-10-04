import torch
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset
from datasets import load_from_disk

# Veri yolu bu dosyanin konumuna gore cozulur, calisma dizinine gore degil.
DATA_DIR = Path(__file__).resolve().parent / "data" / "kate_cd"

class KATECDDataset(Dataset):
    # On isleme egitimle birebir: /255, HWC -> CHW, kanal sirasi [pre, post].
    def __init__(self, split="test", data_dir=DATA_DIR):
        self.dataset = load_from_disk(str(data_dir))[split]

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        sample = self.dataset[idx]
        pre = np.array(sample["pre_image"], dtype=np.float32) / 255.0
        post = np.array(sample["post_image"], dtype=np.float32) / 255.0
        label = np.array(sample["label"], dtype=np.float32) / 255.0
        pre = torch.from_numpy(pre).permute(2, 0, 1)
        post = torch.from_numpy(post).permute(2, 0, 1)
        label = torch.from_numpy(label).unsqueeze(0)
        image = torch.cat([pre, post], dim=0)
        return {"image": image, "label": label}
