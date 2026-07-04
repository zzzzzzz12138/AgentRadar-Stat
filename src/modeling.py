from __future__ import annotations

from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, balanced_accuracy_score, brier_score_loss, confusion_matrix, f1_score, precision_recall_curve, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .model_tasks import NO_LEAKAGE_FEATURES, add_model_task_labels
from .utils import project_path, write_json


FEATURE_COLUMNS = NO_LEAKAGE_FEATURES
TASKS = {
    "task_a": {"label": "task_a_high_potential", "title": "Task A scoring-system proxy"},
    "task_b": {"label": "task_b_proxy_good_project", "title": "Task B project-potential proxy"},
}


def train_models(config: dict[str, Any]) -> dict[str, Any]:
    """Train leakage-aware sklearn models for task A and task B."""
    df = pd.read_csv(project_path(config["paths"]["scored_repos"]))
    if "task_a_high_potential" not in df.columns or "task_b_proxy_good_project" not in df.columns:
        df = add_model_task_labels(df)
    results: dict[str, Any] = {}
    thresholds: list[dict[str, Any]] = []
    permutations: list[dict[str, Any]] = []
    all_importance: list[dict[str, Any]] = []
    calibration: dict[str, Any] = {}
    for task_name, task in TASKS.items():
        task_result = _train_task(df, task_name, task["label"], config)
        results[task_name] = task_result["metrics"]
        thresholds.extend(task_result["thresholds"])
        permutations.extend(task_result["permutation"])
        all_importance.extend(task_result["importance"])
        calibration[task_name] = task_result["calibration"]
        pd.DataFrame(task_result["metrics"]).to_csv(project_path(f"outputs/reports/model_metrics_{task_name}.csv"), index=False, encoding="utf-8-sig")
        pd.DataFrame(task_result["importance"]).to_csv(project_path(f"outputs/reports/feature_importance_{task_name}.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame(thresholds).to_csv(project_path("outputs/reports/model_thresholds.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame(permutations).to_csv(project_path("outputs/reports/permutation_importance.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame(all_importance).to_csv(project_path("outputs/reports/feature_importance.csv"), index=False, encoding="utf-8-sig")
    write_json("outputs/reports/model_calibration.json", calibration)
    _write_compat_outputs(results)
    _write_model_card(results)
    return results


def _train_task(df: pd.DataFrame, task_name: str, label_col: str, config: dict[str, Any]) -> dict[str, Any]:
    y = df[label_col].astype(int)
    X = df[[col for col in FEATURE_COLUMNS if col in df.columns]].apply(pd.to_numeric, errors="coerce").fillna(0)
    if y.nunique() < 2 or len(df) < 20:
        return {"metrics": [{"model_name": "skipped", "reason": "not enough class diversity"}], "thresholds": [], "importance": [], "permutation": [], "calibration": {}}
    random_state = config.get("modeling", {}).get("random_state", 42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=config.get("modeling", {}).get("test_size", 0.25), random_state=random_state, stratify=y)
    cv_splits = 5 if y_train.value_counts().min() >= 5 else 3
    models = {
        "dummy": DummyClassifier(strategy="most_frequent"),
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=700, class_weight="balanced")),
        "random_forest": RandomForestClassifier(n_estimators=120, random_state=random_state, class_weight="balanced"),
        "extra_trees": ExtraTreesClassifier(n_estimators=120, random_state=random_state, class_weight="balanced"),
        "gradient_boosting": GradientBoostingClassifier(random_state=random_state),
        "calibrated_random_forest": CalibratedClassifierCV(RandomForestClassifier(n_estimators=80, random_state=random_state, class_weight="balanced"), cv=3),
    }
    metrics_rows: list[dict[str, Any]] = []
    importance_rows: list[dict[str, Any]] = []
    permutation_rows: list[dict[str, Any]] = []
    threshold_rows: list[dict[str, Any]] = []
    calibration_rows: dict[str, Any] = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        scores = _scores(model, X_test)
        metric = _metrics(y_test, preds, scores)
        cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=random_state)
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring="f1")
        metrics_rows.append({"task": task_name, "model_name": name, **metric, "train_size": len(X_train), "test_size": len(X_test), "cv_mean": float(cv_scores.mean()), "cv_std": float(cv_scores.std())})
        importance_rows.extend(_extract_importance(task_name, name, model, X.columns))
        threshold_rows.extend(_thresholds(task_name, name, y_test, scores))
        calibration_rows[name] = _calibration(y_test, scores)
        if name in {"random_forest", "extra_trees", "gradient_boosting"}:
            permutation_rows.extend(_permutation(task_name, name, model, X_test, y_test, X.columns))
        joblib.dump(model, project_path(f"outputs/models/{task_name}_{name}.joblib"))
    return {"metrics": metrics_rows, "importance": importance_rows, "permutation": permutation_rows, "thresholds": threshold_rows, "calibration": calibration_rows}


