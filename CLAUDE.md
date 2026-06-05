# CLAUDE.md — GitHub AI Daily 项目指引

## 项目简介

每日中午 12:00 自动推送 GitHub Trending Top 10 + AI 行业新闻到个人微信。
技术栈：Python + PushPlus + GitHub Actions。

## 标准文件路径

| 文档 | 路径 | 说明 |
|------|------|------|
| 项目需求 | [docs/requirements.md](docs/requirements.md) | 功能需求、非功能需求 |
| 技术规范 | [docs/tech-spec.md](docs/tech-spec.md) | 技术栈、模块架构、编码规范 |
| 设计规范 | [docs/design-spec.md](docs/design-spec.md) | UI 设计、配色、消息结构 |
| 执行步骤 | [docs/execution-steps.md](docs/execution-steps.md) | 分阶段开发步骤与验收标准 |
| 开发日志 | [devlog/](devlog/) | 每日开发记录（以日期命名 `YYYY-MM-DD.md`） |

## 工作说明

### 开发原则

1. **逐步推进**：按 Phase 顺序开发，一个模块完成并验证后再进入下一个
2. **单模块验证**：每完成一个 `.py` 文件，单独运行验证语法和导入正确
3. **容错优先**：所有外部请求包裹 try/except，单点失败不阻塞整体
4. **日志透明**：关键步骤使用 `logging` 输出，方便 GitHub Actions 排查

### 每日工作流

1. 阅读 `docs/execution-steps.md` 确认当前进度
2. 检查 `devlog/` 最新日志了解昨日完成情况
3. 创建当日 `devlog/YYYY-MM-DD.md` 记录工作计划
4. 按 Phase 顺序实现下一个模块
5. 完成后更新 `devlog/` 和 `docs/execution-steps.md` 勾选状态

### 代码编写习惯

- 每个 `.py` 文件包含模块级 docstring
- dataclass 用于结构化数据（`TrendingRepo`, `NewsItem`）
- 类型注解使用 Python 3.10+ 语法
- 全局 `logging.getLogger(__name__)` 日志实例
- 文件编码 UTF-8

### 推送格式规范

- 板块标题：`##` + emoji 前缀
- GitHub 项目：数字序号 + 📦 + 链接
- AI 新闻：`【来源名】` + `• 标题` + `🔗 链接`
- 分隔线使用 `━━━` 或 `---`

### 配置文件

- PushPlus Token：环境变量 `PUSHPLUS_TOKEN`，不硬编码
- 本地开发：创建 `.env` 文件手动 export（已加入 `.gitignore`）
- GitHub Actions：通过 Secrets 注入
