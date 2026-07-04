请继续在当前 AgentRadar-Stat 项目基础上进行最终展示报告精修。本轮只聚焦 `AgentRadar-Stat 答辩报告`，不再单独优化 HTML 大屏；答辩展示统一以 `outputs/reports/agent_radar_report.html` 和自动导出的 `outputs/reports/agent_radar_report.pdf` 为主。

当前项目已经完成：

1. GitHub API 真实采集 500 个 api_live 仓库；
2. 数据清洗、特征工程、综合评分；
3. 多算法聚类与聚类画像；
4. Task A / Task B 防泄漏监督建模；
5. sklearn 多模型比较；
6. PyTorch TabularWideDeepNet；
7. 用户画像与个性化推荐；
8. DeepSeek Agent 解释；
9. 交互式 HTML 报告与 PDF 导出。

当前报告整体内容尚可，但仍需针对答辩展示做最终精修：视觉层级、背景、字体、图表、表格、Agent 内容、章节文本、PDF 适配和跳转链接都需要进一步优化。本轮目标是让报告达到“班级最好的、最 impressive 的 Python 程序设计期末项目展示页”。

硬约束：

1. 不要重写数据采集、模型、聚类、个性化推荐主逻辑；
2. 不要破坏 `python main.py`、`pytest`、`streamlit run app.py`；
3. 不得读取、打印、保存或提交 `.env` 中真实 API Key；
4. 默认 DeepSeek 模型保持 `deepseek-v4-pro`，但展示层不要把它当作关键词突出；
5. 不得恢复 `sample_fallback` 主展示、`available_time`、`api_budget`、`deepseek-v4-flash`、`st.json`；
6. 答辩展示层默认展示“GitHub 公开仓库数据”，不要把 fallback 机制作为主视觉内容；
7. 所有面向答辩展示的文字以中文为主，专有名词如 GitHub、DeepSeek、AI Agent、PyTorch、PCA 可保留英文；
8. 图表、表格、目录、附录、PDF 均要统一中文化、统一冰蓝科技风；
9. 如果 PDF 自动导出失败，不得中断主流程，但必须在 run_summary 和 Streamlit 中给出清晰提示。

一、最终只保留并精修答辩报告

请明确本轮主展示物为：

* `outputs/reports/agent_radar_report.html`
* `outputs/reports/agent_radar_report.pdf`

`outputs/dashboards/agent_radar_dashboard.html` 可继续生成，但不再作为主要答辩展示对象，也不需要在附录中突出展示。

请在 README、docs/demo_script.md、Streamlit 报告页中统一表述：
“答辩展示以 AgentRadar-Stat 答辩报告为主，报告中已经整合数据采集、趋势洞察、评分排行、聚类画像、模型预测、PyTorch 扩展、个性化推荐与 DeepSeek Agent 解释。”

二、背景图与视觉主题重做

当前背景图几乎看不清，页面留白较多。请不要联网下载图片，直接在项目中生成原创 SVG 背景，避免版权问题和外部依赖。

新增或重写：

* `assets/agent_radar_bg.svg`
* `assets/agent_radar_hero.svg`
* 如需要，可新增 `assets/agent_radar_nodes.svg`

背景设计要求：

1. 浅蓝科技风；
2. 包含雷达扫描圆环、节点网络、GitHub 仓库节点、Agent 决策路径、数据流线、轻量代码网格；
3. 不要黑底，不要深蓝压抑风；
4. 不要太浅到看不见；
5. 页面背景不透明度提高，建议整体可见度 0.18—0.28；
6. Hero 区背景可见度更高，建议 0.25—0.38；
7. 不影响正文阅读；
8. 背景可固定在右上和页面底部，避免大片纯白留白；
9. Report 和 Streamlit 后续应使用同一背景资源。

三、首页 Hero 区重构

当前首页右侧显示“数据采集状态、展示数据源、自动报告状态”等显而易见信息，不适合占据主视觉位置。请删除这些状态卡。

首页 Hero 区应重点展示项目功能和创新点，而不是运行状态。

Hero 标签请改为：

1. `500 个 GitHub 公开仓库`
2. `多模型评分`
3. `聚类画像`
4. `PyTorch 表格神经网络`
5. `个性化推荐`
6. `DeepSeek Agent 解释`
7. `HTML/PDF 自动报告`

