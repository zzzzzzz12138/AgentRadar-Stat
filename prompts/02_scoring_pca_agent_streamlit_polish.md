请继续在当前 AgentRadar-Stat 项目基础上进行第二轮迭代。第一轮已经完成项目骨架、GitHub API-first 数据管道、DeepSeek Client、sample fallback、基础清洗、特征工程、评分、模型、图表、Agent 输出、HTML 大屏和报告，并已跑通 `python main.py`。

执行记录：本提示词对应第二阶段增强，要求保持 `.env` 不读取、不打印、不序列化，默认 DeepSeek 模型为 `deepseek-v4-pro`。

本轮目标不是重写项目，而是在不破坏第一轮可运行闭环的基础上，补强“统计建模深度、聚类分析、模型解释、DeepSeek Agent 质量、Streamlit 展示和报告美观度”。

重要硬约束：

1. 不要重构到无法运行；
2. 不要删除第一轮已生成的核心模块；
3. 真实 GitHub API 仍是主数据源，sample 数据只是 fallback；
4. DeepSeek Agent 仍优先真实调用 API，fallback 仅用于异常兜底；
5. 不得读取、打印、保存或提交真实 `.env` 内容；
6. 不得硬编码 GitHub Token 或 DeepSeek API Key；
7. 默认 DeepSeek 模型保持为 `deepseek-v4-pro`；
8. 继续适配 Windows 11、Python 3.10、CPU-only、PyTorch 环境；
9. 不要新增过重依赖，优先使用现有 requirements 中已有库；
10. 修改完成后必须确保 `python main.py`、`pytest`、`streamlit run app.py` 具备可运行基础。

请先快速检查当前文件结构和主要模块，再按以下任务迭代。

一、补强 PCA 与 KMeans 聚类模块

请在现有代码基础上新增或完善聚类分析功能，优先放入 `src/statistical_analysis.py` 或新建 `src/clustering.py`，并在 `main.py` 中接入。

要求：

1. 从评分后的项目数据中选取数值特征，包括但不限于：

   * log_stars
   * log_forks
   * stars_per_day
   * forks_per_star
   * issue_pressure
   * topic_count
   * readme_length
   * agent_relevance_score
   * reproducibility_score
   * trend_score
   * activity_score
   * community_score
   * documentation_score
   * innovation_score
   * feasibility_score
   * risk_score
   * final_potential_score

2. 对特征进行标准化；

3. 使用 PCA 将项目降至二维，生成：

   * pca_x
   * pca_y
   * pca_explained_var_1
   * pca_explained_var_2

4. 使用 KMeans 聚类，默认 k=5；

5. 为每个 cluster 生成可解释标签，例如：

   * 高热度成熟型
   * 新兴爆发潜力型
   * 文档完善可复现型
   * 高 star 低维护风险型
   * 概念新颖但工程不成熟型

6. 输出包含 cluster_label、cluster_name、pca_x、pca_y 的结果到：

   * `data/processed/clustered_repos.csv`

7. 将聚类结果合并回主评分数据，如果当前主评分结果为 `scored_repos.csv`，则保证最终 scored 数据也包含聚类字段。

8. 保存聚类摘要到：

   * `outputs/reports/cluster_summary.json`
   * `outputs/reports/cluster_summary.md`

二、补强模型对比与解释

请完善 `src/modeling.py`，形成更完整的模型对比模块。

要求：

1. 保留现有 Logistic Regression、Random Forest、Gradient Boosting；

2. 输出统一的模型对比表，包括：

   * model_name
   * accuracy
   * precision
   * recall
   * f1
   * roc_auc，如果无法计算则填 null 并说明原因
   * train_size
   * test_size

3. 保存到：

   * `outputs/reports/model_metrics.csv`
   * `outputs/reports/model_metrics.json`

4. 生成特征重要性结果：

   * Random Forest feature importance；
   * Gradient Boosting feature importance；
   * Logistic Regression coefficient；
   * 若适合，增加 permutation importance；如实现成本较高，可先不做，但需保留接口。

5. 保存到：

   * `outputs/reports/feature_importance.csv`

6. 生成模型解释文字摘要，保存到：

   * `outputs/reports/model_explanation.md`

7. 模型解释中必须说明：

   * 哪些特征最影响高潜力项目判断；
   * star 数是否会支配模型；
   * 文档质量、维护活跃度、复现可行性、风险分在模型中的作用；
   * 模型局限性。

三、完善 PyTorch MLP 输出

请完善 `src/torch_mlp.py`。

要求：

1. 保持 CPU 可运行；

2. 不要显著增加训练时间；

3. 输出训练过程 loss history；

4. 保存：

   * `outputs/models/torch_mlp.pt`
   * `outputs/reports/torch_mlp_metrics.json`
   * `outputs/figures/torch_mlp_loss_curve.png`

