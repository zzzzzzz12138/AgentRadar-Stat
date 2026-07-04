请继续在当前 AgentRadar-Stat 项目基础上进行第三轮迭代。本轮目标是“展示级优化与前端美工升级”，不是重写数据管道，也不是新增大量后端算法。

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

但当前展示效果仍然不够精致，图表、表格、HTML、Streamlit 页面较简略，Agent 输出还存在直接展示 JSON 的问题。本轮必须重点优化视觉风格、排版层级、交互体验和 Agent 解释呈现。

重要硬约束：

1. 不要破坏已经跑通的 `python main.py` 主流程；
2. 不要删除已有核心模块；
3. 不要硬编码 GitHub Token 或 DeepSeek API Key；
4. 不要读取、打印、保存或提交 `.env` 真实内容；
5. 默认 DeepSeek 模型保持 `deepseek-v4-pro`；
6. GitHub API 仍是主数据源，sample 只是 fallback；
7. DeepSeek Agent 仍优先真实调用 API，fallback 只用于异常兜底；
8. 项目继续适配 Windows 11、Python 3.10、CPU-only；
9. 不要新增过重依赖，优先使用现有 pandas、plotly、pyecharts、streamlit、jinja2、matplotlib、seaborn；
10. 所有页面和报告中严禁直接展示原始大段 JSON；
11. 修改完成后确保 `python main.py`、`pytest`、`streamlit run app.py` 具备可运行基础。

本轮统一视觉风格要求：

1. 整体主色调为浅蓝、冰蓝、青蓝、科技蓝，不要深蓝压抑风；
2. 推荐色彩：

   * 主色：#38BDF8 或 #22D3EE
   * 辅色：#60A5FA
   * 背景：#F8FCFF、#EEF8FF、#F0FBFF
   * 卡片白：#FFFFFF
   * 正文深灰：#1F2937
   * 弱文本灰：#64748B
   * 成功绿：#10B981
   * 警告橙：#F59E0B
   * 风险红：#EF4444
3. 页面风格为“清爽冰蓝科技风 / cyber data dashboard”，不要黑底赛博朋克，也不要大红大紫；
4. 卡片采用圆角、浅阴影、细边框、充足留白；
5. 图表标题、图例、坐标轴风格统一；
6. 表格要做 Top 项目高亮、推荐等级徽章、风险标签；
7. HTML 和 Streamlit 都要避免“代码调试感”，要像正式项目展示页。

一、重构并美化 Streamlit App

请重点优化 `app.py`，必要时可新增 `src/ui_components.py` 或 `src/streamlit_components.py` 存放 UI 组件，避免 app.py 过长。

Streamlit 页面必须做到：

1. 顶部 Hero 区：

   * 项目名称 AgentRadar-Stat；
   * 一句话定位；
   * 当前运行模式 badge：api_live / sample_fallback；
   * GitHub API 状态 badge；
   * DeepSeek Agent 状态 badge；
   * 更新时间。

2. 全局样式：

   * 使用 `st.markdown` 注入 CSS；
   * 冰蓝科技风背景；
   * 卡片式布局；
   * 指标卡片；
   * 圆角按钮；
   * 推荐等级 badge；
   * 风险等级 badge；
   * 不要直接展示裸 JSON。

3. 首页：

   * 系统流程图或流程卡片：API采集 → 清洗特征 → 评分建模 → 聚类解释 → Agent推荐 → 报告导出；
   * 核心指标卡片：

     * 项目样本量；
     * API live 数量；
     * fallback 数量；
     * A 级推荐项目数；
     * 高风险项目数；
     * README 获取成功率；
     * 最佳模型 F1；
     * Agent 调用成功率。

4. API 状态页：

   * 展示 GitHub Token 是否配置，但不能展示 Token；
   * 展示 DeepSeek API Key 是否配置，但不能展示 Key；
   * 展示 source_type 分布；
   * 展示 API 采集日志摘要；
   * 展示 rate limit 信息，如果当前代码没有 rate limit 字段，则显示“当前版本未采集 rate limit，建议下一轮接入”；
   * 不能出现报错堆栈裸露。

5. 趋势分析页：

   * 使用 Plotly 图表替代粗糙静态图；
   * 语言分布；
   * 技术方向分布；
   * stars/forks 分布；
   * Top 20 项目交互表；
   * 表格中 full_name 应可点击 repo_url；
   * recommendation_level 用彩色 badge 显示。

