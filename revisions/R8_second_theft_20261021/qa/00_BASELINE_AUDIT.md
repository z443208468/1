# G0 技术基线恢复与交付审计

日期：2026-10-21（Asia/Tokyo）。执行角色：独立 `baseline_restore` 子智能体。仅恢复功能基线，没有为新故事放行。

## 1. 权威版本与读取范围

- 实际读取仓库：`https://github.com/z443208468/1`，分支 `1`。
- HEAD：`7a188794224cbc189adf5424e41bf50b6bea939e`；`git ls-files` 为 **69 个文件**。
- 已完整读取本轮上传工作流的 `SKILL.md`、仓库交接、根 README、构建入口与小修订脚本、引擎与现有逻辑/浏览器测试；检查了数据生成、打印生成、离线打包和设计指南渲染的入口与输出链。
- README 的“当前 R5”是过时创作状态；交接明确 R2—R5 剧情已被否决。本次不会把 R5 文字视为有效新剧情，亦未发现公开树中存在已接入的新故事。
- 原交付 `Tokyo_Scene_Express_R3_1(1).zip` 本轮未提供，不能证明此次重建与原 34 文件包逐字节一致。交接中的旧包 SHA256 只能作为历史索引。
- `取材(4).zip` 未成功传入。本角色没有读取原始照片/视频；此审计不对实地物证作像素或空间认证。

## 2. 实际恢复结果

原仓库文件保持不变。拷贝源文件到 `work/baseline/` 后执行：

```sh
python tools/build_release.py
```

构建成功，实际生成六项：

| 生成项 | 状态 |
|---|---|
| `R3_Offline.html` | 自包含离线可玩页；实际浏览器用 `file://` 打开成功 |
| `play/data.json` | 5 关、终局、提示、来源、中英文数据 |
| `play/data.js` | 网页使用的数据封装 |
| `play/print_zh.html` | 13 个打印页 DOM |
| `play/print_en.html` | 13 个打印页 DOM |
| `play/print.html` | 双语打印入口 |

重建离线页 SHA256：`8cfa78ebd32d5ab910d47ba75c1beea6ca3ae2550ec613b63b963df925b7e79e`。这不是原 ZIP 的散列，也不是新版产物。

`apply_release_refinements.py` 是构建链中的源码修改器，在副本内补入纪念像识别图并调整文字。此次它修改了 `play/app.js`、`play/figures.js`、`tools/build_data.py`、`tools/build_print.py`；逻辑测试还覆盖了副本中的 `qa/logic_results.json`。完整清单在 `work/baseline_inventory.json`。

**后续新版本必须改真实数据源和打印生成器。不能只替换生成后的 data.json/HTML；不得不加区分地将旧修订器施于新引擎。**

## 3. 本轮实际验证

### 逻辑

原 `qa/test_logic.js` 本轮重新执行，**31/31 检查、445 个离散输入枚举**成功。覆盖五关唯一离散答案、空输入、图形旋转/翻面、终局语义、1995 下界、若干存档规范化、提示数量及旧成本算术。

该脚本硬编码日期 `2026-10-20`，其旧字段不构成本轮运行日期；本轮执行日期以本审计与新 smoke 日志为准。

### 浏览器最小复现

使用现有 Node Playwright 与实际 Chromium，运行 `work/baseline_smoke.cjs`，结果见 `work/baseline_smoke_results.json`，**13/13 成功**：

- 直接打开本地离线文件；空答案失败反馈。
- 第一关真实卡片点击、第二关真实翻面/旋转操作。
- `file://` 来源下队名在 reload 后保留。
- S03 的 share 选择向 S04 提供朝向援助；S04 仍需填写解释。
- 完成五关及终局，回执实际显示。
- 切换 joint 结局、切换英文且保留完成状态。
- 390px 视口无水平溢出，未捕获 JS 异常。
- 两种语言打印 HTML 均有 13 页，中文字体已可用。

这里只做最少基线复现，没有为旧稿额外跑完整四组合、浏览器矩阵或所有 PDF 页目视检查；也没有将旧逻辑通过映射为新作品通过。

**未测试**：真人盲测、实地游玩、商业许可、Windows 浏览器保存表现、全部纸面成品视觉质量。PDF 原型及旧设计指南本轮未重新输出，避免将资源投入已否决旧稿；下游完整交付需实际生成并逐页检查新版 PDF。

## 4. 已确认的技术性设计问题