不要再把 `deepseek-v4-pro`、`500 个仓库`、`报告状态：已生成`、`自动报告状态：HTML 已生成` 当作关键词展示。

首页右侧区域改为“项目能力雷达卡”，展示：

1. 真实数据采集：34 个关键词、2711 个候选、1019 个去重仓库、500 个入模项目；
2. 统计建模：评分体系、聚类画像、Task A/B、模型卡；
3. 深度学习扩展：TabularWideDeepNet；
4. 智能解释：7 个 DeepSeek Agent；
5. 个性化决策：用户画像、个性化匹配分、三天复现路线；
6. 可视化交付：交互报告、PDF、Streamlit。

首页不再显示最近更新时间。若需要保留生成时间，请放在页脚或附录，用小字号显示。

四、项目概览卡片重构

删除项目概况中的以下弱展示项：

1. README 成功比例 170/500；
2. 交互图数量 15；
3. 自动报告状态 已生成 HTML/PDF 尝试。

替换为更能体现工作量与能力的指标：

1. 真实 GitHub 仓库：500；
2. 扩展关键词：34；
3. 搜索候选：2711；
4. 去重后仓库：1019；
5. 入模项目：500；
6. A 级推荐项目：100；
7. 高风险项目：101；
8. 聚类算法比较：KMeans / GMM / Agglomerative / DBSCAN；
9. 监督任务：Task A / Task B；
10. sklearn 模型：逻辑回归、随机森林、Extra Trees、梯度提升、校准模型、Dummy 基线；
11. PyTorch 扩展：TabularWideDeepNet；
12. 个性化推荐：20；
13. DeepSeek Agent：7；
14. 输出形态：HTML 报告、PDF 报告、Streamlit。

每张概览卡片增加小图标，图标风格统一浅蓝线性图标。

五、字体系统重做

当前字体层级单调。请统一设置中文与英文字体：

CSS font-family 建议：

1. 正文中文基准字体：`SimSun`, `宋体`, `Noto Serif SC`, serif；
2. 中文大标题：`Noto Serif SC`, `Source Han Serif SC`, `SimSun`, serif；
3. 中文小标题：`Noto Serif SC`, `Microsoft YaHei`, `SimHei`, sans-serif；
4. 英文和数字：`Times New Roman`, `Georgia`, serif；
5. 图表字体：优先 `Microsoft YaHei`, `SimHei`, `Noto Sans SC`, Arial，保证中文不乱码。

标题层级要求：

1. Hero 大标题使用衬线字体，字号更大，字重 800—900；
2. 一级章标题使用衬线字体，增加浅蓝渐变下划线或左侧竖线；
3. 二级小标题使用较稳重的衬线或半衬线风格；
4. 正文使用宋体或宋体优先的中文字体，增强正式感；
5. 关键字加粗并用低饱和蓝色强调；
6. 不要所有内容都用微软雅黑；
7. 行距、段距增加，避免报告像密集表格拼接。

六、色彩系统收敛到低饱和蓝色系

当前部分图表直接发散到绿色、紫色、橙色，色调跨度过大。请统一为浅蓝科技风的低饱和蓝色系。

推荐色板：

1. 主蓝：#38BDF8；
2. 冰蓝：#7DD3FC；
3. 青蓝：#22D3EE；
4. 湖蓝：#60A5FA；
5. 雾蓝：#93C5FD；
6. 淡蓝灰：#CBD5E1；
7. 深蓝灰文字：#0F172A；
8. 辅助蓝紫只作为极少量强调：#818CF8；
9. 高风险 Top 20 允许使用红色系：

   * 中风险：#FDBA74；
   * 高风险：#F87171；
   * 极高风险：#DC2626。

除高风险图外，推荐等级 A/B/C/D 不要使用绿色/橙色/红色大跨度配色，改为：

1. A：#0EA5E9；
2. B：#38BDF8；
3. C：#93C5FD；
4. D：#CBD5E1；
   高风险图可单独用橙红色突出风险。

七、Executive Summary 重写为展示型摘要卡

当前 `Executive Summary` 仍是简单分点，且标题英文。请改为中文标题：

