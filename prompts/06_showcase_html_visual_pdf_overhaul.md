请继续在当前 AgentRadar-Stat 项目基础上进行一次“答辩展示级 HTML、可视化与 PDF 大修”。本轮目标不是继续增加模型算法，而是把已经完成的真实 GitHub API 数据、评分、聚类、机器学习、PyTorch 表格神经网络、个性化推荐和 DeepSeek Agent 解释，以更美观、更丰富、更有交互性、更适合课堂答辩展示的形式呈现出来。

当前项目状态：

1. GitHub API 已扩充到 500 条真实 api_live 仓库；
2. `data/raw/github_repos_raw.csv` 中 `source_type` 全部为 `api_live`；
3. `run_summary.json` 中 `data_mode=api_live`；
4. 已完成 Task A / Task B 标签定义、防泄漏、多算法聚类比较、sklearn 模型比较、PyTorch TabularWideDeepNet、用户画像与个性化推荐；
5. 当前两个 HTML 输出为：

   * `outputs/reports/agent_radar_report.html`
   * `outputs/dashboards/agent_radar_dashboard.html`
6. 当前两个 HTML 已能生成 PDF，但展示效果仍较粗糙，存在内容旧、图表静态、英文过多、布局单薄、缺少交互、报告导航缺失、时间格式不友好等问题。

本轮核心目标：

1. 大修 AgentRadar-Stat Report；
2. 大修 AgentRadar-Stat Big Screen；
3. 将直接插入的 PNG 静态图升级为 Plotly / Pyecharts 网页渲染交互图；
4. 统一浅蓝 / 冰蓝 / 青蓝科技风视觉系统；
5. 全面中文化展示文本；
6. 增强内容丰富度和答辩工作量呈现；
7. 自动生成最终报告 PDF；
8. 在 Streamlit 中通过 PDF 图标或按钮超链接跳转到最终 PDF；
9. 保持 `python main.py`、`pytest`、`streamlit run app.py` 可运行；
10. 不读取、不打印、不保存、不提交 `.env` 真实内容。

硬约束：

1. 不要破坏已经跑通的 GitHub API 数据采集、模型、聚类、个性化推荐和 Agent 主流程；
2. 不要改回 sample 数据；
3. HTML、报告、大屏、Streamlit 展示中不再强调 `sample_fallback`，默认展示为 GitHub 公开仓库数据；
4. 内部日志和 run_summary 仍可保留 fallback 机制，但前端答辩展示层不要把 fallback 作为醒目标签；
5. 默认 DeepSeek 模型保持 `deepseek-v4-pro`；
6. 不要恢复 `available_time`、`api_budget`、`deepseek-v4-flash`、`st.json`；
7. 不得硬编码 GitHub Token 或 DeepSeek API Key；
8. 所有面向答辩展示的文字以中文为主，项目名、GitHub、DeepSeek、AI Agent、Task A、Task B、PCA、KMeans、TabularWideDeepNet 等专有名词可保留英文；
9. 处理中文字体，避免图表、HTML、PDF 中出现方框乱码；
10. 不要新增过重依赖，若为 PDF 自动导出必须新增依赖，应优先做可选依赖，不得导致主流程崩溃。

一、先修复报告仍显示旧 sample 数据的问题

当前 `agent_radar_report.html` 曾出现 `sample_fallback`、150 条项目、sample 仓库名等旧内容。请先彻底修复数据源同步问题：

1. `report_generator.py`、`dashboard.py`、`app.py` 必须优先读取最新主结果：

   * `data/processed/scored_repos.csv`
   * `data/processed/clustered_repos.csv`
   * `outputs/reports/run_summary.json`
   * `outputs/reports/model_metrics_task_a.csv`
   * `outputs/reports/model_metrics_task_b.csv`
   * `outputs/reports/cluster_profile.csv`
   * `outputs/reports/personalized_recommendations.csv`

2. 如果最新结果中 `source_type=api_live`，则展示层统一表述为：

   * “GitHub 公开仓库数据”
   * “本次分析覆盖 500 个真实 GitHub 仓库”
   * “数据采集状态：已完成”
   * 不要在首页 Hero 和核心指标卡中显示 `sample_fallback`。

3. 如果内部确实发生 fallback，只在技术附录或运行状态卡中简要说明，不要作为主视觉标签。

