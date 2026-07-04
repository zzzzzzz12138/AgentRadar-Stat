请继续在当前 AgentRadar-Stat 项目基础上进行“最终答辩报告最后一轮精修”。本轮只聚焦 `outputs/reports/agent_radar_report.html` 与自动导出的 `outputs/reports/agent_radar_report.pdf`，不再优化 HTML 大屏，也不再改模型主逻辑。

当前报告整体已经较完整，但仍存在展示层技术痕迹、字体混用、英文变量名残留、图例未中文化、Agent 内容模板化、个性化推荐理由不自然、部分章节排版不够精致等问题。本轮目标是进行最后一次高质量精修，使报告达到“班级最 impressive 的 Python 程序设计期末项目展示页”标准。

硬约束：

1. 不要重写 GitHub API 采集、评分、聚类、模型训练、PyTorch、个性化推荐主逻辑；
2. 不要破坏 `python main.py`、`pytest`、`streamlit run app.py`；
3. 不得读取、打印、保存或提交 `.env` 中真实 API Key；
4. 默认 DeepSeek 模型仍保持 `deepseek-v4-pro`，但展示层不把模型名当作核心关键词强调；
5. 不得恢复 `available_time`、`api_budget`、`deepseek-v4-flash`、`st.json`；
6. 展示层不得出现 `sample_fallback`、`api_live`、`CPU-only`、`答辩讲法`、`生成时间` 等不适合直接展示给老师的痕迹；
7. 所有面向展示的文字以中文为主，专有名词如 GitHub、DeepSeek、AI Agent、PyTorch、PCA、KMeans、TabularWideDeepNet 可保留英文；
8. 所有图表、图例、hover 弹窗、表格列名、模型名、特征名必须中文化；
9. 所有英文和数字字体必须为 Times New Roman；中文基准字体为宋体；
10. PDF 导出不得因本轮修改失败而中断主流程。

一、全局字体系统最终修正

当前报告中部分英文和数字仍看起来像宋体。请修正全局 CSS，让所有英文、数字优先使用 Times New Roman，中文使用宋体。

CSS 基础策略：

1. `body` 使用：
   `font-family: "Times New Roman", "SimSun", "宋体", serif;`
   这样英文与数字优先 Times New Roman，中文回退宋体。

2. 所有标题也遵循：
   `font-family: "Times New Roman", "SimSun", "宋体", serif;`

3. 中文大标题可通过字重、字号、字距、颜色形成层级，不要依赖微软雅黑。

4. Plotly 图表字体设置为：
   `font.family = "Times New Roman, SimSun, Microsoft YaHei, Arial"`

5. 表格、badge、图例、hover、按钮、页脚均继承同一字体策略。

6. 不要引入外部字体文件，不要把字体文件放入仓库。

二、Hero 区与项目能力雷达卡重排

当前首页左右分栏导致大标题宽度不足，右侧项目能力雷达卡高度与左侧内容不匹配。请重排首页 Hero：

1. Hero 顶部大标题区域占满水平，不分两栏：

   * `AgentRadar-Stat`
   * `AI Agent 开源生态趋势挖掘、质量评分与智能选题决策平台`

2. 大标题下方再分两栏：

   * 左栏：项目定位说明、功能标签、简短介绍；
   * 右栏：项目能力雷达卡。

3. 右侧项目能力雷达卡宽度适当加宽，高度与左侧介绍文本自然对齐。

4. 删除 Hero 与首页中所有显而易见或技术状态型内容：

   * 不显示 `报告状态：已生成`
   * 不显示 `Agent 状态：DeepSeek 解释已生成`
   * 不显示 `自动报告状态`
   * 不显示 `最近更新`
   * 不显示 `生成时间`
   * 不显示 `api_live`
   * 不显示 `sample_fallback`

5. Hero 标签保留功能与创新点：

   * `500 个 GitHub 公开仓库`
   * `多模型评分`
   * `聚类画像`
   * `PyTorch 表格神经网络`
   * `个性化推荐`
   * `DeepSeek Agent 解释`
   * `HTML/PDF 自动报告`

三、项目概览卡片调整

当前项目概览卡片较多，部分图标不明所以，并且存在 `api_live`、`CPU-only`、`HTML/PDF/Streamlit` 等展示层不宜突出的内容。请调整：