6. 评分与推荐页：

   * Top 20 高潜力项目排行榜；
   * 支持按 language、cluster_name、recommendation_level 筛选；
   * 单项目评分卡；
   * trend/activity/community/documentation/innovation/feasibility/risk 分数用雷达图或横向进度条展示；
   * 风险提示用标签展示，而不是 JSON。

7. 聚类地图页：

   * 交互式 PCA/KMeans 散点图；
   * hover 显示 full_name、language、final_potential_score、risk_score、cluster_name；
   * cluster 类型说明卡片；
   * 每个 cluster 展示代表项目 Top 5；
   * 使用统一冰蓝科技风配色。

8. 模型结果页：

   * 模型对比表美化；
   * F1/Accuracy/Precision/Recall 使用指标卡；
   * 特征重要性使用 Plotly 横向条形图；
   * PyTorch loss 曲线展示；
   * 模型解释文字用“结论—证据—局限性”结构，不要只展示 markdown 文件原文。

9. DeepSeek Agent 页：

   * 严禁直接展示原始 JSON；
   * Agent 输出必须解析成可读卡片；
   * 至少包括：

     * 项目推荐理由卡；
     * 风险提示卡；
     * 复现难度卡；
     * 三天复现路线；
     * Codex Prompt 可复制文本框；
     * CriticAgent 审查结果 badge：pass / warning / fail；
   * 如果 fallback_used=true，要显示“当前为 fallback 解释”，但仍用卡片式展示；
   * weak_sentences 不要原样 JSON 展示，应转换为“待补充依据的表述”列表；
   * 对 status=fail 的 CriticAgent 输出，要展示：

     * 审查状态；
     * 发现的问题；
     * 需要补充的数据依据；
     * 修改建议；
   * 不得显示 API Key 或完整请求体。

10. 单项目详情页：

    * 选择项目后展示：

      * 仓库基础信息；
      * repo_url 可点击；
      * 语言、stars、forks、issues、更新时间；
      * 推荐等级；
      * final_potential_score；
      * 风险分；
      * cluster_name；
      * README 质量标签；
      * 是否 CPU 友好；
      * 是否提到 GPU；
      * 是否需要 API Key；
      * Agent 推荐解释；
    * 增加“生成/刷新该项目 Agent 解释”按钮；
    * 结果要缓存，避免重复 API 消耗；
    * 如果暂时实现实时调用成本较高，可先从 outputs/agents 已有结果读取，但 UI 上保留按钮和缓存结构。

11. 报告导出页：

    * 显示 HTML 报告路径；
    * 提供打开说明；
    * 显示报告生成时间；
    * 显示包含哪些章节；
    * 不要只输出文件路径。

二、优化 Agent 输出展示逻辑

请新增或完善一个 Agent 输出解析与展示模块，建议新建：

* `src/agent_display.py`

功能：

1. 读取 `outputs/agents/` 下的 Agent 输出；

2. 兼容 JSON、dict、纯文本三种格式；

3. 将 Agent 输出规范化为统一结构：

   * title
   * status
   * summary
   * key_findings
   * evidence
   * risks
   * recommendations
   * next_steps
   * codex_prompt
   * fallback_used
   * model
   * created_at

4. 对 CriticAgent 特殊处理：

   * status；
   * weak_sentences；
   * evidence_gaps；
   * suggestions；
   * final_verdict。

5. 对 ProjectAdvisorAgent 特殊处理：

   * recommended_projects；
   * reasons；
   * difficulty；
   * three_day_plan；
   * codex_prompt。

6. 严禁在前端直接 `st.json(raw_agent_output)`；

7. 如确实需要展示原始 JSON，只能放在默认折叠的 expander 中，标题为“调试信息”，且默认不展开。

三、重写 HTML 报告视觉样式

请重点优化 `src/report_generator.py` 生成的：

* `outputs/reports/agent_radar_report.html`

要求报告不再像简单文本拼接，而是像正式课程项目成果网页。

视觉风格：

1. 冰蓝科技风；
2. 顶部大标题 Hero；
3. 渐变背景；
4. 指标卡片；
5. 模块化分区；
6. 圆角白色卡片；
7. 浅阴影；
8. 表格美化；
9. 推荐等级 badge；
10. 风险标签；
11. 图表嵌入；
12. 页脚说明数据来源与运行时间。

报告结构必须包括：

1. Hero 区：

   * AgentRadar-Stat；
   * 副标题；
   * 运行模式；
   * 生成时间；
   * GitHub API 状态；
   * DeepSeek Agent 状态。