4. 生成报告前必须覆盖旧 HTML、旧 dashboard 和旧 PDF，避免打开历史版本。

5. 在 `outputs/reports/run_summary.json` 中继续保留真实 data_mode，但前端展示层使用更适合答辩的中文表达：

   * `api_live` → “GitHub 实时采集数据”
   * `sample_fallback` → “离线兜底演示数据”

二、统一视觉系统：冰蓝科技风 + 雷达网络背景

请新增或完善统一主题文件：

* `src/theme.py`
* `src/ui_components.py`

视觉风格要求：

1. 主色调为浅蓝、冰蓝、青蓝、科技蓝；

2. 不是单一蓝色，要使用同色系丰富层次；

3. 推荐色彩：

   * 主色：#38BDF8
   * 亮青：#22D3EE
   * 辅蓝：#60A5FA
   * 深科技字色：#0F172A
   * 正文深灰：#1F2937
   * 弱文本灰：#64748B
   * 背景浅蓝：#F8FCFF
   * 浅渐变背景：#EEF8FF
   * 卡片白：rgba(255,255,255,0.92)
   * 成功绿：#10B981
   * 警告橙：#F59E0B
   * 风险红：#EF4444
   * 紫蓝强调：#8B5CF6

4. 所有 HTML、可视化图表、表格、badge、Streamlit 后续展示应使用同一主题变量；

5. 不要深蓝黑底赛博朋克，不要花哨红紫；

6. 页面要像“清爽冰蓝 AI 数据雷达”，有科技感但可读性强；

7. 卡片使用圆角、浅阴影、细边框、玻璃拟态轻微透明；

8. 页眉或背景加入与项目相关的轻量插画：

   * AI 雷达扫描圈；
   * GitHub 节点网络；
   * Agent 决策路径；
   * 数据流光点；
   * 代码网格；

9. 如果无法联网找图片，请在项目内生成一个纯 SVG 背景文件：

   * `assets/agent_radar_bg.svg`
   * 内容为浅蓝渐变、雷达圆环、节点连线、GitHub/AI/Agent 抽象图形；

10. 将该 SVG 背景用于：

* `agent_radar_report.html`
* `agent_radar_dashboard.html`
* Streamlit CSS 背景；

11. 背景不透明度不要太低，要能看出主题，但不能影响阅读。

三、中文字体与语言统一

请建立统一中文字体策略，避免图表、HTML 和 PDF 中中文显示为方框。

要求：

1. HTML CSS font-family：

   * `"Microsoft YaHei", "Noto Sans SC", "PingFang SC", "SimHei", Arial, sans-serif`
2. 中文标题可使用：

   * `"Noto Serif SC", "Microsoft YaHei", serif`
3. Plotly 图表 layout 中设置：

   * font.family = "Microsoft YaHei, Noto Sans SC, SimHei, Arial"
4. Matplotlib 如仍用于生成备用图，设置中文字体 fallback：

   * Microsoft YaHei
   * SimHei
   * Noto Sans CJK SC
5. 面向答辩展示的 HTML、图表标题、坐标轴、图例、表格列名全部中文化；
6. 保留英文的仅限：

   * AgentRadar-Stat
   * GitHub
   * DeepSeek
   * AI Agent
   * Task A / Task B
   * PCA / KMeans / GMM / DBSCAN
   * TabularWideDeepNet
   * 仓库名、项目名、编程语言名、模型名等专有名词；
7. 不要再出现：

   * `full_name`
   * `final_potential_score`
   * `risk_score`
   * `recommendation_level`
   * `source_type`
   * `pca_x`
   * `pca_y`
   * `count`
   * `cluster`
     这些原始字段作为图表或表格的展示列名；
8. 用中文替代：

   * full_name → 仓库名称
   * final_potential_score → 综合潜力分
   * personalized_score → 个性化匹配分
   * risk_score → 风险分
   * recommendation_level → 推荐等级
   * source_type → 数据来源
   * pca_x → PCA 第一主成分
   * pca_y → PCA 第二主成分
   * count → 项目数量
   * cluster_name → 项目类型
   * language → 主要语言
   * stars_total → Stars
   * forks_total → Forks
   * open_issues_count → Open Issues
   * days_since_update → 距上次更新天数。

四、时间格式友好化

当前 HTML 右上角时间形如 `2026-06-20T23:22:26.193154+00:00`，不适合答辩展示。请新增统一时间格式化函数：

