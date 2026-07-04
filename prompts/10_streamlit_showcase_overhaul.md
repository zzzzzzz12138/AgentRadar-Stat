请继续在当前 AgentRadar-Stat 项目基础上进行“Streamlit 展示级大修”。本轮目标是：把当前 Streamlit 从调试型工程界面升级为与最终 `AgentRadar-Stat 项目报告 HTML/PDF` 完全一致的展示级数据产品界面。

当前最终报告已经形成较成熟的冰蓝科技风、中文化、流程图、项目概览、趋势洞察、评分排行、聚类画像、模型预测、PyTorch 扩展、个性化推荐、DeepSeek Agent 解释和附录交付结构。现在需要将此前针对报告 HTML 从头到尾的全部展示要求，完整迁移并应用到 Streamlit 中，使 Streamlit 与报告在视觉风格、语言体系、内容结构、图表美工、表格排版、交互体验和展示叙事上保持一致。

当前 Streamlit 存在的突出问题包括：

1. 首页仍像调试面板，显示 api_live / fallback、deepseek-v4-pro、最近更新、fallback shown when API disabled/failed 等展示层不宜出现的信息；
2. 指标卡存在 gradient_boosting、TabularWideDeepNet 等英文长词截断；
3. 表格列宽过窄，项目主题等中文被挤成竖排；
4. 图表仍显示 recommendation_level、stars_total、forks_total、risk_score、final_potential_score、cluster_name、pca_x、pca_y 等原始变量名；
5. 图表标题、图例、坐标轴、hover 弹窗仍不够中文化和美观；
6. 侧边栏仍显示 User Profile、Role、Goal、Programming level、CPU-only 等英文或不适合展示的内容；
7. API 状态页仍显示 configured、value hidden、Data mode、api_live、Rate limit not collected、Started/Finished 等调试字段；
8. 个性化推荐解释页面严重竖排，且仍出现 CPU-only、机械模板化推荐理由；
9. DeepSeek Agent 页面仍需要卡片化、中文化、自然化；
10. 报告导出页应突出最终项目报告 HTML/PDF，而不是普通路径说明；
11. 整体背景、卡片、字体、按钮、筛选器、表格、图表之间缺少与最终报告完全一致的统一主题。

硬约束：

1. 不要重写 GitHub API 采集、评分、聚类、模型训练、PyTorch、个性化推荐和 Agent 主逻辑；
2. 不要破坏 `python main.py`、`pytest`、`streamlit run app.py`；
3. 不得读取、打印、保存或提交 `.env` 中真实 API Key；
4. 不得恢复 `available_time`、`api_budget`、`deepseek-v4-flash`、`st.json`；
5. Streamlit 展示层不得出现 `sample_fallback`、`sample fallback`、`api_live`、`CPU-only`、`CPU only`、`生成时间`、`最近更新`、`fallback shown when API disabled/failed` 等调试或不适合展示的文字；
6. Streamlit 展示层不得出现 `recommendation_level`、`risk_level_cn`、`cluster_name`、`pca_x`、`pca_y`、`stars_total`、`forks_total`、`risk_score`、`final_potential_score`、`personalized_score` 等原始字段名；
7. 所有面向用户的文字以中文为主，专有名词 GitHub、DeepSeek、AI Agent、PyTorch、PCA、KMeans、TabularWideDeepNet 可保留英文；
8. 全局字体与报告一致：英文和数字使用 Times New Roman，中文使用宋体或宋体回退；
9. Streamlit 应使用与报告相同的浅蓝、冰蓝、青蓝科技风；
10. 不得直接裸展示 JSON；
11. 所有表格不得出现中文竖排断裂；
12. 修改后重新运行或指导运行 `streamlit run app.py`、`python main.py` 和 `pytest`。

一、统一 Streamlit 视觉系统

请新增或完善以下文件：

* `src/streamlit_theme.py`
* `src/streamlit_components.py`
* 可复用现有 `src/theme.py`、`src/ui_components.py`、`src/agent_display.py`

视觉要求：

1. Streamlit 与最终报告使用同一冰蓝科技风：

   * 主蓝：#38BDF8
   * 冰蓝：#7DD3FC
   * 青蓝：#22D3EE
   * 湖蓝：#60A5FA
   * 雾蓝：#93C5FD
   * 浅背景：#F8FCFF / #EEF8FF
   * 卡片白：rgba(255,255,255,0.94)
   * 正文深蓝灰：#0F172A / #334155