1. 删除以下两张卡片：

   * `真实 GitHub 仓库 500 api_live 主结果`
   * `输出形态 HTML/PDF/Streamlit 答辩交付`

2. 删除整个 HTML 中所有关于 `CPU-only` 的表述，包括：

   * 项目概览卡片；
   * PyTorch 章节正文；
   * 个性化推荐理由；
   * Agent 输出；
   * 亮点章节。

3. 删除整个 HTML 中所有 `sample fallback`、`sample_fallback`、`api_live` 表述。

4. 项目概览剩余卡片应正好排成三行，避免最后一行稀疏。

5. `TabularWideDeepNet` 必须显示完整，不得被截断。可通过：

   * 加宽卡片；
   * 减小该词字号；
   * 允许英文不换行；
   * 或显示为 `表格宽深神经网络`，括号中写 `TabularWideDeepNet`。

6. 卡片中小图标如果不能与内容强匹配，则直接删除；不要使用不明所以的单字母或抽象符号。

7. 若保留图标，必须与内容对应，例如：

   * 数据采集：数据库/云端节点图标；
   * 关键词：放大镜；
   * 去重：合并节点；
   * 模型：芯片；
   * 聚类：节点网络；
   * 个性化：用户画像；
   * Agent：机器人/对话气泡。

8. 卡片中的灰色说明文字字号适当加大，颜色改为深蓝灰或低饱和蓝，例如 `#475569` 或 `#334155`，增强可读性。

四、删除所有“答辩”字样与生成时间

本报告虽然用于答辩，但展示页面不应反复出现“答辩”“答辩讲法”。

请全仓库搜索并删除或替换展示层中的：

1. `答辩讲法`
2. `答辩展示`
3. `答辩报告`
4. `Python 程序设计期末项目` 可以保留在 README 或页脚，但报告主内容中尽量减少；
5. `生成时间`
6. `最近更新`
7. `报告生成时间`

替换建议：

* `答辩报告` → `项目报告`
* `答辩讲法` → 删除
* `用于答辩展示` → `用于项目展示`
* `生成时间` → 删除

页脚不显示生成时间，只保留：
`AgentRadar-Stat · GitHub 开源生态智能决策平台 · 数据、模型与可视化由项目流水线自动生成`

五、章节说明文字全部改成“内容目的型”而非“修改要求型”

当前部分图表说明仍像是在解释修改要求，例如：

* `Top 榜单只显示仓库名，完整 owner/name 和链接放在 hover 中`
* `数据采集漏斗图：只保留搜索候选、去重、相关性过滤和最终入模四个核心步骤`

请全部改为面向报告读者的内容说明。

示例替换：

1. 评分排行章节说明：
   改为：
   `本章从综合潜力与风险暴露两个角度识别开源项目：前者回答“哪些项目最值得优先关注”，后者回答“哪些项目虽然相关但复现或维护风险较高”。`

2. 综合潜力 Top 20 图说明：
   改为：
   `综合潜力 Top 20 展示评分体系下最值得优先关注的仓库，便于快速识别高热度、高活跃度且具备复现价值的项目。`

3. 数据采集漏斗图说明：
   改为：
   `数据采集漏斗展示从关键词搜索候选到最终入模样本的筛选过程，体现采集规模、去重处理和相关性过滤。`

4. 趋势洞察章节说明：
   改为：
   `趋势章节展示语言生态、Stars 长尾分布、关注度与派生开发活跃度关系，以及 AI Agent 相关主题结构。`

5. 模型预测章节说明：
   改为：
   `模型预测章节用于检验评分体系的可解释性，并通过代理标签任务观察哪些原始特征能够解释项目潜力。`

六、交互图图例与 hover 全部中文化并美化

当前图例仍有 `recommendation_level`、`risk_level_cn`、`cluster_name` 等原始字段名。请彻底修复。

1. 所有 Plotly 图例标题中文化：

   * `recommendation_level` → `推荐等级`
   * `risk_level_cn` → `风险等级`
   * `cluster_name` → `项目类型`
   * `task` → `建模任务`
   * `model` → `模型`
   * `metric` → `评价指标`