* `format_display_time(dt)`

要求：

1. 将 ISO 时间转为人能直接看懂的中文时间；
2. 推荐格式：

   * `2026年6月21日 07:22`
   * 或 `2026-06-21 07:22`
3. 如能识别时区，优先显示本地时间 `UTC+8`；
4. Hero 区显示：

   * `最近更新：2026年6月21日 07:22`
5. 不要显示微秒和 `+00:00`；
6. Report、Big Screen、Streamlit、PDF 中统一使用该格式。

五、AgentRadar-Stat Report：重做为正式答辩报告网页

请重点大修：

* `src/report_generator.py`
* 输出：`outputs/reports/agent_radar_report.html`

报告需要从“代码结果拼接页”升级为“正式课程项目成果网页”。

必须新增可跳转目录导航：

1. 左侧固定或顶部吸附目录；
2. 点击可跳转到章节；
3. 当前章节可高亮；
4. 移动端或窄屏下可折叠；
5. 目录建议包括：

   * 项目概览
   * 数据采集
   * 指标体系
   * 趋势洞察
   * 评分排行
   * 聚类画像
   * 模型预测
   * PyTorch 扩展
   * 个性化推荐
   * DeepSeek Agent
   * 项目亮点
   * 局限与展望
   * 附录

Report 首页结构：

1. Hero 大标题：

   * AgentRadar-Stat
   * AI Agent 开源生态趋势挖掘、质量评分与智能选题决策平台
2. 副标题：

   * 基于 GitHub 公开仓库数据、统计建模、PyTorch 表格神经网络与 DeepSeek 多智能体的开源项目决策平台
3. 状态徽章：

   * GitHub 公开仓库数据
   * 500 个仓库
   * deepseek-v4-pro
   * 个性化推荐
   * 可交互报告
4. 最近更新时间：中文友好格式；
5. 不显示 `sample_fallback`；
6. 不显示 `sample fallback only when API fails · keys are never embedded in this report`；
7. 页脚改成更适合答辩展示的表达，例如：

   * `AgentRadar-Stat · Python 程序设计期末项目 · GitHub 开源生态智能决策平台`
   * `数据、模型与可视化由项目流水线自动生成`
   * 不要强调 keys 或 fallback。

核心指标卡片需要更丰富：

1. GitHub 仓库样本量；
2. 采集关键词数量；
3. 去重前项目数；
4. 去重后项目数；
5. 相关性过滤后项目数；
6. A 级推荐项目数；
7. 高风险项目数；
8. 最佳 sklearn 模型与 F1；
9. PyTorch TabularWideDeepNet 指标；
10. 最优聚类模型与 k；
11. 个性化推荐项目数；
12. DeepSeek Agent 数量；
13. README 成功采集比例；
14. 生成图表数量；
15. 自动报告状态。

Executive Summary 要从 5 条扩展到 6—8 条，必须体现工作量：

1. 真实 GitHub API 采集了 500 个 AI Agent 相关项目；
2. 构建了趋势热度、活跃度、社区参与、文档质量、创新性、复现可行性、风险等多维指标；
3. 使用多算法聚类比较形成项目画像；
4. 区分 Task A / Task B 并做防泄漏建模；
5. 使用 sklearn 多模型比较与概率校准；
6. 使用 PyTorch TabularWideDeepNet 做深度学习扩展；
7. 使用用户画像生成个性化推荐；
8. 使用 DeepSeek Agent 进行解释、风险提示和 Codex Prompt 生成。

内容丰富度要求：

1. 每章不能只放图和表，要有“本章看什么、发现什么、为什么重要”；
2. 每张图前后至少有一句解释；
3. 每个表格前有解释标题；
4. 每个模型结果后有方法解释；
5. 每个 Agent 输出后有“用于答辩讲解的关键一句话”。

六、所有可视化改为网页交互图，不再直接插 PNG

当前报告中出现 `language_distribution.png`、`stars_distribution.png` 等静态图文件名和 PNG 插图。请将报告和大屏中所有用于展示的图升级为 Plotly 或 Pyecharts 交互图。

请新增或完善：

* `src/interactive_visualization.py`

要求：