2. 不使用大红色控件作为主视觉。当前多选标签是红色，需要改为浅蓝系标签；
3. 页面背景使用与报告一致的 `assets/agent_radar_bg.svg`，透明度应足够可见但不影响阅读；
4. 所有卡片采用圆角、浅阴影、浅蓝边框、轻玻璃拟态；
5. 所有按钮、下载按钮、选择器、tab、radio、slider 统一浅蓝主题；
6. 全局 CSS 中设置：

   * 英文/数字 Times New Roman；
   * 中文宋体；
   * 卡片标题衬线加粗；
   * 正文行距舒展；
7. Streamlit 默认组件尽量通过 CSS 美化，不要出现原始朴素控件风；
8. 不要引入过重前端依赖。

二、重构 Streamlit 首页

当前首页 Hero 区与指标卡像调试面板。请按报告首页逻辑重构。

首页结构：

1. 顶部 Hero 全宽：

   * `AgentRadar-Stat`
   * `AI Agent 开源生态趋势挖掘、质量评分与智能选题决策平台`
   * 项目定位：
     `以 GitHub 公开仓库为主数据源，构建从采集、建模到个性化推荐和 Agent 解释的完整闭环。`
   * 功能标签：

     * `500 个 GitHub 公开仓库`
     * `多模型评分`
     * `聚类画像`
     * `PyTorch 表格神经网络`
     * `个性化推荐`
     * `DeepSeek Agent 解释`
     * `HTML/PDF 自动报告`

2. 首页不得显示：

   * 最近更新时间；
   * api_live / fallback；
   * deepseek-v4-pro；
   * fallback shown when API disabled/failed；
   * GitHub API-first；
   * saved recommendations 之类英文调试说明。

3. 项目能力雷达改成全宽流程图，而不是目前普通小卡片：

   * 数据入口：GitHub 公开仓库、关键词搜索、seed 仓库补充；
   * 特征建模：清洗特征、七维评分、聚类画像；
   * 预测扩展：Task A/B、sklearn 模型、PyTorch 表格宽深神经网络；
   * 智能决策：用户画像、个性化推荐、DeepSeek Agent 解释；
   * 交付形态：HTML 报告、PDF 报告、Streamlit 交互入口。
     节点之间用箭头或流线连接，使用浅蓝渐变。

4. 首页指标卡改为展示价值型指标：

   * GitHub 仓库样本：500；
   * 扩展关键词：34；
   * 去重后仓库：1001 或当前 run_summary 中实际值；
   * 入模项目：500；
   * A 级推荐项目：100；
   * 高风险项目：104；
   * 聚类画像：4 类或当前最终结果；
   * 监督任务：任务 A / B；
   * 机器学习模型：6 类；
   * 深度学习扩展：表格宽深神经网络；
   * 个性化推荐：20；
   * DeepSeek Agent：7。
     不显示 `api_live`、`fallback`、`Task A F1` 这类过窄难读文本作为首页主卡。

5. 首页 Top Projects 表格当前列过窄，中文竖排严重。请改为“精选项目卡片墙”或横向可滚动表格：

   * 推荐使用卡片：每张卡展示仓库名、主题、语言、Stars、综合潜力分、风险分、项目类型；
   * 仓库名可点击 GitHub；
   * 若保留表格，必须使用 `st.dataframe` 的 column_config 或自定义 HTML 表格，保证列宽合理，中文不竖排。

三、侧边栏用户画像重做

当前侧边栏仍是英文 User Profile、Role、Goal、Programming level，且有 CPU-only。请全面中文化和美化。

1. `User Profile` 改为 `用户画像`;
2. 字段中文化：

   * Role → 身份角色；
   * Goal → 主要目标；
   * Programming level → 编程水平；
   * Preferred languages → 偏好语言；
   * Preferred topics → 偏好主题；
   * Hardware → 运行条件；
   * Risk preference → 风险偏好；
   * Output preference → 输出偏好；
3. 删除 `CPU-only` 表述。运行条件选项改为：

   * 本地普通电脑；
   * 有独立显卡；
   * 云端资源可用；
   * 不确定。
4. 所有红色多选标签改为浅蓝标签；
5. `Save profile` 改为 `保存画像`;
6. 侧边栏导航中文化并美化：

   * 首页；
   * 数据概览；
   * 趋势洞察；
   * 评分排行；
   * 个性化推荐；
   * 聚类画像；
   * 模型预测；
   * DeepSeek Agent；
   * 单项目详情；
   * 报告导出。
