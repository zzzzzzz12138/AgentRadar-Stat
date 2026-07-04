请继续在当前 AgentRadar-Stat 项目基础上进行第三轮迭代。本轮暂时不做展示级美工优化，不重写前端视觉风格。本轮核心目标是：系统性提升聚类建模、机器学习预测、PyTorch 神经网络扩展、多智能体解释和个性化决策能力，使项目体现更高水平的模型选择严谨性、问题适配性和决策价值。

当前项目已经完成：

1. GitHub API-first 数据采集；
2. sample fallback；
3. DeepSeek Client；
4. 数据清洗；
5. 特征工程；
6. 综合评分；
7. PCA/KMeans 聚类；
8. sklearn 模型对比；
9. PyTorch MLP；
10. 静态图表；
11. HTML 大屏；
12. HTML 报告；
13. Streamlit App；
14. DeepSeek Agent 输出；
15. pytest 通过。

本轮不是追求盲目复杂模型，而是在最契合具体研究问题与数据特征的前提下，提升模型严谨性、可解释性和个性化决策能力。

重要硬约束：

1. 不要破坏已经跑通的 `python main.py` 主流程；
2. 不要删除已有核心模块；
3. 不要硬编码 GitHub Token 或 DeepSeek API Key；
4. 不要读取、打印、保存或提交 `.env` 真实内容；
5. 默认 DeepSeek 模型保持 `deepseek-v4-pro`；
6. GitHub API 仍是主数据源，sample 只是 fallback；
7. DeepSeek Agent 仍优先真实调用 API，fallback 只用于异常兜底；
8. 项目继续适配 Windows 11、Python 3.10、CPU-only、PyTorch 环境；
9. CPU-only 不等于只能使用非常简单模型，但不得引入必须 GPU 才能正常运行的模型；
10. 不要新增过重依赖。优先使用已有的 pandas、numpy、scikit-learn、torch、plotly、streamlit、jinja2。若需要新增依赖，必须说明必要性，并保证失败时可 graceful fallback；
11. 所有新增模型必须接入 `main.py`，并补充测试；
12. 所有模型结论必须写入报告或模型说明文件，不能只保存代码结果。
13. 用户画像字段中不得包含 available_time 和 api_budget；如当前代码或文档中已有这两个字段，请删除并同步修改相关函数、Streamlit 表单、Agent prompt、测试和报告。

一、先进行模型任务重新界定，避免循环论证

当前项目中 `recommendation_level` 与 `final_potential_score` 由特征评分体系生成。如果直接用构造评分的同一批特征去预测 `recommendation_level`，容易形成“用规则标签训练规则标签”的循环论证。请在代码与文档中明确区分两类任务：

任务 A：评分体系代理模型
目标：学习当前评分体系对项目推荐等级的判别边界，用于解释评分规则和检验评分体系是否被少数变量支配。
标签：`recommendation_level` 或 high_potential = A/B。
限制：训练时不能使用 `final_potential_score`、各子评分字段作为输入，只能使用原始特征或低层特征，例如 stars_total、forks_total、open_issues_count、project_age_days、days_since_update、readme_length、topic_count、mentions_gpu、mentions_cpu、agent_keyword_count 等。

任务 B：项目潜力代理预测模型
目标：更接近真实开源项目选择问题，预测项目是否具备“短期趋势潜力 / 学习复现价值”。
标签建议使用以下非完全同源代理标签之一：

1. emerging_project_flag：低总 star 但 stars_per_day 或 stars_this_week 较高；
2. reproduction_friendly_flag：README 完整、CPU 友好、低风险；
3. high_attention_low_risk_flag：趋势热度较高且 risk_score 不高；
4. personalized_good_match_flag：在用户画像下是否适合作为推荐项目。

要求：

1. 在 `docs/model_methodology.md` 中明确说明为什么不能盲目把评分标签当作真实未来结果；
2. 在 `src/modeling.py` 或新建 `src/model_tasks.py` 中实现任务 A 与任务 B 的标签构造函数；
3. 输出标签构造摘要到：

   * `outputs/reports/label_definition_report.md`
   * `outputs/reports/label_distribution.json`

二、升级聚类建模：从单一 KMeans 改为“多算法比较 + 稳定性 + 项目画像”

请新增或完善：

* `src/clustering_advanced.py`

要求实现以下内容：

