# 项目需求文档

## 项目名称

GitHub & AI 日报微信推送 (GitHub AI Daily)

## 项目概述

每日中午 12:00 自动向用户个人微信推送一条消息，包含：
- GitHub Trending 热门项目 Top 10（项目介绍 + 链接）
- 当日 AI 行业新闻摘要（附来源链接）

## 功能需求

### F1: GitHub Trending 抓取
- 来源：https://github.com/trending
- 频率：每日一次
- 数量：Top 10
- 内容：项目名、描述、编程语言、今日星数、项目链接

### F2: AI 新闻抓取
- 来源：机器之心、量子位、TechCrunch AI、The Verge AI
- 频率：每日一次
- 数量：每源最多 6 条
- 内容：标题、摘要、来源名称、原文链接
- 容错：单源失败不影响整体

### F3: 消息格式化
- 格式：Markdown
- 风格：简洁直观，淡蓝色主题
- 结构：日期头 → GitHub 板块 → AI 新闻板块 → 更新时间

### F4: 微信推送
- 服务：PushPlus API
- Token 管理：GitHub Secrets（环境变量注入）

### F5: 定时调度
- 平台：GitHub Actions
- 触发：cron `0 4 * * *` UTC（北京时间 12:00）
- 手动触发：支持 workflow_dispatch

## 非功能需求

- **可靠性**：单模块失败不影响整体推送
- **可维护性**：模块化架构，数据源可独立增删
- **安全性**：Token 通过 Secrets 管理，不提交到代码仓库
