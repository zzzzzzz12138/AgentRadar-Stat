请继续在当前 AgentRadar-Stat 项目基础上进行第四轮迭代。本轮目标是“展示级优化与前端美工升级”，重点把项目从功能完整的工程原型升级为适合课程答辩、GitHub 展示和课堂演示的成熟数据产品。

当前项目已经完成：
1. GitHub API-first 数据采集；
2. sample fallback；
3. DeepSeek Client；
4. 数据清洗与特征工程；
5. 综合评分；
6. 高级聚类建模与聚类画像；
7. Task A / Task B 标签定义与防泄漏说明；
8. sklearn 多模型比较；
9. PyTorch baseline MLP 与 TabularWideDeepNet；
10. 用户画像与个性化推荐；
11. DeepSeek Agent 接入 user_profile；
12. HTML 报告新增模型方法与个性化推荐章节；
13. Streamlit 已加入 profile form 和 Personalized 页面；
14. pytest 已通过；
15. 当前默认 DeepSeek 模型为 deepseek-v4-pro；
16. 当前活跃代码与文档中已删除 available_time、api_budget、deepseek-v4-flash、st.json 残留。

本轮不要大改模型逻辑，不要重写数据管道，不要破坏 `python main.py` 闭环。本轮只围绕展示效果、交互体验、报告质量、图表美工、Agent 展示可读性和答辩材料进行升级。

重要硬约束：

1. 不要破坏已经跑通的 `python main.py` 主流程；
2. 不要删除已有核心模块；
3. 不要硬编码 GitHub Token 或 DeepSeek API Key；
4. 不要读取、打印、保存或提交 `.env` 真实内容；
5. 默认 DeepSeek 模型保持 `deepseek-v4-pro`；
6. GitHub API 仍是主数据源，sample 只是 fallback；
7. DeepSeek Agent 仍优先真实调用 API，fallback 只用于异常兜底；
8. 项目继续适配 Windows 11、Python 3.10、CPU-only；
9. 不要新增过重依赖，优先使用已有 pandas、numpy、plotly、pyecharts、streamlit、jinja2、matplotlib、seaborn；
10. 不要恢复 available_time 和 api_budget；
11. 不得直接裸展示 JSON，特别是 Agent 输出；
12. 修改完成后确保 `python main.py`、`pytest`、`streamlit run app.py` 具备可运行基础。

一、统一视觉系统：冰蓝科技风

请为 Streamlit、HTML 报告、HTML 大屏、图表、表格统一视觉风格。

整体风格要求：
1. 主色调为浅蓝、冰蓝、青蓝、科技蓝；
2. 不要深蓝压抑风，不要黑底赛博朋克；
3. 推荐色彩：
   - 主色：#38BDF8
   - 亮青：#22D3EE
   - 辅蓝：#60A5FA
   - 背景：#F8FCFF
   - 浅背景：#EEF8FF
   - 卡片白：#FFFFFF
   - 正文深灰：#1F2937
   - 弱文本灰：#64748B
   - 成功绿：#10B981
   - 警告橙：#F59E0B
   - 风险红：#EF4444
4. 页面应使用卡片式布局、圆角、浅阴影、细边框、充足留白；
5. 推荐等级颜色统一：
   - A：#10B981
   - B：#38BDF8
   - C：#F59E0B
   - D：#EF4444
6. 风险等级颜色统一：
   - low：#10B981
   - medium：#F59E0B
   - high：#EF4444
7. 表格、badge、图例、标题风格保持一致。

建议新增：
- `src/ui_components.py`
- `src/theme.py`
- `src/agent_display.py`

二、重构 Streamlit App：从工具页升级为产品化仪表盘

请重点优化 `app.py`，必要时拆分 UI 组件到 `src/ui_components.py`，避免 app.py 过长。

要求：

1. 全局 CSS：
   - 使用 `st.markdown` 注入自定义 CSS；
   - 冰蓝科技风背景；
   - 卡片式指标区；
   - 圆角 badge；
   - 美化 tabs、sidebar、buttons、dataframe；
   - 不得裸展示 JSON。

2. 顶部 Hero 区：
   - 项目名：AgentRadar-Stat；
   - 副标题：AI Agent 开源生态趋势挖掘、质量评分与智能选题决策平台；
   - 当前数据模式 badge：api_live / sample_fallback；
   - GitHub API 状态 badge；
   - DeepSeek Agent 状态 badge；
   - 默认模型 badge：deepseek-v4-pro；
   - 最近运行时间。