1. 使用同一套标准化特征进行多聚类方法比较：

   * KMeans；
   * GaussianMixture；
   * AgglomerativeClustering；
   * DBSCAN 可选，若效果不稳定可以仅保留诊断结果。

2. 对 k 值进行合理选择：

   * KMeans / GMM 尝试 k=3 到 k=8；
   * 计算 silhouette_score；
   * 计算 Calinski-Harabasz；
   * 计算 Davies-Bouldin；
   * 对 GMM 计算 BIC / AIC；
   * 输出最佳 k 的选择理由。

3. 生成聚类稳定性评估：

   * 使用不同 random_state 重复 KMeans；
   * 计算 Adjusted Rand Index 或聚类一致性摘要；
   * 输出稳定性说明。

4. 生成 cluster profile：
   每个 cluster 需要输出：

   * 样本数量；
   * 平均 final_potential_score；
   * 平均 risk_score；
   * 平均 stars_total；
   * 平均 days_since_update；
   * 平均 readme_length；
   * 主流 language；
   * 主流 topic_label；
   * 推荐等级分布；
   * 代表项目 Top 5。

5. cluster 自动命名不能拍脑袋。请基于 cluster profile 规则生成名称，例如：

   * 高热度成熟型；
   * 新兴爆发潜力型；
   * 文档完善可复现型；
   * 高 star 低维护风险型；
   * 小众垂直工具型；
   * 概念新颖但工程不成熟型。

6. 输出文件：

   * `data/processed/clustered_repos.csv`
   * `outputs/reports/cluster_model_comparison.csv`
   * `outputs/reports/cluster_profile.csv`
   * `outputs/reports/cluster_summary.md`
   * `outputs/reports/cluster_stability.json`

7. 将最终 cluster_label、cluster_name、pca_x、pca_y 合并回主 scored 数据。

8. 在 `docs/model_methodology.md` 中解释：

   * 为什么聚类适合本项目；
   * 为什么不能只看 KMeans；
   * 聚类不是监督预测，而是项目类型画像；
   * 聚类结果如何服务个性化推荐。

三、升级机器学习预测：从基础分类器改为严谨模型比较与校准

请完善或重构：

* `src/modeling.py`
* 可新增 `src/model_selection.py`
* 可新增 `src/model_interpretability.py`

要求：

1. 明确建模特征集：

   * raw_features：原始仓库指标；
   * text_signal_features：README 与 topics 衍生指标；
   * score_features：子评分指标；
   * no_leakage_features：不含 final_potential_score 和直接标签构造字段的特征集。

2. 对任务 A 和任务 B 分别训练模型。

3. 至少包含以下模型：

   * Logistic Regression with class_weight；
   * Random Forest；
   * Extra Trees；
   * HistGradientBoostingClassifier 或 GradientBoostingClassifier；
   * CalibratedClassifierCV 包装一个强基模型；
   * DummyClassifier 作为最低基线。

4. 使用 StratifiedKFold 交叉验证，默认 5 折；如果样本过少则自动降为 3 折。

5. 输出评价指标：

   * accuracy；
   * precision；
   * recall；
   * f1；
   * roc_auc；
   * average_precision；
   * balanced_accuracy；
   * brier_score_loss；
   * confusion matrix；
   * train_size；
   * test_size；
   * cv_mean；
   * cv_std。

6. 做概率校准：

   * 至少输出校准曲线数据；
   * 保存 Brier Score；
   * 说明推荐概率不是绝对真实概率，而是模型置信评分。

7. 做阈值分析：

   * 默认 0.5 阈值；
   * F1 最优阈值；
   * 高召回阈值；
   * 高精度阈值；
   * 输出不同阈值下的 precision/recall/f1。

8. 模型解释：

   * Logistic 系数解释；
   * Random Forest / Extra Trees / Gradient Boosting 特征重要性；
   * permutation importance；
   * 如果当前环境已安装 shap，可选输出 SHAP；未安装则跳过并说明，不要强制新增依赖。

9. 输出文件：

   * `outputs/reports/model_metrics_task_a.csv`
   * `outputs/reports/model_metrics_task_b.csv`
   * `outputs/reports/model_thresholds.csv`
   * `outputs/reports/model_calibration.json`
   * `outputs/reports/feature_importance_task_a.csv`
   * `outputs/reports/feature_importance_task_b.csv`
   * `outputs/reports/permutation_importance.csv`
   * `outputs/reports/model_explanation.md`
   * `outputs/reports/model_card.md`

