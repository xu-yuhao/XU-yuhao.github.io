# 网站更新手册

网址：**<https://xu-yuhao.github.io/>**（第一次发表的步骤见下文"预览和发表"一节里的"第一次发表"）

网站的每一部分都是仓库里的一个文本文件。改完保存（GitHub 上叫 **Commit changes**）以后，`Deploy site` 会自动重新生成网站，3 到 5 分钟后刷新网址就能看到。进度在仓库的 **Actions** 标签页：黄点是正在构建，绿勾是已上线，红叉是出错（这时网站保持上一版不变，见"出错了怎么办"）。

## 三种更新方式

1. **在 GitHub 网页上直接改**。电脑或手机浏览器都行：打开仓库 <https://github.com/xu-yuhao/XU-yuhao.github.io>，找到文件，点右上角铅笔图标，改完点 **Commit changes**。适合加一条新闻、改一个名字这类小改动。
2. **让 Claude Code 改**。在 <https://claude.ai/code> 或手机 Claude App 里选中这个仓库，直接说要做什么，比如"加一条新闻：某某同学获得 2026 年 ASGSR 研究生海报一等奖，2026 年 12 月"，或者把 CV 里的一条引用粘贴过去说"加到论文列表"。它会按 `CLAUDE.md` 里的规则改好文件，开一个 pull request（PR），还可以先截图给你看效果。你在 GitHub 上点 **Merge pull request** 就发表了。适合一次改好几处，或者不想碰格式的时候。
3. **有 DOI 的论文用 DOI 助手**：**Actions → Add publication by DOI → Run workflow**，粘贴 DOI（可以一次粘好几个，用空格或逗号分开），点绿色按钮。一两分钟后 **Pull requests** 里会出现一个 PR，里面是从 Crossref 取来的标准格式条目；看一眼，点 **Merge pull request**。如果这篇论文已经在列表里、只是缺 DOI（比如从 CV 导入的旧论文），它会把 DOI 补进原条目，不会重复添加。第一次用之前要做一个设置，见"第一次发表"第 5 步。

   几种情况：
   - **绿勾但没有出现 PR**：这些 DOI 已经在列表里了，运行页面的 Annotations 里会写 "already in papers.bib"。
   - **红叉**：点进去看 "Could not add" 后面的 DOI，一般是 DOI 打错了，或者 Crossref 和 OpenAlex 都还没收录；这种论文用下面的模板手动加。
   - **PR 里出现了已经在列表里的论文**：说明 CV 里的标题和正式发表的标题差别较大，没能自动认出来（只有完全相同或几乎相同的标题会被识别）。在 PR 的 **Files changed** 里点 ⋯ → **Edit file**，删掉新加的那条，把 `doi = {...},` 这一行复制到原来的条目里。
   - 新条目里的作者是全名（例如 `Xu, Yuhao`），和其他条目的缩写写法不同，显示没有问题；想统一的话在 PR 里一起改。
   - 上一个 DOI 助手的 PR 合并（或关闭）以后再运行下一次，多篇论文尽量一次粘贴。如果某个 PR 提示 "This branch has conflicts"，点 **Close pull request** 关掉它，再重新运行一次 DOI 助手。

## 新闻

新闻在 `_news/` 文件夹，一条新闻一个文件，现在有 79 条（2014 到 2026 年）。`/news/` 页面按年份分组，顶部有年份跳转链接；每条左边是日期和一个小分类标签：年份标题下不再重复年份，只显示 Dec、Fall 或 Dec 5，只知道年份的不显示日期；手机上日期和标签在正文上方。首页显示最新的 3 条。

### 最省事的办法：让 Claude Code 从 CV 更新

CV 更新以后，在 Claude Code 里上传新 CV，说"按新 CV 更新网站的 News"。它会按 `CLAUDE.md` 里写好的规则，只加 CV 里有、网站上还没有的事件，每条都对照 CV 原文核对，开 PR 并截图给你确认。