3. 首页：
   - 用流程卡展示：GitHub API → 清洗特征 → 评分建模 → 聚类画像 → 个性化推荐 → DeepSeek Agent → 报告导出；
   - 核心指标卡：
     - 仓库样本数；
     - api_live 数量；
     - fallback 数量；
     - A 级项目数；
     - 高风险项目数；
     - 最佳 sklearn 模型；
     - 最佳模型 F1；
     - 最终聚类模型与 k 值；
     - PyTorch 模型测试指标；
     - 个性化推荐条数。

4. API 状态页：
   - 显示 GitHub Token 是否配置，但不能显示 Token；
   - 显示 DeepSeek API Key 是否配置，但不能显示 Key；
   - 显示 source_type 分布；
   - 显示 GitHub API 采集摘要；
   - 显示 API 失败或 fallback 原因；
   - 如已有 rate limit 字段则展示，否则显示“当前版本未采集 rate limit，可作为后续扩展”。

5. 趋势分析页：
   - 使用 Plotly 交互图；
   - 语言分布；
   - topic/cluster 分布；
   - star/fork 分布；
   - Top 20 项目表；
   - full_name 可点击 repo_url；
   - recommendation_level 用 badge；
   - 不显示过长 README。

6. 评分与推荐页：
   - 通用 final_potential_score 排行榜；
   - 支持筛选：
     - 推荐等级；
     - 编程语言；
     - cluster_name；
     - 风险分范围；
     - 潜力分范围；
     - Top N；
   - 单项目评分卡；
   - 各子评分用横向进度条或雷达图展示；
   - 风险提示用标签展示。

7. 聚类地图页：
   - 交互式 PCA/KMeans 或最佳聚类散点图；
   - hover 显示 full_name、language、final_potential_score、risk_score、cluster_name；
   - cluster 类型说明卡；
   - 每个 cluster 的代表项目 Top 5；
   - 展示 `cluster_model_comparison.csv` 的模型比较表；
   - 展示最终聚类选择理由；
   - 不裸露 CSV 原始字段。

8. 模型结果页：
   - 展示 Task A 与 Task B 的区别；
   - 展示防泄漏说明；
   - 展示 sklearn 模型对比表；
   - 显示最佳模型指标卡；
   - 显示特征重要性图；
   - 显示 calibration / threshold 摘要；
   - 显示 PyTorch baseline 与 TabularWideDeepNet 对比；
   - 显示训练曲线；
   - 展示 model_card 与 torch_model_card 摘要，不要整段堆文本。

9. 个性化推荐页：
   - 保留用户画像 onboarding；
   - 字段仅包括：
     - user_role
     - main_goal
     - programming_level
     - preferred_languages
     - preferred_topics
     - hardware_condition
     - risk_preference
     - output_preference
   - 不得出现 available_time 和 api_budget；
   - 展示 personalized_score 排行榜；
   - 展示 base_score vs personalized_score 对比；
   - 展示“为什么适合你”的卡片；
   - 展示风险提示；
   - 展示三天路线；
   - 展示可复制 Codex Prompt；
   - 展示“热门但不适合当前画像”的项目；
   - 保留通用榜单作为对比。

10. DeepSeek Agent 页：
    - 严禁直接显示原始 JSON；
    - Agent 输出要转为卡片：
      - 摘要；
      - 关键发现；
      - 数据依据；
      - 风险；
      - 建议；
      - 下一步；
      - Codex Prompt；
      - fallback_used 状态；
    - CriticAgent 输出单独做审查卡：
      - pass / warning / fail badge；
      - 弱依据表述；
      - 缺少的数据依据；
      - 修改建议；
    - ProjectAdvisorAgent 输出：
      - 推荐项目；
      - 个性化匹配理由；
      - 不推荐但热门项目；
      - 三天路线；
      - Codex Prompt。
    - 如能低成本实现，增加“刷新当前项目 Agent 解释”按钮，并使用 outputs/agents/cache 缓存，避免重复消耗 API。

11. 报告导出页：
    - 显示 HTML 报告路径；
    - 显示 HTML 大屏路径；
    - 显示报告章节清单；
    - 显示生成时间；
    - 显示打开方式；
    - 不只输出路径文本。

三、Agent 输出展示卡片化

请新增或完善：

- `src/agent_display.py`

功能要求：

1. 读取 `outputs/agents/` 下 Agent 输出；
2. 兼容 JSON、dict、纯文本；
3. 标准化为：
   - title
   - status
   - summary
   - key_findings
   - evidence
   - risks
   - recommendations
   - next_steps
   - codex_prompt
   - fallback_used
   - model
   - created_at

