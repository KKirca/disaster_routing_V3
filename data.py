import torch
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset
from datasets import load_from_disk

# Veri yolu bu dosyanin konumuna gore cozulur, calisma dizinine gore degil.
DATA_DIR = Path(__file__).resolve().parent / "data" / "kate_cd"

class KATECDDataset(Dataset):
    # On isleme egitimle birebir: /255, HWC -> CHW.
    # mode="prepost": 6 kanal [pre, post]  |  mode="post": 3 kanal, sadece post
    def __init__(self, split="test", data_dir=DATA_DIR, mode="prepost"):
        if mode not in ("prepost", "post"):
            raise ValueError("mode 'prepost' ya da 'post' olmali, verilen: " + str(mode))
        self.dataset = load_from_disk(str(data_dir))[split]
        self.mode = mode

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        sample = self.dataset[idx]
        post = np.array(sample["post_image"], dtype=np.float32) / 255.0
        label = np.array(sample["label"], dtype=np.float32) / 255.0
        post = torch.from_numpy(post).permute(2, 0, 1)
        label = torch.from_numpy(label).unsqueeze(0)
        if self.mode == "post":
            return {"image": post, "label": label}
        pre = np.array(sample["pre_image"], dtype=np.float32) / 255.0
        pre = torch.from_numpy(pre).permute(2, 0, 1)
        image = torch.cat([pre, post], dim=0)
        return {"image": image, "label": label}
