# 开发执行步骤

## 阶段概览

```
Phase 0: 项目基础设施    [✅ 已完成]
Phase 1: 数据源模块      [✅ 已完成]
Phase 2: 格式化 & 推送   [✅ 已完成]
Phase 3: 调度 & 部署     [✅ 已完成]
Phase 4: 测试 & 验收     [▶] 本地测试通过，待 GitHub Actions 部署
```

---

## Phase 0: 项目基础设施 (当前)

### Step 0.1: 项目目录结构
- [x] 创建 `src/`, `src/fetchers/`, `docs/`, `devlog/` 目录
- [x] 创建 `.github/workflows/` 目录

### Step 0.2: 标准文档
- [x] `docs/requirements.md` — 项目需求
- [x] `docs/tech-spec.md` — 技术规范
- [x] `docs/design-spec.md` — 设计规范
- [x] `docs/execution-steps.md` — 本文件

### Step 0.3: 开发日志
- [x] `devlog/` — 每日自动记录

### Step 0.4: CLAUDE.md
- [x] 创建 `CLAUDE.md`，写入项目指引和路径说明

### Step 0.5: 基础代码
- [x] `requirements.txt`
- [x] `src/config.py`
- [x] `src/fetchers/github_trending.py`

---

## Phase 1: 数据源模块

### Step 1.1: GitHub Trending 抓取 (已完成)
- 文件：[src/fetchers/github_trending.py](src/fetchers/github_trending.py)
- 抓取 `https://github.com/trending`，解析 Top 10
- 返回 `TrendingRepo` 列表

### Step 1.2: AI 新闻抓取 ✅ (已完成)
- 文件：[src/fetchers/ai_news.py](src/fetchers/ai_news.py)
- 来源：机器之心 RSS、量子位 Web、TechCrunch AI RSS、The Verge AI RSS
- RSS 源用 lxml 解析，Web 源用 BeautifulSoup
- 每个源独立 try/except，单源失败不影响整体
- 返回统一的 `NewsItem` 列表，带标题去重

---

## Phase 2: 格式化 & 推送

### Step 2.1: 消息格式化 ✅ (已完成)
- 文件：[src/formatter.py](src/formatter.py)
- 输入：GitHub Trending 列表 + AI 新闻列表
- 输出：Markdown 字符串（按设计规范排版）

### Step 2.2: PushPlus 推送 ✅ (已完成)
- 文件：[src/pusher.py](src/pusher.py)
- 调用 PushPlus API 发送 Markdown 消息
- Token 从环境变量读取

### Step 2.3: 主入口 ✅ (已完成)
- 文件：[src/main.py](src/main.py)
- 编排：抓取 → 格式化 → 推送
- 汇总日志输出

---

## Phase 3: 调度 & 部署

### Step 3.1: GitHub Actions 工作流 ✅ (已完成)
- 文件：[.github/workflows/daily-push.yml](.github/workflows/daily-push.yml)
- cron: `0 4 * * *` UTC
- 支持手动触发

### Step 3.2: README ✅ (已完成)
- 文件：[README.md](README.md)
- 使用说明 + 配置指南

---

## Phase 4: 测试 & 验收

### Step 4.1: 本地测试
- `python src/main.py` 手动执行
- 验证微信收到推送

### Step 4.2: Actions 测试
- workflow_dispatch 手动触发
- 验证定时任务正常运行

### Step 4.3: 容错测试
- 模拟某数据源不可用
- 验证标注"获取失败"而非崩溃

---

## 验收标准

- [x] GitHub Trending Top 10 正常抓取
- [x] AI 新闻从 4 个来源正常抓取（IT之家、量子位、TechCrunch AI、The Verge AI）
- [x] Markdown 格式整洁美观
- [x] PushPlus 推送成功到达微信
- [ ] GitHub Actions 每日 12:00 自动执行
- [x] 单源失败不影响整体推送
