# AgentRadar-Stat

<p align="center">
  <strong>AI Agent 开源生态趋势挖掘、质量评分与智能选题决策平台</strong>
</p>

<p align="center">
  基于 GitHub 公开仓库数据、统计建模、PyTorch 表格神经网络与 DeepSeek 多智能体的开源项目决策平台
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-38BDF8?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub-API-60A5FA?style=for-the-badge&logo=github&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-App-22D3EE?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-TabularWideDeepNet-0EA5E9?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/DeepSeek-Agent-38BDF8?style=for-the-badge" />
</p>

---

## 项目简介

**AgentRadar-Stat** 是一个面向 **AI Agent、Coding Agent、MCP、RAG、Workflow Agent、Vibe Coding** 等开源生态的 Python 数据科学项目。

它想解决的问题是：

> 面对 GitHub 上日新月异、数量庞大、质量参差不齐的 AI Agent 开源项目，我们如何不只依靠 Stars 或 Trending 排名，而是结合项目热度、维护活跃度、社区参与度、文档质量、技术创新性、复现可行性、风险水平以及用户自身画像，识别出真正值得学习、复现、二次开发或持续关注的高潜力项目？

因此，本项目将 GitHub 公开仓库数据从简单排行榜升级为一个集：

* **真实数据采集**
* **多维质量评分**
* **趋势洞察**
* **聚类画像**
* **监督预测**
* **PyTorch 深度学习扩展**
* **用户画像个性化推荐**
* **DeepSeek Agent 智能解释**
* **HTML/PDF 自动报告**
* **Streamlit 交互系统**

于一体的完整 Python 数据产品。

---

## 项目亮点

### 真实 GitHub 公开仓库数据

项目以 GitHub API 为主数据源，通过多关键词、多排序策略与 seed 仓库补充构建 AI Agent 开源项目样本。

当前默认分析流程覆盖：

| 模块             | 内容                |
| -------------- | ----------------- |
| 扩展关键词          | 34 个              |
| 候选仓库           | 约 2500+           |
| 去重后仓库          | 约 1000+           |
| 最终入模项目         | 500 个 GitHub 公开仓库 |
| 推荐项目           | A/B/C/D 四级推荐      |
| 个性化推荐          | Top 20            |
| DeepSeek Agent | 7 个智能体            |

---

### 七维项目质量评分

项目不只看 Stars，而是从七个维度综合评价开源项目：

| 维度   | 含义                                  |
| ---- | ----------------------------------- |
| 趋势热度 | 衡量项目关注度与增长信号                        |
| 活跃维护 | 衡量更新频率与维护状态                         |
| 社区参与 | 衡量 Forks、Watchers、Issue 互动等社区信号     |
| 文档质量 | 衡量 README、安装说明、快速开始、示例与依赖说明         |
| 技术创新 | 衡量 AI Agent、RAG、MCP、Workflow 等技术相关性 |
| 复现可行 | 衡量项目是否便于学习、运行和复现                    |
| 风险惩罚 | 衡量维护停滞、Issue 压力、复现复杂度等潜在风险          |

综合潜力分计算逻辑如下：

$$FinalPotentialScore =
0.25 \times TrendScore

* 0.20 \times ActivityScore
* 0.15 \times CommunityScore
* 0.15 \times DocumentationScore
* 0.15 \times InnovationScore
* 0.10 \times FeasibilityScore

- 0.10 \times RiskScore$$

---

### 聚类画像与项目类型识别

项目使用 PCA 与多种聚类方法对仓库进行项目画像分析，包括：

* KMeans 聚类
* 高斯混合模型
* 层次凝聚聚类
* DBSCAN 密度聚类
* 聚类稳定性与模型选择比较
* 每类项目代表仓库展示

聚类结果用于理解不同项目类型，例如：

* 文档完善可复现型
* 概念新颖但工程不成熟型
* 小众垂直工具型
* 高热度成熟型
* 高风险探索型

---

### 任务 A / 任务 B 防泄漏建模

为了避免“用最终评分预测最终评分”的循环论证，项目将监督学习拆分为两个任务：

