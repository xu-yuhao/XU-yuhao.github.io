# 迁移核对清单

更新于 2026-09-29。网站内容来自三个来源：

1. **CV（`Resume_Xu_Yuhao_20260923`，2026 年 9 月 23 日）**：论文、会议、特邀报告、新闻、成员。2024 年 9 月版 CV 补充了 PVAMU 时期的部分内容（本科生等）。
2. **旧 Google Site 的原文**（你贴过来的文字）：首页介绍、研究页、招生页。
3. **旧 Google Site 的页面截图**（5 张）：页面外观、成员页的个人介绍和办公室电话、所有图片（临时版本）。

## 从 CV 导入

| 内容 | 位置 | 数量 |
| --- | --- | --- |
| Refereed Journal Publications | `_bibliography/papers.bib` | 25 篇（CV 的 [1] 到 [25]） |
| Conference Proceedings (Reviewed) | `_bibliography/papers.bib` | 27 篇（[1] 到 [27]） |
| Conference Proceedings (Unreviewed) | `_bibliography/presentations.bib` | 32 个（[1] 到 [32]） |
| Invited Talks | `_bibliography/talks.bib` | 4 个 |
| 新闻（获奖、新成员、毕业、项目、特邀报告、学术服务、新课、实验室大事） | `_news/` | 79 条 |
| 成员 | `_data/people.yml` | 在读：4 名博士生、1 名硕士生、11 名本科生（其中 9 名 Creative Inquiry 学生只列名字）；毕业：8 名研究生、20 名本科生和高中生（其中 6 名 Creative Inquiry 学生只列名字） |

处理原则：

- **没有上网站的**：期刊 [26] 到 [29]（under review），会议摘要 [33]（submitted）。接收以后再加。CV 里的 Research Reports 也没有放。
- **已接收、还没开的会议**（IMECE 2026、ASGSR 2026 两篇、Hawaii International Conference on Education 2027）照常列出，`note` 写 "Accepted"。
- 作者、标题、期刊或会议名称、卷期页码、论文编号都照 CV 原文录入。生成脚本逐条核对过"作者 + 标题 + 出处"能拼回 CV 的原句。作者标记 `*`、`†`、`‡` 照 CV 保留，显示成上标。
- 只做了这些格式调整：地点写成"城市, 州缩写"（例如 Orlando, FL）；跨月的会议取开始的月份；会议的具体日期只保留月份和年份。
- 奖项注在对应报告下面：CV 里写在括号中的奖项（Distinguished Paper、DFD25 海报获奖、SHTC 2025 学生报告奖、ASEE Best Poster）；另外 Sheldon Scott 和 Heba Afzal 在 ASGSR 的海报奖来自 CV 的学生获奖部分，也注在他们的报告下面。
- CV 没有 DOI，所以论文页暂时没有 DOI 按钮。可以把 DOI 粘贴进 DOI 助手批量补上（见 `UPDATING.md`），标题相同或几乎相同的条目会被补上 DOI，不会重复添加。
- **新闻**合并了旧 Google Site 新闻页（截图可见的 10 条，原文基本照搬）和两版 CV：你和学生的全部获奖，研究生入学和毕业，本科生和高中生加入（按项目或学期合并成一条），作为 PI/Co-PI 的项目（按开始年份，不写金额），4 次特邀报告，学术服务（ASGSR 理事会、NASA 工作组、分会场主席、摘要主席、研讨会组织、评委），3 门新课。每条都由程序对照 CV 原文逐条核对过。日期只写到来源给出的精度（例如 "Oct 2025"、"Fall 2025"、"2025"），没有编造具体日期。旧站上 2023 年 PVAMU 的四个奖项有具体月份，按旧站拆成了四条。
- **没有做成新闻的**：你本人的学位和 ASML 工作经历、学会会员、审稿和评审专家、校内委员会、参加过的培训和研讨会、日常授课、论文和会议报告（论文页已有）、只担任委员会成员的学生、Senior Design 课程小组。

成员页的几点说明：

- Md Mainul Islam 是在读博士生（co-advised），2026 年的硕士学位写在这一条的介绍里，没有另列在毕业生里。
- 只做委员会成员的学生没有列入。
- PVAMU 时期（2019 到 2023 年）的本科生列在 alumni 的 "Undergraduate and High School Researchers" 分组里；不想列出时，从 `people.yml` 删掉。

## 从旧 Google Site 迁移

