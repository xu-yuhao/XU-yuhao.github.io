---
layout: banner
permalink: /publications/
title: Publications
nav: true
nav_order: 3

banner:
  image: banners/publications.jpg
  text_color: "#173d98"
  overlay: 0
  shadow: 0
---

<!--
  Refereed journal publications and reviewed conference proceedings (plus chapters, theses): _bibliography/papers.bib
  Unreviewed conference proceedings (abstract review only): _bibliography/presentations.bib
  Invited talks: _bibliography/talks.bib
  A section only appears once it has at least one entry.
-->

<style>
  /* While filtering, hide a whole section once none of its entries match. */
  .pub-group:not(:has(ol.bibliography > li:not(.unloaded))) { display: none; }
  .pub-legend { color: var(--global-text-color-light); font-size: 0.9rem; }
</style>

{% include bib_search.liquid %}

<p class="pub-legend">* corresponding author; † equal contributors; ‡ student (co-)advisee of Dr. Xu.</p>

<div class="publications">

{% capture journal %}{% bibliography --file papers --query @article %}{% endcapture %}
{% if journal contains '<li' %}
<div class="pub-group" markdown="0">
<h2 class="pub-section">Refereed Journal Publications</h2>
{{ journal }}
</div>
{% endif %}

{% capture confpapers %}{% bibliography --file papers --query @inproceedings || @conference %}{% endcapture %}
{% if confpapers contains '<li' %}
<div class="pub-group" markdown="0">
<h2 class="pub-section">Conference Proceedings (Reviewed)</h2>
<p class="pub-legend">Based on review of the entire paper, not just an abstract.</p>
{{ confpapers }}
</div>
{% endif %}

{% capture other %}{% bibliography --file papers --query @incollection || @inbook || @book || @proceedings || @phdthesis || @mastersthesis || @techreport || @misc || @unpublished || @booklet || @manual || @online || @thesis || @report || @software || @dataset %}{% endcapture %}
{% if other contains '<li' %}
<div class="pub-group" markdown="0">
<h2 class="pub-section">Book Chapters, Theses, Reports and Preprints</h2>
{{ other }}
</div>
{% endif %}

{% capture presentations %}{% bibliography --file presentations %}{% endcapture %}
{% if presentations contains '<li' %}
<div class="pub-group" markdown="0">
<h2 class="pub-section">Conference Proceedings (Unreviewed)</h2>
<p class="pub-legend">Based on review of the abstract only.</p>
{{ presentations }}
</div>
{% endif %}

{% capture invited %}{% bibliography --file talks %}{% endcapture %}
{% if invited contains '<li' %}
<div class="pub-group" markdown="0">
<h2 class="pub-section">Invited Talks</h2>
{{ invited }}
</div>
{% endif %}

</div>