| 任务            | 说明                      |
| ------------- | ----------------------- |
| 任务 A：评分体系代理模型 | 检验评分体系边界，观察原始特征能否解释评分等级 |
| 任务 B：项目潜力代理预测 | 预测项目是否具备较高潜力与复现价值       |

建模过程中显式排除最终评分、推荐等级、评分子项等泄漏字段。

使用模型包括：

* 逻辑回归
* 随机森林
* 极端随机树
* 梯度提升树
* 校准随机森林
* 随机基线

输出内容包括：

* Accuracy
* Precision
* Recall
* F1
* ROC AUC
* Brier Score
* 特征重要性
* 模型卡

---

### PyTorch 表格宽深神经网络

项目进一步实现了 **PyTorch 表格宽深神经网络（TabularWideDeepNet）**，用于结构化仓库特征的深度学习扩展实验。

模型结构包括：

* 数值特征分支
* 类别嵌入分支
* 宽分支
* 深层非线性分支
* 特征融合层
* 二分类输出层

该模块体现 PyTorch 在真实表格数据建模中的应用，而不是仅停留在传统机器学习模型对比。

---

### 用户画像个性化推荐

Streamlit App 中支持用户选择自身画像，包括：

* 身份角色
* 主要目标
* 编程水平
* 偏好语言
* 偏好主题
* 运行条件
* 风险偏好
* 输出偏好

系统会在通用综合潜力分基础上生成 **个性化匹配分**，并输出：

* 个性化推荐项目
* 推荐理由
* 风险提示
* 三天复现路线
* 可复制给 Codex 的开发 Prompt

---

### DeepSeek 多智能体解释

项目接入 DeepSeek API，设计了 7 个智能体：

| 智能体        | 职责                 |
| ---------- | ------------------ |
| 采集策略智能体    | 解释关键词、seed 仓库和采集策略 |
| 数据质量诊断智能体  | 检查缺失、重复、字段异常和样本质量  |
| 主题识别智能体    | 判断项目主题与技术方向        |
| 评分解释智能体    | 解释综合潜力分、风险分和七维评分   |
| 个性化项目顾问智能体 | 结合用户画像输出推荐理由与复现路线  |
| 报告生成智能体    | 将图表、字段和模型结果转为报告摘要  |
| 事实审查智能体    | 检查结论是否绑定数据、图表和模型依据 |

Agent 输出不替代统计结果和模型指标，而是把字段、图表和模型结果转化为更容易理解的自然语言解释。

---

## 最终展示形式

本项目形成两个核心展示入口。

### HTML / PDF 项目报告

报告用于完整展示项目成果，路径为：

```text
outputs/reports/agent_radar_report.html
outputs/reports/agent_radar_report.pdf
```

报告内容包括：

1. 项目概览
2. 数据采集
3. 指标体系
4. 趋势洞察
5. 评分排行
6. 聚类画像
7. 模型预测
8. PyTorch 扩展
9. 个性化推荐
10. DeepSeek Agent
11. 项目亮点
12. 局限展望
13. 附录

报告采用浅蓝、冰蓝、青蓝科技风，支持交互图、可点击 GitHub 链接和 PDF 导出。

---

### Streamlit 交互系统

Streamlit 用于实时探索项目数据和个性化推荐，启动命令：

```bash
streamlit run app.py
```

页面结构包括：

1. 首页 / 项目概览
2. 数据采集
3. 指标体系
4. 趋势洞察
5. 评分排行
6. 聚类画像
7. 模型预测
8. PyTorch 扩展
9. 个性化推荐
10. DeepSeek Agent
11. 单项目详情
12. 项目亮点
13. 局限展望
14. 报告导出

Streamlit 更强调交互，例如：

* 用户画像选择
* 项目筛选
* Top N 调整
* 单项目七维评分查看
* 个性化推荐解释
* 聚类地图探索
* DeepSeek Agent 卡片解释
* HTML/PDF 报告下载

---

## 项目结构

