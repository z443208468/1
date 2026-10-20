# 借景怪盗：消失的隅田川 / The River Thief

**R6.0-review：完整设计与可运行、可打印的审阅原型。** 这不是R2—R5的续写；旧代码、史料和否决记录保留在仓库。独立提纲审查只允许本案进入完整原型，未声称用户已接受、游客觉得好玩、实地验证完成或商业可售。

## 先玩，再读作者稿

1. 下载完整ZIP并解压。直接打开根目录的 **`R6_Offline.html`**，选择中文或English。无需服务器、账号或联网。
2. 第一次审阅可选“桌面试玩”，使用题包图示与随身史料；不要将它记录为现场观察。想直接审结局，可在终局使用“辅助结案”，全部六幕和奖励不减少。
3. 纸面试玩每组只需一种语言：`output/pdf/R6_Player_Kit_ZH.pdf`或`R6_Player_Kit_EN.pdf`。A4单面、100%，先按题包索引裁好原件，再出发；不需要双面精密套印。
4. 完整作者稿、物料规格和主持词在`output/pdf/R6_Designer_Guide.pdf`及`design/`。玩家包本身带免费提示、核对答案和完整纸面结尾，能独立于手机使用。

**故事开场：**你们本该收下旅行影戏的最后一幅河景，怪盗空舟却把它“借走”。他留下稲瀬川与千歳座两个名字，并要求把后来出现的东西裁出画框。五站之后，让他用同一张遮片再退一次——这回，让河与搬景的人都留在画面里。

## 五站与玩家行动

|地点|操作|本场发生的变化|
|---|---|---|
|纽扣博物馆外街角|复原三卡，保留遮挡，拼回原三条景|汐不再丢弃被挡住的一片；恢复同一条河|
|两国桥|旋转/翻面河图，分列舞台名和真实地名|保留稲瀬川与隅田川，不让舞台名替换源景|
|芭蕉免费展望庭园|分开1680人物史与1995设施史，判断下界|撤掉1930原始摄影的背书，保留现代参照|
|浜町公园|比较既有年代记录，再校准现代图与取景端|驳回古公园清场理由，保留近景和背景|
|明治座外|四名沿革排序、1928迁址另列|补全开场题签的当代归属，回到同一影戏完整收场|

人物与劫案发生在原创影戏中。真实场馆没有被写成合作方，画面不声称直播，也不声称从公园某一机位拍到了剧院。没有现场NPC、藏点、扫码贴纸、入场任务或真实财物移交。

## 文件导航

|文件/目录|内容|
|---|---|
|`R6_Offline.html`|完整自包含离线游戏，含两语言、前后画面、六幕演出、保存/导入导出、回执|
|`content/game.json`|唯一玩家文字与题目数据源，正式中文和英文短文本、史料、提示、四组合与结局|
|`play/`|网页源文件、原机制引擎与原谜题SVG、原创演出绘制、打印HTML和指南HTML|
|`output/pdf/`|两套实际渲染玩家PDF与完整设计指南PDF|
|`design/01…05`|完整剧本、真相与曝光表、五关合同、主持和纸结尾、运营成本、机制保留与风险|
|`research/`|创作前论文研究、史料、已淘汰A/B/C、D退修与独立复核、基线恢复|
|`qa/`|真实软件结果、内容核验、打印结果、视觉检查、尚未执行的人类/实地测试表|
|`tools/`|离线构建、纸包/指南生成、PDF渲染、发布包生成|
|`MANIFEST.sha256`|发布包文件哈希；用于检验下载/解压完整性|

制作与判定规则：修改`content/game.json`再构建，不直接编辑生成的`play/data.json`、`play/data.js`或离线HTML。构建不会调用旧R3故事生成器，也不会在新版源缺失时借用旧剧情。

## 保存的机制

五组答案和七项终局全部保持R3.1原附件合同。原`engine.js`和`figures.js`字节不变。每关三级免费提示；辅助有记录而无结尾扣减。challenge/share只影响第一次打开S04的校准；solo/joint是独立落款选择；四组合都有完整真相和同一纪念景。正确早解无须逐关盖章。

纸件仍为原三视图、横向景条和框、双面河图/标签、双时间轨、公园两面图/相机/用途片、四名称条/1928条、回执与双面纪念片。新阅读页不是新谜题组件。场景演出不会增加验答字段或隐藏通关条件。

## 重建

预生成的离线页和PDF可直接使用，不必安装工具。开发重建使用Node.js和Python；本轮实际环境是Node 24.19.0、Python 3.12.14，依赖版本见`requirements-build.txt`。PDF需本机Chromium及支持中文的系统字体；字体文件不随包分发。

在本R6目录执行：

```bash
python3 tools/build_release.py
```

这会从源数据重建离线页、打印HTML、指南HTML，检查机制与内容，并运行离散逻辑枚举。若缺少设计章节，指南构建会明确失败。

```bash
python3 -m pip install -r requirements-build.txt
python3 -m playwright install chromium
python3 tools/build_release.py --browser-test --pdf
python3 qa/test_caper.py
```

本机若需指定浏览器可设置`CHROMIUM_PATH`；需自定义字体配置时使用`FONTCONFIG_FILE`。不要提交本地浏览器、Python依赖目录、字体文件或私人实拍原件。PDF渲染器生成全部页面PNG与联系表，输出在`output/qa/`；这些可复建的大图不必进入精简发布ZIP。

完成最终数字目视后，将10张最终联系表保留于`qa/pdf_contacts/`，在`qa/PDF_VISUAL_REVIEW.json`记录实际检查与最终PDF哈希，再运行：

```bash
python3 tools/package_release.py
```

脚本生成`MANIFEST.sha256`和`release/`中的完整ZIP、ZIP校验和与实际解压核验报告。它不会自动替你宣布目视完成；若PDF或正式数据已经变化，应重新执行相关检查并更新真实记录。

## 验证的边界

实际测试使用本地`file://`并强制浏览器离线，覆盖全部关卡、四组合、正确早解、提示/辅助、保存和导入导出、手机窄屏、减少动画偏好及六幕重看。报告绑定当前内容与网页哈希。PDF记录覆盖自动排版与数字页面目视；没有声称把本包送去实体印刷和裁切。

**真实游客盲测、现场复走、团体时长、商业许可与市场定价验证均未执行。** 开场是否有持续悬念、S04清场是否自然、角色是否有吸引力和结尾是否打动人，仍是实际体验要回答的问题。相关空表是NOT_RUN记录，不能当作完成测试。

## English quick start

Unzip the complete release and open `R6_Offline.html` directly. Select English. The game works without a server or internet connection. Use Desktop mode for a review at home; do not mark it as an on-site observation. All chapters and the finale remain available from the start, with free hints and assistance.

Print one English player kit per team at A4, 100%, single-sided. Follow the page index and prepare the original pieces before walking. The kit includes every clue, all three hints per stop, answer checks, independent choice outcomes and the complete paper ending. The separate designer guide contains spoilers.

Follow the fixed five-stop route only within permitted public areas. The Basho garden has opening hours and closed days. There is no museum, sports-centre or theatre entry requirement, no real suspect to find and no venue employee playing a character. The picture show is fictional; illustrations are not live site footage. This release is a complete review prototype, not evidence of visitor, field or commercial validation.