7. 侧边栏应保持固定、简洁，不要挤压主页面内容；
8. 侧边栏宽度若导致主区太窄，可适当减少字段默认展示，或把用户画像放到首页/个性化推荐页的展开面板中；
9. 不再显示 `available_time`、`api_budget`。

四、API 状态页改为“数据概览页”

当前 API 状态页过于调试化，显示 configured、value hidden、Data mode、api_live、Rate limit、Started、Finished、Fallback reason 等。请将其改为更适合展示的“数据概览”页。

页面标题：`数据概览`

内容结构：

1. 样本构建卡片：

   * 关键词搜索候选；
   * 去重后仓库；
   * 相关性过滤后；
   * 最终入模项目；
   * seed 仓库成功数。
2. 数据采集漏斗交互图：

   * 搜索候选；
   * 去重后仓库；
   * 相关性过滤后；
   * 最终入模项目。
3. 数据来源说明：

   * `本系统基于 GitHub 公开仓库元数据、README 文本信号和 topics 信息构建分析样本。`
4. 安全说明可简写为：

   * `项目配置通过环境变量管理，展示页面不包含任何敏感凭据。`
5. 不再显示：

   * GitHub Token configured；
   * DeepSeek Key configured；
   * value hidden；
   * data_mode；
   * api_live；
   * fallback reason；
   * Started/Finished 原始时间；
   * rate limit not collected。
6. 若确需保留技术诊断，只能放入默认折叠的 `高级诊断` expander 中，默认不展开。

五、趋势洞察页重做

当前趋势页图表过于简略，且显示 `language`、`count`、`recommendation_level`、`stars_total`、`forks_total`、`cluster` 等原始字段。

页面标题：`趋势洞察`

页面说明：
`趋势洞察用于观察 AI Agent 相关项目的语言生态、关注度长尾分布、派生开发活跃关系和技术主题结构。`

图表要求：

1. 主要编程语言分布：

   * 标题中文；
   * x/y 轴中文；
   * 不显示 `language`、`count`;
   * 蓝色渐变；
   * 图卡片说明：`观察项目复现门槛和生态主语言。`

2. GitHub Stars 分布特征：

   * 使用对数分箱；
   * 标题中文；
   * 说明：`使用对数分箱展示头部项目与长尾项目差异。`

3. Stars-Forks 气泡散点图：

   * x：Stars（对数刻度）；
   * y：Forks（对数刻度）；
   * 图例中文：推荐等级；
   * hover 中文化；
   * 点击点打开 GitHub；
   * 不显示 `stars_total`、`forks_total`、`recommendation_level`;
   * 提高可读性，避免点挤成一团。

4. 技术主题分布：

   * 技术主题中文化；
   * 不显示 `cluster`;
   * 蓝色系横向条形图。

5. 增加 Top N 控件但美化为浅蓝滑块；

6. 表格部分若展示 Top 项目，应使用卡片或横向滚动表，避免竖排。

六、评分排行页重做

当前评分与推荐页存在筛选器拥挤、红色标签、原始变量名、表格竖排等问题。

页面标题：`评分排行`

页面说明：
`评分排行从综合潜力与风险暴露两个角度识别开源项目：前者回答哪些项目值得优先关注，后者回答哪些项目需要谨慎评估。`

要求：

1. 筛选区改为卡片式筛选器：

   * 推荐等级；
   * 主要语言；
   * 项目类型；
   * 风险分范围；
   * 潜力分范围；
   * Top N；
     使用两行布局，不要挤在一行导致错乱。
2. 所有筛选器中文化，不显示 `Cluster`、`recommendation_level`、`risk_score`。
3. 风险-潜力四象限：

   * 坐标轴中文；
   * 图例中文；
   * hover 中文；
   * 点击 GitHub；
   * 不显示原始字段名。
4. Top 项目表：

   * 当前表格导致项目主题竖排。必须修复；
   * 建议改为“项目卡片列表”：

     * 仓库名；
     * 主题；
     * 语言；
     * Stars/Forks；
     * 潜力分；
     * 风险分；
     * 推荐等级；
     * 项目类型；
     * GitHub 链接按钮。
   * 若保留表格，必须设置列宽，项目主题列至少 90px，仓库名列至少 180px，禁止逐字竖排。