### 自己加一条

打开 `_news` 文件夹 → **Add file → Create new file**，文件名用日期开头，例如 `2026-12-05-doe-poster-award.md`（小写英文，不要空格）。内容照抄下面，把日期、分类和正文换成真实内容：

```markdown
---
layout: post
date: 2026-12-05
date_display: "Dec 2026"
category: award
inline: true
related_posts: false
---

Ph.D. student Jane Doe won First Place in the Graduate Student Poster Competition at the 42nd ASGSR Annual Meeting. Congratulations!
```

- `date` 用来排序，必须写成 年-月-日。
- `date_display` 是页面上显示的日期，按你知道的精度写：`"Dec 2026"`、`"Dec 5, 2026"`、`"Fall 2026"` 或只写 `"2026"`。只写年份时，年份标题下这一条左边不显示日期。整行不写，就按 `date` 显示（首页是 Dec 5, 2026，年份标题下是 Dec 5）。
- `category` 决定小标签，可选：`award`（获奖）、`welcome`（新成员）、`graduation`（答辩、毕业）、`funding`（新项目）、`talk`（特邀报告）、`service`（学术服务）、`teaching`（新课）、`lab`（实验室大事）。不写就没有标签。
- 正文一两句，不能空着（空正文在网站搜索里会变成一条空白结果）。现有新闻的习惯：新成员结尾写 "Welcome!"，学生获奖和毕业结尾写 "Congratulations!"。正文里可以放链接：`[Clemson News](https://news.clemson.edu/...)`。

### 不想要某条新闻

- **暂时隐藏**：打开这条新闻的文件，点铅笔图标，在两行 `---` 之间加一行 `published: false`，保存。新闻页、首页和站内搜索都不再显示它，文件还在，删掉这一行就恢复。
- **彻底删除**：打开文件，点右上角 ⋯ → **Delete file** → **Commit changes**。
- **一次处理很多条**：让 Claude Code 做最省事，例如"把所有 service 类的新闻隐藏"或"把 2019 年以前的新闻都删掉"。

找文件的办法：`_news` 文件夹里的文件名以日期开头，按新闻页上的年份和月份就能找到（Fall 的新闻文件名是 08-20，Spring 是 01-15，Summer 是 06-01，只有年份的是 06-30）；也可以在仓库页面按 `t` 键，输入关键词（例如 `ci-fall`、`grant`）搜文件名，手机上点仓库页面的 **Go to file**。

注意：GitHub 仓库是公开的。隐藏只影响网站，文件本身任何人都能在仓库里看到；彻底删除后，旧版本仍留在仓库的历史记录里。涉及隐私的内容（例如学生要求撤下）请彻底删除；需要从历史记录里也清除时，让 Claude Code 处理。

## 论文

| 类别 | 文件 | 论文页上的栏目 |
| --- | --- | --- |
| 期刊论文 | `_bibliography/papers.bib`，写成 `@article` | Refereed Journal Publications |
| 全文审稿的会议论文 | `_bibliography/papers.bib`，写成 `@inproceedings` | Conference Proceedings (Reviewed) |
| 只审摘要的会议报告（如 ASGSR、APS DFD） | `_bibliography/presentations.bib`，写成 `@inproceedings` | Conference Proceedings (Unreviewed) |
| 特邀报告、系列讲座 | `_bibliography/talks.bib`，写成 `@misc` | Invited Talks |
| 书的章节、学位论文、预印本 | `_bibliography/papers.bib`，写成 `@incollection`、`@phdthesis`、`@misc` | Book Chapters, Theses, Reports and Preprints |

栏目名和 CV 一致。CV 里 "under review" 的期刊论文和 "submitted" 的摘要没有放上网站，接收以后再加；已接收但还没开的会议在 `note` 里写 `Accepted`。

