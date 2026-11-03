# 苍岐工作流交付清单

版本 2026-11-03，项目中转路径 `staging/cangqi-art-workflow/2026-11-03/`。本目录是供合入原项目的文档与工具集。入口见 [README](README.md)。

## 来源和界限

以同日提供的《苍岐现行工作流文档包》为底稿。ArtLab 基线 `dc28f8f`，AssetWorkflow 基线 `66047be`，Novel2Galgame 基线 `4147fe3`（含原快照中的本地改动），AVGStudio 为工作区快照。需求来自《美术审核剥离改造报告》和《非人物场景空间白模工作流设计报告》。试点场景、图片和试点的审图指令不作为正式生产资产。

美术作品只走角色定版、按场审核两次用户决策。演出步骤 2–5 与规则维护仍按原有独审办理。演出册的接口措辞、04／05 和工单模板、两个模型提示里的共同段已对齐。首次场所允许先登制作前置，机位实测后再做结构图。初始工具选择沿用 Three.js 与本地 Qwen-Image-Edit 2509，未设通用像素容差。不能证明的空间事实交演出按原设计修正，有技术告警的成图随场交用户裁定。

## 验证记录

- 本次按规则维护流程委派独立只读子代理复核正文与工具。复核者由空白上下文接收证据，未参与编写；宿主未另提供运行型号。
- 文档复核覆盖两本规则书、维护规则、工单模板、各目录入口、现行状态、Forge 技能说明和六份工作台提示。两个生成提示中的共同段与演出册正本逐字相符，四份非生成提示保持原样。既有用户审、作品登记、技术检查和演出独审分别核对。
- 空间工具在独立测试几何上实际运行两个天气／光照状态。每个状态得灰模、深度、法线、线稿、实体分色与俯视视锥图。遮挡测试区分可见、部分遮挡、全部遮挡和画外。跨状态叠图通过输入／输出指纹回读，替换同尺寸分色图和错误画幅会被拒绝。
- 审核包用 25 个合成情形实际验证，构建离线 HTML、总览、切换预览、对照证据与逐项回复清单。覆盖角色定版、只在 CG 出现的人物、空版本、进度包、首引场与无引用常见心境、同机位跨场、错误版本／叠图、退回重审，以及旧决定的继承范围。测试产物不登记到真实项目。
- 本包不能验证 Windows 上所有进程的实际写盘位置、资产服务是否硬编码旧审核标记、用户机上正在加载的 Qwen 2509 图谱及 Forge 连接。合入本地应用前按工具手册核实。院落三张背景、门和枣树的设计事实保留为现场待办，本次没有改写在用工单、生成正式图或替用户作视觉验收。


## 包内文件

下表列清单本身以外的 43 个文件。SHA-256 就是本包内容的指纹。