```text
AgentRadar-Stat/
├── README.md
├── AGENTS.md
├── requirements.txt
├── .env.example
├── app.py
├── main.py
├── config.yaml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── notebooks/
│   ├── 01_api_collection_cleaning_eda.ipynb
│   ├── 02_modeling_rigor_and_personalization.ipynb
│   └── 03_deepseek_agent_recommendation_demo.ipynb
│
├── src/
│   ├── github_client.py
│   ├── deepseek_client.py
│   ├── data_collect.py
│   ├── sample_data.py
│   ├── data_clean.py
│   ├── feature_engineering.py
│   ├── scoring.py
│   ├── statistical_analysis.py
│   ├── clustering_advanced.py
│   ├── model_tasks.py
│   ├── modeling.py
│   ├── torch_mlp.py
│   ├── torch_tabular.py
│   ├── user_profile.py
│   ├── personalization.py
│   ├── recommendation_engine.py
│   ├── visualization.py
│   ├── interactive_visualization.py
│   ├── dashboard.py
│   ├── agents.py
│   ├── agent_display.py
│   ├── report_generator.py
│   ├── pdf_exporter.py
│   ├── streamlit_theme.py
│   ├── streamlit_components.py
│   └── utils.py
│
├── assets/
│   ├── agent_radar_bg.svg
│   └── agent_radar_hero.svg
│
├── outputs/
│   ├── figures/
│   ├── reports/
│   ├── dashboards/
│   ├── models/
│   └── agents/
│
├── docs/
│   ├── project_design.md
│   ├── demand_document.md
│   ├── user_guide.md
│   ├── development_log.md
│   └── demo_script.md
│
├── prompts/
│   ├── 01_project_scaffold_api_first.md
│   ├── 02_data_pipeline.md
│   ├── 03_modeling_personalization_upgrade.md
│   ├── 04_showcase_html_visual_pdf_overhaul.md
│   └── ...
│
└── tests/
    └── test_core_functions.py
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/AgentRadar-Stat.git
cd AgentRadar-Stat
```

---

### 2. 创建环境

推荐使用 Python 3.10 或以上版本。

```bash
python -m venv .venv
```

Windows PowerShell：

```bash
.venv\Scripts\activate
```

macOS / Linux：

```bash
source .venv/bin/activate
```

---

### 3. 安装依赖

```bash
python -m pip install -r requirements.txt
```

---

### 4. 配置 API Key

复制环境变量模板：

```bash
copy .env.example .env
```

macOS / Linux：

```bash
cp .env.example .env
```

在 `.env` 中填写：

```env
GITHUB_TOKEN=你的 GitHub Token
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
USE_DEEPSEEK_AGENTS=true
OFFLINE_FALLBACK=true
MAX_REPOS=500
PER_KEYWORD_LIMIT=50
MAX_README_REPOS=300
MAX_AGENT_REPOS=40
```

注意：

* `.env` 不应上传 GitHub；
* `.env.example` 保留空 Key；
* GitHub Token 用于提高 API 访问稳定性；
* DeepSeek API 用于生成智能体解释。

---

### 5. 运行完整流水线

```bash
python main.py
```

该命令会依次完成：

1. 读取配置；
2. GitHub 数据采集；
3. README 文本抓取；
4. 数据清洗；
5. 特征工程；
6. 综合评分；
7. 聚类画像；
8. 任务 A / B 标签构造；
9. 机器学习模型训练；
10. PyTorch 模型训练；
11. 个性化推荐生成；
12. DeepSeek Agent 分析；
13. 图表生成；
14. HTML/PDF 项目报告生成；
15. 运行摘要输出。

---

### 6. 启动 Streamlit App

```bash
streamlit run app.py
```

浏览器中打开：

```text
http://localhost:8501
```

---

### 7. 查看项目报告

运行 `python main.py` 后，可打开：

```text
outputs/reports/agent_radar_report.html
outputs/reports/agent_radar_report.pdf
```

---

### 8. 运行测试

```bash
pytest
```

---

## 核心配置说明

主要配置位于：

```text
config.yaml
```

常用配置包括：