每个栏目按年份分组，同一年内按月份从新到旧排，所以新条目加在文件的哪个位置都行；写上 `month` 排序最准确；同一年里没写 `month` 的几条，先后顺序不保证固定，在意顺序就把月份写上。你的名字（`Xu, Y.` 或 `Xu, Yuhao`）会自动加下划线。期刊论文会显示卷号、期号和页码。

期刊论文模板（复制到 `papers.bib` 里，每一项都换成真实信息）：

```bibtex
@article{doe2026droplet,
  title   = {Title of the Paper},
  author  = {Doe‡, J. and Hicks, M.C. and Xu*, Y.},
  journal = {Combustion and Flame},
  volume  = {280},
  number  = {2},
  pages   = {114321},
  month   = oct,
  year    = {2026},
  doi     = {10.xxxx/xxxxx},
  abbr    = {CNF},
  bibtex_show = {true},
}
```

会议报告模板（`presentations.bib`）：

```bibtex
@inproceedings{doe2026asgsr,
  title     = {Title of the Talk},
  author    = {Doe‡, J. and Xu*, Y.},
  booktitle = {42nd Annual Meeting of the American Society for Gravitational and Space Research},
  location  = {Arlington, VA},
  month     = dec,
  year      = {2026},
  abbr      = {ASGSR},
  note      = {Poster},
}
```

规则：

- 第一行花括号里的 `doe2026droplet` 是条目的编号，随便起，但三个文件里都不能重复。
- 作者写成"姓, 名缩写"，用 ` and ` 连接。和 CV 一样的标记直接写在姓后面：`*` 通讯作者，`†` 共同第一作者，`‡` 你指导的学生，例如 `Liu‡, X. and Xu*, Y.`；网站上会显示成上标，论文页顶部有说明。
- 不知道的字段整行删掉，不要空着，也不要乱填。
- `abbr` 是论文前面的彩色小标签，颜色在 `_data/venues.yml` 里设；不写就没有标签。
- `%` 开头的注释行里不能出现 `@` 符号，否则网站构建会失败。
- 想在首页列出代表作：在这几篇的条目里加 `selected = {true},`，再打开 `_pages/about.md`，把 `{% comment %}` 和 `{% endcomment %}` 之间的 `## Selected publications` 和下面那一行移到注释外面（文件里有说明）。
- 想加 PDF：把文件上传到 `assets/pdf/`，条目里加 `pdf = {文件名.pdf},`，论文下面会出现 PDF 按钮。

## 成员和照片

成员名单在 `_data/people.yml`。你和在读研究生的介绍照搬旧 Google Site，只改了个别笔误。Md Mainul Islam 没有出现在旧站截图里，这一条的介绍按 CV 写。本科生和毕业生名单按 2026 年 9 月的 CV 填写。

研究生显示成"照片 + 介绍"，和旧站一样；本科生分组写了 `style: list`，显示成名字加说明的列表；Creative Inquiry 学生单独一组，写了 `style: names`，只在一行里列名字。每个分组下都有以 `#` 开头的示例，复制后删掉每行开头的 `# ` 再改：

```yaml
  - group: Current Students
    members:
      - name: Xi Liu
        role: Ph.D. Student
        photo: people/xi_liu.jpg
        bio: "Xi received her B.S. degree in Building Environment and Equipment Engineering in 2015 from ..."
        interests: "combustion diagnostics; sustainable fuels; life-cycle analysis"
```

- `role` 显示在名字后面，`bio` 是介绍，`interests` 显示在 "Current research interest:" 后面。哪一项不需要，整行删掉。
- 缩进只能用空格，和上下条目对齐。
- 文字两边的英文双引号要保留，否则内容里出现冒号就会导致构建失败。
- 学生毕业后，把这一条剪切到文件末尾 `alumni:` 下面对应分组（`Graduate Students`、`Undergraduate and High School Researchers`；Creative Inquiry 学生放到 alumni 的 `Creative Inquiry Students`）的 `members:` 下面，缩进和原来一样（`- name` 前 6 个空格，`info` 前 8 个空格），只保留 `name` 和一行 `info`，例如：

  ```yaml
  alumni:
    - group: Graduate Students
      members:
        - name: Jane Doe
          info: "Ph.D. 2028, Clemson University; now at GE Aerospace"
  ```
