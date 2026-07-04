# PyTorch Tabular Model Card

## Model
TabularWideDeepNet 使用数值特征分支、类别 Embedding 分支和 wide 分支共同建模表格数据。

## Why This Structure
- AgentRadar-Stat 数据既有连续 GitHub 指标，也有 language、license、cluster_name 等类别字段。
- Embedding 能保留类别字段的可学习表示，数值分支负责 stars、issues、README 等连续信号。
- CPU-only 环境下该结构比大型深度模型更稳妥，训练耗时可控。

## Task
默认训练 Task B：项目潜力代理预测，不把 final_potential_score 作为输入特征。

## Metrics
- status: ok
- model_name: TabularWideDeepNet
- task: task_b_proxy_good_project
- train_size: 105
- valid_size: 22
- test_size: 23
- best_epoch: 2
- early_stop_epoch: 2
- valid_auc: 0.9285714285714285
- valid_f1: 0.9285714285714286
- test_auc: 0.9603174603174603
- test_f1: 0.9629629629629629
- test_loss: 0.5990766286849976
- parameter_count: 4229
- training_seconds: 4.482
- device: cpu

## Interpretation
如果该模型没有超过 sklearn 最佳模型，结论应理解为表格神经网络扩展实验，而不是必须替代树模型。
小样本下树模型通常更稳，神经网络的价值在于展示类别 Embedding、early stopping 和端到端训练流程。