2. 所有 hovertemplate 使用中文字段，不得显示原始字段名：

   * 仓库名称
   * GitHub 链接
   * 项目主题
   * 主要语言
   * Stars
   * Forks
   * Open Issues
   * 综合潜力分
   * 个性化匹配分
   * 风险分
   * 推荐等级
   * 项目类型
   * 点击打开 GitHub 仓库

3. 优化 hover 样式：

   * 背景：`rgba(248,252,255,0.96)`
   * 边框：`#38BDF8`
   * 字体：Times New Roman + 宋体 fallback；
   * 字号：13—14px；
   * 不要默认黑框；
   * hoverlabel 中统一 `align='left'`；
   * 数值保留两位小数；
   * hover 中用 `<b>` 强调仓库名。

4. 所有仓库级图表仍保持点击跳转 GitHub：

   * Stars-Forks 气泡散点图；
   * 综合潜力 Top 20；
   * 高风险项目 Top 20；
   * 风险-潜力四象限；
   * PCA / 聚类地图；
   * 个性化分 vs 通用潜力分；
   * 个性化推荐 Top 15。

七、综合潜力 Top 20 配色调整

当前综合潜力 Top 20 按推荐等级配色，所有项目都是 A 时颜色单一。请改为按综合潜力分使用低饱和蓝色渐变。

要求：

1. 使用蓝色渐变，例如从 `#BAE6FD` 到 `#0EA5E9`；
2. 综合潜力分越高颜色越深；
3. 不再按 `推荐等级` 着色；
4. 不显示 `recommendation_level` 图例；
5. 条形末端显示分数；
6. 只显示仓库名，不显示 owner；
7. hover 中显示完整 owner/name、项目主题、Stars、Forks、潜力分、风险分、GitHub 链接；
8. 点击条形打开 GitHub。

八、高风险项目 Top 20 排序修复

当前高风险项目 Top 20 中第一条 mcp 风险分并非最高，说明排序或条形方向有误。请修复：

1. 按 `risk_score` 降序排序；
2. 排名最高的风险分必须位于第一位或图表最上方；
3. 如果使用横向条形图，注意 Plotly 的 y 轴顺序；
4. 条形末端显示风险分；
5. 高风险图允许使用橙红色系；
6. hover 显示风险等级和风险原因；
7. 只显示仓库名，不显示 owner；
8. 点击跳转 GitHub。

九、聚类画像章节排版修复

当前聚类类型数量图、聚类方法解释与聚类画像摘要分两栏后存在大片空白。请改为全部单独全宽展示：

1. 风险-潜力四象限：全宽；
2. PCA / 聚类项目地图：全宽；
3. 聚类类型数量图：全宽；
4. 聚类方法解释：全宽；
5. 聚类画像摘要：全宽。

聚类类型数量图：

1. 不要留大片空白；
2. 高度根据类别数量自动调整；
3. 横向条形；
4. 蓝色渐变；
5. 中文项目类型完整显示。

聚类方法解释：

1. `agglomerative` → `层次凝聚聚类`
2. `kmeans` → `KMeans 聚类`
3. `gaussian_mixture` 或 `gmm` → `高斯混合模型`
4. `dbscan` → `DBSCAN 密度聚类`
5. 表格居中，最佳模型行高亮。

十、模型预测章节配色和中文名修复

Task A / Task B 模型对比图：

1. 不得出现紫色；
2. 使用低饱和蓝色系；
3. 任务名中文化：

   * `任务 A：评分体系代理模型`
   * `任务 B：项目潜力代理预测`
4. 模型名中文化：

   * `logistic_regression` → `逻辑回归`
   * `random_forest` → `随机森林`
   * `extra_trees` → `极端随机树`
   * `gradient_boosting` → `梯度提升树`
   * `hist_gradient_boosting` → `直方梯度提升`
   * `calibrated_random_forest` → `校准随机森林`
   * `calibrated_classifier` → `概率校准模型`
   * `dummy` → `随机基线`
5. 图例、轴标题、hover 全中文；
6. 图中不得显示 `calibrated_random_forest` 原文。

Task A / Task B 模型结果表：

1. 模型列显示中文名；
2. 不得显示 `calibrated_random_forest` 原文；
3. 最佳模型行高亮；
4. 小数保留三位；
5. 表格居中。

特征重要性图：

