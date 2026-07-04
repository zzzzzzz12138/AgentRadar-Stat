# Demo Script

## 3-5 分钟答辩展示路线

### 0:00-0:30 打开答辩报告

先打开 `outputs/reports/agent_radar_report.html` 或 `outputs/reports/agent_radar_report.pdf`。开场说明 AgentRadar-Stat 是一个基于 GitHub 公开仓库的 AI Agent 开源项目雷达，本轮展示基于 500 个真实 GitHub 公开仓库。

讲解重点：

- 仓库样本量、关键词数量、去重前后数量和入模项目数。
- 数据状态显示为 GitHub 公开仓库数据。
- 答辩展示以 AgentRadar-Stat 答辩报告为主，报告中已整合数据采集、趋势洞察、评分排行、聚类画像、模型预测、PyTorch 扩展、个性化推荐与 DeepSeek Agent 解释。

### 0:30-1:10 采集漏斗与 Top 榜

展示数据采集漏斗和综合潜力 Top 15 / Top 20。

讲解重点：

- 从搜索候选到去重，再到相关性过滤，最后进入评分和建模。
- Top 榜不是单纯 Stars 排名，而是综合潜力、风险和复现可行性的结果。

### 1:10-1:50 风险-潜力四象限

放大讲风险-潜力四象限。

讲解重点：

- 高潜力低风险：优先推荐。
- 高潜力高风险：谨慎探索。
- 低潜力低风险：普通参考。
- 低潜力高风险：暂不推荐。

### 1:50-2:25 PCA 聚类地图

展示 PCA / 聚类项目地图和聚类类型分布。

讲解重点：

- 聚类用于项目画像，不作为监督学习标签。
- 中文聚类标签横向显示，避免竖排断裂。
- 每个点都可以悬停查看仓库、语言、潜力分和风险分。

### 2:25-3:05 使用报告目录导航

展示左侧可跳转目录，快速跳转到模型、推荐和 Agent 章节。

讲解重点：

- 报告从项目概览、数据采集、指标体系一路到模型、个性化推荐和 Agent 解释。
- 每章都有“看什么、发现什么、为什么重要”的解释，不只是图表堆叠。

### 3:05-3:40 模型严谨性章节

跳转到“模型预测”和“PyTorch 扩展”章节。

讲解重点：

- Task A / Task B 分离。
- 训练时排除最终评分、推荐等级和评分子项等直接泄漏字段。
- sklearn 多模型比较与 TabularWideDeepNet 共同展示建模工作量。

### 3:40-4:20 个性化推荐与 DeepSeek Agent

跳转到“个性化推荐”和“DeepSeek Agent”章节。

讲解重点：

- 个性化分和通用潜力分可能不同。
- Agent 输出以中文卡片展示，不展示原始 JSON。
- ProjectAdvisorAgent 给出适合当前画像的项目和复现路线。
- CriticAgent 用于审查报告可信度和证据缺口。

### 4:20-5:00 Streamlit 展示页与报告导出

运行 `streamlit run app.py`，先展示 Streamlit 首页、数据概览和评分排行，再打开“报告导出”页。

讲解重点：

- Streamlit 已与最终项目报告统一冰蓝科技风、中文标签和卡片式布局。
- 页面提供 HTML 项目报告和 PDF 项目报告。
- 如果 PDF 未生成，说明需要安装 Playwright 和 Chromium 后重新运行 `python main.py`。

## Screenshot Checklist

Save screenshots under `outputs/screenshots/`:

1. HTML Report Hero
2. HTML Report 可跳转目录
3. 数据采集漏斗
4. 综合潜力 Top 榜
5. 风险-潜力四象限
6. PCA 聚类地图
7. 模型预测章节
8. PyTorch 扩展章节
9. 个性化推荐章节
10. DeepSeek Agent 卡片
11. Streamlit 首页
12. Streamlit 数据概览页
13. Streamlit 报告导出页
14. PDF 报告第一页

## Validation Commands

```powershell
python main.py
$env:OMP_NUM_THREADS='1'; $env:LOKY_MAX_CPU_COUNT='1'; pytest -q
streamlit run app.py
```