5. 在 `main.py` 中确保 PyTorch MLP 失败不会中断整个流程，而是记录 warning 并继续生成报告。

四、增强可视化

请完善 `src/visualization.py` 和 `src/dashboard.py`，在已有 9 张图基础上新增或优化以下图表。

静态图表：

1. PCA/KMeans 聚类散点图；
2. 风险—潜力四象限图；
3. 模型对比柱状图；
4. cluster 类型数量图；
5. 推荐等级 A/B/C/D 分布图；
6. README 文档质量与 final_potential_score 关系图。

交互式图表或 HTML 大屏：

1. 项目综合评分 Top 20 交互排行榜；
2. PCA/KMeans 交互散点图，hover 展示 full_name、language、final_potential_score、risk_score、cluster_name；
3. 风险—潜力四象限交互图；
4. 推荐等级分布图；
5. GitHub API 采集状态卡片；
6. DeepSeek Agent 调用状态卡片。

输出路径：

* 静态图保存到 `outputs/figures/`
* HTML 大屏保存到 `outputs/dashboards/agent_radar_dashboard.html`

如果中文字体显示困难，可先使用英文图标题，但 README 或报告中要说明原因；如果能稳定设置中文字体，则优先使用中文标题。

五、深化 DeepSeek Agent prompt

请完善 `src/agents.py` 中 7 个 Agent 的 system prompt 和输出结构。不要让 Agent 输出空泛套话，必须基于真实字段和统计结果。

要求：

1. CollectorAgent 输出：

   * 采集关键词策略；
   * GitHub API 采集范围；
   * 数据代表性风险；
   * 是否需要补充关键词。

2. DataQualityAgent 输出：

   * 样本量；
   * source_type 分布；
   * API 成功率；
   * README 获取成功率；
   * 缺失值风险；
   * 极端值风险；
   * 是否适合继续建模。

3. TopicAgent 输出：

   * 项目主题分类；
   * 判断依据；
   * 可能误判风险。

4. ScoringAgent 输出：

   * 推荐等级；
   * final_potential_score；
   * trend/activity/community/documentation/innovation/feasibility/risk 各项解释；
   * 为什么推荐或不推荐；
   * 风险提示。

5. ProjectAdvisorAgent 输出：

   * Top 5 推荐项目；
   * 推荐理由；
   * 复现难度；
   * 是否适合 CPU；
   * 是否需要 API Key；
   * 三天复现路线；
   * 可复制给 Codex 的开发 Prompt。

6. ReportAgent 输出：

   * 项目整体摘要；
   * 核心发现；
   * 数据依据；
   * 模型依据；
   * 局限性。

7. CriticAgent 输出：

   * 检查报告中是否存在无依据判断；
   * 标出需要补充数据依据的句子；
   * 给出修改建议；
   * 输出 pass/warning/fail 状态。

所有 Agent 输出应保存到 `outputs/agents/`，并记录：

* agent_name
* model
* fallback_used
* created_at
* evidence_fields
* output_path

如果 DeepSeek API 失败，fallback 输出也必须尽量包含真实字段，而不是空模板。

六、完善 HTML 报告

请完善 `src/report_generator.py` 生成的 `outputs/reports/agent_radar_report.html`。

报告需要更像正式课程项目成果，而不是简单拼接文本。请至少包含以下结构：

1. 项目标题与一句话定位；
2. 数据来源与运行模式；
3. GitHub API 采集摘要；
4. 数据清洗与特征工程摘要；
5. 核心指标卡片：

   * 项目样本量；
   * api_live / sample_fallback 数量；
   * 平均 star；
   * README 获取成功率；
   * A 类推荐项目数量；
   * 高风险项目数量；
6. 趋势分析；
7. 综合评分体系说明；
8. Top 10 高潜力项目表；
9. Top 10 高风险项目表；
10. PCA/KMeans 聚类分析；
11. 机器学习模型结果；
12. PyTorch MLP 结果；
13. DeepSeek Agent 自动解释；
14. CriticAgent 审查结果；
15. 项目边界与局限性；
16. 附录：字段说明与评分公式。

样式要求：

1. 页面整体美观，至少包含基础 CSS；
2. 卡片式布局；
3. 表格可读；
4. 图表能够嵌入或链接；
5. 报告中明确显示当前数据模式：api_live 或 sample_fallback；
6. 报告中不得出现 API Key。

七、升级 Streamlit App

请完善 `app.py`，在不大幅复杂化的前提下，让它更像一个可展示的数据产品。

建议采用 sidebar + tabs 或多 section 结构。至少包含以下页面或标签：

1. 首页：

   * 项目定位；
   * 技术路线；
   * 当前运行模式；
   * 核心指标卡片。

