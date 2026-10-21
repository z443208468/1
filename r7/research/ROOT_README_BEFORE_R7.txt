# 东京五景点城市实景悬疑冒险｜R6完整审阅版

## 先读正式交接

接手项目请先完整阅读 [PROJECT_HANDOFF_FOR_NEXT_SESSION.md](PROJECT_HANDOFF_FOR_NEXT_SESSION.md)。其中的来源权威顺序、历史资料与冻结机制仍有效。**R2、R3、R3.1、R4、R5故事均已被用户否决，不能续写或换名重用。** 旧源代码、史料、实拍研究及历次文件全部保留。

## 当前交付：《借景怪盗：消失的隅田川》 / The River Thief

版本：**R6.0-review**，2026-10-20。制作位于独立分支 `story/r6-history-adventure-20261020`，未覆盖旧游戏。完整双语玩家内容已接入新离线程序，并生成实际玩家PDF与设计指南。

- [完整交付ZIP](r6/release/Tokyo_Five_Sites_R6_Review_20261020.zip)（下载并解压）
- [离线试玩HTML](r6/R6_Offline.html)（下载文件后直接打开）
- [中文玩家题包，30页](r6/output/pdf/R6_Player_Kit_ZH.pdf)
- [English player kit, 30 pages](r6/output/pdf/R6_Player_Kit_EN.pdf)
- [完整设计指南](r6/output/pdf/R6_Designer_Guide.pdf)
- [R6使用方法、构建命令与文件导航](r6/README.md)

游客带着同一幅未完成的河景，沿纽扣博物馆外街角、两国桥、芭蕉免费展望庭园、浜町公园、明治座外的固定路线，拆解一个旅行影戏怪盗的退场。五站的操作逐步改变构图、题签、摄影年代的解释与取景方案；终局在同一景框里完成完整退场。

## 可复核的制作与验证

- [创作前论文与叙事研究](r6/research/00_NARRATIVE_RESEARCH.md)
- [历史来源与因果边界](r6/research/01_HISTORY_AND_CAUSALITY.md)
- [候选、否决与独立复核入口](r6/research/README.md)
- [完整剧本、人物行动与真相时间线](r6/design/01_STORY_AND_TRUTH.md)
- [五关机制与故事合同](r6/design/02_FIVE_STAGE_CONTRACTS.md)
- [主持与完整纸面结尾](r6/design/03_HOST_AND_PAPER_ENDING.md)
- [运营、路线与成本假设](r6/design/04_OPERATIONS_AND_COSTS.md)
- [保留机制、变更边界与剩余体验风险](r6/design/05_MECHANICS_PRESERVATION_AND_LIMITS.md)
- [实际测试范围与未执行事项](r6/qa/RELEASE_REVIEW.md)
- [发布包解压校验](r6/release/package_validation.json)

原机制引擎与原题图保持字节一致，五关答案、终局七项、免费提示、辅助、早解与四种选择组合保留。正式R6内容已执行29项逻辑检查、445种组合枚举、72项离线浏览器检查和49项画面检查；另有71项静态内容核验。逐项证据保存在 `r6/qa/`，这些不是故事质量评分。

**当前状态是完整、可运行、可打印、可测试的审阅产品。** 独立提纲审查仅同意进入完整制作，没有替用户宣布故事好玩或感人。真实游客盲测、东京现场复走、实体打印裁切与商业使用确认尚未执行，记录明确标为 `NOT_RUN`。

## 历史档案

原69个跟踪文件中，除本入口说明外均保留原字节；此前根README另存于 [ROOT_README_BEFORE_R6.md](revisions/R5_history_first_20261020/ROOT_README_BEFORE_R6.md)。旧目录中的“当前”“最新”等字样是历史记录，不覆盖正式交接对R2—R5故事的否决。

本仓库是公开项目。不附私人实拍原件、付费题包、第三方全文或字体文件；示意图不冒充历史原图或现场测绘。现实场馆没有被写成合作方。
