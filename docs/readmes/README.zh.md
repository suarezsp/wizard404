<div align="center">

<img src="../imgs/w404_banner.png" alt="Wizard404" width="720"/>

# Wizard404

### 文档搜索与管理 — CLI + Web

**扫描 · 导入 · 搜索 · 浏览 · 整理 · 清理。**  
同一代码库。同一 API。终端与浏览器。文档尽在掌握。

[文档](../) · [快速开始](#快速开始) · [参与贡献](../../CONTRIBUTING.md)

**阅读语言：** [English](../../README.md) · [Español](README.es.md) · [Polski](README.pl.md) · [中文](README.zh.md) · [Русский](README.ru.md) · [Deutsch](README.de.md)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

**MIT** · Python · FastAPI · React · CLI + Web

</div>

---

> **Wizard404** 集中管理文档的搜索与整理（PDF、文本、Office、图片、音频、视频）：扫描目录、导入索引、按内容搜索，并从 CLI 或网页端浏览。面向小团队、文档分散的企业，以及将核心（`wizard404_core`）作为库复用的开发者。

---

## 什么是 Wizard404？

Wizard404 是一个**开源的文档搜索与管理平台**，而不仅是文件浏览器。它是完整技术栈：可复用的 Python **核心**、**REST API**（FastAPI）、交互式 **CLI**（w404）以及功能相同的 **Web 应用**（React）。

传统工具需要逐个打开文件。Wizard404 **对内容建立索引**，因此可按关键词搜索、按类型或大小筛选，直达目标文档。你可以扫描文件夹、查看按扩展名与熵的统计、按类型/日期/大小整理文件并清理缓存与日志，在终端或浏览器中完成。

默认使用 **SQLite** 运行整套系统。一个后端，一条命令即可启动。

```bash
# CLI — 两步打开菜单
./w404

# Web — 后端 + 前端
./run-dev.sh
# API：http://localhost:8000 · 应用：http://localhost:5173
```

---

## 预览

| CLI — 主菜单 | 扫描结果 — 熵与按扩展名 |
|--------------|--------------------------|
| <img src="../imgs/scp-1.png" alt="CLI 菜单" width="400"/> | <img src="../imgs/scp-2.png" alt="扫描结果" width="400"/> |

*左：主菜单（扫描、导入、搜索、浏览、整理、清理）。右：按扩展名与熵汇总的扫描结果。*

---

## 功能一览

| 功能 | CLI | Web | 说明 |
|------|-----|-----|------|
| **扫描目录** | 是 | 是 | 分析类型、大小、扩展名；熵汇总；按扩展名下钻。 |
| **导入文档** | 是 | 是 | 将文件加入索引（路径或 Chrome/Edge 中“选择文件夹”）。 |
| **搜索** | 是 | 是 | 在目录或已索引文档中按关键词；筛选与语义选项。 |
| **浏览 / 索引** | 是 | 是 | 列出已索引文档；查看详情与摘要。 |
| **整理** | 是 | 否 | 按类型、日期或大小将文件移至文件夹。 |
| **清理** | 是 | 否 | 查找缓存、日志、小文件；安全删除。 |

*导入与“查看已索引”建议在 **Web**（浏览 + 导入）中使用。CLI 会跳转到应用以保持体验一致。*

---

## 解决的问题

- **按内容查找文档** — 按关键词搜索合同、报告或报价，无需逐个打开 PDF 或 Office 文件。
- **整理下载与文件夹** — 按类型、日期或大小排序（整理）；检测缓存与临时文件（清理）。
- **统一搜索入口** — 扫描目录、导入索引，在磁盘或索引中从 CLI 或 Web 搜索。

---

## 架构

按层划分的 monorepo：核心、API、CLI、前端。

```
backend/          FastAPI 应用，auth、health、config
  app/            路由（auth、documents、scan）、服务、数据库
  wizard404_core  发现、提取器（PDF、Office、文本、图片、媒体）、搜索、语义、摘要
cli/              w404 — TUI 菜单与直接命令（scan、import、search、organize、cleanup）
frontend/         React + Vite + Tailwind — 16-bit 风格 UI，Scan、Import、Search、Explore、文档详情
docs/             架构、贡献、Web 目录访问、核心即库
```

---

## 快速开始

### 1. 克隆与依赖

- **Python 3.10+**
- **Node 18+**（可选，用于前端）
- **SQLite**（默认；可选 PostgreSQL）

```bash
git clone <仓库地址>
cd wizard404
```

### 2. 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

可选：`python -m scripts.seed_admin` 创建默认用户。API：**http://localhost:8000**，文档：**http://localhost:8000/docs**。

### 3. CLI（w404）

在仓库根目录：

```bash
./w404
```

打开交互式菜单。若后端未运行，CLI 可启动它并设置默认令牌（用户 `w404` / `w404`）。然后使用**扫描目录**、**导入文档**、**搜索**、**浏览**、**整理**、**清理**。

直接命令示例：

```bash
./w404 scan .
./w404 import docs/
./w404 search 合同 --path docs/
./w404 organize /path -d ~/Desktop/Organized --by type
./w404 cleanup /path --dry-run
```

### 4. Web（后端 + 前端）

在仓库根目录：

```bash
./run-dev.sh
```

后端在后台，前端在前台。应用地址：**http://localhost:5173**。首次使用请先安装后端 venv 与 `frontend/node_modules`（步骤 2 及 `cd frontend && npm install`）。

---

## 适用场景与受众

- **小团队与公司**，文档分散在多个文件夹与邮件中。
- **开发者**，希望将核心作为库复用 — 参见 [将核心作为库使用](../core-as-library.md)。

---

## 开发

```bash
# 后端测试
cd backend && source venv/bin/activate && pytest tests -v

# 前端测试
cd frontend && npm run test

# 各项目内 lint / 格式化（backend: ruff/black；frontend: eslint/prettier）
```

---

## 许可证

MIT。见 [LICENSE](../../LICENSE)。

---

## 参与贡献

我们希望贡献流程简单明了。详见 [贡献指南 (CONTRIBUTING.md)](../../CONTRIBUTING.md) 中的环境、代码规范与流程。想法与建议可提 issue 或查看 CONTRIBUTING 中的「Good First Issues」。行为准则：[CODE_OF_CONDUCT.md](../../CODE_OF_CONDUCT.md)。

---

<div align="center">

**Wizard404** — Python · FastAPI · React · Vite · Tailwind · CLI + Web

</div>