2. API 采集与数据状态：

   * 是否检测到 GitHub Token；
   * 是否检测到 DeepSeek API Key；
   * 当前 source_type；
   * 样本量；
   * API 采集日志摘要；
   * fallback 状态说明。

3. 趋势分析：

   * 语言分布；
   * 技术主题分布；
   * star/fork 分布；
   * Top 项目表。

4. 评分与推荐：

   * final_potential_score 排行榜；
   * 推荐等级筛选；
   * 风险—潜力四象限图；
   * 单项目评分卡。

5. 聚类地图：

   * PCA/KMeans 散点图；
   * cluster_name 筛选；
   * 各 cluster 代表项目。

6. 模型结果：

   * 模型对比表；
   * 特征重要性；
   * PyTorch MLP loss 曲线。

7. DeepSeek Agent：

   * 用户可选择一个项目；
   * 展示 ScoringAgent 或 ProjectAdvisorAgent 输出；
   * 显示 fallback_used 状态；
   * 不显示任何 API Key。

8. 报告导出：

   * 展示 HTML 报告路径；
   * 提供生成状态；
   * 提醒如何打开报告。

注意：

* 如果某些文件尚未生成，页面要友好提示先运行 `python main.py`；
* 不要因为缺少某个输出文件导致 Streamlit 崩溃；
* 页面整体要适合课堂演示。

八、补充测试

请完善 `tests/test_core_functions.py`，至少测试：

1. sample 数据能生成；
2. 清洗后没有重复 full_name；
3. 特征工程能生成核心字段；
4. scoring 能生成 final_potential_score 和 recommendation_level；
5. PCA/KMeans 能生成 pca_x、pca_y、cluster_label；
6. model_metrics 文件能生成；
7. report HTML 文件能生成；
8. `.env` 不会被读取、打印或写入输出文件。

如果当前测试依赖外部 API，请改为使用 sample fallback 数据，保证 `pytest` 可稳定运行。

九、更新 README、AGENTS.md 和 docs

请同步更新：

1. `README.md`
2. `AGENTS.md`
3. `docs/project_design.md`
4. `docs/user_guide.md`
5. `docs/development_log.md`
6. `prompts/02_scoring_pca_agent_streamlit_polish.md`

README 中新增：

1. 第二轮新增功能；
2. PCA/KMeans 聚类说明；
3. 模型对比说明；
4. DeepSeek Agent 输出说明；
5. Streamlit 页面说明；
6. HTML 报告说明；
7. 常见问题：

   * GitHub API 失败怎么办；
   * DeepSeek API 失败怎么办；
   * 为什么会使用 sample_fallback；
   * 如何确认没有泄露 API Key。

AGENTS.md 中新增：

1. 后续修改必须保护 `.env`；
2. 不要删除 fallback 数据；
3. 不要把 DeepSeek 输出当成事实本身；
4. 报告结论必须绑定字段、图表或模型结果；
5. 新增功能必须接入 main.py 和测试。

十、主流程接入要求

请检查并完善 `main.py`，确保一键运行顺序为：

1. 读取配置；
2. GitHub API 数据采集或 sample fallback；
3. 数据清洗；
4. 特征工程；
5. 评分；
6. PCA/KMeans 聚类；
7. 统计分析；
8. sklearn 模型训练与解释；
9. PyTorch MLP；
10. 静态图表生成；
11. HTML 大屏生成；
12. DeepSeek Agent 分析；
13. HTML 报告生成；
14. 输出最终运行摘要。

最终运行摘要需要明确显示：

* data_mode: api_live 或 sample_fallback；
* raw_data_path；
* processed_data_path；
* scored_data_path；
* clustered_data_path；
* dashboard_path；
* report_path；
* model_metrics_path；
* agent_output_dir；
* fallback_used；
* warnings。

十一、完成后请运行或指导我运行

请尽量运行：

1. `python main.py`
2. `pytest`

如果当前环境缺依赖或无法运行，请说明缺哪些包，并给出安装命令。不要私自读取或打印 `.env`。

十二、完成后汇报

请最后按以下格式汇报：

1. 本轮修改了哪些文件；
2. 新增了哪些文件；
3. PCA/KMeans 是否已接入主流程；
4. 模型对比和特征重要性是否已生成；
5. PyTorch MLP 输出是否完整；
6. HTML 大屏是否更新；
7. HTML 报告是否更新；
8. Streamlit 是否已升级；
9. DeepSeek Agent prompt 是否深化；
10. 测试是否通过；
11. `deepseek-v4-pro` 是否仍为默认模型；
12. 是否有任何旧 flash 模型名残留；
13. 是否存在 API Key 泄露风险；
14. 下一轮还需要做哪些展示级优化。
