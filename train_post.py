import csv, time, torch
from pathlib import Path
from torch.utils.data import DataLoader
from data import KATECDDataset
from models.unet import UNet

ROOT = Path(__file__).resolve().parent
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
EPOCHS, BATCH, LR, PATIENCE = 50, 8, 1e-4, 20
CKPT = ROOT / "checkpoints" / "post_best.pth"
LOG = ROOT / "logs" / "train_post.csv"
torch.manual_seed(42)

train_loader = DataLoader(KATECDDataset("train", mode="post"), batch_size=BATCH, shuffle=True)
val_loader = DataLoader(KATECDDataset("validation", mode="post"), batch_size=BATCH, shuffle=False)

model = UNet(in_channels=3, out_channels=1).to(DEVICE)
opt = torch.optim.Adam(model.parameters(), lr=LR)
loss_fn = torch.nn.BCEWithLogitsLoss()

def run_epoch(loader, train):
    model.train(train)
    total_loss, inter, ssum = 0.0, 0.0, 0.0
    with torch.set_grad_enabled(train):
        for batch in loader:
            x = batch["image"].to(DEVICE)
            y = batch["label"].to(DEVICE)
            logits = model(x)
            loss = loss_fn(logits, y)
            if train:
                opt.zero_grad()
                loss.backward()
                opt.step()
            total_loss += loss.item() * x.size(0)
            pred = (torch.sigmoid(logits) > 0.5).float()
            inter += (pred * y).sum().item()
            ssum += pred.sum().item() + y.sum().item()
    return total_loss / len(loader.dataset), 2 * inter / (ssum + 1e-6)

CKPT.parent.mkdir(exist_ok=True)
LOG.parent.mkdir(exist_ok=True)
best, wait = float("inf"), 0
with open(LOG, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["epoch", "train_loss", "train_dice", "val_loss", "val_dice", "sure_s"])
    for ep in range(1, EPOCHS + 1):
        t0 = time.time()
        tr_l, tr_d = run_epoch(train_loader, True)
        va_l, va_d = run_epoch(val_loader, False)
        w.writerow([ep, tr_l, tr_d, va_l, va_d, round(time.time() - t0, 1)])
        f.flush()
        mark = ""
        if va_l < best:
            best, wait = va_l, 0
            torch.save(model.state_dict(), CKPT)
            mark = "  <- en iyi"
        else:
            wait += 1
        print("ep {:2d} | train {:.4f} / dice {:.3f} | val {:.4f} / dice {:.3f}{}".format(ep, tr_l, tr_d, va_l, va_d, mark), flush=True)
        if wait >= PATIENCE:
            print("Erken durma:", PATIENCE, "epoch iyilesme yok")
            break
print("En iyi val loss:", best)