4. 对 CriticAgent 特殊处理：
   - status；
   - weak_sentences；
   - evidence_gaps；
   - suggestions；
   - final_verdict。

5. 对 ProjectAdvisorAgent 特殊处理：
   - profile_summary；
   - recommendation_logic；
   - top_projects；
   - not_recommended_even_if_popular；
   - codex_prompt。

6. 前端不允许 `st.json(raw_agent_output)`；
7. 如果确实要保留调试信息，只能放在默认折叠的 expander 中，标题为“调试信息”，且默认不展开；
8. 不得显示 API Key 或完整请求体。

四、重写 HTML 报告为正式网页成果

请重点优化 `src/report_generator.py` 输出的：

- `outputs/reports/agent_radar_report.html`

报告不应再像简单文本拼接，而应像正式课程项目成果网页。

视觉要求：
1. 冰蓝科技风；
2. 顶部 Hero；
3. 渐变背景；
4. 指标卡片；
5. 模块化分区；
6. 圆角白色卡片；
7. 浅阴影；
8. 表格美化；
9. 推荐等级 badge；
10. 风险标签；
11. 图表嵌入；
12. 页脚说明数据来源与运行时间；
13. 不显示原始 JSON。

报告结构必须包括：

1. Hero：
   - AgentRadar-Stat；
   - 副标题；
   - 运行模式；
   - 生成时间；
   - GitHub API 状态；
   - DeepSeek Agent 状态；
   - deepseek-v4-pro 模型标识。

2. Executive Summary：
   - 3—5 条核心结论；
   - 每条结论必须有数据依据。

3. 核心指标卡片：
   - 样本量；
   - api_live / sample_fallback；
   - A 级项目数；
   - 高风险项目数；
   - 最佳 sklearn 模型；
   - 最佳模型 F1；
   - 最终聚类模型与 k；
   - PyTorch 模型指标；
   - personalized 推荐数。

4. 数据来源与采集：
   - GitHub API 主流程；
   - sample fallback 机制；
   - 当前运行模式；
   - API 失败原因摘要；
   - 不出现真实 Key。

5. 评分体系：
   - 评分公式；
   - 各维度解释；
   - Top 10 高潜力项目；
   - Top 10 高风险项目。

6. 聚类分析：
   - 多算法比较；
   - 最终模型选择理由；
   - cluster profile；
   - 代表项目；
   - PCA 图嵌入。

7. 机器学习：
   - Task A / Task B 定义；
   - 防泄漏说明；
   - 模型对比；
   - 最佳模型；
   - 阈值与校准摘要；
   - 特征重要性图；
   - model card 摘要。

8. PyTorch 表格神经网络：
   - baseline MLP；
   - TabularWideDeepNet；
   - 为什么使用类别 embedding + 数值分支；
   - 训练结果；
   - 与 sklearn 对比；
   - torch model card 摘要。

9. 个性化推荐：
   - 用户画像字段；
   - personalized_score 机制；
   - 示例用户画像；
   - personalized 推荐 Top 项目；
   - 通用榜单与个性化榜单差异；
   - Codex Prompt 示例。

10. DeepSeek Agent：
    - Agent 输出卡片；
    - ProjectAdvisorAgent 个性化解释；
    - CriticAgent 审查结果；
    - fallback_used 状态说明；
    - 不显示 JSON。

11. 项目边界与局限：
    - 不预测商业价值；
    - API 数据有时点性；
    - README 文本分析可能误判；
    - 代理标签不是未来真实结果；
    - Agent 输出是辅助解释；
    - sample fallback 仅为演示兜底。

12. 附录：
    - 字段说明；
    - 评分公式；
    - 运行命令；
    - API 配置说明，但不包含真实 Key。

五、优化 HTML 大屏

请优化 `src/dashboard.py` 输出的：

- `outputs/dashboards/agent_radar_dashboard.html`

要求：
1. 冰蓝科技风；
2. 顶部标题栏；
3. 指标卡片；
4. 图表网格布局；
5. 风险—潜力四象限图；
6. PCA 聚类图；
7. Top 项目排行榜；
8. 个性化推荐榜；
9. 模型结果卡片；
10. Agent 状态卡片；
11. API 状态卡片；
12. 不展示 JSON；
13. 页面打开后能直接作为课堂展示大屏。

六、统一图表美工

请优化 `src/visualization.py` 中全部静态图。

