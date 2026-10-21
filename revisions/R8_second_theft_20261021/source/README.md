# R8 离线程序的构建与验证

## 可运行交付

`python source/build.py` 在发布目录根部执行（或在任意目录调用该脚本的路径）会生成 `R8_Offline.html`、相同内容的 `play/index.html`，并复制 `play/content.json`。游戏直接通过 `file://` 打开；没有运行时服务器、外部脚本、外部字体、登录或自动网络请求。史料链接仅由使用者主动打开。构建依赖 Python 3 标准库。

运行时文本与插图分别来自 `content.json` 和 `figures.js`；应用、状态与样式分别来自 `app.js`、`engine.js`、`style.css`。所有内容被嵌入单个 HTML，JSON 的 `<` 被安全转义。

## 状态合同

- 五站可以自由查看；核心案不以五站完成数或年代题为门槛。L、D、D-17 可从开场索取。
- `checkCase` 只接受 B 对同次 D-17、归还主张对 L+D，以及历史题材不证明物件年代/归属的结论。A 的年代反证独立显示为已核或未核。
- `disclosure` 与 `resolution` 独立。公开之后，角色知识不能撤回；从 `REQUEST_FRONT` 变成 `REQUEST_CONTINUOUS`，结算后是 `SALE_WITHDRAWN`。
- `completion` 保存已实际执行的处置快照。后续试题练习可以使当前答题草稿变为未验，但不能让已归还的真景芯和外框退回原持有人，也不能抹掉已完成的归还。
- 拒绝转交、暂停、早停、充分证据提前解案都是可执行动作。看作者真相不会变成检验通过。
- 重演先保管真景芯，再入演示圆片、形成正面遮挡、打开旁视。只有选择分支而未操作图件不能完成重演。
- 现场备用、桌面资料、第二级以上提示、完整辅助与资料查看均会保留证据取得方式。改回实地模式不清除记录。

`window.R8Engine` 与 CommonJS 导出 `initial / act / checkStage / checkCase / replayReady / world / sourceDateVerified / exportSave / importSave / restore`。`act` 不修改传入对象，返回 `{state,result}`。

## 存档边界

存档格式为 `TOKYO_CNW_R8_SAVE`、schema 1、程序 R8.1。导入限制大小并严格验证字段、枚举、答题结果、原记录、重演先后约束和完成账本的一致性；陌生字段、凭空追加 completed/fieldVerified 或矛盾的完成历史会被拒绝。合法完成记录可以重新导入并保留既有处置。导入文件是使用者提供的游戏进度，不具备签名认证，不能证明真实到场、真人操作或现实取证，界面从不作此认证。

localStorage 不可用时，当前页继续运行并显示提示，使用者可手动导出 JSON。清除浏览器数据或关闭未保存的私密窗口可能丢失进度；导出按钮始终可用。

## 原创图件 API

`window.R8Figures` 与 CommonJS 导出相同的纯渲染函数。除 `d17()`、`sourceChain()` 返回组合 HTML 外，其余为独立 SVG 字符串：

- `icon(name)`：塔楼、高架、柳枝、原画、模写、铜像、现场照。
- `layer({order})`：按真实绘制层序重排的 S01 示意。
- `river(draft)`：无字河网，`mainBridge/branchBridge/mouthBridge` 改变实际桥条；`riverReference()` 是仅供桌面/备用的对应关系。
- `memorial()`：无解答箭头与年代的识别示意；`sourceChain()` 是备用用的完整来源链，不能默认用于实地题面。
- `park({rotation,mirror})`：320×320 无字空间图；`facade()` 为匿名取景局部。
- `replay({mask,view,insert})`、`perspective({mask})`：320×180 几何。圆心(160,90)、半径16；遮片宽48、高84，遮住时左上(136,48)。旁视将同一底板、圆片、缺口、折痕作统一仿射投影，不删除圆片。
- `d17()`：六帧同次虚构演示图，00:00 开、00:01 进入、00:02 遮住、00:03 退出、00:04 再显、00:05 同次分层旁视。每帧保留同一圆片、缺口、折痕。其编号不单独证明身份。
- `scene()`：原创纪念场景，非历史复制品。

