# P1-A：基线、保留范围与读取记录

本阶段在流程提交fb143ee之后进行，尚未撰写完整新故事。日期2026-10-20。

## 1. 保留与废止

保留：research/、evidence/、methods/全部原研究，五处实景及其限制，用户R3.1附件中的五关操作、题图、选项、正确答案、提示和两处独立分支。原始照片/视频不公开上传。

废止：所有旧故事的现行创作地位，包括旧比赛、送景社、原角色关系、家庭首演。旧文本留存仅为版本与否决记录，不再当作选题、人物或情节素材。新的角色和异常必须由02—04文档的历史关系推导。

## 2. 本轮实际取得什么

- GitHub实际读取分支1，起点cc48a94；流程提交后读取fb143ee对应的Git对象。
- 重新读取research/01_FIVE_SITE_DOSSIERS.md。此前完整历史目录、实拍对照和R4研究内容已在本对话提供，引用时区分旧记录与本轮重开来源。
- 在容器实际检查本轮上传Tokyo_Scene_Express_R3_1(1).zip：34个非目录文件，ZIP SHA256为570fdfb2b52f037978e3113f101f3ad6034a3b6219914968ee107aee71903144。
- 读取附件design/02_R3_MECHANICS.md和play/data.json，提取五关字段/选项/答案与finalAnswer为本地mechanics_lock.json。没有重写原件。
- 当前只挂载上述ZIP，未取得旧原JPEG/MP4；不声称本轮重看44份实拍。空间依据沿用既有实拍报告和附件自制示意，不从新网页猜现场像素。
- 公共git clone在容器因DNS失败，随后继续使用已连接GitHub工具；没有将失败说成仓库不存在。

## 3. 机械投影

S1：order=[tower,sign,roof]，reading=occlusion。
S2：rotation=0，mirror=false，stage=inase，place=sumida。
S3：life=1680，earliest=1995，dateMeaning=lower_bound。
S4：rotation=0，mirror=false，camera=playground，building=sports，purpose=capture。
S5：order=[kisho,hisamatsu,chitose,meiji]，move=location。
终局：scene=sumida；stage=inase；object=contemporary；time=1995_or_later；park=capture_sports_playground；recipient=meijiza；channel=game_receipt。

share仅使首次进入S4时大锚点姿态为(0,false)；challenge为(3,true)。两者均要判断视点、建筑、用途。更改S3选择不重置已做S4。最终solo/joint另选，四种组合都有效。错误可重试、三级免费提示、辅助有记录但不削减结局。提前有根据的完整答案可以结案，不加盖章条件。

## 4. 研究工具本轮实际结果

SciSpace成功检索了“文化遗产实景游戏怎样使地点历史和物理特征成为叙事及决策的必要条件”。结果中有三个直接相关方向：
- Haahr，Reconciling immersion and presence：现场存在感不能被数字剧情吞没。SciSpace的2017会议条目与另查到的2018期刊条目DOI不同，分开登记，不合并为同一出版物。
- Shin等，Narrative design for Rediscovering Daereungwon：利用各地点的独特属性组织连续叙事。本轮打开KAIST研究团队及机构摘要页核实；并纠正插件把Jungwha Kim识别成Jinwoo Kim的元数据问题。
- DaCosta与Kinsell，Serious Games in Cultural Heritage：定位游戏应重视地点文化意义。插件摘要取得；出版社正文返回429，未冒称全文已读。

采用的是设计约束，不据摘要宣称本路线的体验或销售已获证明。没有把本项目改为AR；仍用原纸件与文本。

本轮另打开麦基Do Your Scenes Turn?作者正文，Alexandrian Don't Prep Plots主文。采用：场景有价值变化；NPC有可行动目标而非只配合剧情。旧麦基人物研究、GUMSHOE与Nicholson记录保留，不重复声称读完整本书。

## 5. 来源访问差异，单独记录

本次web打开中央区浜町公园页面，返回正文为2029年度、页面标2024-08-22；上一轮记录称2030年度。本轮不能确认是缓存、页面版本差别还是旧次读取有误。玩家故事不使用截止年份，统一保留“部分区域施工，以当日现场公告为准”。这不是改变路线或答案。

本次IRIS2026公告页返回最新可见条目为7月23日，没有复现旧记录称9月发布的10—12月休馆公告；因此不把该旧日期再写为本轮已证当前营业状态。所有玩法本来就不入馆。没有据此承诺开放，也不要求用户补拍。

## 6. 验收边界

本轮只新增流程、材料转化、人物、剧本与自查记录；不改旧程序和图卡几何。凡“画动起来、画中街道、角色说话”等仅作为虚构文本情境，不视为已交付动画、音频或真人演出。不能要求实际招牌变形、博物馆工作人员配合或剧院开门。