1. 所有特征显示中文名；
2. 不得显示变量名，例如：

   * `agent_relevance_score`
   * `has_demo`
   * `has_requirements`
   * `mentions_gpu`
   * `mentions_api_key`
   * `has_quickstart`
   * `stars_per_day`
   * `size`
3. 增加更完整中文映射：

   * `agent_relevance_score` → `AI Agent 相关性`
   * `has_demo` → `包含 Demo 示例`
   * `has_requirements` → `包含依赖说明`
   * `mentions_gpu` → `提及 GPU`
   * `mentions_api_key` → `提及 API Key`
   * `has_quickstart` → `包含快速开始`
   * `has_example` → `包含示例`
   * `readme_length` → `README 长度`
   * `days_since_update` → `距上次更新天数`
   * `log_stars` → `Stars 对数`
   * `log_forks` → `Forks 对数`
   * `topic_count` → `Topic 数量`
   * `issue_pressure` → `Issue 压力`
   * `stars_per_day` → `日均 Stars`
   * `watchers_total` → `Watchers 数`
   * `size` → `仓库规模`
   * `forks_total` → `Forks`
   * `stars_total` → `Stars`
   * `open_issues_count` → `Open Issues`
4. 使用蓝色系；
5. hover 中文化。

十一、PyTorch 表格宽深神经网络流程图重做

当前 PyTorch 流程图仍像小卡片加箭头，不够像模型结构图。请重做为真正的网络结构流程图。

要求：

1. 使用 HTML/CSS 或 SVG 绘制；
2. 分支结构清晰，而不是单行卡片：

   * 输入层；
   * 数值特征分支；
   * 类别嵌入分支；
   * 宽分支；
   * 深层残差 MLP；
   * 特征融合；
   * 二分类输出；
3. 用连线和箭头体现分支汇合；
4. 节点使用蓝色渐变；
5. 节点内部有简短解释；
6. 图下说明：
   `该结构面向表格型仓库特征：数值指标进入数值分支，语言、主题、聚类类型等类别信息进入嵌入分支，宽分支保留线性信号，深层分支学习非线性交互。`
7. 删除 `CPU-only` 相关表述；
8. `embedding` 显示为 `类别嵌入`；
9. `wide` 显示为 `宽分支`。

十二、个性化分 vs 通用潜力分图调整

当前 Top 项目文字标签带箭头，影响可读性。请删除样本点旁边的箭头和项目名标注。

要求：

1. 删除点旁的文本标签和箭头；
2. hover 中展示项目名；
3. Top 项目可通过更深颜色或更大点体现；
4. 点适当增大；
5. 透明度 0.65—0.8；
6. 对角线保留；
7. 图例中文化；
8. 点击点打开 GitHub。

十三、个性化推荐表推荐理由自然语言化

当前推荐理由列像 Python 字符串列表，存在引号和重复模板。请重写推荐理由生成与展示：

1. 不显示引号；
2. 不显示列表符号；
3. 不显示 `语言匹配：...` 这种机械片段；
4. 将理由自然合并为 1—2 句中文；
5. 每个项目的理由应结合：

   * 项目主题；
   * 用户偏好语言；
   * 用户偏好主题；
   * 风险偏好；
   * 硬件条件；
   * 文档/复现信号；
   * 项目类型；
6. 示例：

   * `该项目以 Python 为主，主题与 MCP 工具生态高度相关，文档和复现信号较完整，适合作为可复现项目优先选择。`
   * `该仓库综合潜力较高，同时风险分较低，适合希望快速理解 AI Agent 工程结构的用户。`
7. 删除 `CPU-only` 表述；
8. 保留“推荐理由”列，但必须自然成句；
9. 仓库名称可点击 GitHub；
10. 表格居中，长文本自然换行。

十四、DeepSeek Agent 章节去掉“答辩讲法”并进一步自然化

1. 删除所有 Agent 卡片下的 `答辩讲法`；
2. Agent 卡片中不得出现：

   * `fallback`
   * `已生成解释`
   * `未显式给出`
   * `字段依据`
   * `api_status`
   * `readme_fetch_status`
   * `finding/evidence`
   * Python dict 或 JSON 痕迹；
3. 每张 Agent 卡片改成更自然的三段式：

   * `智能体职责`
   * `核心判断`
   * `建议动作`