10. `model_card.md` 必须写清楚：

    * 任务定义；
    * 标签来源；
    * 是否存在代理标签局限；
    * 输入特征；
    * 禁止使用的泄漏字段；
    * 模型选择理由；
    * 评价结果；
    * 最佳模型；
    * 适用边界；
    * 不适用场景。

四、升级 PyTorch 神经网络：从普通 MLP 改为表格数据适配型神经网络

当前 PyTorch MLP 太基础。请升级为更适合本项目表格数据的神经网络结构。不要盲目引入 GPU 专用大模型，也不要只停留在最简单 MLP。

请新增或重构：

* `src/torch_tabular.py`

保留原 `src/torch_mlp.py` 作为 baseline，新增高级 PyTorch 表格模型。

推荐实现结构：

1. TabularWideDeepNet：

   * 数值特征分支：BatchNorm + Linear + GELU/ReLU + Dropout；
   * 类别特征分支：Embedding 层，处理 language、license、topic_label、cluster_name、source_type 等；
   * Wide 分支：保留部分原始数值特征；
   * Deep 分支：多层残差 MLP；
   * 输出层：二分类概率；
   * 支持任务 A 与任务 B。

2. 模型训练规范：

   * train/valid/test split；
   * Stratified split；
   * EarlyStopping；
   * AdamW；
   * weight_decay；
   * Dropout；
   * ReduceLROnPlateau 或简单学习率调度；
   * gradient clipping；
   * random seed；
   * CPU 自动识别；
   * 小样本下防止过拟合。

3. 训练输出：

   * train_loss；
   * valid_loss；
   * valid_auc；
   * valid_f1；
   * test_auc；
   * test_f1；
   * best_epoch；
   * early_stop_epoch；
   * 参数量；
   * 训练耗时。

4. 保存文件：

   * `outputs/models/torch_mlp_baseline.pt`
   * `outputs/models/torch_tabular_widedeep.pt`
   * `outputs/reports/torch_model_metrics.json`
   * `outputs/reports/torch_training_history.csv`
   * `outputs/figures/torch_training_curve.png`
   * `outputs/reports/torch_model_card.md`

5. `torch_model_card.md` 必须解释：

   * 为什么表格数据使用类别 embedding + 数值分支；
   * 为什么不使用 GPU 专用大型模型；
   * 为什么该结构比普通 MLP 更适配本项目；
   * 是否出现过拟合；
   * 与 sklearn 最佳模型相比是否更优；
   * 若不更优，也要说明神经网络作为扩展实验的价值。

6. 主流程要求：

   * `main.py` 同时运行 sklearn 模型和 PyTorch 模型；
   * PyTorch 失败不能中断主流程，必须记录 warning；
   * 所有结果写入报告。

五、构建用户画像与个性化推荐引擎

本项目要从通用平台升级为“个性化、有针对性”的开源项目决策平台。请新增：

* `src/user_profile.py`
* `src/personalization.py`
* `src/recommendation_engine.py`

用户进入 Streamlit 时，应先进行一个 onboarding 画像选择界面，收集用户目标与偏好。先实现本地 session_state，不需要登录账号系统，不采集隐私，不接数据库。

用户画像字段建议包括：

1. user_role：
   - 快速了解 AI Agent 生态的学习者；
   - 想选择学习/复现项目的开发者；
   - 寻找课程项目/创新实践方向的学习者；
   - 技术社区观察者；
   - 开源项目维护者；
   - AI 工具与软件工程研究者；
   - 其他。

2. main_goal：
   - 快速了解趋势；
   - 选择可复现项目；
   - 寻找课程项目；
   - 寻找科研入门方向；
   - 寻找开源贡献对象；
   - 评估技术生态；
   - 生成 Codex 开发 Prompt；
   - 比较项目风险。

3. programming_level：
   - 入门；
   - 中等；
   - 熟练；
   - 高阶。

4. preferred_languages：
   - Python；
   - TypeScript；
   - JavaScript；
   - Go；
   - Rust；
   - Java；
   - C++；
   - 无明显偏好。

5. preferred_topics：
   - Coding Agent；
   - RAG Agent；
   - MCP Tool；
   - Workflow Agent；
   - Research Agent；
   - Data Agent；
   - Multimodal Agent；
   - AutoML Agent；
   - Local LLM；
   - Agent Framework。

6. hardware_condition：
   - CPU-only；
   - 有普通 GPU；
   - 有较强 GPU；
   - 云端资源可用；
   - 不确定。