* `执行摘要`
  或
* `核心发现`

不要再显示 `Executive Summary`。

摘要内容不要用普通 bullet list。改成 6 张“发现卡片”或 2×3 网格，每张卡片包含：

1. 小标题；
2. 一句发现；
3. 对应数字证据；
4. 小图标。

建议六张卡片：

1. 真实采集规模：500 个 GitHub 公开仓库；
2. 评分体系：从热度、活跃、社区、文档、创新、复现、风险七维度综合评价；
3. 聚类画像：比较多种聚类算法，形成项目类型画像；
4. 预测建模：Task A / Task B 防泄漏建模，最佳 F1 指标；
5. 深度学习：PyTorch TabularWideDeepNet 在 CPU 环境完成扩展实验；
6. 个性化推荐：结合用户画像输出项目、理由、风险、复现路线与 Codex Prompt。

八、项目方法流程图改为真正流程图

当前“项目方法流程图”只是小卡片排列。请重做为真正流程图样式。

要求：

1. 横向或纵向流程线；
2. 节点之间有箭头；
3. 每个节点有编号和图标；
4. 节点分为四层：

   * 数据层：GitHub API、README、topics；
   * 特征层：清洗、特征工程、指标体系；
   * 模型层：评分、聚类、监督预测、PyTorch；
   * 决策层：个性化推荐、DeepSeek Agent、HTML/PDF/Streamlit；
5. 每个节点有一句简短说明；
6. 使用 CSS 流程图实现，不要只是普通卡片；
7. 在 PDF 中也能正常排版。

九、数据采集漏斗图调整

删除数据采集漏斗图中的：

1. README 抓取；
2. Agent 分析。

漏斗只保留：

1. 关键词搜索候选：2711；
2. 去重后仓库：1019；
3. 相关性过滤后：500；
4. 最终入模项目：500。

同时：

1. 使用浅蓝渐变，不要出现绿色和紫色；
2. 去掉重复标题；
3. 图表标题只保留页面文字标题，不要 Plotly 再重复一次；
4. hover 模板中文化并美化；
5. 漏斗旁增加“采集策略说明卡”：

   * 34 个关键词；
   * stars / updated / forks / best match 四种搜索策略；
   * 11 个 seed 仓库成功拉取；
   * full_name 去重；
   * 相关性过滤。

十、所有交互图去重标题并优化 hover

当前所有可视化图标题重复：正文写一次，Plotly 图内又写一次。请统一策略：

1. 每个图只保留卡片标题；
2. Plotly 图内 `title` 设为空；
3. 图卡片顶部写中文标题和解释；
4. hover 弹窗必须美化，不要使用原始字段名；
5. hovertemplate 使用中文字段，例如：

   * 仓库名称；
   * GitHub 链接；
   * 主要语言；
   * Stars；
   * Forks；
   * 推荐等级；
   * 综合潜力分；
   * 风险分；
   * 项目类型；
   * 技术主题。
6. hover 背景使用白色或淡蓝；
7. hover 字体使用中文字体；
8. 数字保留合理小数；
9. 不出现 `full_name`、`final_potential_score`、`risk_score`、`cluster_name` 等原始字段名。

十一、所有仓库级图增加点击跳转 GitHub 功能

以下图中的点或条形都对应具体 GitHub 仓库，必须增加点击跳转仓库链接的能力：

1. Stars-Forks 气泡散点图；
2. 综合潜力 Top 20；
3. 高风险项目 Top 20；
4. 风险-潜力四象限；
5. PCA / 聚类项目地图；
6. 个性化分 vs 通用潜力分；
7. 个性化推荐 Top 15。

实现方式：

1. Plotly customdata 放入 repo_url；
2. HTML 页面注入 JavaScript：

   * 监听 plotly_click；
   * 如果 customdata 中有 repo_url，则 window.open(repo_url, "_blank")；
3. 鼠标悬浮提示中写明：

   * `点击打开 GitHub 仓库`。
4. PDF 中不能点击也没关系，但 HTML 必须可点击。

十二、Stars-Forks 气泡散点图优化

当前点集中在一小坨，可读性差。请优化：

