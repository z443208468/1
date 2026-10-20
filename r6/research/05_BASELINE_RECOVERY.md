# R3.1 技术基线恢复与集成报告

核验时间：2026-10-20；仓库基线 `7a188794224cbc189adf5424e41bf50b6bea939e`。本报告只认定旧产品的技术资产和实际运行结果，不评价旧故事或证明新故事已通过。

## 1. 权威原包已取得，前期下载阻塞已由用户重新上传解除

- 实际读取：`upload/Tokyo_Scene_Express_R3_1(2).zip`。
- SHA256：`570fdfb2b52f037978e3113f101f3ad6034a3b6219914968ee107aee71903144`，与正式交接完全一致。
- 34个文件；内部 `MANIFEST.sha256` 的33条数据全部重新计算匹配，0项差异。
- 原样解压保全目录：`r3-attachment/`。未在该目录执行会修改文件的构建/测试。
- 实际测试使用副本 `r3-attachment-test/`；先前仓库重建使用独立副本 `r3-baseline/`。两者均不是新 worktree；主仓库旧文件未改。
- 原始JPEG/MP4没有在本次恢复中读取；本报告不新增实拍观察结论。

## 2. 源码重建与原包关系

仓库隔离副本执行 `python3 tools/build_release.py` 成功。与随后取得的原包逐文件比较：34项中28项在重建树出现，16项字节相同，12项不同，6项尚未生成/属于打包元数据。详见 `baseline_hash_comparison.json`。

关键可运行资产 `R3_Offline.html`、`play/app.js`、`play/engine.js`、`play/figures.js`、`play/data.json`、`play/data.js` 均与实际原ZIP一致。旧 `apply_release_refinements.py` 会修改源文件，故只在隔离副本运行。

生成器差异很小但不能混称字节一致：恢复后的 `build_data.py` 比原包多建目录一行；`build_print.py` 有注释、未使用import和一个CSS空格差异，生成的中英文打印HTML亦因此字节不一致。设计/运营文件和测试记录存在实质版本差异，应以原附件的机制说明为权威，再查正式交接更晚约束。

已由实际附件抽出 `baseline_mechanics_contract.json`：含五关类型、卡片ID、选项值、正确答案、提示数量、证据ID、终局七字段、旋转初态、独立分支和早解规则。新版可对照此文件做语义回归。

## 3. 本轮实际执行结果

|验证|结果|准确范围|
|---|---|---|
|原附件逻辑脚本|31/31 PASS；445个枚举组合|只证明离散规则和既定算术，不证明场景可达或趣味|
|原附件浏览器脚本|20/20 PASS|Chromium加载完整离线HTML；保留原脚本的set_content模式|
|实际file URL打开与本地存档|PASS|真实本地HTML打开，修改队名后reload保留|
|challenge+solo / challenge+joint / share+solo / share+joint|四组全部完成|UI作答和选择；每组仅完成S03就能在终局提交完整答案，不强制盖章|
|S04初始校准|PASS|challenge=(3,true)，share=(0,false)|
|已进入S04后更改S03策略|PASS|不重置玩家已转动的图|
|中英玩家PDF重新渲染|各13页|有中文字形、非空白，26页缩略联系表目视未见截断/溢出|
|设计指南PDF重新渲染|17页|文本提取无替代字符；本次没有逐页高倍率目视审校指南|
|现场游客盲测/商业许可|NOT_RUN|不得根据以上软件结果宣称已验证|

实际浏览器附加记录见 `baseline_runtime_probe.json`；原脚本结果副本位于 `r3-attachment-test/qa/`。PDF数量/提取探针见 `baseline_pdf_probe.json`。原脚本里固定的浏览器路径描述和历史测试日期不应被当成这轮运行环境的准确记录，本报告为本轮范围校正。

## 4. 本次发现的两项原版UI缺陷（未修改旧基线）