要求：
1. 统一浅蓝、青蓝、冰蓝配色；
2. 标题统一；
3. 坐标轴标签统一；
4. 网格线弱化；
5. 字体清晰；
6. 输出 dpi 至少 180；
7. 尺寸适合报告嵌入；
8. 避免默认 Matplotlib 丑样式；
9. 推荐等级颜色统一；
10. 风险颜色统一；
11. 如中文字体不稳定，则图表标题统一英文，但报告和 Streamlit 正文可以中文。

需要重点优化这些图：
1. star 分布；
2. stars-forks 散点图；
3. topic / language 分布；
4. 相关性热力图；
5. Top potential；
6. Top risk；
7. PCA cluster；
8. risk-potential quadrant；
9. model comparison；
10. feature importance；
11. PyTorch training curve；
12. personalized vs base score 对比图。

七、表格展示格式化

请新增或完善表格格式化函数，建议放在：

- `src/ui_components.py`
- `src/report_generator.py`

要求：
1. full_name 显示为可点击链接；
2. final_potential_score 保留 2 位小数；
3. personalized_score 保留 2 位小数；
4. risk_score 保留 2 位小数；
5. recommendation_level 显示为彩色 badge；
6. cluster_name 显示为标签；
7. source_type 显示为 api_live / sample_fallback badge；
8. 不显示过长 README；
9. Top 项目表按分数降序；
10. 高风险表按 risk_score 降序；
11. 列名友好化，例如：
    - 仓库
    - 语言
    - Stars
    - Forks
    - 推荐等级
    - 潜力分
    - 个性化分
    - 风险分
    - 项目类型
    - 数据来源

八、生成展示材料与截图目录

请创建：

- `outputs/screenshots/`

并更新 `docs/demo_script.md`。

要求写出课堂展示顺序：

1. Streamlit 首页；
2. API 状态页；
3. 趋势分析页；
4. 评分排行榜页；
5. 聚类地图页；
6. 模型结果页；
7. 个性化推荐页；
8. DeepSeek Agent 页；
9. HTML 报告首页；
10. HTML 大屏页；
11. README 项目亮点。

如果不引入浏览器自动化依赖，则无需自动截图，只创建目录和截图清单说明即可。

九、更新 README 和文档

请更新：

1. `README.md`
2. `docs/user_guide.md`
3. `docs/demo_script.md`
4. `docs/development_log.md`
5. `AGENTS.md`

README 新增或强化：
1. 项目最终展示形态；
2. Streamlit Dashboard；
3. HTML Report；
4. HTML Big Screen；
5. Agent Explanation Cards；
6. Personalized Recommendation；
7. Model Rigor；
8. Risk-Potential Quadrant；
9. PCA Cluster Map；
10. Screenshots 占位说明。

docs/demo_script.md 必须包含 3—5 分钟课堂展示话术大纲。

十、运行与验证

修改完成后，请运行或指导我运行：

1. `python main.py`
2. `pytest`
3. `streamlit run app.py`

如果 pytest 出现线程池退出卡住，保留说明：
- Windows 下可设置 `OMP_NUM_THREADS=1`
- `LOKY_MAX_CPU_COUNT=1`

检查：
1. HTML 报告是否明显变美；
2. HTML 大屏是否可作为展示页面；
3. Streamlit 是否不再像调试工具；
4. Agent 输出是否卡片化；
5. 图表是否统一冰蓝科技风；
6. 表格是否 badge 化；
7. 个性化推荐页是否可展示；
8. 模型结果页是否能体现方法严谨性；
9. 是否仍保持 deepseek-v4-pro；
10. 是否无 deepseek-v4-flash、available_time、api_budget、st.json 残留；
11. 是否无 API Key 泄露。

十一、完成后汇报

请最后按以下格式汇报：

1. 本轮修改了哪些文件；
2. 新增了哪些文件；
3. Streamlit 具体优化了哪些页面；
4. HTML 报告具体优化了哪些章节；
5. HTML 大屏具体优化了哪些模块；
6. 图表是否统一冰蓝科技风；
7. 表格是否 badge 化；
8. Agent JSON 是否已转为卡片式展示；
9. 个性化推荐页展示是否优化；
10. 模型结果页展示是否优化；
11. 是否创建 outputs/screenshots；
12. README 和 demo_script 是否更新；
13. `python main.py` 是否通过；
14. `pytest` 是否通过；
15. 是否仍保持 deepseek-v4-pro；
16. 是否仍无 available_time、api_budget、deepseek-v4-flash、st.json 残留；
17. 是否存在 API Key 泄露风险；
18. 下一轮最终答辩收尾还需要做什么。