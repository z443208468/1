# 请别替我签收 / Before You Sign

R7 · 东京五处真实地点的现实悬疑冒险 · 完整可玩原型

三张景片、一只纸框，一份写着“1930”的制作稿。你答应协助复原东京旧景，却发现自己的正确操作被剪成一份交付见证。摄影助理绫说：“请别替我签收。我拿走的不是他们丢的东西。”

在纽扣博物馆外、两国桥、芭蕉免费庭园、浜町公园、明治座外，接景、校图、拆开两条时间线、找到取景端，再把旧名字放回其沿革。最后用开头同一套纸件，把影像省掉的一段动作做回来。

## 立即游玩

1. 下载本目录完整ZIP并解压，或直接下载 `R7_Offline.html`。
2. 用支持JavaScript的浏览器打开离线HTML。无需安装、账号、GPS或网络；设备预览器若不执行脚本，请用浏览器打开。
3. 选择中文或English。桌面模式使用内置原创示意；现场模式按合法公共通道观察，不以题图导航。
4. 需要纯纸版时，打印 `output/pdf/R7_Player_Kit_ZH.pdf` 或 `R7_Player_Kit_EN.pdf`。A4、单面、100%；只打印一种语言。按前部索引裁原活动件，纪念片留到终章。

提示免费，辅助不减结局。正确早解直接接受；独立/交换校准与分别/共同落款为两次独立选择，四种组合都得到完整真相和奖励。浏览器本地保存，跨设备可导出/导入。

## 文件入口

|用途|文件|
|---|---|
|单文件离线游戏|R7_Offline.html|
|中文/英文玩家PDF|output/pdf/R7_Player_Kit_ZH.pdf；R7_Player_Kit_EN.pdf|
|设计指南PDF（含剧透）|output/pdf/R7_Designer_Guide.pdf|
|可直接打印HTML|play/print_zh.html；play/print_en.html|
|完整中文作者稿|design/01_FULL_STORY.md|
|五站合同、主持、运营、机制边界|design/02—05开头的文档|
|完整双语正文、对白、提示和答案|content/game.json|
|原机制冻结合同|content/mechanics_contract.json|
|研究、淘汰候选、独立结构复查、恢复记录|research/|
|实际机器日志、截图、PDF审阅记录|qa/|
|生成器与打包器|tools/|
|交付ZIP及解压验证|release/|

设计指南与研究含完整剧透。玩家包中的后半部也含自助核对答案与六幕结尾，准备时按说明遮住，不必预读。所有提示和答案开放可取，没有以藏信息充当难度。

## 路线和适用范围

固定路线：纽扣博物馆外公共街角 → 两国桥 → 芭蕉庵史迹展望庭园免费区域 → 浜町公园开放公共通道 → 明治座外公共步道。没有第六必经点，不进真实剧场或体育中心交件，不要求工作人员配合。

2—4人是小组假设，单人可玩。全程140—190分钟是设计预算，未进行现场计时。庭园限时，公园部分区域施工；资料核验日2026-10-21，出行当日仍应复核。正式开放信息与成本假设见运营文档。

人物、案情、制作审阅台和收据均为原创虚构，页面不会给真实机构发消息。地点史实有来源；题图与分镜是原创示意，不是实况录像或历史照片。

## 开发与复现

从本目录运行。需要Node、Python、本地Chromium、中文字体和 requirements-build.txt 所列包；这是生成/测试依赖，游玩无需安装。

```sh
python3 -m pip install -r requirements-build.txt
python3 -m playwright install chromium
node tools/build_runtime.mjs
python3 tools/build_print.py
python3 qa/audit_content.py
node qa/verify_mechanics.mjs
node qa/test_logic.mjs
python3 qa/test_runtime.py
python3 qa/test_narrative.py
python3 tools/build_guide.py
python3 tools/render_pdfs.py --skip-build
```

也可 `python3 tools/build_release.py --pdf --browser-test`。已有Chromium时设置 `CHROMIUM_PATH`；已有字体配置时设置 `FONTCONFIG_FILE`。先确认依赖版本与当前环境；仓库不附字体文件。

改文案只改 `content/game.json`，再生成程序与纸包。最终PDF有变化必须重新生成全部对应页图并实际查看，更新 `qa/PDF_VISUAL_REVIEW.json`，然后运行：

```sh
python3 tools/package_release.py
```

打包器拒绝旧报告、缺失文件与过期PDF证明，并实际解压核对每项SHA。不能用自动生成的空审阅记录冒充人眼检查。

## 状态和继承

这是可运行、可打印、可供目标游客测试的完整原型。实际技术结果以本包QA日志为准。人类盲测、实体裁切、东京复走和商业运营确认尚未执行；不把理论、AI审查或测试数量称作故事趣味认证。

原R3.1的五套机制、卡片类别、答案、提示、辅助、分支和早解保留。R2—R6被拒故事不继承；旧文件与已恢复R6包保留在仓库历史目录。新作品位于独立分支 `delivery/r7-tokyo-20261021`，没有覆盖原分支。恢复记录明确区分实际取回的104文件R6包和未找到的122文件维护包。
