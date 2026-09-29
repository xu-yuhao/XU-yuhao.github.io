---
layout: banner
title: Home
permalink: /

banner:
  image: banners/home.jpg
  title: Thermo-Fluids Research Laboratory
  text_color: "#e4eed8"
  overlay: 0.25

social: true # icons from _data/socials.yml, at the bottom of the page
---

Welcome to the homepage of Dr. Yuhao Xu's Thermo-Fluids Research Laboratory.

_About Dr. Xu:_ Dr. Yuhao Xu is an Assistant Professor in the Department of Mechanical Engineering at Clemson University. Dr. Xu joined Clemson in 2023. Prior to that, he was an Assistant Professor at Prairie View A&M University (PVAMU), a Historically Black College and University (HBCU). He also worked at ASML-Hermes Microvision Inc., where he applied high-resolution e-beam systems in the semiconductor industry. Dr. Xu has a Ph.D. and M.S. in Mechanical Engineering from Cornell University, an M.S. in Mechanical Engineering from Washington State University, and a B.Eng. in Building Environment and Equipment Engineering from Southeast University (China).

_About our research:_ With the continuous expansion of world energy consumption, exploring renewable solutions to reduce the consumption of petroleum-based fuels and harmful emissions is an integral part of worldwide energy policies. In this context, our research concerns the combustion of renewable liquid fuels derived from biofeedstocks, evaluates their burning characteristics in the context of currently used practical fuels, and quantifies their particulate emissions during combustion. Our research also focuses on developing tools at the micro- and nano-scale to address problems in energy and environment.

We thank the following sponsors for supporting our research.

{% include sponsors.liquid %}

{% comment %}
  To list selected publications on the home page: add  selected = {true},  to those entries in
  _bibliography/papers.bib, then move the two lines below out of this comment block.

## Selected publications
{% include selected_papers.liquid %}
{% endcomment %}

## Recent news

{% include news_list.liquid limit=3 %}

See all [news]({{ '/news/' | relative_url }}).

<p class="xg-contact">For research collaborations and position openings, please contact Dr. Yuhao Xu at <a href="mailto:yuhaox@clemson.edu">yuhaox@clemson.edu</a>.</p>