def _scores(model: Any, X: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        return 1 / (1 + np.exp(-model.decision_function(X)))
    return model.predict(X)


def _metrics(y_true: pd.Series, preds: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    out = {
        "accuracy": float(accuracy_score(y_true, preds)),
        "precision": float(precision_score(y_true, preds, zero_division=0)),
        "recall": float(recall_score(y_true, preds, zero_division=0)),
        "f1": float(f1_score(y_true, preds, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, preds)),
        "brier_score_loss": float(brier_score_loss(y_true, np.clip(scores, 0, 1))),
        "confusion_matrix": confusion_matrix(y_true, preds).tolist(),
    }
    try:
        out["roc_auc"] = float(roc_auc_score(y_true, scores))
    except ValueError:
        out["roc_auc"] = None
    try:
        out["average_precision"] = float(average_precision_score(y_true, scores))
    except ValueError:
        out["average_precision"] = None
    return out


def _thresholds(task: str, model: str, y_true: pd.Series, scores: np.ndarray) -> list[dict[str, Any]]:
    precision, recall, thresholds = precision_recall_curve(y_true, scores)
    rows: list[dict[str, Any]] = []
    candidates = {"default_0.5": 0.5}
    if len(thresholds):
        f1_values = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-9)
        candidates["best_f1"] = float(thresholds[int(np.nanargmax(f1_values))])
        high_recall = np.where(recall[:-1] >= 0.85)[0]
        high_precision = np.where(precision[:-1] >= 0.85)[0]
        candidates["high_recall"] = float(thresholds[high_recall[-1]]) if len(high_recall) else 0.3
        candidates["high_precision"] = float(thresholds[high_precision[0]]) if len(high_precision) else 0.7
    for name, threshold in candidates.items():
        pred = (scores >= threshold).astype(int)
        rows.append({"task": task, "model_name": model, "threshold_name": name, "threshold": threshold, "precision": float(precision_score(y_true, pred, zero_division=0)), "recall": float(recall_score(y_true, pred, zero_division=0)), "f1": float(f1_score(y_true, pred, zero_division=0))})
    return rows


def _extract_importance(task: str, model_name: str, model: Any, columns: pd.Index) -> list[dict[str, Any]]:
    estimator = model[-1] if hasattr(model, "steps") else model
    if hasattr(estimator, "feature_importances_"):
        values, kind = estimator.feature_importances_, "feature_importance"
    elif hasattr(estimator, "coef_"):
        values, kind = estimator.coef_[0], "coefficient"
    else:
        return []
    return [{"task": task, "model_name": model_name, "feature": col, "importance": float(val), "abs_importance": float(abs(val)), "importance_type": kind} for col, val in zip(columns, values)]


def _permutation(task: str, model_name: str, model: Any, X_test: pd.DataFrame, y_test: pd.Series, columns: pd.Index) -> list[dict[str, Any]]:
    result = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42, scoring="f1")
    return [{"task": task, "model_name": model_name, "feature": col, "importance_mean": float(mean), "importance_std": float(std)} for col, mean, std in zip(columns, result.importances_mean, result.importances_std)]


def _calibration(y_true: pd.Series, scores: np.ndarray) -> dict[str, Any]:
    frac, mean_pred = calibration_curve(y_true, np.clip(scores, 0, 1), n_bins=5, strategy="uniform")
    return {"mean_predicted_value": mean_pred.tolist(), "fraction_of_positives": frac.tolist(), "brier_score_loss": float(brier_score_loss(y_true, np.clip(scores, 0, 1)))}


def _write_compat_outputs(results: dict[str, Any]) -> None:
    task_a = pd.DataFrame(results["task_a"])
    task_a.to_csv(project_path("outputs/reports/model_metrics.csv"), index=False, encoding="utf-8-sig")
    write_json("outputs/reports/model_metrics.json", results)
    write_json("outputs/models/model_metrics.json", results)
    if not task_a.empty and "f1" in task_a:
        best = task_a.sort_values("f1", ascending=False).iloc[0]
        project_path("outputs/reports/model_explanation.md").write_text(f"# Model Explanation\n\nBest Task A model: {best['model_name']} with F1={best['f1']:.3f}.\n\nTask B is reported in `model_metrics_task_b.csv`. Probability scores are model confidence estimates, not true future-success probabilities.", encoding="utf-8")


def _write_model_card(results: dict[str, Any]) -> None:
    def best(task: str) -> str:
        df = pd.DataFrame(results[task])
        if df.empty or "f1" not in df:
            return "n/a"
        row = df.sort_values("f1", ascending=False).iloc[0]
        return f"{row['model_name']} (F1={row['f1']:.3f})"
    md = [
        "# Model Card",
        "## Task definitions",
        "- Task A: scoring-system proxy model; label is A/B recommendation level. Purpose is scoring-rule explanation.",
        "- Task B: project-potential proxy model; label combines emerging, reproduction-friendly, and high-attention-low-risk signals.",
        "## Leakage control",
        "Inputs exclude `final_potential_score`, `recommendation_level`, and sub-score fields directly used by scoring.",
        "## Feature set",
        ", ".join(FEATURE_COLUMNS),
        "## Model selection",
        "Compared Dummy, Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and calibrated Random Forest with stratified CV.",
        f"Best Task A model: {best('task_a')}",
        f"Best Task B model: {best('task_b')}",
        "## Boundaries",
        "Proxy models over public GitHub metadata and README-derived signals; not forecasts of commercial value or future popularity.",
    ]
    project_path("outputs/reports/model_card.md").write_text("\n\n".join(md), encoding="utf-8")