1. 使用 Plotly 生成 HTML fragment；
2. HTML 报告中嵌入交互图，不只是链接或 PNG；
3. HTML 大屏中嵌入交互图；
4. Plotly 配色统一冰蓝科技风；
5. hover 信息中文化；
6. 图标题中文化；
7. 坐标轴中文化；
8. 图例中文化；
9. 图中不要显示原始字段名；
10. 兼容 PDF 导出：交互图在 HTML 中可交互，导出 PDF 时能正常显示静态画面。

至少生成并嵌入以下交互图：

1. 编程语言分布图；

   * 标题：主要编程语言分布
   * 横轴：仓库数量
   * 纵轴：编程语言

2. Stars 分布图；

   * 使用 log 或分箱，避免极端值挤压；
   * 标题：GitHub Stars 分布特征

3. Stars-Forks 气泡散点图；

   * x：Stars
   * y：Forks
   * size：Open Issues 或 README 长度
   * color：推荐等级
   * hover：仓库名称、语言、潜力分、风险分

4. 技术主题分布图；

   * Agent / RAG / MCP / Coding Agent / Workflow / Data Agent 等

5. 综合潜力 Top 20 排行榜；

   * 横向条形图；
   * 颜色按推荐等级；
   * hover 显示风险、语言、项目类型

6. 高风险项目 Top 20；

   * 横向条形图；
   * 颜色按风险等级；
   * 体现风险解释

7. 风险—潜力四象限图；

   * x：风险分
   * y：综合潜力分
   * color：推荐等级
   * size：Stars 或个性化分
   * 添加象限背景或注释：

     * 高潜力低风险：优先推荐
     * 高潜力高风险：谨慎探索
     * 低潜力低风险：普通参考
     * 低潜力高风险：暂不推荐

8. PCA / 聚类项目地图；

   * x：PCA 第一主成分
   * y：PCA 第二主成分
   * color：项目类型
   * hover 显示仓库、语言、潜力分、风险分

9. 聚类类型数量图；

   * 修复当前中文标签竖排断裂问题；
   * 标签完整横向显示；
   * 标题中文化。

10. Task A / Task B 模型对比图；

    * x：模型
    * y：F1 / AUC
    * 分组：Task A / Task B

11. 特征重要性图；

    * 中文变量名；
    * 展示模型判断依据。

12. PyTorch 训练曲线；

    * train / valid loss；
    * 如果有 AUC/F1 也展示。

13. 个性化分 vs 通用潜力分对比图；

    * 展示个性化推荐与通用排名差异。

14. 推荐等级占比环形图；

15. 数据采集漏斗图：

    * 去重前 2561
    * 去重后 1004
    * 相关性过滤后 500
    * README 抓取数量
    * Agent 分析数量。

七、Report 中新增“项目方法流程图”和“指标体系图”

为了体现工作量，请新增两个图形化模块，不一定用复杂库，可以用 HTML/CSS 卡片流程实现：

1. 方法流程图：

   * GitHub API 采集
   * README 文本解析
   * 特征工程
   * 综合评分
   * 聚类画像
   * 监督预测
   * PyTorch 扩展
   * 个性化推荐
   * DeepSeek Agent 解释
   * HTML/PDF/Streamlit 展示

2. 指标体系图：

   * 趋势热度
   * 活跃维护
   * 社区参与
   * 文档质量
   * 技术创新
   * 复现可行
   * 风险惩罚
   * 个性化匹配

每个节点带图标、简短解释和颜色标签。

八、AgentRadar-Stat Big Screen：重做为答辩大屏

请重点大修：

* `src/dashboard.py`
* 输出：`outputs/dashboards/agent_radar_dashboard.html`

大屏定位：

1. 不是报告，不要太长；
2. 是答辩时投屏打开的“总览驾驶舱”；
3. 一屏或两屏内展示最 impressive 的内容；
4. 要视觉冲击力强、图表多、信息密度高但不乱。

Big Screen 结构建议：

1. 顶部 Hero：

   * AgentRadar-Stat 智能开源项目雷达
   * 500 个 GitHub 公开仓库 · 多模型评分 · 个性化推荐 · DeepSeek Agent 解释
   * 最近更新：中文时间
   * 不显示 ISO 时间；
   * 不显示 fallback。

2. 第一行 KPI 卡片：

   * 仓库样本量 500
   * 关键词 34
   * 去重前 2561
   * 去重后 1004
   * 入模项目 500
   * A 级推荐 100
   * 最佳模型 F1
   * 聚类类型 k
   * 个性化推荐 20
   * Agent 数 7