7. risk_preference：
   - 低风险稳健；
   - 平衡；
   - 愿意尝试前沿高风险项目。

8. output_preference：
   - 想要排行榜；
   - 想要三天复现路线；
   - 想要学习路径；
   - 想要技术对比；
   - 想要 Codex Prompt；
   - 想要研究选题建议。

请实现：

1. `UserProfile` dataclass；
2. `build_user_profile_from_dict()`；
3. `profile_to_weight_adjustments()`；
4. `compute_personalized_score()`；
5. `generate_personalized_recommendations()`；
6. `explain_personalized_match()`。

个性化分数建议：

personalized_score
= base_score * base_weight
+ preference_match_score
+ feasibility_match_score
+ goal_match_score
+ language_match_score
+ topic_match_score
+ hardware_match_score
− personalized_risk_penalty

其中权重由用户画像决定。例如：

1. 课程项目/创新实践用户：
   - 提高 documentation_score、feasibility_score、CPU friendliness、Codex prompt 可生成性；
   - 降低高 GPU 依赖项目和复现链路过复杂项目。

2. 技术社区观察者：
   - 提高 trend_score、community_score、activity_score；
   - 关注 issue_pressure、更新频率和维护风险。

3. 开源维护者：
   - 提高 community_score、issue_pressure、recent_update、PR 协作信号；
   - 输出项目运营和社区维护建议。

4. 研究者：
   - 提高 innovation_score、topic novelty、cluster 稀缺性；
   - 输出研究问题、技术路线和可扩展方向。

5. 开发者：
   - 提高 feasibility_score、documentation_score、language match、hardware match；
   - 输出复现难度、工程路线和二次开发建议。

输出文件：

* `outputs/reports/personalized_recommendations.csv`
* `outputs/reports/personalized_recommendations.json`
* `outputs/reports/personalization_rules.md`

六、将个性化推荐接入 DeepSeek Agent

请升级 `src/agents.py` 中的 ProjectAdvisorAgent 和 ScoringAgent。

要求：

1. Agent 输入必须包含 user_profile；

2. Agent 输出不能只给通用推荐；

3. Agent 必须解释：

   * 为什么该项目适合该用户；
   * 哪些项目虽排名高但不适合该用户；
   * 哪些项目分数不最高但与用户目标高度匹配；
   * 该用户的风险提示；
   * 推荐的学习、复现或二次开发路线。

4. ProjectAdvisorAgent 输出结构建议：

{
"status": "pass",
"profile_summary": "...",
"recommendation_logic": "...",
"top_projects": [
{
"full_name": "...",
"personalized_score": 0.0,
"base_score": 0.0,
"match_reasons": ["..."],
"risk_warnings": ["..."],
"recommended_action": "...",
"three_day_plan": ["Day 1...", "Day 2...", "Day 3..."],
"codex_prompt": "..."
}
],
"not_recommended_even_if_popular": [
{
"full_name": "...",
"reason": "..."
}
],
"next_steps": ["..."]
}

5. Agent fallback 输出也必须基于 user_profile 和真实字段，不允许空泛模板。

七、将个性化推荐接入 Streamlit，但先不做美工

本轮不做大规模美工，但要让功能可用。请修改 `app.py`：

1. 首页或侧边栏增加 Onboarding / 用户画像设置区域；

2. 使用 `st.session_state` 保存用户画像；

3. 用户未完成画像时，显示“请先完成偏好设置以获得个性化推荐”；

4. 画像设置包括：

   * 身份角色；
   * 主要目标；
   * 编程水平；
   * 偏好语言；
   * 偏好主题；
   * 硬件条件；
   * 风险偏好；
   * 输出偏好。
注意：用户画像中不要再包含 available_time 和 api_budget 字段。所有代码、表单、dataclass、Agent prompt、测试和报告中均不得继续引用这两个字段。

5. 个性化推荐页展示：

   * personalized_score 排行榜；
   * base_score vs personalized_score 对比；
   * 为什么推荐；
   * 风险提示；
   * 三天路线；
   * 可复制 Codex Prompt；
   * “不适合但热门项目”列表。

6. 保留原通用排行榜，用于对比个性化推荐差异。

7. 页面可以朴素，但不得直接展示原始 JSON。

八、报告中新增模型方法与个性化推荐章节

请修改 `src/report_generator.py`，在 HTML 报告中新增：