1. x 和 y 都使用 log10 或 symlog 显示；
2. 轴标题写为：

   * `Stars（对数刻度）`
   * `Forks（对数刻度）`
3. 对极端值做轻微 winsorize 或设置合适的 range；
4. 气泡大小不要差异过大，使用 sqrt 缩放；
5. 增加透明度；
6. 增加四分位参考线；
7. hover 显示仓库名、语言、Stars、Forks、Open Issues、推荐等级；
8. 颜色使用低饱和蓝色系，不要绿橙红混杂；
9. 增加图下注释：对数坐标用于避免头部项目压缩长尾项目。

十三、技术主题分布图中文化

将技术主题全部转为中文：

1. Agent → 智能体框架；
2. MCP → MCP 工具生态；
3. RAG → 检索增强生成；
4. Coding Agent → 编程智能体；
5. Workflow → 工作流自动化；
6. Data Agent → 数据智能体；
7. Multi-Agent → 多智能体协作；
8. Local LLM → 本地大模型。

颜色使用蓝色系渐变。

十四、评分排行章节重排

评分排行中的两张图不再两栏展示，每张图独占一行全宽。

综合潜力 Top 20：

1. 只显示仓库名，不显示 owner；

   * `langgenius/dify` 显示为 `dify`；
   * hover 中显示完整仓库名和链接；
2. 图宽占满水平；
3. 条形末端显示分数；
4. 颜色使用蓝色系；
5. 点击条形跳转 GitHub。

高风险项目 Top 20：

1. 只显示仓库名，不显示 owner；
2. 可用红色系突出风险；
3. 条形末端显示风险分；
4. hover 显示风险等级、风险原因、仓库链接；
5. 点击跳转 GitHub。

十五、高潜力项目表调整

高潜力项目表请调整字段：

1. 保留：

   * 名次；
   * 仓库名称；
   * 项目主题；
   * 主要语言；
   * Stars；
   * Forks；
   * 推荐等级；
   * 综合潜力分；
   * 风险分；
   * 项目类型；
2. 删除：

   * 个性化分；
   * 推荐理由；
3. 新增：

   * 项目主题；
4. 仓库名称必须可点击跳转 GitHub；
5. 所有单元格水平、垂直居中；
6. 表格宽度按内容自适应，不要强制拉满导致列过宽；
7. 长仓库名允许换行，但不要截断到不可读；
8. 项目类型显示为蓝色系标签；
9. 推荐等级显示为 badge；
10. 表格分页或分段展示，避免 PDF 页面切断行。

十六、聚类画像章节重排

风险-潜力四象限和 PCA / 聚类项目地图都必须单图占满水平，不再两栏。

风险-潜力四象限：

1. 全宽展示；
2. 背景分区淡蓝色；
3. 象限标签位置不要压住数据点；
4. 数据点放大一点；
5. hover 美化；
6. 点击跳转 GitHub。

PCA / 聚类项目地图：

1. 全宽展示；
2. 点大小适当增大；
3. cluster 颜色只用蓝色系不同深浅；
4. hover 美化；
5. 点击跳转 GitHub；
6. 图下增加解释：聚类用于项目画像，不作为监督标签。

聚类类型数量图、聚类方法解释和聚类画像摘要可以两栏，但必须：

1. 左右高度匹配；
2. 不出现大片空白；
3. 图卡片高度自动适应；
4. 聚类类型数量图不再下面空一大片；
5. 聚类方法解释中的 `agglomerative` 改为 `层次凝聚聚类`；
6. `k=6` 可保留；
7. 聚类画像摘要表格中文化。

十七、模型预测章节重排与中文化

模型预测中的两张图和两张表都必须全宽展示。

Task A / Task B 模型对比图：

1. 行或图例不要显示变量名；
2. 模型中文名映射：

   * logistic_regression → 逻辑回归；
   * random_forest → 随机森林；
   * extra_trees → 极端随机树；
   * gradient_boosting → 梯度提升树；
   * hist_gradient_boosting → 直方梯度提升；
   * calibrated_classifier → 概率校准模型；
   * dummy → 随机基线；
3. Task A 显示为：

   * `任务 A：评分体系代理模型`
4. Task B 显示为：

   * `任务 B：项目潜力代理预测`