| 配置项               | 说明                    |
| ----------------- | --------------------- |
| MAX_REPOS         | 最终保留的最大仓库数            |
| PER_KEYWORD_LIMIT | 每个关键词最大采集数            |
| MAX_README_REPOS  | README 抓取数量上限         |
| MAX_AGENT_REPOS   | DeepSeek Agent 深度分析数量 |
| keywords          | GitHub 搜索关键词          |
| seed_repositories | 手动补充的高相关仓库            |
| scoring_weights   | 综合评分权重                |
| model_params      | 模型训练参数                |
| output_paths      | 输出文件路径                |

---

## 数据流程

```text
GitHub API / seed 仓库
        ↓
仓库元数据 + README + topics
        ↓
数据清洗与去重
        ↓
特征工程
        ↓
七维评分体系
        ↓
综合潜力分 / 风险分 / 推荐等级
        ↓
聚类画像 + 监督预测 + PyTorch 扩展
        ↓
用户画像个性化推荐
        ↓
DeepSeek Agent 解释
        ↓
HTML/PDF 报告 + Streamlit App
```

---

## 输出文件

常见输出路径如下：

| 文件                                                 | 说明            |
| -------------------------------------------------- | ------------- |
| `data/raw/github_repos_raw.csv`                    | GitHub 原始仓库数据 |
| `data/processed/cleaned_repos.csv`                 | 清洗后数据         |
| `data/processed/scored_repos.csv`                  | 评分后项目数据       |
| `data/processed/clustered_repos.csv`               | 聚类后项目数据       |
| `outputs/reports/stat_summary.json`                | 统计摘要          |
| `outputs/reports/cluster_profile.csv`              | 聚类画像          |
| `outputs/reports/model_card.md`                    | 机器学习模型卡       |
| `outputs/reports/torch_model_card.md`              | PyTorch 模型卡   |
| `outputs/reports/personalized_recommendations.csv` | 个性化推荐结果       |
| `outputs/reports/agent_radar_report.html`          | HTML 项目报告     |
| `outputs/reports/agent_radar_report.pdf`           | PDF 项目报告      |
| `outputs/models/`                                  | 训练好的模型文件      |
| `outputs/agents/`                                  | Agent 输出与缓存   |

---

## Streamlit 页面说明

### 首页 / 项目概览

展示项目定位、能力流程图、核心指标和精选项目卡片墙。

### 数据采集

展示从关键词搜索、seed 仓库补充、去重过滤到最终入模的样本构建过程。

### 指标体系

展示七维评分逻辑和个性化匹配机制。

### 趋势洞察

展示编程语言分布、Stars 分布、Stars-Forks 关系、技术主题结构和精选项目。

### 评分排行

支持按推荐等级、语言、项目类型、风险分和潜力分筛选项目，并查看单项目评分构成。

### 聚类画像

展示 PCA 项目地图、聚类方法比较、聚类类型数量和各类代表项目。

### 模型预测

区分任务 A 和任务 B，展示模型指标、特征重要性和防泄漏建模逻辑。

### PyTorch 扩展

展示表格宽深神经网络结构、训练曲线和模型卡摘要。

### 个性化推荐

根据用户画像生成个性化项目排序、推荐理由、风险提示、三天复现路线和 Codex Prompt。

### DeepSeek Agent

展示 7 个智能体的自然语言解释卡片。

### 单项目详情

展示单个仓库的基础信息、七维评分构成、README 信号和 Agent 解释。

### 报告导出

提供 HTML 项目报告和 PDF 项目报告的打开与下载入口。

---

## DeepSeek Agent 说明

DeepSeek Agent 用于增强系统解释能力。系统设计了 7 个智能体：

```text
采集策略智能体
数据质量诊断智能体
主题识别智能体
评分解释智能体
个性化项目顾问智能体
报告生成智能体
事实审查智能体
```

Agent 输出示例包括：

* 该项目为什么值得关注；
* 该项目可能存在哪些风险；
* 该项目适合哪类用户；
* 如何在三天内复现；
* 给 Codex 的开发 Prompt；
* 报告结论是否有数据依据。

---

## GitHub Token 与 DeepSeek API 说明

### GitHub Token

GitHub Token 用于提高 API 请求额度和采集稳定性。

创建方式：

1. 打开 GitHub；
2. 进入 Settings；
3. Developer settings；
4. Personal access tokens；
5. 创建 Token；
6. 填入 `.env` 的 `GITHUB_TOKEN`。