3. 中部核心图：

   * 风险—潜力四象限图，放大；
   * PCA 项目地图，放大；
   * Top 15 综合潜力榜；
   * Top 15 个性化推荐榜。

4. 底部或右侧：

   * 数据采集漏斗；
   * 推荐等级占比；
   * 聚类类型分布；
   * 模型对比简图；
   * Agent 状态卡。

5. 大屏中所有图都要交互；

6. 去掉原始字段名；

7. 统一中文图名；

8. 不要用 PNG；

9. 修复 cluster 标签竖排问题；

10. 页面背景使用 agent_radar_bg.svg 或 CSS 科技网格背景；

11. 图表卡片要有标题、说明和小标签；

12. 不要显示 “Report ready”“API status primary source” 这类英文调试词，改为中文：

    * 报告状态：已生成
    * 数据状态：GitHub 公开仓库数据
    * Agent 状态：DeepSeek 解释已生成。

九、表格全面优化

请为 Report 和 Streamlit / Big Screen 可复用表格新增统一渲染函数。

建议放在：

* `src/ui_components.py`
* 或 `src/report_components.py`

表格要求：

1. 仓库名可点击跳转 GitHub；
2. 表头中文化；
3. 推荐等级用彩色 badge；
4. 风险等级用彩色 badge；
5. 项目类型用标签；
6. 数据来源不在主表中展示；
7. 不显示 README 大段文本；
8. 分数保留两位小数；
9. Top 表增加名次列；
10. 对高潜力项目可加“推荐理由”短句；
11. 对高风险项目可加“风险提示”短句；
12. 表格行距、字体、边框、hover 效果都要美化。

十、DeepSeek Agent 展示内容丰富化

当前 Agent 章节太粗糙。请完善 Agent 输出展示，不能只显示 “explanation generated”。

请新增或完善：

* `src/agent_display.py`

要求：

1. 读取 `outputs/agents/`；
2. 将每个 Agent 输出转为中文卡片；
3. 每个 Agent 卡片包含：

   * Agent 名称；
   * 职责说明；
   * 一句话结论；
   * 关键发现；
   * 数据依据；
   * 风险提示；
   * 行动建议；
   * 是否 fallback；
   * 使用模型 deepseek-v4-pro；
4. ProjectAdvisorAgent 单独展示：

   * 适合当前用户画像的 Top 项目；
   * 为什么适合；
   * 热门但不适合的项目；
   * 三天复现路线；
   * Codex Prompt 示例；
5. CriticAgent 单独展示：

   * 审查结论；
   * 哪些表述需要补证据；
   * 修改建议；
   * 当前报告可信度评价；
6. 不要展示原始 JSON；
7. 如保留调试信息，只能折叠隐藏，默认不展开；
8. 在 Report 与 Streamlit 中都使用同一 Agent 展示组件。

十一、PDF 自动生成

用户需要自动生成最终报告 PDF，并在 Streamlit 中通过 PDF 图标或按钮跳转到 PDF。

请新增：

* `src/pdf_exporter.py`

目标输出：

* `outputs/reports/agent_radar_report.pdf`

要求：

1. `python main.py` 运行后自动尝试生成 PDF；
2. 优先使用 Playwright 渲染 HTML 为 PDF：

   * 如果 `playwright` 已安装，则使用；
   * 如果未安装，不要让主流程崩溃；
   * 输出 warning，并在 README 中提示安装：

     * `python -m pip install playwright`
     * `python -m playwright install chromium`
3. 可选备选方案：

   * 如果系统有 Edge/Chrome，可尝试命令行 headless 打印 PDF；
   * 如实现成本较高，可先保留 Playwright 方案；
4. PDF 页面格式：

   * A4；
   * print background = true；
   * 保留背景、颜色、图表；
   * 页面分页不截断卡片；
5. 为 HTML 增加 print CSS：

   * `@media print`
   * 避免卡片分页断裂；
   * 隐藏交互控件；
   * 保留目录和图表；
6. 如果 PDF 成功生成，在 run_summary 写入：

   * report_pdf_path；
   * pdf_generated=true；
7. 如果失败，写入：

   * pdf_generated=false；
   * pdf_warning；
8. 不得因为 PDF 失败中断 `python main.py`。