- 分组里没有人或所有人都隐藏时，这个分组自动隐藏；毕业生全部隐藏时 Alumni 标题也不显示。

### 名单太长时：隐藏、只列名字、删除

四种做法，都只改 `_data/people.yml`：

- **隐藏一个人**：在这个人的 `- name:` 下面加一行 `hide: true`，和下面的 `info` 或 `role` 对齐（前面 8 个空格）。页面上不显示，但记录留在文件里，删掉这一行就恢复。
- **隐藏整组**：在分组的 `- group:` 下面加一行 `hide: true`（和 `members:` 对齐）。在读和毕业生里各有一组 Creative Inquiry Students，都不想列就两组都加。
- **只列名字**：把分组的 `style: list` 改成 `style: names`；没有 `style` 这一行的分组（例如毕业生的前两组），就在 `members:` 上面加一行 `style: names`（和 `members:` 对齐）。每个人的说明会隐藏，只剩一行名字；删掉或改回就恢复。
- **彻底删掉**：删除这个人的 `- name:` 一行和它下面缩进更深的所有行（本科生和毕业生只有 `info` 一行，研究生还有 `role`、`photo`、`bio`、`interests`）。

例如：

```yaml
  - group: Creative Inquiry Students
    hide: true
    note: "Creative Inquiry team “Droplet Combust & Flame”"
    style: names
    members:
      - name: Jane Doe
        info: "Creative Inquiry (Fall 2026)"
```

### 加学生照片（headshot）

1. 准备照片：正方形或接近正方形，脸在中间，宽 400 到 800 像素，1 MB 以内，jpg 或 png。页面上裁成正方形显示（电脑上 150 像素宽，手机上 96 像素）。
2. 文件名用小写英文和下划线，例如 `jane_doe.jpg`。
3. 在 GitHub 上依次点开 `assets` → `img` → `people` 文件夹，点 **Add file → Upload files**，把照片拖进去，点 **Commit changes**。手机浏览器也能上传。
4. 打开 `_data/people.yml`，在这个学生的条目里把 `photo:` 改成 `photo: people/jane_doe.jpg`（前面不要加 `assets/img/`）。
5. 保存，3 到 5 分钟后在成员页看到。没填 `photo` 的人显示姓名首字母。

现有的 5 张照片（包括你的 `yuhao_xu.jpg`）是从截图里裁的，只有 111×108 像素。换清晰的原图时，用同样的文件名上传到 `assets/img/people/`，覆盖旧文件即可，`people.yml` 不用改。文件名要完全一样，包括大小写和扩展名（`.jpg` 不能换成 `.png`）。

也可以直接在 Claude Code 里上传照片，说"把这张设为 Xi Liu 的头像"。

## 其他内容在哪

| 内容 | 文件 |
| --- | --- |
| 首页介绍（About Dr. Xu、About our research） | `_pages/about.md` |
| 首页赞助方 logo | `_data/sponsors.yml`，图片在 `assets/img/sponsors/` |
| 研究方向和配图 | `_pages/research.md`，图片在 `assets/img/research/` |
| 招生信息 | `_pages/openings.md` |
| 首页底部的联系图标（邮箱、Google Scholar、ORCID 等） | `_data/socials.yml` |
| 页面最后一句 "For research collaborations..." 和邮箱 | `_pages/about.md`、`research.md`、`openings.md` 的最后一行。邮箱还写在 `_data/people.yml`、`_data/socials.yml` 和招生页正文里，换邮箱时一起改 |
| 成员页上你的职位、办公室、电话 | `_data/people.yml` 里的 `pi:` |
| 左上角的名字（Xu Research Group）和 logo | `_config.yml` 里的 `navbar_brand`、`navbar_logo` |
| 浏览器标签页上的网站名（Thermo-Fluids Research Laboratory）、描述、页脚 | `_config.yml` 开头几行 |
| 颜色、字体、横幅高度等样式 | `_sass/_custom.scss` |