### DeepSeek API Key

DeepSeek API Key 用于智能体解释。

配置：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_MODEL=deepseek-v4-pro
```

如果未配置 DeepSeek Key，系统仍可通过规则模板生成基础解释，但推荐配置真实 API 以获得更完整的 Agent 输出。

---

## PDF 报告生成

项目支持自动生成 PDF 项目报告：

```text
outputs/reports/agent_radar_report.pdf
```

如需启用更稳定的 HTML 转 PDF，可安装 Playwright：

```bash
python -m pip install playwright
python -m playwright install chromium
```

然后重新运行：

```bash
python main.py
```

如果 PDF 生成失败，主流程不会中断，系统会保留 HTML 报告并在运行摘要中记录提示。

---

## 开发与测试

运行测试：

```bash
pytest
```

测试内容包括：

* 数据处理函数；
* 评分逻辑；
* 用户画像构建；
* 个性化推荐；
* 聚类与模型输出；
* Agent fallback；
* 报告文件生成；
* API Key 安全检查。

---

## 安全说明

本项目不会在代码中硬编码 API Key。

请注意：

* `.env` 不应提交到 GitHub；
* `.env.example` 只保留空字段；
* 输出报告不包含真实 Token；
* Agent 输出不应暴露敏感信息；
* GitHub 公开仓库数据用于学习和项目展示，不涉及私有仓库。

---

## 常见问题

### 1. GitHub API 请求失败怎么办？

请检查：

```bash
python scripts/check_github_api.py
```

也可以检查：

* 网络是否能访问 GitHub；
* `.env` 中是否配置 `GITHUB_TOKEN`；
* 是否遇到 GitHub API 限流；
* 是否需要配置代理。

---

### 2. Streamlit 页面打不开怎么办？

确认已安装依赖：

```bash
python -m pip install -r requirements.txt
```

然后运行：

```bash
streamlit run app.py
```

---

### 3. DeepSeek Agent 没有生成真实解释怎么办？

检查 `.env`：

```env
DEEPSEEK_API_KEY=你的 DeepSeek API Key
USE_DEEPSEEK_AGENTS=true
```

如果未配置 API Key，系统会使用基础规则解释兜底。

---

### 4. PDF 没有生成怎么办？

先确认 HTML 报告是否存在：

```text
outputs/reports/agent_radar_report.html
```

再安装 Playwright：

```bash
python -m pip install playwright
python -m playwright install chromium
```

重新运行：

```bash
python main.py
```

---

### 5. 如何只看最终展示结果？

运行完整流程后直接查看：

```text
outputs/reports/agent_radar_report.html
outputs/reports/agent_radar_report.pdf
```

或启动：

```bash
streamlit run app.py
```

---

## 后续扩展方向

后续可继续扩展：

1. 增量采集与时间序列跟踪；
2. 加入 PR / Issue 互动质量分析；
3. 引入真实用户反馈作为推荐标签；
4. 增加项目复现成功率评估；
5. 部署 Streamlit 在线版本；
6. 自动生成项目复现脚手架；
7. 增强 DeepSeek Agent 的多轮交互能力；
8. 引入更严格的离线评测机制。

---

## 项目声明

本项目用于 Python 程序设计课程项目、数据科学项目实践与 AI Agent 开源生态分析学习。

项目评分、推荐等级和 Agent 解释均基于采集时点的 GitHub 公开数据与代理指标构建，不能等同于项目未来商业价值或长期成功概率。实际选择项目时仍需结合个人目标、技术背景和复现条件进行判断。

---

## 致谢

本项目开发过程中综合使用了 Python 数据分析、机器学习、PyTorch、Streamlit、Plotly、GitHub API、DeepSeek API 与 AI Coding Agent 协作开发方法。

感谢 GitHub 开源社区提供的公开仓库数据，也欢迎对 AI Agent 开源生态、数据科学项目和智能推荐系统感兴趣的同学进一步交流。

---

## 欢迎 Star

本项目已上传至 GitHub，欢迎感兴趣的同学查看、体验和交流。

如果这个项目对你有帮助，欢迎给仓库点一个 Star 支持一下。
