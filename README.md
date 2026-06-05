# GitHub & AI 日报微信推送

每日中午 12:00 自动推送 **GitHub Trending Top 10** + **AI 行业新闻** 到你的个人微信。

## 效果预览

```
📅 2026年6月5日 星期五 · GitHub & AI 日报
━━━━━━━━━━━━━━━━━━

🔷 GitHub Trending Top 10

1. 📦 owner/awesome-project
   🔤 Python · ⭐ 1,234 stars today
   📝 一个很棒的开源项目简介
   🔗 github.com/owner/awesome-project

...

━━━━━━━━━━━━━━━━━━

🤖 AI 行业新闻

【机器之心】
• AI 领域重大突破：...
  🔗 jiqizhixin.com/...

【量子位】
• 大模型最新进展：...
  🔗 qbitai.com/...

━━━━━━━━━━━━━━━━━━
🕐 更新时间：2026-06-05 12:00
```

## 快速开始

### 1. 注册 PushPlus

访问 [pushplus.plus](https://www.pushplus.plus) 注册账号，获取你的 **Token**。

### 2. 配置 GitHub Secrets

在 GitHub 仓库中：
- 进入 **Settings → Secrets and variables → Actions**
- 点击 **New repository secret**
- Name: `PUSHPLUS_TOKEN`
- Value: 你的 PushPlus Token

### 3. 启用 GitHub Actions

- 进入 **Actions** 标签页
- 点击 "I understand my workflows, go ahead and enable them"

### 4. 手动测试

- 进入 Actions → **GitHub & AI 日报推送** → **Run workflow**
- 点击运行，检查微信是否收到推

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 设置 Token
export PUSHPLUS_TOKEN=你的Token
# Windows: set PUSHPLUS_TOKEN=你的Token

# 运行
python -m src.main
```

## 项目结构

```
├── .github/workflows/daily-push.yml   # 定时调度
├── src/
│   ├── main.py           # 主入口
│   ├── config.py         # 配置管理
│   ├── formatter.py      # Markdown 格式化
│   ├── pusher.py         # PushPlus 推送
│   └── fetchers/
│       ├── github_trending.py  # GitHub Trending 抓取
│       └── ai_news.py          # AI 新闻抓取
├── docs/                 # 项目文档
├── devlog/               # 开发日志
└── CLAUDE.md             # 项目指引
```

## 自定义

- 修改 AI 新闻来源：编辑 `src/config.py` 中的 `ai_news_sources`
- 调整推送时间：修改 `.github/workflows/daily-push.yml` 中的 cron 表达式
- 更换推送服务：修改 `src/pusher.py` 中的 API 调用
