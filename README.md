# 东京五景点互动冒险｜R8《第二次失窃》

2026-10-21。当前制作版本为 **R8《第二次失窃》 / The Second Theft**，交付层级为**完整实验原型**：完整作者稿、五站规则、双语离线程序、双语打印源、原创纸件、运营说明、生成器和检查记录。

**Gate2 仍为 REJECTED。** S01 馆外输入对正常玩家行动的必要贡献、S04 现代取景操作对核心事件的必要贡献、S05 现场相对于随身沿革卡的贡献仍有具体反例。完整构建、软件检查通过不代表这些问题已解决，也不代表用户已认可新故事、真人盲测、实地游玩或商业许可已经通过。

## 当前入口

- [R8 源码、文档和构建说明](revisions/R8_second_theft_20261021/README.md)
- [R8 跨对话交接与有效合同](R8_HANDOFF_20261021.md)
- [本轮项目合同](revisions/R8_second_theft_20261021/design/00_PROJECT_CONTRACT.md)
- [完整作者稿](revisions/R8_second_theft_20261021/design/05_FULL_STORY.md)
- [谜题、行动和状态合同](revisions/R8_second_theft_20261021/design/03_M2_M3_SPEC.md)
- [制作、主持与验收指南](revisions/R8_second_theft_20261021/design/06_DELIVERY_GUIDE.md)
- [来源与现场证据](revisions/R8_second_theft_20261021/research/01_HISTORY_EVIDENCE.md)
- [路线、运营与预算假设](revisions/R8_second_theft_20261021/operations/01_ROUTE_OPERATIONS_COSTS.md)
- [新版工作流独立审查](revisions/R8_second_theft_20261021/qa/03_V3_WORKFLOW_INDEPENDENT_AUDIT.md)

R8 按本轮上传的 CNW Interactive Workflow 3.0 执行候选淘汰、独立人物推演、M2/M3 联合设计及有限返修。旧版本的具体剧情不作为当前剧情基线；新作品的实际状态以 R8 合同、源码、受测哈希和对应报告为准。审查中的历史失败记录保留原判，不会被新文件标题覆盖。

## 从源码生成 R8

Python 3.9+ 与 Node.js 18+ 可生成离线程序和打印 HTML，不需要读取用户原始照片或访问网络。

```sh
cd revisions/R8_second_theft_20261021
python source/build.py
node source/build_print.cjs
```

生成 `R8_Offline.html`、`play/index.html` 以及 `print/Player_ZH.html`、`print/Player_EN.html`、`print/Designer_Guide.html`。两个游戏 HTML 都可独立离线打开，内含文本、样式、图形和验答；无需账户、外部脚本、字体下载或运行服务器。

```sh
node source/test_engine.js
python source/check_traceability_v3.py design/04_TRACEABILITY.json --level prototype
```

PDF 渲染及真实浏览器检查还需要本机可调用的 Playwright、Chromium 和支持中文的系统字体。依赖、命令与检查范围见 [R8 构建说明](revisions/R8_second_theft_20261021/README.md)。正式 PDF、ZIP、浏览器和字体二进制不纳入这份源码目录；综合交付包与源码构建结果分别核对，不把仅有文档当作可玩软件。

## 关键运行规则

- 路线为纽扣博物馆外公共街角 → 两国桥 → 免费芭蕉史迹展望庭园 → 浜町公园 → 明治座外公共步道，没有第六必经点，也不要求入场、真实寄送或场馆人员扮演角色。
- 全部现代人物、通信、物件交接与 D-17 记录均属原创虚构；历史来源只能证明相应历史与空间关系。
- 玩家从开场可联系三人、索取原记录、拒绝转交、提前结束或凭充分证据提前解案。五站完成数和可选年代题不会锁住核心处置。
- 实地模式默认隐藏备用答案；桌面、备用、含答案的资料与提示有永久来源记录，不能被模式切换伪装为实地验证。
- 公开时机与处置方式是独立选择；角色已获知的信息和已经完成的物件归还不会因修改试题草稿而倒回。

## 验证怎样读

`qa/` 内报告分别声明对象、范围和版本，历史报告只证明当时实际测试的快照。状态检查、浏览器操作和版面检查不等同吸引力、现场必要性或游客体验验证。真人盲测、现场实走、实际纸件裁切持握和商业授权没有执行记录时，继续保留 `NOT_RUN` 或相应未授权状态。

有具体反例的设计门记 `REJECTED`；只有缺少必要证据或权限时才用 `BLOCKED`。`site_binding=required` 保持有效，不通过降低要求修改评级。

## 历史版本与恢复资料

以下文件继续保留，均不是当前新故事：

- [2026-10-20 历史交接](PROJECT_HANDOFF_FOR_NEXT_SESSION.md)：解释 R2—R5 的失败与 R3.1 产品类别。其旧“具体字段全部冻结”口径已被本轮重新核对机制的授权及 R8 合同更新。
- [R5 历史优先重构存档](revisions/R5_history_first_20261020/README.md)：剧情已被否决，不称为当前版本。
- [R4 故事修订存档](revisions/R4_story_20261020/README.md)：剧情已被否决。
- 根目录 `play/`、`tools/`、旧 `design/`：R3.1 的历史程序、生成器和研究。根目录的 `python tools/build_release.py` 生成旧 R3.1，不会生成 R8；不得用其成功结果替代 R8 的检查。

## 公开范围

不提交用户原始照片、视频、路人或车牌影像、定位元数据、私人对话、截图、字体与浏览器二进制。公开内容为原创程序/示意图、文字研究摘要、资料索引和有范围的检查记录，不镜像第三方全文或付费题包。任何现实场馆的开放都不自动构成商业合作授权。
