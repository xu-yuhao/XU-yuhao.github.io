# Thermo-Fluids Research Laboratory website

Source for <https://xu-yuhao.github.io/>, the website of Dr. Yuhao Xu's Thermo-Fluids Research Laboratory (Department of Mechanical Engineering, Clemson University). It replaces the Google Site at <https://sites.google.com/view/yuhaoxu>.

- Built with [Jekyll](https://jekyllrb.com/) and the [al-folio](https://github.com/alshedivat/al-folio) v1.2 starter (MIT, see `LICENSE-al-folio`).
- Every push to `main` that changes site content rebuilds the site (`.github/workflows/deploy.yml`) and publishes it to the `gh-pages` branch.
- Publications, news and people are plain text files edited by hand. `.github/workflows/add-publication.yml` is an optional helper that turns DOIs into BibTeX entries and opens a pull request.

How to update content: [`UPDATING.md`](UPDATING.md) (Chinese).