1. `play/app.js` 明文标示“记录模式，不改变答案”。`mode` 只进入设置/保存/回执，`submit()` 不读取它；每关及终局都只由 `E.check(expected, input)` 决定。**桌面与实地在旧源码中确实使用同一题面/答案体系，现场勾选不是必要输入。**
2. `observed` 是自由勾选的自报记录；旧实现没有把真实环境信息接入推理判定。若新版声称具有场景依赖，应改变信息取得方式、证据选择和推理操作，而不是要求打勾或添加 GPS 形式门槛。
3. 旧 `challenge/share` 的行为差异是第一次进入 S04 时的朝向援助；`solo/joint` 主要改终局文字。代码具备两条独立变量，但这不证明它们具有足够戏剧后果。新版是否修改由 M2/M3 设计决定。
4. 旧状态恢复对 `inputs/passed/hints/observed/assisted` 只做对象类型检查，未按字段完整规范化。新引擎宜逐字段恢复并校验实际结案条件，避免把导入的 `completed` 当真实性证明。
5. 旧生成器的打印文案有相当部分为直接内嵌，故事改写不能仅修改数据源。需要对剧情、操作词、答案、提示、道具和终局做一致性核对。

## 5. 可用构建依赖与复现

现成可用：Python、Node.js、Python `fitz`/Pillow/reportlab、Poppler。默认 Python 无 `playwright`/`markdown_it`；默认系统无 Chromium 或 CJK 字体。Node 的 Playwright 已安装，可直接 `require('playwright')`。

为本项目在 `work/deps/` 准备并实际启动了公共构建依赖：

| 用途 | 工作区路径 |
|---|---|
| Chromium headless | `/workspace/scratch/04ab10133470/work/deps/chrome-headless-shell-linux64/chrome-headless-shell` |
| 中文字体 | `/workspace/scratch/04ab10133470/work/deps/fonts/NotoSansCJKsc-Regular.otf` |
| Fontconfig | `/workspace/scratch/04ab10133470/work/deps/fonts.conf` |

浏览器来自 Google Chrome for Testing 官方元数据公布的稳定版 `156.0.8078.47`：

- 元数据：`https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json`
- 下载：`https://storage.googleapis.com/chrome-for-testing-public/156.0.8078.47/linux64/chrome-headless-shell-linux64.zip`
- Noto CJK 字体：`https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf`

Playwright 的默认 CDN 下载返回 195 字节 `Site Unavailable` HTML，不是浏览器 ZIP；没有将它当作成功。改用上述官方已列明的文件后下载、解压与实际启动成功。

渲染时设置：

```sh
FONTCONFIG_FILE=/workspace/scratch/04ab10133470/work/deps/fonts.conf node work/baseline_smoke.cjs
```

Node launch 指定上表的 `executablePath`，`headless: true` 与 `args: ['--no-sandbox']`。当前工具的默认进程沙箱阻止 Chromium 启动；通过 `exec_command` 的 `require_escalated` 自动审核获准执行本地浏览器后成功。后续本地浏览器测试同样需要该执行方式，不能把默认沙箱的 `Operation not permitted` 当成游戏故障。

字体/浏览器只作内部依赖，**不放入仓库或交付 ZIP**。最终 PDF 可以嵌入字体子集；浏览器 HTML 使用系统字体回退或明确可选依赖，不能令游客下载开发工具。

## 6. 下游不得缩水的交付类别

| 类别 | 新版实际需形成的产物 |
|---|---|
| 完整作者稿 | 开场、人物、事件/场戏、五站转折、分支、终局、独立真相年表 |
| 机制规格 | 真物证/道具、输入、答案、失败反馈、三级提示、辅助、跨站回收和替代路径 |
| 玩家包 | 中英文题包与实体材料 HTML；实际渲染 PDF；原创示意与规则 |
| 软件 | 新故事已接入的单文件离线 HTML；保存、双语、验答、选项与终局 |
| 源码 | 可重建的数据源、引擎、图形、打印/打包生成器、复现命令 |
| 运营 | 真实走法、免费区/开放/施工边界、时长与预算假设、天气替代 |
| QA | 新版逻辑/浏览器/打印实测日志、哈希、缺陷与已测/未测分层 |
| 总包 | 真正可下载 ZIP，不以研究/概念说明替代 |

结论：**现有公开源可恢复 R3.1 功能基线；恢复结果是旧故事原型，尚无合格新故事。** 后续可复用离线交付方式、双语数据、免费三级提示、辅助留痕、早解权和打印链，但新机制是否成立必须重新经过 M2/M3 与 M4。