5. 单项目评分卡中 Trend / Activity / Community 等英文改为：

   * 趋势热度；
   * 活跃维护；
   * 社区参与；
   * 文档质量；
   * 技术创新；
   * 复现可行；
   * 风险惩罚。
6. 进度条统一蓝色系，风险惩罚可用橙红色。

七、个性化推荐页重做

当前个性化推荐页仍显示 CPU-only、图例原始字段、表格竖排，且推荐解释页面出现严重竖排和机械模板。

页面标题：`个性化推荐`

页面说明：
`个性化推荐把通用潜力分转化为面向用户画像的匹配分，使系统能够根据目标、语言偏好、主题偏好和风险偏好给出差异化项目建议。`

要求：

1. 顶部画像摘要卡：

   * 目标；
   * 编程水平；
   * 偏好语言；
   * 偏好主题；
   * 运行条件；
   * 风险偏好；
   * 输出偏好。
     不显示 CPU-only。
2. 个性化分 vs 通用潜力分图：

   * 坐标轴中文；
   * 图例中文；
   * hover 中文；
   * 删除原始字段名；
   * 点更大；
   * 点击 GitHub。
3. 个性化推荐 Top 15：

   * 使用横向条形图或卡片；
   * 仓库名只显示 repo 名，hover 显示完整名称；
   * 蓝色渐变。
4. 个性化推荐表必须避免中文竖排：

   * 推荐改为卡片式列表；
   * 每个项目卡片包括：

     * 名次；
     * 仓库名；
     * 项目主题；
     * 主要语言；
     * 个性化匹配分；
     * 通用潜力分；
     * 风险分；
     * 推荐理由；
     * GitHub 链接。
5. 推荐理由自然成句，不使用引号、列表字符串或机械片段；
6. 删除所有 CPU-only 表述；
7. “查看推荐解释”按钮点击后展示宽屏解释卡，不得像当前一样文字逐字竖排；
8. 解释卡结构：

   * 为什么适合你；
   * 三天复现路线；
   * 风险提示；
   * Codex Prompt；
   * 热门但不适合当前画像。
     每个部分用全宽卡片展示，不要两栏挤压；
9. Codex Prompt 使用代码块或文本框，宽度足够，不要竖排；
10. “热门但不适合当前画像”表格也要中文化、宽度合理。

八、聚类画像页重做

当前聚类页仍显示 `cluster_name`、`pca_x`、`pca_y`，且页面内容截断、表格竖排。

页面标题：`聚类画像`

页面说明：
`聚类画像用于把仓库划分为不同项目类型，帮助理解项目在潜力、风险和工程成熟度上的差异。聚类结果用于解释项目结构，不作为监督学习标签。`

要求：

1. PCA / 聚类项目地图：

   * 坐标轴中文；
   * 图例标题为项目类型；
   * hover 中文；
   * 点击 GitHub；
   * 不显示 `cluster_name`、`pca_x`、`pca_y`;
2. 聚类指标卡：

   * 最终聚类模型；
   * 最优 k；
   * 稳定性 ARI；
   * 聚类类型数量；
     显示中文，不出现 `kmeans` 作为主要展示，可显示 `KMeans 聚类`。
3. 聚类类型数量图：

   * 横向条形；
   * 中文项目类型；
   * 蓝色系；
   * 不显示 `count`、`cluster`;
4. 每个聚类代表项目不要用大表格竖排，改为项目卡片：

   * 仓库名；
   * 主题；
   * 语言；
   * 潜力分；
   * 风险分；
   * GitHub 链接。
5. 聚类方法比较表中文化并居中：

   * 模型；
   * k；
   * 轮廓系数；
   * DB 指数；
   * 选择分。
6. 避免页面底部出现大段空白或滚动截图截断。

九、模型结果页重做

当前模型结果页需要同步报告的模型中文化和内容目的型说明。

页面标题：`模型预测`

页面说明：
`模型预测用于检验评分体系的可解释性，并通过代理标签任务观察哪些原始特征能够解释项目潜力。`

要求：

1. 清晰展示任务定义：

   * 任务 A：评分体系代理模型；
   * 任务 B：项目潜力代理预测；
     并说明防泄漏：不直接使用最终评分、推荐等级和评分子项作为输入。
2. 模型对比图：

   * 模型名中文化；
   * 任务名中文化；
   * 图例中文；
   * 蓝色系；
   * 不显示 raw model id。
3. 特征重要性图：

   * 特征名中文化；
   * 不显示 agent_relevance_score、has_demo、has_requirements 等变量名；