2. Executive Summary：

   * 3—5 条核心结论；
   * 每条结论必须带对应数据依据，例如样本量、Top 项目、模型指标、聚类数量。

3. 核心指标卡片：

   * 样本量；
   * api_live / sample_fallback；
   * A 级项目数量；
   * 高风险项目数量；
   * 平均 final_potential_score；
   * 最佳模型 F1；
   * README 获取成功率；
   * Agent fallback 比例。

4. 数据来源与采集：

   * GitHub API 主流程；
   * sample fallback 说明；
   * 当前运行模式；
   * API 失败原因摘要，如果有；
   * 不要出现真实 Key。

5. 趋势分析：

   * 语言分布；
   * 技术方向分布；
   * star/fork 分布；
   * 嵌入关键图表 PNG 或 Plotly HTML；
   * 不要只给链接。

6. 综合评分：

   * 评分公式；
   * 评分维度说明；
   * Top 10 高潜力项目表；
   * Top 10 高风险项目表；
   * recommendation_level badge。

7. 聚类分析：

   * PCA/KMeans 图嵌入；
   * cluster 类型解释；
   * 各 cluster 数量；
   * 每类代表项目；
   * 不要展示原始 JSON。

8. 模型结果：

   * 模型对比卡片；
   * 最佳模型说明；
   * 特征重要性图；
   * PyTorch MLP loss 曲线；
   * 模型局限性。

9. DeepSeek Agent 解释：

   * 各 Agent 输出以卡片展示；
   * CriticAgent 输出改为“审查结果卡”，不显示 JSON；
   * 如果 status=fail，改写为“发现若干需补充依据的表述”，并列出可读建议；
   * ProjectAdvisorAgent 输出 Top 推荐项目、理由、风险、三天路线。

10. 项目边界与局限：

    * 不预测商业价值；
    * API 采集存在时点性；
    * README 文本分析存在误判；
    * Agent 输出是辅助解释；
    * 评分权重可调整。

11. 附录：

    * 字段说明；
    * 评分公式；
    * 运行命令；
    * GitHub API / DeepSeek API 配置方式，不能包含真实 Key。

四、优化 HTML 大屏

请优化 `src/dashboard.py` 输出的：

* `outputs/dashboards/agent_radar_dashboard.html`

要求：

1. 统一冰蓝科技风；
2. 顶部标题栏；
3. 指标卡片；
4. 图表网格布局；
5. 风险—潜力四象限图；
6. PCA 聚类图；
7. Top 项目排行榜；
8. Agent 状态卡片；
9. API 状态卡片；
10. 不展示 JSON；
11. 页面打开后视觉上能直接作为课堂展示大屏。

如果使用 pyecharts，请设置统一主题、背景色、标题样式和图例样式。
如果使用 plotly，请使用统一 template 和 color_discrete_sequence。

五、统一图表美工

请优化 `src/visualization.py` 中全部静态图。

要求：

1. 统一配色为浅蓝、青蓝、冰蓝；
2. 图表标题统一；
3. 坐标轴标签统一；
4. 网格线弱化；
5. 字体尽量清晰；
6. 输出分辨率提高，例如 dpi=180 或 220；
7. 图表尺寸适合报告嵌入；
8. 避免默认 Matplotlib 丑样式；
9. 推荐等级颜色统一：

   * A：#10B981
   * B：#38BDF8
   * C：#F59E0B
   * D：#EF4444
10. 风险颜色统一：

* low：#10B981
* medium：#F59E0B
* high：#EF4444

如中文字体不稳定，则统一使用英文标题，但页面和报告正文可以继续中文。

六、优化表格展示

请新增或完善表格格式化函数，建议放在：

* `src/ui_components.py`
* 或 `src/report_generator.py`

要求：

1. full_name 显示为可点击链接；
2. final_potential_score 保留 2 位小数；
3. risk_score 保留 2 位小数；
4. recommendation_level 显示为彩色 badge；
5. cluster_name 显示为标签；
6. source_type 显示为 api_live / fallback badge；
7. 不要在表格中显示过长 README；
8. Top 项目表要按 final_potential_score 降序；
9. 高风险表要按 risk_score 降序；
10. 表格列名应友好，例如：

    * 仓库
    * 语言
    * Stars
    * Forks
    * 推荐等级
    * 潜力分
    * 风险分
    * 项目类型
    * 数据来源

七、Agent 输出内容本身也要优化

请检查 `src/agents.py` 中 prompt，减少空泛输出，要求 DeepSeek 返回更适合前端展示的结构化 JSON，但前端不能裸展示 JSON。