5. 图中指标名中文化：

   * F1；
   * AUC；
   * 准确率；
   * 平衡准确率。

特征重要性图：

1. 不显示原始变量名；
2. 特征中文名映射：

   * agent_relevance_score → AI Agent 相关性；
   * has_demo → 是否包含 Demo；
   * has_requirements → 是否包含依赖说明；
   * readme_length → README 长度；
   * days_since_update → 距上次更新天数；
   * log_stars → Stars 对数；
   * log_forks → Forks 对数；
   * topic_count → Topic 数量；
   * issue_pressure → Issue 压力；
   * reproducibility_score → 复现可行分；
   * documentation_score → 文档质量分；
   * activity_score → 活跃维护分；
   * community_score → 社区参与分；
3. 全宽展示；
4. 颜色用蓝色系；
5. hover 中文化。

Task A 模型结果表和 Task B 模型结果表：

1. 模型列显示中文名；
2. 指标列中文化；
3. 单元格居中；
4. 小数保留 3 位；
5. 最佳模型行高亮；
6. 加解释：Task A 解释评分体系是否被少数变量支配；Task B 解释项目潜力代理预测。

十八、PyTorch 章节中文化

将以下展示文字改为中文：

1. `PyTorch TabularWideDeepNet` → `PyTorch 表格宽深神经网络（TabularWideDeepNet）`
2. `embedding` → `类别嵌入`
3. `wide` → `宽分支`
4. `deep branch` → `深层非线性分支`
5. `Task B` → `任务 B：项目潜力代理预测`

章节排版：

1. 用结构图展示模型：

   * 数值特征分支；
   * 类别嵌入分支；
   * 宽分支；
   * 深层残差 MLP；
   * 二分类输出；
2. 训练曲线全宽；
3. 模型卡改为“为什么这样设计 / 结果如何 / 局限是什么”三张说明卡；
4. 不要直接堆 Markdown 原文。

十九、个性化推荐章节调整

个性化分 vs 通用潜力分图：

1. 样本点更大；
2. 增加透明度；
3. 对 Top 5 个性化项目显示标签；
4. 对角线更明显；
5. hover 美化；
6. 点击跳转 GitHub。

个性化推荐表：

1. 最左侧增加名次列；
2. 仓库名称可点击 GitHub；
3. 项目类型列显示与高潜力表一致的分类标签；
4. 删除“推荐动作”列；
5. 增加“推荐理由”列；
6. 推荐理由必须基于项目主题与用户画像，不要固定套话；
7. 推荐理由应由 DeepSeek Agent 或规则增强生成，例如：

   * `适合 Python + CPU-only 用户，README 与示例较完整，适合作为三天复现项目。`
   * `与 RAG/Coding Agent 偏好匹配，生态热度高，但需注意依赖复杂度。`
8. 保留：

   * 名次；
   * 仓库名称；
   * 项目主题；
   * 项目类型；
   * 主要语言；
   * 个性化匹配分；
   * 通用潜力分；
   * 风险分；
   * 推荐理由；
9. 单元格水平、垂直居中；
10. 长文本推荐理由可换行，但不要挤压其他列。

二十、DeepSeek Agent 章节重点重做

这是本轮内容修改重点。当前 Agent 卡片内容有 fallback 式文本、字段堆叠、“未显式给出”等不适合答辩展示的内容。请全面重写 Agent 展示逻辑。

修改：

* `src/agents.py`
* `src/agent_display.py`
* `src/report_generator.py`

要求：

1. 每个 Agent 卡片全宽展示，不再两栏；
2. 每个 Agent 卡片都必须有：

   * 中文 Agent 名称；
   * 英文内部类名小标签；
   * 角色定位；
   * 一句话结论；
   * 关键依据；
   * 风险提醒；
   * 行动建议；
   * 用于答辩讲解的一句话；
3. 不显示原始 JSON；
4. 不显示 `fallback based on real fields`；
5. 不显示 `未显式给出`；
6. 不显示 Python dict 原样字符串；
7. 不显示 `finding: ... evidence: ...` 这种调试痕迹；
8. 如果 DeepSeek API 真实输出不可用，也要用规则生成“像正式解释卡”的中文内容；
9. 所有 Agent 输出必须结合真实项目数据和 user_profile；
10. 每个 Agent 输出至少 3 条关键依据和 2 条行动建议。