## 改排版、加图片

页面的样子由三样东西决定：每个页面文件开头 `---` 之间的设置（横幅、菜单顺序），页面正文里的写法（图片、并排），以及 `_sass/_custom.scss` 里的样式（颜色、字体、间距）。

### 图片放在哪

所有图片都在 `assets/img/` 下面：

| 文件夹 | 用途 | 建议尺寸 |
| --- | --- | --- |
| `banners/` | 每页顶部的横幅照片 | 宽 1920 像素左右，高 400 到 600 像素，jpg，500 KB 以内 |
| `people/` | 成员照片 | 正方形，400 到 800 像素 |
| `research/` | 研究页配图 | 宽 800 像素以上 |
| `sponsors/` | 首页赞助方 logo | 高 300 像素左右，png |
| `logo/` | 左上角的 Clemson 标志 | 高 60 像素以上，透明背景 png |

上传方法和上面的照片一样：打开文件夹 → **Add file → Upload files** → **Commit changes**。**换图最省事的办法是用同一个文件名上传，覆盖旧文件**，页面文件一个字都不用改。文件名要完全一样，包括大小写和扩展名；换好后刷新还是旧图的话，按 Ctrl+Shift+R（Mac 上 Cmd+Shift+R）强制刷新。

### 现在的图片都是临时的

这次的图片全部是从你发来的 Google Sites 截图里裁出来的，分辨率很低，在大屏幕上会发虚：

- 横幅：`banners/home.jpg`、`banners/office.jpg`（成员页和招生页共用）、`banners/research.jpg`、`banners/publications.jpg`、`banners/news.jpg`。
- 照片：`people/` 里的 5 张。
- 研究配图：`research/` 里的 4 张。
- 赞助方 logo：`sponsors/` 里的 5 张。
- Clemson 标志：`logo/clemson.png`。

请用原图替换，文件名保持不变。横幅最好换成自己拍的实验室、设备或校园照片；左上角的 Clemson 标志和首页的赞助方 logo 建议换成各机构提供的官方标志文件。

### 每页顶部的横幅

在页面文件开头的 `banner:` 里设置，例如 `_pages/research.md`：

```yaml
banner:
  image: banners/research.jpg   # assets/img/ 下面的文件；删掉这一行就是深灰色的纯色横幅（同时删掉 text_color，标题变回白色）
  title: Research               # 横幅上的字，不写就用页面标题
  text_color: "#1f4a24"         # 字的颜色，必须带英文双引号
  overlay: 0                    # 把照片压暗多少，0 到 0.7；白字压在亮照片上看不清时调大
  shadow: 0                     # 字后面的暗色光晕，0 表示没有
  position: center              # 照片被裁切时保留哪一部分：top、center 或 bottom
```

某一页不想要照片，删掉 `image` 这一行（连同 `text_color`），就是深灰色的纯色横幅。页面开头如果还没有 `banner:`，照上面的格式加上即可，注意 `image` 等几行前面有两个空格。

横幅的高度和标题字号在 `_sass/_custom.scss` 的 `.xg-banner` 那一段。

### 在页面里加图片

在 `about.md`、`research.md`、`openings.md` 这类 `.md` 页面的正文里：

最简单的写法，一行就行：

```markdown
![Group photo, Fall 2026](/assets/img/research/group-2026.jpg)
```

需要图注、点击放大、限制宽度时，用这一行（`max-width` 可以不写，不写就铺满整栏；写了图片会居中）：