建议每个 Agent 输出结构为：

{
"status": "pass/warning/fail",
"summary": "一句话摘要",
"key_findings": [
{"finding": "...", "evidence": "..."}
],
"risks": [
{"risk": "...", "severity": "low/medium/high", "evidence": "..."}
],
"recommendations": [
{"action": "...", "reason": "..."}
],
"next_steps": [
"..."
]
}

ProjectAdvisorAgent 额外输出：

{
"recommended_projects": [
{
"full_name": "...",
"reason": "...",
"difficulty": "...",
"cpu_friendly": true,
"three_day_plan": ["Day 1...", "Day 2...", "Day 3..."],
"codex_prompt": "..."
}
]
}

CriticAgent 额外输出：

{
"status": "pass/warning/fail",
"weak_sentences": [
{
"sentence": "...",
"problem": "...",
"needed_evidence": "..."
}
],
"suggestions": [
"..."
],
"final_verdict": "..."
}

八、增强交互功能

请在 Streamlit 中至少增加以下交互：

1. 推荐等级筛选；
2. 语言筛选；
3. cluster 类型筛选；
4. 风险分范围 slider；
5. 潜力分范围 slider；
6. Top N 控制；
7. 单项目选择器；
8. 单项目详情卡；
9. Agent 输出类型选择器；
10. 报告路径复制提示。

如果可以实现，增加“实时生成单项目 Agent 解释”按钮：

1. 用户选择项目；
2. 点击按钮；
3. 调用 ScoringAgent；
4. 保存到 outputs/agents/cache/；
5. 页面展示卡片式结果；
6. 如果 DeepSeek API 失败，显示 fallback 卡片；
7. 不要重复调用同一项目同一 Agent，优先读缓存。

九、生成截图素材目录

请创建：

* `outputs/screenshots/`

并在 `docs/demo_script.md` 中写明课堂展示建议截图：

1. Streamlit 首页；
2. 趋势分析页；
3. 评分排行榜页；
4. PCA 聚类地图页；
5. 单项目详情页；
6. Agent 推荐页；
7. HTML 报告首页；
8. HTML 大屏页。

如果无法自动截图，可只创建目录并写说明，不要引入复杂浏览器自动化依赖。

十、更新 README 和文档

请更新：

1. `README.md`
2. `docs/user_guide.md`
3. `docs/demo_script.md`
4. `docs/development_log.md`
5. `AGENTS.md`

README 必须新增“展示效果”部分：

1. Streamlit Dashboard；
2. HTML Report；
3. HTML Big Screen；
4. Agent Explanation Cards；
5. Risk-Potential Quadrant；
6. PCA Cluster Map；
7. Screenshots 占位说明。

同时新增“第三轮优化内容”：

1. 冰蓝科技风视觉系统；
2. Agent JSON 转卡片；
3. HTML 报告升级；
4. Streamlit 交互增强；
5. 图表统一美工；
6. 表格 badge 化；
7. 单项目详情页优化。

十一、运行与验证

修改完成后，请运行或指导我运行：

1. `python main.py`
2. `pytest`
3. `streamlit run app.py`

检查：

1. `outputs/reports/agent_radar_report.html` 是否明显变美；
2. `outputs/dashboards/agent_radar_dashboard.html` 是否可作为展示大屏；
3. Streamlit 是否不再直接裸展示 JSON；
4. Agent 输出是否变成卡片；
5. 图表是否统一蓝色科技风；
6. 表格是否有 badge 和更好排版；
7. 是否仍保持 `deepseek-v4-pro`；
8. 是否没有 `deepseek-v4-flash` 残留；
9. 是否没有泄露 API Key；
10. `python main.py` 是否仍然跑通。

十二、完成后汇报

请最后按以下格式汇报：

1. 本轮修改了哪些文件；
2. 新增了哪些文件；
3. Streamlit 具体优化了哪些页面；
4. HTML 报告具体优化了哪些模块；
5. HTML 大屏具体优化了哪些图表；
6. Agent JSON 是否已改为卡片式展示；
7. 图表是否已统一冰蓝科技风；
8. 表格是否已 badge 化；
9. 是否增加了交互筛选功能；
10. 是否增加了单项目详情页；
11. 是否增加了实时或缓存式 Agent 解释按钮；
12. 是否创建 outputs/screenshots；
13. 运行测试是否通过；
14. 是否仍存在前端展示粗糙、JSON 裸露或 API Key 泄露风险；
15. 下一轮还需要做哪些最终答辩级收尾。