Agent 中文名称：

1. CollectorAgent → 采集策略智能体；
2. DataQualityAgent → 数据质量诊断智能体；
3. TopicAgent → 主题识别智能体；
4. ScoringAgent → 评分解释智能体；
5. ProjectAdvisorAgent → 个性化项目顾问智能体；
6. ReportAgent → 报告生成智能体；
7. CriticAgent → 事实审查智能体。

ProjectAdvisorAgent 必须输出真正可展示内容：

1. 当前用户画像摘要；
2. Top 5 推荐项目；
3. 每个项目为什么适合；
4. 热门但不适合项目；
5. 风险提示；
6. 三天复现路线；
7. Codex Prompt 示例。

CriticAgent 必须输出：

1. 审查结论；
2. 报告中已绑定的数据依据；
3. 仍需谨慎表述的地方；
4. 如何在答辩中避免夸大；
5. 总体可信度评价。

Agent 卡片美工：

1. 左侧有 Agent 图标；
2. 顶部有蓝色渐变标题条；
3. 用小标签展示 `数据依据`、`风险提示`、`行动建议`；
4. 关键句用浅蓝背景 callout；
5. 每个卡片之间留足间距；
6. PDF 中不分页切断卡片。

二十一、项目亮点章节重做

当前项目亮点章节不要简单分点。请改为“亮点矩阵”或“创新能力卡片墙”。

至少包含 8 张卡片：

1. 真实 GitHub API 数据采集；
2. 500 个开源仓库生态样本；
3. 多维评分体系；
4. 多算法聚类画像；
5. 防泄漏监督建模；
6. PyTorch 表格神经网络；
7. 用户画像个性化推荐；
8. DeepSeek 多智能体解释；
9. HTML/PDF/Streamlit 多形态交付；
10. Codex 协作式工程开发。

每张卡片包含：

1. 亮点标题；
2. 一句话解释；
3. 对应产物文件或图表；
4. 答辩时一句话讲法。

二十二、局限与展望章节重做

当前局限与展望不要简单分点。请改为两栏结构：

左栏：研究边界

1. GitHub 数据具有时点性；
2. README/topics 文本信号可能误判；
3. Task A/B 是代理标签；
4. Agent 输出是解释层；
5. 评分体系不是商业价值预测。

右栏：后续扩展

1. 增量采集与时间序列跟踪；
2. 引入真实用户反馈作为推荐标签；
3. 接入 PR / issue 互动质量；
4. 更严格的离线评测；
5. Streamlit 在线部署；
6. 生成项目复现脚手架。

每条内容用图标和短句，避免纯 bullet list。

二十三、附录调整

附录中：

1. 保留运行命令；
2. 保留 HTML 报告路径；
3. 保留 PDF 报告路径；
4. 删除 HTML 大屏行；
5. PDF 报告路径必须可点击跳转；
6. HTML 报告路径也可点击跳转；
7. 增加“主要数据文件”；
8. 增加“主要模型输出”；
9. 增加“主要推荐输出”；
10. 不显示真实 API Key；
11. 不显示过长本地临时路径；
12. 用相对路径：

* `outputs/reports/agent_radar_report.html`
* `outputs/reports/agent_radar_report.pdf`
* `data/processed/scored_repos.csv`
* `outputs/reports/model_card.md`
* `outputs/reports/personalized_recommendations.csv`

二十四、左侧目录调整

左侧报告目录目前位置偏上。请调整：

1. 桌面端目录竖直居中；
2. 使用 position sticky；
3. top 设置为 50%;
4. transform translateY(-50%);
5. 目录项间距适当增大；
6. 当前章节高亮；
7. 目录标题可写为“报告目录”；
8. PDF 打印时目录可保留在首页或转为顶部目录，避免遮挡内容；
9. 移动端改为顶部横向导航。

二十五、表格整体排版规则

所有表格必须：

