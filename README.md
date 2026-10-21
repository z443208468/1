# 东京五景点城市实景冒险

当前执行要求更新：2026-10-21。

**谜题要改。旧“不得修改已定谜题”的冻结要求已撤销，冻结文件已删除。** 谜题、玩家行动与人物事件从五处景点的背景特性共同设计；旧答案、道具、分支和终局字段不再是兼容约束。

本次用户只要求**设计档案、完整游戏剧本和设计好的游戏机制**，不编写程序或生成器。NovelForge负责故事剧情创作，现场材料由执行者核读并作为项目来源输入。

- [当前唯一执行交接](PROJECT_HANDOFF_FOR_NEXT_SESSION.md)
- [历史研究来源](research/00_SOURCE_REGISTER.md)
- [五处景点资料](research/01_FIVE_SITE_DOSSIERS.md)
- [现场证据对照](evidence/02_SITE_BY_SITE_CROSSCHECK.md)

R2—R5故事均不能当作当前获准故事。下列旧程序、机制及交付说明为历史档案，不是本次任务要求。

<details>
<summary>以下为历史R4与R3.1说明，仅供档案／机制恢复，不代表当前故事获准</summary>

# 东京五景点实景解谜：R4故事修订与R3.1机制基线

## 最新：只改故事的R4修订

2026-10-20。新稿《借景急便：首演取消之前》已完成研究、人物、全文、现场短版与兼容审查。

- [R4目录与研究说明](revisions/R4_story_20261020/README.md)
- [完整新故事](revisions/R4_story_20261020/story/01_FULL_STORY.md)
- [现场短版](revisions/R4_story_20261020/story/02_PLAYER_TEXT.md)
- [兼容审查与边界](revisions/R4_story_20261020/story/04_COMPATIBILITY_AUDIT.md)

历史R4曾按R3.1冻结机制；该要求已于2026-10-21被用户明确撤销，当前谜题必须重设计。**新故事尚未接入下方旧离线程序；未获游客盲测或商业发行通过。** 原故事、代码与历史研究保留。

## 以下为保留的R3.1基线说明

# 东京五景点实景解谜：研究档案与R3.1功能原型

当前项目：《借景急便：旧名收件人》/ SCENE EXPRESS。2026-10-20。
完整作者稿、五站规则、双语离线原型、可打印道具与软件检查已经交付；不是经过实际游客和商业许可验收的发行成品。

## 阅读入口
- `project/STATUS.md`：当前完成度与恢复入口。
- `design/01_R3_STORY.md`：完整故事、人物与暗线。
- `design/02_R3_MECHANICS.md`：五关题面规格、答案、提示与终局。
- `commercial/01_PRODUCT_AND_COSTS.md`：产品假设、成本公式、运营检查。
- `qa/02_R3_BENCHMARK_AND_LIMITS.md`：对标口径、已测试与未测试边界。
- `research/`、`evidence/`、`methods/`、`requirements/`：历次文献、实拍对照、设计理论、用户要求和已否决方案，全部保留。

## 从仓库源码构建
需要Python 3与Node.js。仓库存的是源码；不要在未构建时将缺少data.js的index.html当作完整发布包。

```sh
python tools/build_release.py
# 得到 R3_Offline.html、play/data.js、play/data.json、双语打印HTML
```

打开`R3_Offline.html`可离线试玩，打开`play/print.html`选择中/英文打印。构建过程中幂等应用第三关参考图等小修订，不联网、不读取用户原件。

PDF和完整浏览器复现另需Python依赖`playwright`、`markdown-it-py`以及Chromium：
```sh
python -m pip install playwright markdown-it-py
# 设置 CHROMIUM_PATH 为本机Chromium/Chrome可执行路径；默认/usr/bin/chromium
python tools/build_release.py --pdf
```

```sh
node qa/test_logic.js
python qa/test_browser.py
```

下载交付ZIP已带生成后的离线页、双语PDF和设计PDF，不需要安装以上依赖。代码执行结果与测试范围见qa报告。原测试环境禁止文件导航，采用精确离线HTML内容注入；不声称已部署网页或原生持久化验收。

## 不变约束
起点纽扣博物馆外部→两国桥→芭蕉免费区域→浜町公园→明治座外观；无新必去景点，不购额外场馆门票，不把明治座当获准使用的舞台。不采用第六颗纽扣旧案、日月拆字、公园编号密码、未证实的球纹机关。

## 公开范围
仓库为public；不发布原始路人图像、车牌、精确位置元数据、私人聊天或原视频，不附字体文件。研究为独立摘要与来源索引，不镜像第三方全文、付费题包或馆藏高清图。功能图为原创示意，不是官方测绘或历史原图。现实场馆没有为本产品提供合作授权。

</details>