4. Task A / Task B 模型结果表：

   * 模型列中文；
   * 指标列中文；
   * 最佳模型行高亮；
   * 不显示 calibrated_random_forest 原文。
5. PyTorch 表格宽深神经网络区：

   * 复用报告中的网络结构图；
   * 不再显示 CPU-only；
   * 英文/中文说明自然；
   * 训练曲线中文化；
   * 模型卡摘要以“为什么这样设计 / 结果如何 / 局限是什么”三张卡片展示。
6. 不直接堆 markdown 文件原文。

十、DeepSeek Agent 页重做

当前 Agent 页需要与报告中的 Agent 卡片风格一致，并去除调试感。

页面标题：`DeepSeek Agent`

页面说明：
`DeepSeek Agent 负责把字段、图表和模型结果转化为可读解释，帮助用户理解推荐理由、风险来源和下一步操作。`

要求：

1. 不显示原始 JSON；
2. 不显示 fallback、api_status、readme_fetch_status 等字段；
3. 不显示 “explanation generated”；
4. 不显示 “未显式给出”；
5. 每个 Agent 用全宽卡片展示；
6. Agent 中文名称：

   * 采集策略智能体；
   * 数据质量诊断智能体；
   * 主题识别智能体；
   * 评分解释智能体；
   * 个性化项目顾问智能体；
   * 报告生成智能体；
   * 事实审查智能体。
7. 每张卡片包括：

   * 智能体职责；
   * 核心判断；
   * 建议动作；
   * 相关依据；
8. ProjectAdvisorAgent 展示：

   * 当前用户画像摘要；
   * Top 5 推荐项目；
   * 推荐理由；
   * 三天路线；
   * Codex Prompt；
9. CriticAgent 展示：

   * 审查结论；
   * 已绑定的数据依据；
   * 需要谨慎表达的地方；
   * 如何避免夸大。
10. Agent 卡片统一冰蓝科技风，避免单调白底。

十一、单项目详情页重做

当前单项目详情页可进一步产品化。

页面标题：`单项目详情`

要求：

1. 顶部搜索 / 选择项目；
2. 项目基础信息卡：

   * 仓库名；
   * GitHub 链接；
   * 语言；
   * Stars；
   * Forks；
   * Open Issues；
   * 项目主题；
   * 项目类型；
   * 推荐等级；
3. 七维评分雷达图或进度条：

   * 趋势热度；
   * 活跃维护；
   * 社区参与；
   * 文档质量；
   * 技术创新；
   * 复现可行；
   * 风险惩罚；
4. README 信号卡：

   * 是否包含安装说明；
   * 是否包含快速开始；
   * 是否包含示例；
   * 是否包含依赖说明；
   * 是否提及 GPU / API Key 等；
     说明自然中文，不要显示 has_demo 等字段名。
5. Agent 解释按钮：

   * `生成该项目解释`
   * 使用缓存；
   * 输出卡片化解释；
   * 不显示 JSON。
6. 项目详情页不得出现中文竖排或列宽挤压。

十二、报告导出页重做

页面标题：`报告导出`

要求：

1. 突出最终项目报告：

   * `打开 AgentRadar-Stat 项目报告 PDF`
   * `打开交互式 HTML 项目报告`
2. 使用醒目的 PDF 图标按钮或下载按钮；
3. 不再突出 HTML 大屏；
4. 显示报告包含内容：

   * 数据采集；
   * 指标体系；
   * 趋势洞察；
   * 评分排行；
   * 聚类画像；
   * 模型预测；
   * PyTorch 扩展；
   * 个性化推荐；
   * DeepSeek Agent。
5. 如果 PDF 不存在，提示：

   * `请先运行 python main.py 生成报告。`
6. 不显示生成时间；
7. 不显示本地绝对路径；
8. 使用相对路径或下载按钮。

十三、全局表格问题修复

这是当前 Streamlit 最严重的问题之一。所有表格必须避免中文竖排。

请建立统一表格渲染函数：

* `render_project_cards(df, ...)`
* `render_project_table(df, ...)`
* 或二者结合。

要求：

1. 优先用项目卡片替代宽表；
2. 如果使用表格：

   * 仓库名列至少 180px；
   * 项目主题列至少 100px；
   * 项目类型列至少 150px；
   * 数值列可窄；
   * 禁止表格把“项目主题”拆成单字竖排；
   * 长文本列自然换行；
   * 表格横向滚动，而不是强行压缩；
