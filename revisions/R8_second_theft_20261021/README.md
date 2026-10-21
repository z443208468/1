# R8《第二次失窃》｜可复现源码与制作档案

本目录对应 2026-10-21 的 R8 完整实验原型。故事与交互程序已合流；本目录存放可复现源码和文字证据，生成的游戏 HTML、打印 HTML/PDF、ZIP、截图与开发依赖不提交到版本库。

**Gate2 = REJECTED，site_binding = required。** 具体实景依赖反例继续有效；R8 不等于用户已认可、真人盲测通过、现场实测通过或商业可发行。完整产品类别与设计门通过分别记录。

## 阅读顺序

1. `design/00_PROJECT_CONTRACT.md`：有效用户指令、更新后的机制边界和交付层级。
2. `design/01_M1_INDEPENDENT_CANDIDATES.md` 与 `design/02_SELECTED_EVENT.md`：候选、淘汰及阶段性选案。阶段旧稿不覆盖最终规则。
3. `design/03_M2_M3_SPEC.md`、`design/04_TRACEABILITY.json`：行动、图件、谜题和证据的关联。
4. `design/05_FULL_STORY.md`、`design/06_DELIVERY_GUIDE.md`：完整作者稿和主持制作指南。
5. `source/content.json`、`engine.js`、`app.js`、`figures.js`：实际运行的单一内容与状态实现。
6. `qa/`：按报告的受审哈希阅读独立审查、原始失败与定点复测，不能只读 PASS 数。

`design/characters/*_v2.md` 为修订人物关系；对应无 v2 后缀文件保留初版过程。真实史料和像素观察的证据边界在 `research/`，运营条件和预算假设在 `operations/`。

## 生成离线游戏与打印源

以下命令均从本版本目录运行；脚本本身以各自所在目录定位源码，不依赖仓库克隆到特定机器路径。

```sh
python source/build.py
node source/build_print.cjs
```

Python 使用标准库；打印 HTML 生成器使用 Node.js 标准库。输出：

|输出|用途|
|---|---|
|`R8_Offline.html`、`play/index.html`|两个字节一致的独立离线入口|
|`play/content.json`|构建时使用的双语数据副本|
|`print/Player_ZH.html`、`print/Player_EN.html`|双语玩家题包和可打印纸件|
|`print/Designer_Guide.html`|完整作者稿与设计/运营说明|
|`qa/software_build.json`|生成程序的哈希、大小和来源清单|

离线游戏不需要 Node、Python、浏览器扩展、登录或网络服务器。开发工具只用于生成和验证。无中文字体的设备可能使用其系统回退字体；正式打印应先检查中文显示与 50mm 比例尺。

## 软件、追踪与浏览器检查

```sh
node source/test_engine.js
python source/check_traceability_v3.py design/04_TRACEABILITY.json --level prototype
```

真实浏览器检查和 PDF 输出需要 Node 的 `playwright` 包、本机 Chromium/Chrome 可执行文件及中文系统字体。`CHROMIUM_PATH` 应设为使用者本机路径；没有设置时由 Playwright 选择其已安装浏览器。源码不捆绑这些依赖。

```sh
CHROMIUM_PATH=/path/to/chromium node source/test_browser.cjs
CHROMIUM_PATH=/path/to/chromium REVIEW_SCREENSHOT_DIR=./qa_work/final_independent_review node qa/final_independent_probe.cjs
CHROMIUM_PATH=/path/to/chromium node source/render_print.cjs
```

`render_print.cjs` 读取已生成的打印 HTML，输出三份 PDF 及 `print/print_geometry.json`。它检查内容框、页脚与水平溢出，无法代替逐页目视与真实裁切。只需复现默认正式输出时不使用 `--draft`。临时目录的迁移注意事项见 `qa/REPOSITORY_PREPARATION.md`。

若交付包包含最终 manifest，可在对应完整包根目录运行：

```sh
python source/validate_delivery.py delivery_manifest.json --root .
```

manifest 的实际文件名以最终包为准；源代码目录没有 PDF/ZIP 等派生物，不能拿完整交付包的 manifest 对这个仅源码目录作全文件通过声明。

## 数据、图件和存档维护

`source/README.md` 列出引擎与纯图形 API。所有修改先进入源码，再重建；不要只改输出 HTML/PDF。D-17 是固定六帧原演示示意；玩家重演是另一项操作。A 的年代结论与核心取物结论独立。完成账本保留已执行处置，新的试题草稿只能改变当前答题验证状态。

本地保存不可用时软件继续运行并提示导出 JSON。导入会校验格式、枚举与因果一致性，但不签名认证真实经历；没有任何导入会被称为真实到场证明。

## 仓库快照与最终同步

`qa/repository_source_snapshot.json` 记录本次源码复制的逐文件哈希，性质为仓库准备快照，**不是最终发行签章**。印刷源与最终审查可能随后同步，最终受测版本以对应报告的 artifact/source hash 和最终交付清单为准。旧失败报告保留原始版本与定位，不倒写成已修复时的评语。

`qa/REPOSITORY_PREPARATION.md` 记录迁移路径检查、未包含项和根代理最终同步事项。源码整理未执行 git commit 或 push。

## 最终合流与综合包清单

最终软件为 122581 字节，SHA-256 `2ae06c03275df27323377c92b07592aa31e7f8c13504f31abb087300c8f9a646`。主体独审35项与最终S03增量9项分别记录；新解包17项也已运行。中文/英文玩家PDF各21页、设计指南10页，共52页已实际渲染检查，PDF在综合交付ZIP，不进入本源码提交。

完整验收见 `qa/05_ACCEPTANCE_STATUS.md`，M1家族索引见 `design/01b_M1_EVENT_COMPARISON.md`。其中指向成品根 `PROJECT_MANIFEST.json` 的说明对应综合ZIP；其原样快照在 `qa/FULL_DELIVERY_MANIFEST.json`。此快照不能用本源码目录作为根来宣称通过，因为这里刻意不分发生成PDF/HTML。源码文件单独由 `SOURCE_MANIFEST.json` 记录。

两个印刷脚本的临时目录已改为版本根内 `qa_work/print_draft`，或通过 `R8_PRINT_OUT` 指定；独审脚本默认写系统临时截图目录及 `.rerun.json`，不覆盖历史记录。无须依赖本轮工作区绝对路径。
