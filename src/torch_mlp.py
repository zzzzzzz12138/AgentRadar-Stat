from __future__ import annotations

from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from .modeling import FEATURE_COLUMNS
from .utils import project_path, write_json


def train_torch_mlp(config: dict[str, Any]) -> dict[str, Any]:
    """Train a tiny CPU-only PyTorch MLP when torch is installed."""
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, TensorDataset
    except Exception as exc:  # noqa: BLE001
        result = {"status": "skipped", "reason": f"torch unavailable: {exc}"}
        write_json("outputs/models/torch_mlp_metrics.json", result)
        write_json("outputs/reports/torch_mlp_metrics.json", result)
        return result

    df = pd.read_csv(project_path(config["paths"]["scored_repos"]))
    y = df["recommendation_level"].isin(["A", "B"]).astype("float32")
    if y.nunique() < 2 or len(df) < 20:
        result = {"status": "skipped", "reason": "not enough class diversity"}
        write_json("outputs/models/torch_mlp_metrics.json", result)
        write_json("outputs/reports/torch_mlp_metrics.json", result)
        return result

    torch.manual_seed(config.get("modeling", {}).get("random_state", 42))
    X = df[FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0).astype("float32")
    X = (X - X.mean()) / X.std().replace(0, 1)
    dataset = TensorDataset(torch.tensor(X.values), torch.tensor(y.values).view(-1, 1))
    loader = DataLoader(dataset, batch_size=32, shuffle=True)
    model = nn.Sequential(nn.Linear(len(FEATURE_COLUMNS), 16), nn.ReLU(), nn.Linear(16, 1), nn.Sigmoid())
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.BCELoss()
    losses = []
    for _ in range(int(config.get("modeling", {}).get("torch_epochs", 5))):
        total = 0.0
        for xb, yb in loader:
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            total += float(loss.item())
        losses.append(total / max(1, len(loader)))
    with torch.no_grad():
        preds = (model(torch.tensor(X.values)) >= 0.5).float().view(-1)
        acc = float((preds == torch.tensor(y.values)).float().mean().item())
    torch.save(model.state_dict(), project_path("outputs/models/torch_mlp.pt"))
    torch.save(model.state_dict(), project_path("outputs/models/torch_mlp_baseline.pt"))
    fig_path = project_path("outputs/figures/torch_mlp_loss_curve.png")
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4))
    plt.plot(range(1, len(losses) + 1), losses, marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Binary cross entropy loss")
    plt.title("PyTorch MLP Loss Curve")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=140)
    plt.close()
    result = {
        "status": "ok",
        "accuracy_in_sample": acc,
        "loss_history": losses,
        "loss_curve_path": str(fig_path),
        "model_path": str(project_path("outputs/models/torch_mlp.pt")),
        "baseline_model_path": str(project_path("outputs/models/torch_mlp_baseline.pt")),
        "device": "cpu",
    }
    write_json("outputs/models/torch_mlp_metrics.json", result)
    write_json("outputs/reports/torch_mlp_metrics.json", result)
    return result