- **网站名称**：和旧站一样，左上角是 Clemson 标志加 "Xu Research Group"（`_config.yml` 的 `navbar_brand`）。"Thermo-Fluids Research Laboratory" 写在四处：首页横幅（`_pages/about.md` 里 `banner:` 的 `title`）、浏览器标签页（`_config.yml` 的 `title`）、搜索引擎摘要（`description`）和页脚（`footer_text`）。改名时这几处一起改。
- **首页**：About Dr. Xu 和 About our research 两段用你的原文，改了个别笔误和标点。
- **赞助方**：和旧站一样是 5 个 logo（NASA、NSF、Department of Education、TEES、Sigma Xi），数据在 `_data/sponsors.yml`。CV 里另有 ONR 和 Princeton PACRI，旧站没放，文件里留了注释掉的条目。
- **研究页** `/research/`：三个方向的文字照搬原文。6 张配图里有 4 张从截图裁出（临时），另外 2 张（*C. elegans*、SERS 芯片）在截图里不完整，页面源码里用注释留了位置和写好的代码行。
- **招生页** `/openings/`：原文照搬，链接保留；指向旧 Google Site 论文页的链接改成新站的 `/publications/`；改了个别笔误。"Full financial aid" 橙色、"Spring 2026" 加粗、Notes 斜体，和旧站一致。
- **成员页**：你的职位、办公室（231 Fluor Daniel Engineering Innovation Building (EIB)）、电话和 4 位研究生的介绍来自截图，改了个别笔误。截图只到 Ananth Sundar 为止，截图以下旧站还有哪些内容无法得知，本科生和毕业生名单仍按 CV。

## 外观（仿照旧 Google Site）

和旧站一致的地方：Clemson 标志加 "Xu Research Group" 的顶栏，菜单顺序 Home、People、Research、Publications、Openings、News，每页顶部的照片横幅和标题，Lora 衬线字体，Clemson 橙色的小标题，首页的斜体小标签和赞助方 logo 行，成员页"照片在左、介绍在右"的排法，研究页并排的配图和图注。

有意保留的不同：

- **论文页**保留了 al-folio 的格式：顶部搜索框、按年份分组、彩色期刊标签、作者标记上标、Bib 按钮。旧站是一整段小字列表，只有两个栏目；这里的栏目名和分法按 CV（现在显示四个栏目；书的章节、学位论文等有条目后才会出现第五个）。
- **首页**底部多了最近 3 条新闻、社交图标（Google Scholar、ORCID 等）和页脚，旧站没有。
- **正文链接**用比 Clemson 橙深一点的颜色（#B85000），因为 #F56600 在白底上对比度只有 3.1:1，小字不易辨认；标题和名字仍用 #F56600，但标题加粗、名字字号放大到 24 像素，达到大字号的对比度要求。
- **暗色模式**关掉了，旧站也没有。
- **图片**全部是从截图裁出来的临时版本，见 `UPDATING.md` 的"现在的图片都是临时的"。

## 需要你看一下

- [ ] 招生页写着 "These positions can start as early as Spring 2026"，邮件标题示例是 "Spring 2026"，页尾是 "updated on August 28, 2025"。现在已经是 2026 年 9 月，按你的实际情况改（`_pages/openings.md`）。
- [ ] 研究页和首页的研究介绍是旧站的内容，写的是燃料燃烧、碳烟诊断和微流控。近年的超临界水氧化、SPARC 中心等方向没有提到，要不要补一段由你决定。
- [ ] 用原图替换所有临时图片（文件名不变）：5 张横幅、5 张照片、4 张研究配图、5 个赞助方 logo、Clemson 标志；再补上研究页缺的 2 张图。横幅建议换成自己拍的实验室或校园照片。
- [ ] 旧 Google Site 新闻页的截图到 2023 年 2 月为止，下面如果还有更早的新闻，截图没有显示；这些年份的新闻目前按 CV 补齐。
- [ ] 只有年份的新闻（多数项目、2019 年等）在当年里的先后顺序是估计的；知道月份的话，改 `date` 和 `date_display` 即可。
- [ ] 首页赞助方 logo 下面的链接：截图上看不到旧站实际链到哪里，现在链到各机构的官网首页（`_data/sponsors.yml` 的 `url`），需要的话改成具体项目页。
- [ ] 首页代表作（可选）：给想展示的论文加 `selected = {true},`，再按 `_pages/about.md` 里注释的说明打开 "Selected publications"。

## 与最初方案不同的地方

- 按你的要求，**取消了每周自动更新论文**，只保留一个手动的 DOI 助手（Actions → Add publication by DOI）。
- 模板是 al-folio v1.2，布局和样式在 `al_folio_core` 等 gem 里，仓库只放内容和配置。升级时要同时改 `Gemfile` 和 `Gemfile.lock`（在本地运行 `bundle update`，或者让 Claude Code 来做）。
- 为了让新闻显示"只有月份或年份"的日期，新闻列表用的是仓库里自己的 `_includes/news_list.liquid`；期刊论文的卷期页码由 `_includes/hook/bib.liquid` 补上。这两个是新增文件，不覆盖主题自带的文件。
- 为了仿照旧站外观，复制并修改了主题的两个文件：`assets/css/main.scss`（加载 `_sass/_custom.scss`）和 `_includes/header.liquid`（logo、名字、搜索按钮）。升级主题时要对比这两个文件。