十二、Streamlit 中加入 PDF 图标跳转

请修改 `app.py`：

1. 在首页或报告导出页加入一个醒目的 PDF 图标按钮：

   * 文案：`打开最终报告 PDF`
   * 图标：📄 或 Font Awesome PDF 图标；
2. 点击后可打开：

   * `outputs/reports/agent_radar_report.pdf`
3. 若 Streamlit 本地无法直接超链接本地文件，则提供：

   * 下载按钮 `st.download_button`
   * 或显示本地路径和打开说明；
4. 同时提供：

   * 打开 HTML 报告；
   * 打开 HTML 大屏；
5. 报告导出页显示：

   * HTML 报告状态；
   * PDF 报告状态；
   * 大屏状态；
   * 生成时间；
   * 文件大小；
6. 保持冰蓝科技风。

十三、README 与文档同步更新

请更新：

1. `README.md`
2. `docs/user_guide.md`
3. `docs/demo_script.md`
4. `docs/development_log.md`
5. `AGENTS.md`

README 新增：

1. 最终展示形态；
2. HTML 交互报告；
3. HTML 答辩大屏；
4. 自动 PDF 报告；
5. Streamlit PDF 跳转；
6. 交互可视化图清单；
7. 中文显示与字体说明；
8. 如何安装 PDF 导出依赖；
9. 如何运行：

   * `python main.py`
   * `streamlit run app.py`
10. 如何打开：

* `outputs/reports/agent_radar_report.html`
* `outputs/reports/agent_radar_report.pdf`
* `outputs/dashboards/agent_radar_dashboard.html`

docs/demo_script.md 需要写 3—5 分钟答辩展示路线：

1. 先打开 Big Screen；
2. 展示 500 条 GitHub 仓库、采集漏斗、Top 榜；
3. 展示风险—潜力四象限；
4. 展示 PCA 聚类地图；
5. 展示 Report 的目录导航；
6. 展示模型严谨性章节；
7. 展示个性化推荐；
8. 展示 DeepSeek Agent 解释；
9. 最后打开 Streamlit 报告导出页和 PDF。

十四、运行验证

修改完成后请运行：

1. `python main.py`
2. `pytest`
3. 如安装了 Playwright，则测试 PDF 生成；
4. `streamlit run app.py`

检查输出：

1. `outputs/reports/agent_radar_report.html`
2. `outputs/reports/agent_radar_report.pdf`
3. `outputs/dashboards/agent_radar_dashboard.html`
4. `outputs/reports/run_summary.json`

必须验证：

1. Report 不再显示 sample_fallback 为主模式；
2. Report 不再显示 150 条 sample 数据；
3. Report 首页显示 500 条 GitHub 仓库；
4. Big Screen 显示中文标题和中文图表；
5. 时间格式为中文友好格式；
6. Report 有可跳转目录；
7. 可视化图为 HTML 交互图，而不是静态 PNG 文件名；
8. 聚类类型图不再出现中文竖排断裂；
9. 页脚不再显示 `sample fallback only when API fails · keys are never embedded in this report`；
10. PDF 能生成或给出可理解 warning；
11. Streamlit 能看到 PDF 图标/下载按钮；
12. 没有 API Key 泄露；
13. `available_time`、`api_budget`、`deepseek-v4-flash`、`st.json` 不得残留。

十五、完成后汇报

请最后按以下格式汇报：

1. 本轮修改了哪些文件；
2. 新增了哪些文件；
3. Report 是否已改为 500 条 GitHub 真实数据展示；
4. Report 是否已新增可跳转目录；
5. Report 是否仍显示 sample_fallback；
6. Big Screen 是否已中文化；
7. Big Screen 是否修复 ISO 时间；
8. Big Screen 是否修复 cluster 中文竖排问题；
9. 所有展示图是否改为交互图；
10. 新增了哪些交互图；
11. 是否生成 agent_radar_bg.svg；
12. 是否生成 PDF；
13. PDF 路径是什么；
14. Streamlit 是否加入 PDF 图标/下载按钮；
15. README 和 demo_script 是否更新；
16. `python main.py` 是否通过；
17. `pytest` 是否通过；
18. 是否存在 API Key 泄露风险；
19. 如果 PDF 自动生成失败，原因是什么，如何安装依赖解决；
20. 下一轮是否只需做微调和截图材料。
