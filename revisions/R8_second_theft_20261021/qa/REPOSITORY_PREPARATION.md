# R8 仓库源码准备记录

2026-10-21。执行范围仅为源码、文档与非图像 QA 归档；未修改 release 目录，未提交或推送。根代理仍负责最终同步、diff 审查和仓库提交。

## 1. 归档范围

已从 R8 发布工作目录复制 `source/`、`design/`、`research/`、`operations/` 和 `qa/` 内的 UTF-8 文本、JSON 与脚本。逐文件准备快照在 `repository_source_snapshot.json`。复制时不跟随符号链接，未包含 PDF、ZIP、原始照片/视频、截图、字体、浏览器或 git 元数据。

新版本目录是 `revisions/R8_second_theft_20261021/`。根 README 改为 R8 入口，新增根 `R8_HANDOFF_20261021.md`。旧版程序、源码、故事与交接原文件均保留。

当前 `source/` 和 QA 来源可能仍由相应作者做最后更新。准备快照不等同最后验收版本；应同步最终印刷源和独审结果后再审核提交。历史报告里的受审 hash、失败与当时缺口照实保留。

## 2. 已实际在新目录构建

从 revision 根实际运行：

```sh
python source/build.py
node source/build_print.cjs
python source/check_traceability_v3.py design/04_TRACEABILITY.json --level prototype
```

三条命令均正常退出。软件生成根离线页、play 副本和数据；打印生成两语玩家 HTML 及设计指南 HTML。追踪检查结果为 `REFERENCES_STRUCTURALLY_VALID`，无结构错误或警告，不是现场/体验验收。

构建出的 `R8_Offline.html` 为 122581 字节，SHA256 `2ae06c03275df27323377c92b07592aa31e7f8c13504f31abb087300c8f9a646`，与当时根代理发布候选相同；`play/index.html` 字节一致。机器记录见 `repository_rebuild_check.json`。

生成文件留在本地用于核验，由本版本目录的忽略规则排除。此步没有渲染或复制 PDF，也没有重跑浏览器或输出截图，避免把迁移检查伪装成又一次玩法验证。

## 3. 路径检查与依赖

|入口|输入定位|默认输出|迁移结论|
|---|---|---|---|
|`source/build.py`|`Path(__file__).resolve().parent`，同目录六类源码|revision 根离线页、play 与 qa|已实际构建，可从任意工作目录调用脚本路径|
|`source/build_print.cjs`|`__dirname` 下 content/figures；revision 的 design 完整稿与指南|revision 的 print|已实际构建，所需两份设计稿均存在|
|`source/render_print.cjs`|revision 的 print HTML|同目录 PDF 与 geometry JSON|默认路径已由前一步生成；实际 PDF 重渲染留给印刷验收|
|`source/test_engine.js`|同目录 engine/figures|revision 的 qa|无环境绝对路径；既有逻辑结果作为原快照保留|
|`source/test_browser.cjs`|revision 的 R8_Offline.html|qa 报告及截图|输入已生成；需要本机 Playwright/Chromium|
|`qa/final_independent_probe.cjs`|相邻 revision 的软件与源码|qa JSON，截图位置可配置|正式输入路径成立；截图默认位置需下述修正|
|追踪、交付校验脚本|显式命令行给定 JSON/root|标准输出|不依赖本次工作区；完整包 manifest 不能在仅源码目录冒称全通过|

没有发现当前可执行构建源必须读取 `/workspace`、`/root` 或本轮下载字体的绝对路径。浏览器路径由 `CHROMIUM_PATH` 配置，字体由使用者本机提供。历史审计/原始素材 manifest 中保留的 `/workspace/...` 与 `work/...` 是当时运行或证据位置，并非恢复当前程序必需的输入。

## 4. 已交根代理的具体临时路径建议

以下定位针对复制时快照，**本角色没有并行修改这些脚本**：

|位置|当前行为|建议统一修改|
|---|---|---|
|`source/build_print.cjs` 第7行|`--draft` 使用 `path.resolve(ROOT,'../../work/print_draft')`，迁到 revision 后会落到 repo/work|用 `process.env.R8_PRINT_DRAFT_DIR || path.join(ROOT,'qa_work','print_draft')`|
|`source/render_print.cjs` 第7行|相同的 `--draft` 跨目录输出|与生成器使用同一环境变量和默认路径|
|`qa/final_independent_probe.cjs` 第12行|默认截图在 `../../work/final_independent_review`|保留 `REVIEW_SCREENSHOT_DIR`，默认改 `path.join(ROOT,'qa_work','final_independent_review')`|

两打印脚本由印刷作者更新，独审脚本由独审作者更新；之后根代理复制最终源。常规正式构建不使用 `--draft`，当前仍能正常复现。

## 5. 收口交给根代理

同步最后源码与 QA 后，检查源快照、实际生成哈希、独审报告的受测 hash 和最终 manifest 是否一致；不修改历史报告的旧 hash 来制造一致。更新交接中的阶段说明时，仍保留 G2 REJECTED、真人/现场 NOT_RUN、用户未确认新剧情等真实边界。

源码目录不提交生成物、截图、开发依赖或原始取材。ROOT 内新文件只有文档和新 revision，旧程序没有被覆盖；不要将根旧构建入口误当 R8。最终 diff 和提交由根代理执行。

## Controller最终同步补记

已同步最终冻结的source、设计、研究、运营和QA；加入候选家族索引、最终独审、受限模型走查、52页打印QA、17项冷启动和最终验收。此前列出的临时输出路径已经由对应制作/审查代理改为可配置或系统临时目录。此报告前段49文件与当时快照仍为历史准备记录，不伪改为最终复制数量。
