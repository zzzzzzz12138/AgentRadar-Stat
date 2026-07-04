from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from .model_tasks import NO_LEAKAGE_FEATURES, add_model_task_labels
from .utils import project_path


CATEGORICAL_FEATURES = ["language", "license", "topic_label", "cluster_name", "source_type"]


def train_torch_tabular(config: dict[str, Any]) -> dict[str, Any]:
    """Train a CPU-friendly wide/deep tabular neural net for task B."""
    try:
        import torch
        from torch import nn
        from torch.utils.data import DataLoader, TensorDataset
    except Exception as exc:  # noqa: BLE001
        result = {"status": "skipped", "reason": f"torch unavailable: {exc}"}
        _write_json("outputs/reports/torch_model_metrics.json", result)
        _write_model_card(result)
        return result

    started = time.perf_counter()
    df = pd.read_csv(project_path(config["paths"]["scored_repos"]))
    df = add_model_task_labels(df)
    target = "task_b_proxy_good_project"
    y = df[target].astype("float32")
    if y.nunique() < 2 or len(df) < 30:
        result = {"status": "skipped", "reason": "not enough rows or class diversity for tabular net"}
        _write_json("outputs/reports/torch_model_metrics.json", result)
        _write_model_card(result)
        return result

    seed = int(config.get("modeling", {}).get("random_state", 42))
    torch.manual_seed(seed)
    np.random.seed(seed)
    numeric_cols = [col for col in NO_LEAKAGE_FEATURES if col in df.columns]
    cat_cols = [col for col in CATEGORICAL_FEATURES if col in df.columns]
    X_num = df[numeric_cols].apply(pd.to_numeric, errors="coerce").fillna(0).astype("float32")
    X_num = ((X_num - X_num.mean()) / X_num.std().replace(0, 1)).fillna(0).astype("float32")
    cat_maps = {}
    cat_arrays = []
    for col in cat_cols:
        codes, uniques = pd.factorize(df[col].fillna("unknown").astype(str), sort=True)
        cat_maps[col] = {str(value): int(i) for i, value in enumerate(uniques)}
        cat_arrays.append(codes.astype("int64"))
    X_cat = np.vstack(cat_arrays).T if cat_arrays else np.zeros((len(df), 0), dtype="int64")

    idx = np.arange(len(df))
    train_idx, temp_idx = train_test_split(idx, test_size=0.30, stratify=y, random_state=seed)
    valid_idx, test_idx = train_test_split(temp_idx, test_size=0.50, stratify=y.iloc[temp_idx], random_state=seed)
    train_loader = _loader(torch, X_num.values, X_cat, y.values, train_idx, shuffle=True)
    valid_loader = _loader(torch, X_num.values, X_cat, y.values, valid_idx)
    test_loader = _loader(torch, X_num.values, X_cat, y.values, test_idx)

    model = TabularWideDeepNet(nn, num_numeric=len(numeric_cols), cat_cardinalities=[len(cat_maps[c]) for c in cat_cols])
    opt = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", factor=0.6, patience=2)
    loss_fn = nn.BCELoss()
    best_state = None
    best_valid = float("inf")
    patience = 4
    waited = 0
    history = []
    max_epochs = int(config.get("modeling", {}).get("torch_epochs", 18))
    for epoch in range(1, max_epochs + 1):
        model.train()
        train_loss = 0.0
        for xb_num, xb_cat, yb in train_loader:
            opt.zero_grad()
            pred = model(xb_num, xb_cat)
            loss = loss_fn(pred, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            opt.step()
            train_loss += float(loss.item())
        valid_loss, valid_auc, valid_f1 = _evaluate(model, valid_loader, loss_fn)
        scheduler.step(valid_loss)
        row = {"epoch": epoch, "train_loss": train_loss / max(1, len(train_loader)), "valid_loss": valid_loss, "valid_auc": valid_auc, "valid_f1": valid_f1}
        history.append(row)
        if valid_loss < best_valid:
            best_valid = valid_loss
            best_state = {key: value.detach().clone() for key, value in model.state_dict().items()}
            waited = 0
        else:
            waited += 1
        if waited >= patience:
            break
    if best_state:
        model.load_state_dict(best_state)
    test_loss, test_auc, test_f1 = _evaluate(model, test_loader, loss_fn)
    model_path = project_path("outputs/models/torch_tabular_widedeep.pt")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": model.state_dict(), "numeric_cols": numeric_cols, "categorical_cols": cat_cols, "cat_maps": cat_maps}, model_path)

    hist = pd.DataFrame(history)
    hist_path = project_path("outputs/reports/torch_training_history.csv")
    hist_path.parent.mkdir(parents=True, exist_ok=True)
    hist.to_csv(hist_path, index=False, encoding="utf-8-sig")
    fig_path = _plot_history(hist)
    result = {
        "status": "ok",
        "model_name": "TabularWideDeepNet",
        "task": "task_b_proxy_good_project",
        "train_size": int(len(train_idx)),
        "valid_size": int(len(valid_idx)),
        "test_size": int(len(test_idx)),
        "best_epoch": int(hist.sort_values("valid_loss").iloc[0]["epoch"]) if not hist.empty else None,
        "early_stop_epoch": int(history[-1]["epoch"]) if history else None,
        "valid_auc": float(max(item["valid_auc"] for item in history if item["valid_auc"] == item["valid_auc"])) if history else None,
        "valid_f1": float(max(item["valid_f1"] for item in history)) if history else None,
        "test_auc": test_auc,
        "test_f1": test_f1,
        "test_loss": test_loss,
        "parameter_count": int(sum(p.numel() for p in model.parameters())),
        "training_seconds": round(time.perf_counter() - started, 3),
        "device": "cpu",
        "model_path": str(model_path),
        "history_path": str(hist_path),
        "training_curve_path": str(fig_path),
    }
    _write_json("outputs/reports/torch_model_metrics.json", result)
    _write_model_card(result)
    return result


class TabularWideDeepNet:  # factory wrapper keeps torch import optional at module import time.
    def __new__(cls, nn: Any, num_numeric: int, cat_cardinalities: list[int]):
        import torch

        class _Net(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.embeddings = nn.ModuleList([nn.Embedding(max(2, size), min(8, max(2, (size + 1) // 2))) for size in cat_cardinalities])
                emb_dim = sum(emb.embedding_dim for emb in self.embeddings)
                self.numeric = nn.Sequential(nn.BatchNorm1d(num_numeric), nn.Linear(num_numeric, 32), nn.GELU(), nn.Dropout(0.15))
                deep_in = 32 + emb_dim
                self.deep = nn.Sequential(nn.Linear(deep_in, 48), nn.GELU(), nn.Dropout(0.20), nn.Linear(48, 24), nn.GELU())
                self.wide = nn.Linear(num_numeric, 1)
                self.out = nn.Linear(24 + 1, 1)

            def forward(self, x_num: Any, x_cat: Any) -> Any:
                if self.embeddings and x_cat.shape[1] > 0:
                    emb = torch.cat([emb(x_cat[:, i]) for i, emb in enumerate(self.embeddings)], dim=1)
                else:
                    emb = x_num.new_zeros((x_num.shape[0], 0))
                deep = self.deep(torch.cat([self.numeric(x_num), emb], dim=1))
                wide = self.wide(x_num)
                return torch.sigmoid(self.out(torch.cat([deep, wide], dim=1)))

        return _Net()


def _loader(torch: Any, x_num: np.ndarray, x_cat: np.ndarray, y: np.ndarray, idx: np.ndarray, shuffle: bool = False) -> Any:
    from torch.utils.data import DataLoader, TensorDataset

    dataset = TensorDataset(torch.tensor(x_num[idx], dtype=torch.float32), torch.tensor(x_cat[idx], dtype=torch.long), torch.tensor(y[idx], dtype=torch.float32).view(-1, 1))
    return DataLoader(dataset, batch_size=32, shuffle=shuffle)


def _evaluate(model: Any, loader: Any, loss_fn: Any) -> tuple[float, float, float]:
    model.eval()
    losses, preds, labels = [], [], []
    with __import__("torch").no_grad():
        for xb_num, xb_cat, yb in loader:
            prob = model(xb_num, xb_cat)
            losses.append(float(loss_fn(prob, yb).item()))
            preds.extend(prob.view(-1).tolist())
            labels.extend(yb.view(-1).tolist())
    auc = float(roc_auc_score(labels, preds)) if len(set(labels)) > 1 else float("nan")
    f1 = float(f1_score(labels, np.array(preds) >= 0.5, zero_division=0))
    return float(np.mean(losses)), auc, f1


def _plot_history(hist: pd.DataFrame) -> Path:
    fig_path = project_path("outputs/figures/torch_training_curve.png")
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 4))
    if not hist.empty:
        plt.plot(hist["epoch"], hist["train_loss"], marker="o", label="train_loss")
        plt.plot(hist["epoch"], hist["valid_loss"], marker="o", label="valid_loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("TabularWideDeepNet Training Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_path, dpi=140)
    plt.close()
    return fig_path


def _write_json(path: str, payload: dict[str, Any]) -> None:
    target = project_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_model_card(metrics: dict[str, Any]) -> None:
    target = project_path("outputs/reports/torch_model_card.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# PyTorch Tabular Model Card",
        "",
        "## Model",
        "TabularWideDeepNet 使用数值特征分支、类别 Embedding 分支和 wide 分支共同建模表格数据。",
        "",
        "## Why This Structure",
        "- AgentRadar-Stat 数据既有连续 GitHub 指标，也有 language、license、cluster_name 等类别字段。",
        "- Embedding 能保留类别字段的可学习表示，数值分支负责 stars、issues、README 等连续信号。",
        "- CPU-only 环境下该结构比大型深度模型更稳妥，训练耗时可控。",
        "",
        "## Task",
        "默认训练 Task B：项目潜力代理预测，不把 final_potential_score 作为输入特征。",
        "",
        "## Metrics",
    ]
    for key, value in metrics.items():
        if key not in {"model_path", "history_path", "training_curve_path"}:
            lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "如果该模型没有超过 sklearn 最佳模型，结论应理解为表格神经网络扩展实验，而不是必须替代树模型。",
            "小样本下树模型通常更稳，神经网络的价值在于展示类别 Embedding、early stopping 和端到端训练流程。",
        ]
    )
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