```liquid
{% include figure.liquid path="assets/img/research/group-2026.jpg" zoomable=true max-width="600px" caption="Group photo, Fall 2026." %}
```

几张图并排，手机上自动变成上下排列：

```html
<div class="xg-figures" markdown="0">
  {% include figure.liquid path="assets/img/research/a.png" zoomable=true caption="第一张的图注" %}
  {% include figure.liquid path="assets/img/research/b.png" zoomable=true caption="第二张的图注" %}
</div>
```

只放一张并居中时，把 `class="xg-figures"` 改成 `class="xg-figures xg-single"`。研究页现在就是这样写的，照抄最稳。旧站研究页还有两张图（*C. elegans* 和 SERS 芯片）在截图里不完整，没有放；`_pages/research.md` 里用注释留了位置，代码行也写好了，上传图片后按注释操作即可。

注意：`{% comment %}` 和 `{% endcomment %}` 之间的内容不会显示。

### 改颜色、字体和间距

网站自己加的样式（颜色、字体、横幅、成员页等）都在 `_sass/_custom.scss` 一个文件里，开头有说明；其余样式是主题自带的：

- `--xg-orange` 是标题和名字用的 Clemson 橙（#F56600）；`--xg-link` 是正文链接的颜色，比 Clemson 橙深一些，因为 #F56600 在白底上的对比度不够，小字不容易看清。
- 字体在 `body` 那一段，现在是 Lora，和旧站一样的衬线字体，字体文件放在 `assets/fonts/lora/`，不依赖外部网站。
- 其余各段依次是导航栏、横幅（`.xg-banner`）、首页 logo 行（`.xg-sponsors`）、研究页配图（`.xg-figures`）、成员页（`.xg-person`，照片大小在 `.xg-photo`）。

不熟悉 CSS 的话，最稳的办法是让 Claude Code 改，并让它截图给你确认后再合并。

### 导航栏

- 菜单顺序由每个页面文件开头的 `nav_order` 决定，数字小的在左边，Home 固定在最前面；菜单上的文字就是页面的 `title`。
- 左上角的名字和 logo：`_config.yml` 里的 `navbar_brand`、`navbar_logo`。平板宽度（576 到 900 像素）下为了让菜单排成一行，只显示 logo，不显示名字。
- 菜单文字或左上角的名字改长以后，平板和手机上的导航栏可能挤成两行，挡住页面顶部。改这类文字最好让 Claude Code 来做，并检查各种屏幕宽度。

### 首页赞助方

`_data/sponsors.yml`，一个 logo 一条（`name`、`logo`、`url`），按文件里的顺序显示。CV 里还有 Office of Naval Research 和 Princeton PACRI 两个资助方，旧站没有放；文件末尾有写好但注释掉的条目。要显示它们，先把 logo 以 `onr.png`、`princeton.png` 为文件名上传到 `assets/img/sponsors/`，再删掉这两个条目（共 6 行）开头的 `# `；上面那行英文说明不要动。Princeton 这一条显示的名字是 "Princeton University"，想写 PACRI 就改 `name`。

### 哪些文件是从主题复制来改的

`assets/css/main.scss`（只加了一行 `@use "custom";`，用来加载 `_sass/_custom.scss`）和 `_includes/header.liquid`（导航栏的 logo、名字和搜索按钮）是 al-folio 主题原文件的副本。以后升级主题时，让 Claude Code 把这两个文件和新版主题对比一下。其他为排版新加的文件（`_layouts/banner.liquid`、`_sass/_custom.scss`、`_includes/sponsors.liquid`、`_includes/person_photo.liquid`）不会被主题升级覆盖，但它们套在主题的页面结构上，升级后仍要把各页看一遍。

## 预览和发表

### 网址

发表后的网址是 **<https://xu-yuhao.github.io/>**。以后可以绑定自己的域名（Settings → Pages → Custom domain），需要时再说。