## 软件检查

从发布目录运行：

```sh
node source/test_engine.js
python source/build.py
CHROMIUM_PATH=/path/to/chrome-headless-shell node source/test_browser.cjs
```

引擎检查只需 Node.js。实际浏览器检查还需 Node 的 `playwright` 与可启动的 Chromium；受限容器可能需要允许启动本地浏览器进程。CJK 截图使用操作系统可用的中文字体，可通过 `FONTCONFIG_FILE` 指向本地安装；不将下载的浏览器或字体打包到游戏中。

结果写在 `qa/logic_results.json`、`qa/browser_results.json`、`qa/software_build.json` 和 `qa/screenshots/`。软件检查覆盖四种组合、直接早解、原记录、草稿失效、不可逆完成、存档拒绝、语言切换、移动端溢出及存储失败降级。它们不是游客盲测、现场可读性验证或娱乐性证明。

## 已知流程边界

这是完整实验原型。Gate2 仍为 REJECTED：S01 馆外输入对正常玩家行动的必要贡献不足，S04 以现代空间关系为主，S05 主要依赖随身沿革卡。这些反例没有被软件自动测试消除。交付时必须保留相关说明与后续验证要求。


## 印刷构建与版面复核

从发布目录运行以下命令，生成自包含 HTML 和三份 A4 PDF。`build_print.cjs` 只需 Node.js；`render_print.cjs` 需要可被 `require('playwright')` 找到的 Playwright、可启动的 Chromium，以及含中文和日文汉字的本地字体。依赖与浏览器、字体不随作品打包。

```sh
node source/build_print.cjs
CHROMIUM_PATH=/path/to/chromium node source/render_print.cjs
```

默认正式输出为 `print/`。`--draft` 生成带 DRAFT 标记的试排稿，默认写入发布目录内 `qa_work/print_draft/`；环境变量 `R8_PRINT_OUT` 可以为两个脚本指定其他输出目录。两次调用须使用同一目录。例如，将试排中间件保存在另一个工作目录：

```sh
R8_PRINT_OUT=/absolute/work/print_draft node source/build_print.cjs --draft
R8_PRINT_OUT=/absolute/work/print_draft CHROMIUM_PATH=/path/to/chromium node source/render_print.cjs --draft
```

`FONTCONFIG_FILE` 可按本机环境指定字体配置。渲染器等待字体和指南分页完成，检查每页 A4 高度、内容区、纵横溢出与页脚碰撞，输出 `print_geometry.json`；正式模式发现溢出即停止。设计指南从 `design/05_FULL_STORY.md` 与 `design/06_DELIVERY_GUIDE.md` 生成，正文与表格按整块分页。玩家包使用当前 `content.json` 与 `figures.js`。

PDF 生成后还须实际栅格化并逐页目视检查；几何报告不能替代看图。例如：

```sh
mkdir -p /absolute/work/print_pages
pdftoppm -scale-to 1500 -png print/Player_ZH.pdf /absolute/work/print_pages/zh
pdftoppm -scale-to 1500 -png print/Player_EN.pdf /absolute/work/print_pages/en
pdftoppm -scale-to 1500 -png print/Designer_Guide.pdf /absolute/work/print_pages/guide
```

栅格页、接触表和浏览器环境只作工作证据，不加入发布附件。正式打印选择 A4 单面、100% 原尺寸；每包的 50 mm 校准尺用于发现打印机缩放。底板、遮片与标记的几何验证不等于真实裁切、风中持握或游客现场操作已经通过。

## 全新解包检查

`test_cold_start.cjs` 接受一个已解包的发布根目录和输出JSON路径，以全新Chromium上下文实际打开独立文件并操作；不读取作者浏览器缓存。

```sh
CHROMIUM_PATH=/path/to/chromium node source/test_cold_start.cjs /path/to/extracted/Tokyo_CNW_R8 /tmp/r8-cold-start.json
```

该检查通过正式控件进行拒交、早解和归还，记录组件SHA。最终包清单应在所有源件和报告冻结后更新，不把旧报告标成新版本重新跑过。
