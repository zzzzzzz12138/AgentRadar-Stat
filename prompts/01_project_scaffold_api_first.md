你现在是资深 Python 数据科学工程师，请从零开始实现一个名为 AgentRadar-Stat 的课程项目。

项目主题是：AI Agent 开源生态趋势挖掘、质量评分与智能选题决策平台。项目目标是以真实 GitHub API 数据为基准，结合 GitHub Trending、GitHub REST API、GitHub Search API、README 文本和 DeepSeek API 多智能体，采集 AI Agent、LLM、RAG、Coding Agent、MCP、Vibe Coding、Workflow Agent、Data Agent 等相关开源项目数据，完成数据清洗、特征工程、统计分析、综合评分、聚类建模、机器学习建模、PyTorch MLP、DeepSeek 项目推荐智能体、Streamlit 交互展示、HTML 大屏和自动 HTML 报告生成。

重要硬约束：

1. 真实 GitHub API 是主数据源，不是可选项。
2. 本地 sample 数据只是 GitHub API 失效、限流、网络异常或课堂展示环境不可用时的兜底方案。
3. 7 个 Agent 必须以 DeepSeek API 调用为主，规则模板 fallback 只用于 DeepSeek API 失败时兜底。
4. 不要硬编码任何 API Key。
5. GitHub Token 和 DeepSeek API Key 均从 .env 或环境变量读取。
6. 项目必须适配 Windows 11、Python 3.10、CPU-only、有 PyTorch 环境。
7. 不依赖 GPU。
8. 不要把所有逻辑写进 app.py，必须保持模块化。
9. 必须保证 python main.py、streamlit run app.py、pytest 具备可运行基础。
10. API 调用失败时不能让项目崩溃，必须记录错误并自动 fallback。

需求文档详见《项目需求文档.md》，但本轮严禁一次性实现全部内容。请先只完成第一阶段：项目骨架 + GitHub API 主数据管道 + DeepSeek Client 基础封装 + sample 兜底数据 + 最小可运行闭环。

一、创建完整项目结构：

AgentRadar-Stat/
├── README.md
├── AGENTS.md
├── requirements.txt
├── .env.example
├── app.py
├── main.py
├── config.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── notebooks/
│   └── 01_api_collection_cleaning_eda.ipynb
├── src/
│   ├── data_collect.py
│   ├── github_client.py
│   ├── deepseek_client.py
│   ├── data_clean.py
│   ├── feature_engineering.py
│   ├── scoring.py
│   ├── statistical_analysis.py
│   ├── modeling.py
│   ├── torch_mlp.py
│   ├── visualization.py
│   ├── dashboard.py
│   ├── agents.py
│   ├── report_generator.py
│   └── utils.py
├── outputs/
│   ├── figures/
│   ├── reports/
│   ├── dashboards/
│   ├── models/
│   └── agents/
├── docs/
│   ├── project_design.md
│   ├── demand_document.md
│   ├── user_guide.md
│   ├── development_log.md
│   └── demo_script.md
├── prompts/
│   └── 01_project_scaffold_api_first.md
└── tests/
└── test_core_functions.py

二、编写 .env.example：

必须包含以下配置项，但不要填真实 Key：

GITHUB_TOKEN=
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
USE_DEEPSEEK_AGENTS=true
OFFLINE_FALLBACK=true
MAX_REPOS=300
MAX_README_REPOS=120
MAX_AGENT_REPOS=30

三、编写 config.yaml：

包含：

1. GitHub API 配置；
2. DeepSeek API 配置；
3. 采集关键词；
4. 最大采集仓库数；
5. README 最大抓取数量；
6. Agent 最大分析项目数；
7. 是否允许 sample fallback；
8. 评分权重；
9. 模型训练参数；
10. 输出路径。

四、编写 src/github_client.py：

实现 GitHub API Client，要求：

1. 从环境变量读取 GITHUB_TOKEN；
2. 若有 Token，则使用 Authorization: Bearer；
3. 请求头包含 Accept: application/vnd.github+json；
4. 支持搜索仓库；
5. 支持获取单个仓库详情；
6. 支持获取 README 内容；
7. 可选支持获取最近 PR；
8. 支持分页；
9. 支持 rate limit 基础处理；
10. 支持 timeout 和 retry；
11. 所有 API 错误写入日志；
12. 返回结构化 DataFrame 或 dict；
13. 不得因单个仓库请求失败中断整个项目。

五、编写 src/deepseek_client.py：

实现 DeepSeek API Client，要求：