### 第一次发表（只做一次）

1. 打开 <https://github.com/xu-yuhao/XU-yuhao.github.io/compare/main...claude/website-migration-github-pages-2bimfr>，点 **Create pull request**，再点一次 **Create pull request**，然后点 **Merge pull request → Confirm merge**。
2. 打开 **Actions** 标签页，等最上面那一条 `Deploy site`（标题以 "Merge pull request" 开头的那条，不是更早那条只做检查的）出现绿勾，大约 3 到 5 分钟。旁边可能同时出现一个红叉的 `pages build and deployment`，GitHub 也可能发一封构建失败的邮件。这是旧的 Pages 设置还在直接构建 `main`，做完下一步就不会再出现。
3. **Settings → Pages → Build and deployment**：Source 选 **Deploy from a branch**，Branch 选 **gh-pages**，文件夹选 **/(root)**，点 **Save**。如果下拉里还没有 gh-pages，等一两分钟刷新页面再选。
4. 过一两分钟打开 <https://xu-yuhao.github.io/>。如果还是旧页面，强制刷新一次（电脑上按 Ctrl+Shift+R，Mac 上按 Cmd+Shift+R）。
5. **Settings → Actions → General → Workflow permissions**：勾选 **Allow GitHub Actions to create and approve pull requests**，点 **Save**。只有 DOI 助手需要这一步。
6. 确认新网站没问题以后，在旧的 Google Site 首页放一个指向新网址的链接，并把 Clemson 教师页、Google Scholar 等处的主页链接改成新网址。

### 以后的预览

GitHub Pages 本身没有"草稿预览"，改动一合并就上线。实际用起来有三种办法：

- **直接看线上**：改完 3 到 5 分钟刷新网址。发现问题就再改一次。如果改动是通过 PR 合并的，也可以在那个 PR 页面点 **Revert**：它会生成一个撤销用的新 PR，再点 **Create pull request** 和 **Merge pull request**，几分钟后网站就回到之前的样子。
- **用 Claude Code 改**：让它在开 PR 之前构建网站并截图给你，确认后再合并。
- **本地预览**（需要装 Ruby 3.3）：在仓库目录运行 `bundle install`，然后 `bundle exec jekyll serve`，浏览器打开 <http://localhost:4000>。

第一次发表之前，新网址上只有 2024 年那个空仓库的说明页，没有人会去访问，所以直接发表再检查也没有风险；旧的 Google Site 在你改链接之前照常运行。

## 出错了怎么办

`Deploy site` 出现红叉时，网站保持上一版不变。点进红叉看报错，最常见的原因有：

- `people.yml` 或 `sponsors.yml` 缩进不对，或者文字没加双引号（报错里有文件名和 `Psych::SyntaxError` 字样，后面的 line 数字就是出错的行号）；
- 页面里的 `{% include ... %}` 那一行少了英文双引号、结尾的 `%}` 不完整，或者图注里又用了英文双引号（报错里有 `Liquid` 字样和页面文件名）；
- BibTeX 条目少了逗号或花括号，或者注释行里出现了 `@`（报错里有 `BibTeX` 字样）。

改正后再保存一次即可。实在看不懂，把报错贴给 Claude Code 让它修。DOI 助手的红叉见上面"三种更新方式"第 3 条。

## 可选设置

- 仓库名改成全小写的 `xu-yuhao.github.io`（Settings → General → Repository name）。现在带大写的名字也能正常使用，改成小写是为了和 GitHub 文档的写法一致。
- DOI 助手遇到 arXiv 等不在 Crossref 登记的 DOI 时，会改用 OpenAlex 查询。每天的免费额度足够用；如果以后提示超出额度，在 <https://openalex.org/settings/api> 申请一个免费 key，存为仓库 secret `OPENALEX_API_KEY`（Settings → Secrets and variables → Actions → New repository secret）。