1. 模型任务定义与防泄漏说明；
2. 聚类模型比较；
3. 聚类画像；
4. 机器学习模型卡摘要；
5. PyTorch 表格神经网络模型卡摘要；
6. 个性化推荐机制；
7. 示例用户画像推荐结果；
8. 个性化推荐与通用评分榜差异；
9. Agent 如何结合用户画像生成解释。

报告可以暂时保持现有视觉风格，不做大规模美工，但内容必须完整、严谨、可展示。

九、更新 Notebook

请新增或完善：

* `notebooks/02_modeling_rigor_and_personalization.ipynb`

Notebook 应展示：

1. 标签任务定义；
2. 聚类模型比较；
3. cluster profile；
4. sklearn 模型比较；
5. 特征重要性；
6. PyTorch 表格神经网络训练摘要；
7. 用户画像示例；
8. personalized_score 与 final_potential_score 对比；
9. 个性化推荐结果示例。

Notebook 不必写得极长，但要有清晰 Markdown 说明，适合老师检查方法过程。

十、更新文档

请更新：

1. `README.md`
2. `docs/model_methodology.md`
3. `docs/user_guide.md`
4. `docs/development_log.md`
5. `docs/demo_script.md`
6. `AGENTS.md`
7. 新建或更新 `prompts/03_modeling_personalization_upgrade.md`

README 中新增“模型严谨性升级”和“个性化推荐”部分，包括：

1. 为什么不盲目追求复杂模型；
2. 聚类模型比较；
3. 监督预测任务定义；
4. 标签泄漏防控；
5. PyTorch 表格神经网络；
6. 用户画像与个性化推荐；
7. DeepSeek Agent 如何结合用户画像生成解释。

十一、测试要求

请完善测试文件，至少增加：

1. 用户画像 dataclass 能正常创建；
2. profile_to_weight_adjustments 能输出合理权重；
3. personalized_score 能生成；
4. 个性化推荐结果不为空；
5. 聚类模型比较文件能生成；
6. label_definition_report 能生成；
7. model_card 能生成；
8. torch_model_card 能生成；
9. main.py 在无 DeepSeek API 或 GitHub API 失败时仍能 fallback；
10. 不会读取、打印或输出 `.env` 内容。

十二、主流程接入顺序

请检查并完善 `main.py`，确保一键运行顺序为：

1. 读取配置；
2. GitHub API 数据采集或 sample fallback；
3. 数据清洗；
4. 特征工程；
5. 综合评分；
6. 高级聚类模型比较与最终聚类；
7. 标签任务定义；
8. sklearn 模型比较与解释；
9. PyTorch baseline MLP；
10. PyTorch TabularWideDeepNet；
11. 个性化推荐示例；
12. DeepSeek Agent 通用解释；
13. DeepSeek Agent 个性化解释；
14. 图表生成；
15. HTML 大屏生成；
16. HTML 报告生成；
17. 输出最终运行摘要。

最终运行摘要需增加：

* best_cluster_model；
* best_k；
* cluster_stability；
* best_sklearn_model_task_a；
* best_sklearn_model_task_b；
* best_torch_model；
* personalization_demo_path；
* model_card_path；
* torch_model_card_path；
* warnings。

十三、完成后运行或指导我运行

请尽量运行：

1. `python main.py`
2. `pytest`

如当前环境缺依赖，请说明缺哪些包并给出安装命令。不要私自读取、打印或提交 `.env`。

十四、完成后汇报

请最后按以下格式汇报：

1. 本轮修改了哪些文件；
2. 新增了哪些文件；
3. 是否完成任务 A / 任务 B 标签定义；
4. 是否避免了 final_potential_score 泄漏进预测特征；
5. 聚类模型是否完成多算法比较；
6. 最终选择了哪个聚类模型、k 值是多少、理由是什么；
7. 是否生成 cluster profile；
8. sklearn 模型比较是否完成；
9. 是否生成 model_card；
10. PyTorch 是否升级为 TabularWideDeepNet 或等价表格神经网络；
11. PyTorch 模型是否生成 model_card；
12. 个性化推荐引擎是否完成；
13. Streamlit 是否已加入用户画像设置和个性化推荐页；
14. DeepSeek Agent 是否已结合 user_profile；
15. 报告是否新增模型方法和个性化推荐章节；
16. Notebook 是否新增；
17. 测试是否通过；
18. 是否仍保持 `deepseek-v4-pro`；
19. 是否存在 API Key 泄露风险；
20. 下一轮前端美工优化还需要重点处理哪些页面。