4. 如果有数据依据，可写成中文自然句：

   * `系统结合仓库来源、README 文档信号、综合潜力分和风险分判断项目质量。`
5. ProjectAdvisorAgent 需要保留 Top 5 推荐项目、三天复现路线、Codex Prompt，但文字自然化；
6. CriticAgent 需要说明“结论均应回到字段、图表和模型卡验证”，但不要写“答辩”；
7. 所有 Agent 卡片全宽展示；
8. 卡片美工保持冰蓝科技风。

十五、项目亮点与附录文件链接可点击

项目亮点中所有“产物：相对路径”都要变成可点击链接。

示例：

1. `data/raw/github_repos_raw.csv`
2. `data/processed/scored_repos.csv`
3. `outputs/reports/stat_summary.json`
4. `outputs/reports/cluster_model_comparison.csv`
5. `outputs/reports/model_card.md`
6. `outputs/reports/torch_model_card.md`
7. `outputs/reports/personalized_recommendations.csv`
8. `outputs/agents/`
9. `outputs/reports/agent_radar_report.html`
10. `README.md`

附录中：

1. HTML 报告路径可点击；
2. PDF 报告路径可点击；
3. 主要数据文件可点击；
4. 主要模型输出可点击；
5. 主要推荐输出可点击；
6. 删除数据模式行；
7. 删除生成时间行；
8. 删除密钥说明行，或改成更自然的：
   `项目配置通过环境变量管理，展示报告不包含任何敏感凭据。`

十六、全局删除词扫描

请全仓库展示文件生成逻辑中扫描并消除以下不应出现在最终 HTML/PDF 中的词：

1. `sample_fallback`
2. `sample fallback`
3. `api_live`
4. `CPU-only`
5. `CPU only`
6. `答辩讲法`
7. `生成时间`
8. `最近更新`
9. `recommendation_level`
10. `risk_level_cn`
11. `cluster_name`
12. `task_b_proxy_good_project`
13. `calibrated_random_forest`
14. `agent_relevance_score`
15. `has_demo`
16. `has_requirements`
17. `embedding`
18. `wide`

注意：

* 这些词可以出现在源码变量名中，但不得出现在最终 `agent_radar_report.html` 和 `agent_radar_report.pdf` 的可见文本中。
* 若源码中必须使用变量名，不要强行破坏代码；重点是展示层映射。

十七、PDF 适配与检查

重新生成 PDF，确保：

1. 首页无巨大空白；
2. 文字不截断；
3. `TabularWideDeepNet` 不截断；
4. 表格行不被裁切；
5. 图表图例中文化；
6. 无变量名残留；
7. 无生成时间；
8. 无 `api_live`；
9. 无 `sample_fallback`；
10. 无 `CPU-only`；
11. 附录链接可点击或至少显示为清晰相对路径。

十八、运行验证

完成后运行：

1. `python main.py`
2. `pytest`
3. 若可用，重新生成 `outputs/reports/agent_radar_report.pdf`
4. 可选启动 `streamlit run app.py` 检查报告入口。

检查文件：

1. `outputs/reports/agent_radar_report.html`
2. `outputs/reports/agent_radar_report.pdf`

十九、完成后汇报

请按以下格式汇报：

1. 本轮修改了哪些文件；
2. 字体系统如何保证英文和数字为 Times New Roman、中文为宋体；
3. Hero 区如何重排；
4. 项目概览删去了哪些卡片；
5. 是否删除全部 `CPU-only`、`api_live`、`sample_fallback`、`答辩讲法`、`生成时间` 展示文本；
6. 图例与 hover 是否全部中文化；
7. 综合潜力 Top 20 是否改为蓝色渐变；
8. 高风险 Top 20 排序是否修复；
9. 聚类章节是否全部全宽展示；
10. 模型名和特征名是否全部中文化；
11. PyTorch 结构图是否重做；
12. 个性化散点图是否删除箭头标注；
13. 个性化推荐理由是否自然成句；
14. DeepSeek Agent 卡片是否删除答辩讲法并自然化；
15. 项目亮点和附录路径是否可点击；
16. HTML/PDF 是否重新生成；
17. `python main.py` 是否通过；
18. `pytest` 是否通过；
19. 是否存在 API Key 泄露风险；
20. 仍需人工检查的地方。