1. **已通过后清空卡片仍显示成功剧情。** 用UI完成S01，再点清空排列，`passed[0]`和成功文本仍留存。玩家当前答案和所见后果不一致。建议新版修复显示/已过状态的失效处理，答案、提示、奖励规则无需变化。
2. **格式有效但卡片ID异常的导入JSON可导致渲染异常。** 实际导入 `inputs[0].order=['unknown_card']` 后报 `Cannot read properties of undefined (reading 'label')`。`engine.restore`仅归一化顶层枚举，没有校验各关输入结构。建议新版在UI导入入口和初次恢复时过滤未知ID、非法类型；这是容错，不需要修改谜题。

没有证据表明这些缺陷使冻结机制必须变更。不要把修复UI错误包装成新增关卡或收紧早解。

## 5. 新故事集成必须覆盖的文本层

`play/data.json`和`play/data.js`是生成物，源头在 `tools/build_data.py`。字段结构：顶层 `version/title/subtitle/opening/safety/stages/sources/finalFields/finalAnswer/ending/buildNotes`。每站含 `id/title/site/type/intro/prompt/cards/fields/answer/hints/success/lead/evidence/sources/minutes`，多数自然语言为 `{zh,en}`。`finalAnswer`与各关`answer`冻结；选项值、卡片ID、旋转语义冻结。

仅改数据不够：`play/app.js`还硬编码旧开场标题“公开试单”、人物名、S04合作提示、终局“投递”文案、回执标签等。`play/index.html`含旧标题、版本与打印入口；`style.css`带旧角色class（可以保留非语义样式）。新故事要同时替换显示层，保留校验/导航/分支。

`tools/build_print.py`有大量硬编码剧情：原件请帖、伊都/澪/莲、REN便签、送景社/比赛、过站连接、纪念品文案，不是完全由JSON驱动。新版应将这些改为明确的双语内容源；生成器再渲染。原版13页结构：封面与委托、S01、S01B景片、S02、S02B河图及来源、S03、S04、S04B图卡、S05、终局表、回执景片、来源1、来源2。可增加纯叙事阅读页以容纳完整内容，但不能悄悄新增必解印刷件或密码。

原 `tools/render_guide.py`固定读取旧故事/机制/运营/QA/来源五份Markdown。新版本必须改成新版本入口文件，防止生成17页旧剧本。

建议隔离布局 `r6/`：以实际原附件机制和图形为底座，`content/`放双语新文本与冻结contract；`tools/`从该源生成 `play/data.*`、打印HTML和离线单页；`qa/`同时做机制语义不变和新文案无旧剧情残留检查。新版构建不得调用根旧版的refinement脚本。

## 6. 已配置的实际工具环境

Python依赖已装于任务临时目录：`runtime-python/`，Playwright 1.51.0、markdown-it-py 4.2.0。最新默认Playwright所请求Chromium下载归档损坏；固定版的微软备用镜像下载成功。浏览器：Chromium Headless Shell 134.0.6998.35，Playwright build1161。默认沙箱禁止启动浏览器，本轮经自动审批允许的提权命令执行，仅加载本地HTML。

复用环境变量：

```bash
PYTHONPATH=/workspace/scratch/dd7b8a58cbfe/runtime-python
CHROMIUM_PATH=/workspace/scratch/dd7b8a58cbfe/runtime-browsers/chromium_headless_shell-1161/chrome-linux/headless_shell
FONTCONFIG_FILE=/workspace/scratch/dd7b8a58cbfe/runtime-fonts/fonts.conf
```

中文渲染字体：Noto Sans CJK SC Regular，下载自Noto官方GitHub并仅放临时目录。Fontconfig临时配置已识别。**字体文件、浏览器二进制、依赖目录均不得提交公开GitHub或成品ZIP**。最终用户只运行HTML/PDF，不需要这些构建工具。

原脚本在 `set_content` 下报告本地保存不可用，属于about:blank来源限制；实际file URL测试已证明本浏览器文件来源存档可用，不能把二者混为同一结论。其他浏览器/手机Safari仍待目标设备测试。

## 7. 当前可复用资产与状态

实际附件原件、冻结机制合同、原图形函数、完整控制和验答引擎、原版PDF基线已经恢复。可以继续制作完整新故事产品，不能继续旧故事。状态为 **BASELINE_RECOVERED / SOFTWARE_BASELINE_REPRODUCED**；新故事未在本子任务中编写、未审阅、未自判合格。
