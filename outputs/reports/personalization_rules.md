# Personalization Rules

本文件说明 AgentRadar-Stat 如何将通用评分转为用户画像下的个性化推荐分。

## User Profile
- user_role: 想选择学习/复现项目的开发者
- main_goal: 选择可复现项目
- programming_level: 中等
- preferred_languages: ['Python']
- preferred_topics: ['Coding Agent', 'RAG Agent']
- hardware_condition: CPU-only
- risk_preference: 平衡
- output_preference: ['想要排行榜', '想要三天复现路线', '想要 Codex Prompt']

## Scoring Formula

`personalized_score = base_score * base_weight + preference + feasibility + goal + language + topic + hardware - risk_penalty`

## Active Weights
- base_weight: 0.450
- preference_weight: 0.100
- feasibility_weight: 0.180
- goal_weight: 0.100
- language_weight: 0.070
- topic_weight: 0.070
- hardware_weight: 0.100
- risk_penalty_weight: 0.140

## Leakage Control

- 个性化推荐是在评分结果之上做排序适配，不把用户画像字段写入监督训练标签。
- 监督模型仍使用 no_leakage_features，避免直接使用 final_potential_score 和子评分字段预测评分标签。
- DeepSeek Agent 的个性化解释只作为说明层，不替代真实字段和模型指标。