1. 从环境变量读取 DEEPSEEK_API_KEY；
2. base_url 默认 https://api.deepseek.com；
3. model 默认 deepseek-v4-pro，可在 .env/config.yaml 中修改；
4. 使用 OpenAI SDK 兼容方式调用；
5. 支持 chat_completion(messages, temperature, max_tokens, timeout)；
6. 支持 JSON 输出解析；
7. 支持异常捕获；
8. API 失败时返回 fallback 信息；
9. 不在日志中输出 API Key；
10. 所有调用保存简要日志到 outputs/agents/agent_call_log.jsonl。

六、编写 src/data_collect.py：

实现数据采集主流程：

1. 使用 GitHub API 作为主数据源；
2. 关键词包括 ai-agent、agentic-ai、llm-agent、coding-agent、rag、langchain、llama、mcp、codex、copilot、claude-code、cursor、workflow-agent、research-agent、data-agent、automl、multimodal；
3. 按关键词搜索仓库；
4. 对仓库 full_name 去重；
5. 采集仓库详情；
6. 采集 README 文本；
7. 可选采集最近 PR 特征；
8. 保存 data/raw/github_repos_raw.csv；
9. 保存 data/raw/readme_texts.csv；
10. 保存 data/raw/api_collection_log.json；
11. 如果 GitHub API 不可用且 OFFLINE_FALLBACK=true，则生成或读取 sample 数据；
12. 输出字段 source_type 必须明确为 api_live 或 sample_fallback。

七、生成本地兜底演示数据：

在 data/sample/ 下生成 sample_trending_projects.csv，至少包含 150 条模拟但合理的 AI Agent 开源项目数据。字段包括：

repo_id, owner, repo_name, full_name, repo_url, description, language, topics, stars_total, forks_total, watchers_total, open_issues_count, created_at, updated_at, pushed_at, license, default_branch, has_issues, has_wiki, has_pages, archived, size, stars_this_week, readme_text, collected_at, source_type, api_status

要求：

1. sample 数据只作为 fallback，不作为主流程；
2. 项目主题覆盖 Coding Agent、RAG Agent、Research Agent、Workflow Agent、MCP Tool、Multimodal Agent、AutoML Agent、Data Agent；
3. stars、forks、issues、README 长度、更新时间之间应有一定统计关系，不能完全随机；
4. 至少包含短期暴涨型项目、高 star 低维护项目、文档完善可复现项目、高风险项目、低 star 高潜力新兴项目；
5. sample 数据必须足够支撑统计分析、聚类、评分和模型训练。

八、编写 src/data_clean.py：

实现读取 data/raw/github_repos_raw.csv 或 fallback sample 数据、去重、缺失值处理、时间字段转换、数值字段类型转换、archived 项目标记、README 文本基础清洗、API 状态标记，并输出 data/processed/cleaned_repos.csv。所有关键函数必须有 docstring 和中文注释。

九、编写 src/feature_engineering.py：

实现 project_age_days、days_since_update、log_stars、log_forks、stars_per_day、forks_per_star、issue_pressure、topic_count、readme_length、has_install_section、has_quickstart、has_demo、has_example、has_requirements、mentions_gpu、mentions_cpu、mentions_api_key、mentions_docker、agent_keyword_count、agent_relevance_score、reproducibility_score、risk_score，并输出 data/processed/feature_repos.csv。

十、编写 src/scoring.py：

实现 trend_score、activity_score、community_score、documentation_score、innovation_score、feasibility_score、risk_score、final_potential_score、recommendation_level。评分过程使用 MinMaxScaler 或分位数标准化，避免单一 star 指标支配全部结果。recommendation_level 分为 A、B、C、D 四类。

十一、编写 src/statistical_analysis.py：

输出样本规模、API 采集成功率、语言分布、技术主题分布、stars/forks/issues/readme_length 描述统计、相关系数矩阵、Top 10 高潜力项目、Top 10 高风险项目，并保存到 outputs/reports/stat_summary.md 和 outputs/reports/stat_summary.json。

十二、编写 src/modeling.py：

实现 Logistic Regression、Random Forest、Gradient Boosting。任务为预测是否高潜力项目，即 A/B 为 1，C/D 为 0。输出 accuracy、precision、recall、f1、confusion matrix、feature importance，并保存模型到 outputs/models/。

十三、编写 src/torch_mlp.py：

使用 PyTorch 实现 CPU 可运行的 MLP 二分类模型。要求设置随机种子、使用 Dataset/DataLoader、训练轮数适中、输出 loss 曲线和模型评估指标，并保存模型文件。

