---
layout: banner
permalink: /research/
title: Research
nav: true
nav_order: 2

banner:
  image: banners/research.jpg
  text_color: "#1f4a24"
  overlay: 0
  shadow: 0
---

{% comment %}
  Figures: image files are in assets/img/research/. A row of figures is a <div class="xg-figures" markdown="0">
  block with one "include figure.liquid" line per figure (copy one of the lines below); the figures sit side by
  side and wrap on phones.
  Use <div class="xg-figures xg-single" markdown="0"> for a single centered figure.
  The images below were cut from a screenshot of the old Google Site, so they are small. To replace one,
  upload the original under the same file name (or change path="..." to the new name).
{% endcomment %}

## Droplet combustion of liquid fuels

In this area of research, we study the combustion dynamics of an isolated droplet surrounded by a near-spherical flame, which is the canonical combustion configuration for liquid fuels. The spherical symmetry is experimentally achieved by burning fuel droplets in an environment with reduced Reynolds and Rayleigh numbers. Techniques used for this purpose include burning small fuel droplets, dropping the experimental package in a drop tower, or conducting experiments onboard the International Space Station. Liquid fuels of interest include practical transportation fuels (gasoline, diesel, and jet fuel), surrogate fuels, and bio-derived fuels (e.g., butanol and algae-derived biofuels). The current work in this area focuses on building a High Pressure Combustion Apparatus to study the burning characteristics of hydrocarbons and biofuels at elevated pressures representative of practical engines.

<div class="xg-figures" markdown="0">
  {% include figure.liquid path="assets/img/research/decane-droplet.png" zoomable=true alt="A free-floating n-decane droplet burning in microgravity" caption="A free-floating <em>n</em>-decane droplet burning in microgravity." %}
  {% include figure.liquid path="assets/img/research/ahrd-droplet.png" zoomable=true alt="AHRD droplet burning in microgravity and droplet diameter histories" caption="(a) A fiber-supported AHRD droplet burning in microgravity. (b) A self-illuminated AHRD flame image. (c) Evolution of scaled droplet diameters for AHRD, RD50, and DF2. (AHRD = hydro-processed renewable diesel derived from microalgae, DF2 = #2 diesel fuel, and RD50 = an equivolume mixture of AHRD and DF2.)" %}
</div>

## Laser-based diagnostics of sooting dynamics

In this area, we work on a nonintrusive and cost-effective method to obtain quantitative soot volume fraction measurements that provide spatial and temporal resolution of these dynamics. A full-field light extinction technique is being developed for this purpose. It is based on the attenuation of light when a single-wavelength light beam passes through the soot-containing region of the flame. This technique can be incorporated into various combustion systems. Experimental results from this technique will be extremely useful in evaluating the soot emissions during the combustion of biofuels and providing data for model validation.

<div class="xg-figures xg-single" markdown="0">
  {% include figure.liquid path="assets/img/research/fflem-schematic.png" zoomable=true alt="Schematic of the full-field light extinction method" caption="Schematic of the full-field light extinction method (FFLEM)." %}
</div>

## Characterization of microfluidic devices for energy and biomedical applications

This research area focuses on fabricating mechanical devices at the micro-/nano-scale and exploring their applications in energy and biomedical research. Projects in this area include the following: (1) developing a novel method based on Leidenfrost levitation and exploring its potential as a biomass reactor and (2) developing microfluidic biosensors for the detection of pathogens.

{% comment %}
  Two figures from the old site are not here yet because they were not fully visible in the screenshot.
  Upload them to assets/img/research/ and add these lines inside the <div> below:
  {% include figure.liquid path="assets/img/research/c-elegans.png" zoomable=true alt="Manipulation of C. elegans" caption="Manipulation of <em>C. elegans</em>." %}
  {% include figure.liquid path="assets/img/research/sers-chip.png" zoomable=true alt="Microfluidics chip coupled with SERS spectroscopy" caption="A microfluidics chip coupled with surface enhanced Raman scattering (SERS) spectroscopy." %}
  With more than one figure, change class="xg-figures xg-single" to class="xg-figures".
{% endcomment %}

<div class="xg-figures xg-single" markdown="0">
  {% include figure.liquid path="assets/img/research/leidenfrost.png" zoomable=true alt="Leidenfrost levitation" caption="Leidenfrost levitation." %}
</div>

<p class="xg-contact">For research collaborations and position openings, please contact Dr. Yuhao Xu at <a href="mailto:yuhaox@clemson.edu">yuhaox@clemson.edu</a>.</p>