1. 文字水平居中；
2. 文字垂直居中；
3. 表格本身居中；
4. 列宽依据内容设置，不要强制均分；
5. 长文本列允许换行；
6. 数值列右对齐或居中，但全表视觉统一；
7. 表头加浅蓝背景；
8. 行 hover 使用极浅蓝；
9. badge 居中；
10. PDF 中不切断单行；
11. 不出现单元格内容被裁切。

二十六、PDF 适配

请强化 print CSS：

1. A4 页面；
2. print background true；
3. 卡片避免分页切断；
4. 表格行避免分页切断；
5. Agent 卡片避免分页切断；
6. 图表缩放到页面宽度；
7. 图表高度合理，避免一页只有半张图；
8. 首页不要留巨大空白；
9. 字体在 PDF 中不乱码；
10. PDF 中链接尽可能保留。

二十七、Streamlit 报告入口微调

Streamlit 中：

1. 报告导出页仅突出答辩报告；
2. PDF 图标按钮更醒目；
3. 可打开 / 下载：

   * `outputs/reports/agent_radar_report.pdf`
   * `outputs/reports/agent_radar_report.html`
4. 不再突出 HTML 大屏；
5. 文案改为：

   * `打开 AgentRadar-Stat 答辩报告 PDF`
   * `打开交互式 HTML 答辩报告`
6. 如果 PDF 不存在，提示先运行 `python main.py` 或安装 Playwright。

二十八、运行验证

完成后运行：

1. `python main.py`
2. `pytest`
3. 如可用，重新生成 PDF；
4. 启动 `streamlit run app.py` 做页面检查。

必须检查：

1. 首页不再显示“报告状态已生成、自动报告状态、最近更新时间”占据主视觉；
2. Hero 关键词已改为项目功能与创新点；
3. 背景图明显可见但不影响阅读；
4. 字体层级更丰富；
5. 执行摘要已改为中文展示卡；
6. 方法流程图是真流程图；
7. 数据采集漏斗已删除 README 抓取和 Agent 分析；
8. 所有图表不再重复标题；
9. hover 弹窗中文化；
10. 仓库级图表点击可跳转 GitHub；
11. Stars-Forks 图可读性改善；
12. 技术主题分布已中文化；
13. Top 榜图一图占满水平；
14. Top 榜图只显示仓库名不显示 owner；
15. 高潜力项目表已删除个性化分和推荐理由，并新增项目主题；
16. 聚类两张核心图全宽；
17. 模型预测图表全宽；
18. 模型名和特征名已中文化；
19. 个性化推荐表已新增名次、推荐理由，删除推荐动作；
20. Agent 卡片全宽、中文、无 JSON、无 fallback 调试痕迹；
21. 项目亮点和局限展望已卡片化；
22. 附录删除 HTML 大屏行并加入 PDF 可点击链接；
23. 左侧目录竖直居中；
24. PDF 输出正常；
25. 无 API Key 泄露风险；
26. 无 `available_time`、`api_budget`、`deepseek-v4-flash`、`st.json` 残留。

二十九、完成后汇报

请按以下格式汇报：

1. 本轮修改了哪些文件；
2. 新增了哪些文件；
3. 背景 SVG 是否生成，路径是什么；
4. 首页 Hero 调整了哪些内容；
5. 字体系统如何调整；
6. 色彩系统如何调整；
7. 执行摘要是否已卡片化；
8. 方法流程图是否已重做；
9. 数据采集漏斗是否删去 README 抓取和 Agent 分析；
10. 交互图标题是否去重；
11. 仓库级图表是否支持点击跳转 GitHub；
12. Stars-Forks 图如何优化；
13. 技术主题是否中文化；
14. Top 图是否全宽且只显示仓库名；
15. 表格字段是否按要求调整；
16. 聚类章节是否按要求重排；
17. 模型预测章节是否中文化并全宽展示；
18. 个性化推荐表推荐理由是否已由 Agent/规则生成；
19. DeepSeek Agent 卡片是否全面重做；
20. 项目亮点与局限展望是否卡片化；
21. 附录是否删除 HTML 大屏行并加入 PDF 可点击链接；
22. PDF 是否成功生成；
23. Streamlit 报告入口是否更新；
24. `python main.py` 是否通过；
25. `pytest` 是否通过；
26. 是否有 API Key 泄露风险；
27. 是否仍有需要最终人工微调的页面或图表。
