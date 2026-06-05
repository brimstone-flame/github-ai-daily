# 技术规范

## 语言与运行环境

- **语言**: Python 3.11+
- **包管理**: pip + requirements.txt
- **运行环境**: GitHub Actions `ubuntu-latest` runner

## 依赖库

| 库 | 版本 | 用途 |
|----|------|------|
| requests | >=2.31.0 | HTTP 请求（抓取网页、调用 API） |
| beautifulsoup4 | >=4.12.0 | HTML/XML 解析 |
| lxml | >=5.0.0 | BeautifulSoup 的 XML 解析后端（RSS） |

## 模块架构

```
main.py  (入口，编排流程)
  ├── config.py          (配置管理，环境变量读取)
  ├── fetchers/
  │   ├── github_trending.py  (GitHub Trending 抓取)
  │   └── ai_news.py          (AI 新闻多源抓取)
  ├── formatter.py       (Markdown 消息格式化)
  └── pusher.py          (PushPlus API 推送)
```

## 数据流

1. `main.py` 调用各模块
2. `fetchers` 返回结构化数据（dataclass）
3. `formatter` 将数据转为 Markdown 字符串
4. `pusher` 将 Markdown 发送至 PushPlus API
5. 每个模块独立 try/except，单模块失败不阻塞

## 错误处理规范

- 每个 fetcher 内部捕获异常，记录日志后返回空数据
- `main.py` 汇总各模块结果，缺失数据在消息中标注「获取失败」
- PushPlus 推送失败记录日志但不抛异常（避免 GitHub Actions 标记为 failed）

## 编码规范

- 文件编码：UTF-8
- 类型注解：使用 Python 3.10+ 语法 (`list[dict]`, `str | None`)
- 日志：使用 `logging` 标准库，INFO 级别
- 命名：snake_case 函数/变量，PascalCase dataclass

## 安全规范

- PushPlus Token 通过环境变量 `PUSHPLUS_TOKEN` 注入
- 不硬编码任何密钥
- 不向日志输出 Token
- `.gitignore` 忽略 `.env` 文件