| 项目相对路径 | 相对输入快照 | 字节数 | SHA-256 |
| --- | --- | ---: | --- |
| `AVGStudio/AGENTS.md` | 沿用 | 1743 | `1ef319d11583a5f91c4f5bd184b90e24462ec9acc4eb9815f5852e257b1eb492` |
| `AVGStudio/CURRENT.md` | 修订 | 25663 | `08acf04bff3e016e0a27a31eaed0671b5c50c94b0fffafed1c21e652ac87a1db` |
| `AVGStudio/README.md` | 沿用 | 253 | `8fa9c9393bd6ca7f1171b0570a11e6b1c1533477f146c858bbe707e982aa4f6e` |
| `AVGStudio/agent.md` | 沿用 | 117 | `26f33c16e8e257b09b43ab8c9ead62168ae812a1454c43e254ecbaf26268c743` |
| `AVGStudio/templates/04-整场设计.md` | 修订 | 4231 | `51783fcd1cfacfcbf94b5fb3cd3c609196606928f84ed5ccea53a23cb3278079` |
| `AVGStudio/templates/05-登记交接.md` | 修订 | 3050 | `98b23dc5f30df9742e90af2f6b94c7d454ccd82f2cc43950da0108dedb0d97a6` |
| `AssetWorkflow/AGENTS.md` | 沿用 | 129 | `e096febc5d1d276b55e6d3027a02c7f4f215be04246ec7ecbb3b0994bcaa8010` |
| `AssetWorkflow/README.md` | 修订 | 1936 | `8c0fcc0d3300b55951a71e0c20e8c867197749aa5fdf342c390468905e51a31f` |
| `AssetWorkflow/templates/design-task.md` | 修订 | 2003 | `f4fa705bf9d82e8e6234596193b24f526c7daf049e1ff37490809130365aecfa` |
| `AssetWorkflow/templates/entity.json` | 沿用 | 144 | `f151fc8216a38203c250cf8bbe83bb04bfed6bba82a65752cc4b20ab75ae9d92` |
| `AssetWorkflow/templates/render-task.md` | 修订 | 2642 | `f879fce9757ebdb8c61b3967a1d3f25f61bc6e010aa2144286706ac468a3aef3` |
| `Cangqi-ArtLab/AGENTS.md` | 修订 | 1085 | `e6e0a8b56a31a0c931b42797daeda68d867a4920794aaa0337179bcd376f9c8a` |
| `Cangqi-ArtLab/CLAUDE.md` | 沿用 | 3983 | `d340e315f267c86443256c2a6d0fb7278881cf28f165b428301ddb4175e12d48` |
| `Cangqi-ArtLab/README.md` | 沿用 | 530 | `bf97e9f73a8a803bc725f3b82801ee48ec1af7d91f7312f7620bad2f1d19b934` |
| `Cangqi-ArtLab/README.zh-CN.md` | 沿用 | 530 | `bf97e9f73a8a803bc725f3b82801ee48ec1af7d91f7312f7620bad2f1d19b934` |
| `Cangqi-ArtLab/agent-sprite-forge/skills/codeart2d/SKILL.md` | 沿用 | 9848 | `6d00b1e35d29549e1772cb80737fb169f9483de739a7d7900dbf65c37da69ed8` |
| `Cangqi-ArtLab/agent-sprite-forge/skills/generate2dmap/SKILL.md` | 沿用 | 11789 | `b1d0b1842a2d8a22572b72e615b0ada9e3c624998274d8e41c6136e4496fd204` |
| `Cangqi-ArtLab/agent-sprite-forge/skills/generate2dmedia/SKILL.md` | 沿用 | 8604 | `26f8c9fef202c7bb25ddee1197f164b439aea3d32b815842bcc4ff2a2559ada2` |
| `Cangqi-ArtLab/agent-sprite-forge/skills/generate2dsprite/SKILL.md` | 沿用 | 14298 | `6449ff93a8ebd554ae9ed732f148a03ea6ebda62e3357db3d8479b52eadf6209` |
| `Cangqi-ArtLab/agent-sprite-forge/skills/video2dsprite/SKILL.md` | 沿用 | 15298 | `5c14c84df107ccb60553a36c2cf4a690aaaa13b85aa5280257e572a27ba52f92` |
| `Cangqi-ArtLab/config/build-art-review.py` | 新增 | 28870 | `66dd4f41d9d1880dae56aed42015033d3549a355d00ebfa6606f898951f1c69c` |
| `Cangqi-ArtLab/config/space-blockout/compare.py` | 新增 | 3863 | `9cc896a762c93f39c4f201819c0330fa25efabeb10eaef0101e0b1db6292fbc3` |
| `Cangqi-ArtLab/config/space-blockout/d_child.py` | 新增 | 1583 | `f849bb04378bb1472beaac640b9e14c1df04107c77a081f77cdfdb2957f1b352` |
| `Cangqi-ArtLab/config/space-blockout/package-lock.json` | 新增 | 1949 | `83a72f0a36674f21cbe7614f46243109460c8db0c53614faf9d70bc6eedfdcbd` |
| `Cangqi-ArtLab/config/space-blockout/package.json` | 新增 | 153 | `64648379dc8fa3224d204e5f18308d93f667bcf85c9695d4216a1e7d1ef6b1e8` |
| `Cangqi-ArtLab/config/space-blockout/passes.js` | 新增 | 10877 | `72a5629a5f5e28e01a722da9faa7f3ea5ce31fb6ce4e67ccafd8dba044e3efcf` |
| `Cangqi-ArtLab/config/space-blockout/render.mjs` | 新增 | 2879 | `7fa5d22bd4141dd9638f65d448bc73e91bd2736348be5cf45c44b2fd84b3c8c6` |
| `Cangqi-ArtLab/config/space-blockout/scene.template.json` | 新增 | 592 | `5a755290a0f810103ffeb73e1568f1282c583383cf7a8d6c61ab0cc0ecae84be` |
| `Cangqi-ArtLab/config/工具用法.md` | 修订 | 62434 | `6a005d7f32ba180287cb1ab98e871f89dfb3019ae0735c17355cecdf6e504ebf` |
| `Cangqi-ArtLab/docs/reference/VN美术资产管理_研究资料与生产模板.xlsx` | 沿用 | 44375 | `deefd8baf7c3314803c9578bc74c60106d04928e7015a397d0f75610c709914e` |
| `Cangqi-ArtLab/docs/苍岐演出与美术统一规则.md` | 修订 | 64898 | `273541d4cc483abe1ba9e4b3c4f960a77c39aade5f5e331d5f2128de3fe1def7` |
| `Cangqi-ArtLab/docs/苍岐美术生产规则.md` | 修订 | 40060 | `3a0c6a66626bf39ac6a4fe472d355dc0cd6cb109fbcb52badd372c7e80f8f4b6` |
| `Novel2Galgame/AGENTS.md` | 沿用 | 6494 | `8cdd6cbc5cbb114f48b7a30d6f7697e8fa19fc46521fdd8c6b16b61e337036dd` |
| `Novel2Galgame/CLAUDE.md` | 沿用 | 11884 | `112b78826b081874dddaf15accce504eb9426739dde79caafe5625a8d2b3ed79` |
| `Novel2Galgame/README.md` | 沿用 | 16716 | `48cdc73a55e9115df1b7adceec0ae33f52dfbd2bf4756396b3602dbbb6b3808c` |
| `Novel2Galgame/agent.md` | 沿用 | 605 | `36873049f5427d6c5bfee516d179fce792209649a2df27bdbd211ce09fe4ac25` |
| `Novel2Galgame/data/prompts/attribution.md` | 沿用 | 2354 | `6030532bc0dbd69c8b6cab0067790d18cda21e03ee62f80fc20878443fb84e7b` |
| `Novel2Galgame/data/prompts/fidelity-review.md` | 沿用 | 1665 | `c7c81f9ba0c3c08c1937516974df158143d4bd0f927197feeb1537e7e093283d` |
| `Novel2Galgame/data/prompts/narrative-parsing.md` | 沿用 | 1965 | `d4117ca11c572125673d0b6246ddd12a1bd8a34351735823d12e70bbffd93cbf` |
| `Novel2Galgame/data/prompts/scene-segmentation.md` | 沿用 | 1586 | `25801df65d30e6ca79004e3f532074552488a64e188f72da69f8b0d55d7a3bd3` |
| `Novel2Galgame/data/prompts/visual-prompt.md` | 修订 | 8500 | `47ccdcac0802578ae28f040e9bcdc70aafb119e4f9b5f1f018f82b38f3f1f70f` |
| `Novel2Galgame/data/prompts/vn-mapping.md` | 修订 | 10027 | `da2da01f0edd466924760d5d33e14009bcc406c6ce432580b13aeca88b510732` |
| `README.md` | 新增 | 2238 | `106bfbc8889091c5d33084d219f29e38b2b630f236c4804d12a27d595974a56d` |
