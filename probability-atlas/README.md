# Probability Archive｜概率论课堂档案馆 v0.1

`study-map` 中的独立静态子项目。用课堂时间、原始转录和可追溯的分析记录课程推进，优先支持阅读、回看与核对。HTML、CSS、原生JavaScript及JSON，无后端、账号、数据库或构建流程。

## 本地启动

在终端进入 `probability-atlas` 目录：

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

浏览器访问 [http://127.0.0.1:8765/](http://127.0.0.1:8765/)。如果端口被占用，可换成其他端口。需要HTTP服务读取JSON，请不要以双击HTML的 `file://` 方式启动。退出服务使用终端的 `Ctrl+C`。

页面适配手机宽度。若在同一局域网手机访问电脑服务，使用 `python -m http.server 8765 --bind 0.0.0.0`，然后在手机打开电脑局域网IP及端口；是否可达取决于本机防火墙和网络设置。

KaTeX脚本、样式和字体在 `vendor/katex/`，运行时不依赖CDN。首次启动无须 `npm install`。

本版使用KaTeX 0.19.1，许可和发布来源保存在该目录的 `LICENSE`、`VERSION.txt`。验收范围见 [验收记录](docs/verification.md)。

## 页面与稳定链接

- 首页：课程概况、档案数量、最近课程及主题。
- 课堂时间线：按日期进入课堂。
- 课堂详情：课堂脉络、重点讲解、例题、考试提示、个人学习记录、原始资料，以及跨课知识联系。
- 知识索引：由知识点反向定位课堂，区分课堂讲授联系与整理分析。
- 检索：日期、知识点、关键词和老师强调内容。

链接使用hash路由，部署在子目录也不需要服务器重写：

```text
#/timeline
#/lesson/2026-10-29
#/lesson/2026-10-29?t=00%3A23%3A28
#/concepts
#/concept/cdf
```

时间戳链接定位原始转录段落。现有资料没有可靠录音URL，所以页面不提供虚构音频跳转。10.29原录音开头约5分钟缺失，`00:00:00`表示文件起点，不代表上课起点。

## 文件与数据结构

```text
probability-atlas/
  index.html, styles.css, app.js
  data/lessons.json
  data/concepts.json
  data/transcripts/YYYY-MM-DD.json
  sources/transcripts/       原始TXT副本
  sources/courseware/        课件PDF副本
  sources/analysis/          既有分析报告副本
  vendor/katex/             本地公式渲染依赖及许可
  scripts/import_archive.py
  scripts/validate_archive.py
  docs/material-audit.md
```

`lessons.json` 保存 `schemaVersion`、`course`、`sourceTypes`和 `lessons`。`course.progress`是截至指定日期的有证据课程进度，不代表整学期完成百分比。

每节课的 `id`和 `date`为 `YYYY-MM-DD`，新增课堂不会改变旧ID。`coverage`区分重点整理与勘察摘要。`conceptIds`引用知识索引。`recording`保存末段时间戳和可确认的缺录信息；不清楚的值留空，不猜测时长。

`sections`中的 `outline`、`explanations`、`examples`、`examTips`、`personalNotes`、`connections`均为数组。无证据的栏目保留空数组 `[]`，页面显示缺资料提示，而不是生成填充内容。每条记录形如：

```json
{
  "id": "marginal-projection",
  "title": "投影与积分范围",
  "text": "有来源支持的摘要。",
  "sourceType": "transcript_summary",
  "sources": [{"sourceId": "transcript", "timestamp": "00:23:28"}],
  "formula": "f_X(x)=\\int_{-\\infty}^{+\\infty} f_{X,Y}(x,y)\\,dy"
}
```

上例演示字段形状，实际 `sourceId`必须使用该节课 `sources`中已有ID。`formula`可省略；写LaTeX时JSON反斜杠需要转义。

来源类型：

| sourceType | 意义 |
|---|---|
| `teacher_quote` | 转录中可逐字定位的老师原话，不把润色摘要冒充原话 |
| `transcript_summary` | 对课堂转录的摘要，仍需对应时间戳 |
| `ai_analysis` | 基于材料作的整理、知识联系或推测，与老师明示分开 |
| `personal_record` | 用户亲自提供的学习体验，不从转录推断 |

每节课的 `sources`保存 `id`、`label`、`kind`、项目内 `path`与追溯用 `originalPath`。引用可加 `timestamp`、物理 `page`、文本 `line`。课件 `pageCount`供页码范围校验。聊天个人自述没有本地原文件时允许 `kind: "personal"`、`path: null`，页面只显示来源说明。

`concepts.json`保存 `concepts`数组。每个知识点有稳定 `id`、名称、别名、描述及 `lessonIds`；它必须与课堂的 `conceptIds`双向一致。`relations`通过 `targetId`连接其他知识点，`type`只取 `classroom`或 `analysis`，并附带包括 `lessonId`、`sourceId`和可用时间戳的证据。

`data/transcripts/日期.json` 保存 `lessonId`与 `blocks`；每段有稳定 `id`、`timestamp`、`speaker`、`text`。说话人标签来自转写，不独立证明身份或多位任课老师。

## 如何增加下一节课

1. 将新转录保留在课程原资料目录；如有新课件，也一并保存。先确认日期、格式和缺录情况。
2. 阅读现有导入脚本的 `--help`并检查其内容映射。导入器是这批十一节课的快照工具，不会凭一个新文件名自动产生可信摘要；日常新增课推荐直接维护JSON。
3. 给新课堂分配新的日期ID，生成转录JSON并复制需要的来源文件。原文件保持不动。
4. 逐项添加有证据的栏目、来源和时间戳。个人体验没有用户自述则留空；考试提示保留老师表述的适用范围；推测用 `ai_analysis`。
5. 扩展 `conceptIds`与知识点 `lessonIds`两个方向；新增关系时写清来源和类型。
6. 更新 `course.progress`的说明及 `asOf`，不要自动覆写上级项目的 `data/courses.json`。
7. 运行验证并在浏览器检查新增课、原始段落定位、公式和手机布局。

```powershell
python scripts/validate_archive.py
```

验证器使用Python标准库，检查ID、双向关系、来源副本、时间戳、逐字引文、课件页码元数据和HTML/CSS本地资源路径。它不能代替人工判断“摘要是否忠于课堂”，也不能验证未取得的录音。

若要从这批原资料重新生成初始快照，命令为：

```powershell
python scripts/import_archive.py --source "D:\HuaweiMoveData\Users\郑皓雯\Desktop\study-map\概率论与数理统计" --report "D:\HuaweiMoveData\Users\郑皓雯\Documents\ChatGPT\alt+G\课程勘察\概率论十节课_课程勘察报告.md"
```

当现有 `lessons.json`或 `concepts.json`已经存在时，导入器会在写入前拒绝重建。只有显式加 `--force`才会重建项目生成的数据和来源副本，**这会覆盖手工修改的JSON**，不适合日常追加课堂。导入器不修改来源目录的原文件。

## GitHub Pages预览与部署

本次不自动执行commit、push或部署。检查文件和数据后，由你决定是否发布。

两种部署范围均可：

1. **从study-map仓库根发布**：在GitHub仓库的 Settings → Pages 选择要发布的分支和根目录，站点下以 `/probability-atlas/`进入本项目。保留相对资源路径及整个子项目。
2. **只发布该子目录**：使用你选择的Pages发布流程，仅把 `probability-atlas/`内容作为发布根目录，或复制到一个独立仓库后发布。站点入口此时为根路径。

GitHub分支发布支持仓库根或 `/docs`，不能在其文件夹下拉框中直接选任意子目录。只发布本项目时，应使用第二种范围及相应发布流程；从仓库根发布会同时纳入根目录的其他可发布学习文件。步骤依据 [GitHub Pages官方发布源说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

只发布本子目录的具体操作：审核内容后，把 `docs/deploy-pages.yml.example` 复制为仓库根的 `.github/workflows/probability-pages.yml`，由你提交并推送。在 Settings → Pages 将Source改为GitHub Actions，然后在Actions中手动运行 `Publish Probability Archive`。示例只设手动触发，不随push自动发布；上传范围为 `probability-atlas/`，最终入口在该Pages站点根目录。当前示例文件放在docs中，不会执行；一个仓库的Pages站点会被后续Pages发布替换，应选择你希望保留的发布范围。

该静态目录包含原始课堂TXT、PDF副本、分析报告及已经写入的个人记录。发布这个目录就会一并发布这些内容；如仅打算展示公开部分，应先另行确认发布范围并移除相应数据和引用，再运行验证。不要只删文件却保留无效链接。

部署后检查首页、`#/lesson/2026-10-29`直链、时间戳、原始材料下载和公式。hash路由不需要GitHub Pages的404重写配置。

## 已知资料边界

本版导入十一份真实转录，以10.29为重点示范，其余为有证据的勘察档案。缺第一章PDF、原音视频、可靠音频定位链接及正式考试通知。指定名称的分析文件未在仓库找到，使用可访问的对应勘察报告内容。详见 [资料勘察记录](docs/material-audit.md)。