十四、编写 src/visualization.py 与 src/dashboard.py：

生成至少 9 张静态图表和 1 个 HTML 大屏。图表包括 stars 分布、stars-forks 散点图、技术方向数量条形图、相关性热力图、final_potential_score Top 10、risk_score Top 10、模型混淆矩阵、特征重要性、风险—潜力四象限图。HTML 大屏需额外展示 GitHub API 采集状态和 agent 调用状态。图表保存到 outputs/figures/，HTML 大屏保存到 outputs/dashboards/。

十五、编写 src/agents.py：

实现 7 个 DeepSeek API Agent。必须优先调用 DeepSeek API，fallback 模板只在 API Key 缺失、API 调用失败或 USE_DEEPSEEK_AGENTS=false 时启用。

Agent 包括：

1. CollectorAgent：根据关键词和技术方向生成采集策略；
2. DataQualityAgent：基于数据质量指标生成数据质量摘要；
3. TopicAgent：根据 name、description、topics、README 判断项目主题；
4. ScoringAgent：根据评分字段生成推荐理由和风险解释；
5. ProjectAdvisorAgent：根据用户约束推荐 Top 5 项目；
6. ReportAgent：生成结构化报告摘要；
7. CriticAgent：检查报告是否存在没有数据依据的夸大表述。

要求：

1. 每个 Agent 有清晰 system prompt；
2. 每个 Agent 输入必须包含真实字段摘要；
3. 每个 Agent 输出保存到 outputs/agents/；
4. Agent 输出不得替代真实统计结果；
5. CriticAgent 必须检查结论是否绑定字段、指标或图表；
6. API 失败时必须记录 fallback_used=true。

十六、编写 src/report_generator.py：

根据 processed 数据、统计结果、图表、模型结果和 agent 输出，生成 outputs/reports/agent_radar_report.html。报告至少包括项目背景、数据来源、GitHub API 采集摘要、数据清洗摘要、描述性统计、评分 Top 10、风险 Top 10、模型结果、agent 自动解释、CriticAgent 审查结果、局限性说明。

十七、编写 app.py：

使用 Streamlit 构建最小可运行界面，至少包含首页、API 采集、数据概览、趋势分析、项目评分、聚类地图、模型结果、agent 推荐、单项目详情、报告导出。页面必须显示当前数据模式：api_live 或 sample_fallback。

十八、编写 main.py：

实现一键流水线。运行 python main.py 后依次完成：

1. 读取 .env 和 config.yaml；
2. 尝试 GitHub API 采集；
3. GitHub API 失败时启用 sample fallback；
4. 数据清洗；
5. 特征工程；
6. 评分；
7. 统计分析；
8. 模型训练；
9. PyTorch MLP 训练；
10. 图表生成；
11. HTML 大屏生成；
12. agent 分析；
13. HTML 报告生成。

十九、编写 README.md：

README 必须像正式 GitHub 项目一样完整，包括项目背景、核心功能、项目亮点、真实 GitHub API 主流程、sample fallback 说明、agent 说明、目录结构、环境安装、.env 配置、运行命令、数据字段说明、评分方法、模型方法、页面截图占位、后续开发计划。

二十、编写 AGENTS.md：

写给后续 Codex / AI Coding Agent 使用，要求包括：

1. 不要破坏目录结构；
2. 修改代码后运行 main.py 或相关测试；
3. 不要硬编码 GitHub Token 或 DeepSeek API Key；
4. 新增功能要同步更新 README；
5. 代码保持模块化；
6. 关键函数要有 docstring；
7. 不要删除 sample 数据；
8. 真实 GitHub API 是主流程；
9. sample 数据只是 fallback；
10. agent 应优先真实调用 API；
11. 优先保证 Windows 11 CPU 环境可运行。

二十一、requirements.txt 至少包括：

pandas、numpy、requests、beautifulsoup4、scikit-learn、matplotlib、seaborn、plotly、pyecharts、streamlit、pyyaml、python-dotenv、jinja2、joblib、torch、pytest、openpyxl、openai

二十二、必须保证以下命令可以运行：

python main.py、streamlit run app.py、pytest

完成后请告诉我：

1. 创建了哪些文件；
2. 每个文件的作用；
3. 如何配置 GitHub Token 和 DeepSeek API Key；
4. 如何运行项目；
5. 当前是否优先走 GitHub API；
6. API 失败时是否能 fallback；
7. agent 是否真实调用 API；
8. 当前已实现哪些功能；
9. 哪些功能留到下一轮迭代；
10. 是否有任何报错、依赖风险或 API 限流风险。