3. 列名中文化；
4. 仓库名可点击 GitHub；
5. 推荐等级、风险等级、项目类型显示 badge；
6. 所有数值保留合理位数；
7. 表头浅蓝背景；
8. hover 浅蓝；
9. 单元格水平、垂直居中；
10. 所有页面复用同一函数。

十四、全局图表问题修复

建立统一 Plotly 主题函数：

* `apply_streamlit_plotly_theme(fig)`
* `format_hover_template(...)`
* `rename_plotly_fields(...)`

要求：

1. 所有图表中文标题、中文坐标轴、中文图例；
2. 不显示 raw field；
3. 图例标题中文；
4. hover 美化：

   * 浅蓝背景；
   * 蓝色边框；
   * 中文字段；
   * Times New Roman + 宋体；
   * 数字保留两位；
5. 使用蓝色系，不使用大跨度红绿紫；
6. 高风险图可用橙红色；
7. 仓库级图表点击或链接打开 GitHub；
8. 图表在 Streamlit 中宽度自适应；
9. 不出现过小图表和大片空白；
10. 不出现重复标题。

十五、全局文本残留扫描

完成后，最终 Streamlit 页面可见文本中不得出现：

1. `sample_fallback`
2. `sample fallback`
3. `api_live`
4. `CPU-only`
5. `CPU only`
6. `recommendation_level`
7. `risk_level_cn`
8. `cluster_name`
9. `pca_x`
10. `pca_y`
11. `stars_total`
12. `forks_total`
13. `risk_score`
14. `final_potential_score`
15. `personalized_score`
16. `calibrated_random_forest`
17. `agent_relevance_score`
18. `has_demo`
19. `has_requirements`
20. `fallback shown`
21. `generated explanation`
22. `value hidden`
23. `configured`
24. `Data mode`
25. `Rate limit not collected`
26. `最近更新`
27. `生成时间`

注意：这些词可以作为源码变量名存在，但不得作为最终页面可见文字出现。

十六、README 与文档同步

请更新：

1. `README.md`
2. `docs/user_guide.md`
3. `docs/demo_script.md`
4. `docs/development_log.md`
5. `AGENTS.md`

文档说明：

1. Streamlit 已与最终项目报告统一视觉系统；
2. Streamlit 展示页包括首页、数据概览、趋势洞察、评分排行、个性化推荐、聚类画像、模型预测、DeepSeek Agent、单项目详情、报告导出；
3. Streamlit 适合课堂实时演示；
4. 报告 HTML/PDF 适合最终展示与提交；
5. 不要在 README 中突出 `api_live`、`sample_fallback` 等调试词。

十七、运行与验证

完成后运行或指导运行：

1. `python main.py`
2. `pytest`
3. `streamlit run app.py`

请重点检查：

1. 首页是否像报告首页一样成熟；
2. 是否删除所有调试标签和最近更新时间；
3. 侧边栏是否中文化、蓝色化；
4. 所有表格是否不再中文竖排；
5. 所有图表是否不再显示原始变量名；
6. 个性化推荐解释是否不再竖排；
7. 是否删除 CPU-only；
8. API 状态页是否变成数据概览页；
9. 模型页是否体现方法严谨性；
10. Agent 页是否卡片化且无 JSON；
11. 报告导出页是否突出 PDF/HTML 项目报告；
12. 是否无 API Key 泄露风险。

十八、完成后汇报

请按以下格式汇报：

1. 本轮修改了哪些文件；
2. 新增了哪些 UI 组件或主题文件；
3. 首页如何重构；
4. 侧边栏用户画像如何中文化；
5. API 状态页如何改为数据概览页；
6. 趋势洞察页优化了哪些图表；
7. 评分排行页如何修复表格竖排；
8. 个性化推荐页如何修复解释竖排和 CPU-only；
9. 聚类画像页如何中文化；
10. 模型预测页如何中文化并展示方法严谨性；
11. DeepSeek Agent 页如何卡片化；
12. 单项目详情页新增了哪些内容；
13. 报告导出页是否加入 PDF/HTML 项目报告入口；
14. 是否完成全局 Plotly 主题；
15. 是否完成统一表格渲染；
16. 是否通过残留词扫描；
17. `python main.py` 是否通过；
18. `pytest` 是否通过；
19. `streamlit run app.py` 是否可运行；
20. 是否存在 API Key 泄露风险；
21. 仍需人工检查的页面。
