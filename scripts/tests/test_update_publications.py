"""Offline tests for scripts/update_publications.py.

Run from the repo root:  python -m unittest discover -s scripts/tests -v
"""

import json
import re
import shutil
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import update_publications as up  # noqa: E402

ORCID = "0000-0002-1825-0097"

OPENALEX_PAGE = {
    "meta": {"count": 3, "per_page": 100, "next_cursor": None},
    "results": [
        {
            "id": "https://openalex.org/W1000000001",
            "doi": "https://doi.org/10.1016/J.COMBUSTFLAME.2025.114000",
            "title": "Cool flame <i>n</i>-heptane droplets & soot",
            "display_name": "Cool flame n-heptane droplets & soot",
            "publication_year": 2025,
            "type": "article",
            "authorships": [
                {
                    "author_position": "first",
                    "author": {"id": "https://openalex.org/A1", "display_name": "Yuhao Xu", "orcid": f"https://orcid.org/{ORCID}"},
                    "institutions": [{"display_name": "Clemson University"}],
                    "raw_author_name": "Yuhao Xu",
                },
                {
                    "author_position": "last",
                    "author": {"id": "https://openalex.org/A2", "display_name": "C. Thomas Avedisian", "orcid": None},
                    "institutions": [{"display_name": "Cornell University"}],
                    "raw_author_name": "C. T. Avedisian",
                },
            ],
            "primary_location": {"source": {"display_name": "Combustion and Flame", "type": "journal", "host_organization_name": "Elsevier BV"}},
            "biblio": {"volume": "271", "issue": None, "first_page": "114000", "last_page": None},
        },
        {
            "id": "https://openalex.org/W1000000002",
            "doi": "https://doi.org/10.2514/6.2026-0001",
            "title": "Supercritical water oxidation reactor modeling",
            "publication_year": 2026,
            "type": "article",
            "authorships": [
                {
                    "author_position": "first",
                    "author": {"id": "https://openalex.org/A3", "display_name": "Jane Doe", "orcid": None},
                    "institutions": [],
                    "raw_author_name": "Jane Doe",
                },
                {
                    "author_position": "last",
                    "author": {"id": "https://openalex.org/A1", "display_name": "Yuhao Xu", "orcid": f"https://orcid.org/{ORCID}"},
                    "institutions": [{"display_name": "Clemson University"}],
                    "raw_author_name": "Y. Xu",
                },
            ],
            "primary_location": {"source": {"display_name": "AIAA SCITECH 2026 Forum", "type": "conference", "host_organization_name": "AIAA"}},
            "biblio": {"volume": None, "issue": None, "first_page": None, "last_page": None},
        },
        {
            "id": "https://openalex.org/W1000000004",
            "doi": "https://doi.org/10.48550/arxiv.2607.00001",
            "title": "Flame segmentation with foundation models",
            "publication_year": 2026,
            "type": "preprint",
            "authorships": [
                {
                    "author_position": "first",
                    "author": {"id": "https://openalex.org/A1", "display_name": "Yuhao Xu", "orcid": f"https://orcid.org/{ORCID}"},
                    "institutions": [],
                    "raw_author_name": "Yuhao Xu",
                }
            ],
            "primary_location": {"source": {"display_name": "arXiv (Cornell University)", "type": "repository", "host_organization_name": "Cornell University"}},
            "biblio": {},
        },
        {
            "id": "https://openalex.org/W1000000003",
            "doi": None,
            "title": "A work without a DOI",
            "publication_year": 2024,
            "type": "article",
            "authorships": [],
        },
    ],
}

CROSSREF_BIBTEX = (
    " @article{Xu_2025, title={Cool flame <mml:math>n</mml:math>-heptane droplets &amp; soot}, volume={271}, "
    "ISSN={0010-2180}, url={http://dx.doi.org/10.1016/j.combustflame.2025.114000}, DOI={10.1016/j.combustflame.2025.114000}, "
    "journal={Combustion and Flame}, publisher={Elsevier BV}, author={Xu, Yuhao and Avedisian, C. Thomas}, year={2025}, "
    "month=jan, pages={114000} }"
)

EXISTING_BIB = """@article{old2019,
  title = {Something older},
  author = {Xu, Yuhao},
  year = {2019},
  doi = {https://doi.org/10.1000/OLD.1},
}
"""


class FakeFetch:
    def __init__(self, crossref_ok=True):
        self.calls = []
        self.headers = []
        self.crossref_ok = crossref_ok
        self.extra_openalex = []
        self.crossref_extra = {}

    def __call__(self, url, accept="application/json", retries=3, headers=None):
        self.calls.append(url)
        self.headers.append(headers or {})
        if url.startswith(f"{up.OPENALEX}/works/doi:"):
            doi = urllib.parse.unquote(url.split("/works/doi:")[1])
            for record in OPENALEX_PAGE["results"] + self.extra_openalex:
                if up.normalize_doi(record.get("doi")) == doi:
                    return 200, json.dumps(record)
            return 404, "not found"
        if url.startswith(up.OPENALEX):
            return 200, json.dumps({"meta": {"next_cursor": None}, "results": OPENALEX_PAGE["results"] + self.extra_openalex})
        if url.startswith(up.CROSSREF) and url.split("?")[0].endswith("/transform/application/x-bibtex"):
            doi = urllib.parse.unquote(url.split("/works/")[1].split("/transform")[0])
            if self.crossref_ok and doi == "10.1016/j.combustflame.2025.114000":
                return 200, CROSSREF_BIBTEX
            if doi in self.crossref_extra:
                return 200, self.crossref_extra[doi]
            return 404, "Resource not found."
        if url.startswith(up.CROSSREF):
            return 404, "Resource not found."
        raise AssertionError(f"unexpected URL {url}")


class HelpersTest(unittest.TestCase):
    def test_normalize_doi(self):
        self.assertEqual(up.normalize_doi("https://doi.org/10.1016/J.X.1"), "10.1016/j.x.1")
        self.assertEqual(up.normalize_doi("doi: 10.1/ABC"), "10.1/abc")
        self.assertEqual(up.normalize_doi("http://dx.doi.org/10.2/x"), "10.2/x")
        self.assertIsNone(up.normalize_doi(None))

    def test_existing_dois_and_keys(self):
        self.assertEqual(up.existing_dois(EXISTING_BIB), {"10.1000/old.1"})
        self.assertEqual(up.existing_keys(EXISTING_BIB), {"old2019"})

    def test_parse_crossref_entry(self):
        entry_type, key, fields = up.parse_bibtex_entry(CROSSREF_BIBTEX)
        self.assertEqual((entry_type, key), ("article", "Xu_2025"))
        self.assertEqual(fields["month"], "jan")
        self.assertEqual(fields["author"], "Xu, Yuhao and Avedisian, C. Thomas")
        self.assertEqual(fields["pages"], "114000")

    def test_make_key_unique(self):
        taken = {"xu2025cool"}
        self.assertEqual(up.make_key("Yuhao Xu", 2025, "Cool flames", taken), "xu2025coola")
        self.assertEqual(up.make_key("Müller, Jörg", 2024, "The effect of", set()), "muller2024effect")

    def test_clean_text_keeps_encoded_less_than(self):
        self.assertEqual(up.clean_text("Flow at Re &lt; 1 and We &gt; 10 in <mml:math>n</mml:math>-heptane"), "Flow at Re < 1 and We > 10 in n-heptane")
        self.assertEqual(up.clean_text("<jats:italic>n</jats:italic>-decane &amp; air"), "n-decane & air")

    def test_balance_braces(self):
        self.assertEqual(up.balance_braces("{GPU} flames"), "{GPU} flames")
        self.assertEqual(up.balance_braces("Measuring the }-shaped front"), "Measuring the -shaped front")
        self.assertEqual(up.balance_braces("open { brace"), "open  brace")

    def test_escape(self):
        self.assertEqual(up.escape_bibtex("A & B 50% #1 a_b"), r"A \& B 50\% \#1 a\_b")
        self.assertEqual(up.escape_bibtex(r"already \& fine"), r"already \& fine")

    def test_config_parser_without_yaml(self):
        text = (
            'orcid: "0000-0002-1825-0097"   # comment\n'
            "openalex_author_ids: []\n"
            "work_types: [article, review]\n"
            "ignore_dois:\n"
            '  - "10.1/abc"\n'
            "  - 10.2/def\n"
            "venue_abbreviations:\n"
            '  "Combustion and Flame": "CNF"\n'
            "empty:\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as fh:
            fh.write(text)
        real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

        def no_yaml(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError
            return real_import(name, *args, **kwargs)

        import builtins

        builtins.__import__ = no_yaml
        try:
            config = up.load_config(Path(fh.name))
        finally:
            builtins.__import__ = real_import
        self.assertEqual(config["orcid"], "0000-0002-1825-0097")
        self.assertEqual(config["openalex_author_ids"], [])
        self.assertEqual(config["work_types"], ["article", "review"])
        self.assertEqual(config["ignore_dois"], ["10.1/abc", "10.2/def"])
        self.assertEqual(config["venue_abbreviations"], {"Combustion and Flame": "CNF"})
        self.assertIsNone(config["empty"])

    def test_config_parser_unindented_list(self):
        # The GitHub web editor makes it easy to write list items at column 0, which YAML accepts.
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as fh:
            fh.write('orcid: "x"\nignore_dois:\n- "10.1/abc"\n- 10.2/def\nmailto: ""\n')
        import builtins

        real_import = builtins.__import__

        def no_yaml(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError
            return real_import(name, *args, **kwargs)

        builtins.__import__ = no_yaml
        try:
            config = up.load_config(Path(fh.name))
        finally:
            builtins.__import__ = real_import
        self.assertEqual(config["ignore_dois"], ["10.1/abc", "10.2/def"])
        self.assertEqual(config["mailto"], "")
        self.assertEqual(config["orcid"], "x")


class RunTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.bib = self.dir / "papers.bib"
        self.bib.write_text(EXISTING_BIB, encoding="utf-8")
        self.config = self.dir / "sync.yml"
        self.config.write_text(
            f'orcid: "{ORCID}"\nwork_types: []\nvenue_abbreviations:\n  "Combustion and Flame": "CNF"\nignore_dois:\n',
            encoding="utf-8",
        )
        self.summary = self.dir / "summary.md"

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_script(self, *extra, fetch=None):
        fetch = fetch or FakeFetch()
        code = up.run(["--config", str(self.config), "--bib", str(self.bib), "--summary", str(self.summary), *extra], fetch=fetch)
        return code, fetch

    def test_adds_new_entries_crossref_then_openalex_fallback(self):
        code, fetch = self.run_script()
        self.assertEqual(code, 0)
        text = self.bib.read_text(encoding="utf-8")
        self.assertIn(up.MARKER, text)
        # Crossref entry: key rewritten, junk fields dropped, markup stripped, DOI normalised.
        self.assertIn("@article{xu2025cool,", text)
        flat = re.sub(r" +", " ", text)
        self.assertIn(r"title = {Cool flame n-heptane droplets \& soot},", flat)
        self.assertNotIn("ISSN", text)
        self.assertNotIn("month", text)
        self.assertIn("doi = {10.1016/j.combustflame.2025.114000}", flat)
        self.assertIn("abbr = {CNF}", flat)
        # Conference paper falls back to OpenAlex metadata.
        self.assertIn("@inproceedings{doe2026supercritical,", text)
        self.assertIn("booktitle = {AIAA SCITECH 2026 Forum}", flat)
        self.assertIn("author = {Doe, Jane and Xu, Yuhao}", flat)
        # Preprint falls back to @misc with the venue in `note` (what the site's layout displays).
        self.assertIn("@misc{xu2026flame,", text)
        self.assertIn("note = {arXiv (Cornell University)}", flat)
        # Work without DOI ignored; pre-existing entry untouched.
        self.assertNotIn("without a DOI", text)
        self.assertTrue(text.startswith(EXISTING_BIB))
        summary = self.summary.read_text(encoding="utf-8")
        self.assertIn("Y. Xu (last; Clemson University)", summary)
        self.assertIn("| OpenAlex |", summary)
        self.assertTrue(any(f"authorships.author.orcid:{ORCID}" in c for c in fetch.calls))

    def test_idempotent(self):
        self.run_script()
        first = self.bib.read_text(encoding="utf-8")
        self.summary.unlink()
        self.run_script()
        self.assertEqual(first, self.bib.read_text(encoding="utf-8"))
        self.assertFalse(self.summary.exists())

    def test_ignore_list(self):
        self.config.write_text(f'orcid: "{ORCID}"\nignore_dois:\n  - "https://doi.org/10.2514/6.2026-0001"\n', encoding="utf-8")
        self.run_script()
        text = self.bib.read_text(encoding="utf-8")
        self.assertNotIn("Supercritical water oxidation", text)
        self.assertIn("xu2025cool", text)
        self.assertIn("DOIs skipped via ignore list: 1", self.summary.read_text(encoding="utf-8"))

    def test_title_match_without_doi_is_skipped(self):
        # A conference paper typed in by hand (no DOI, different capitalisation/markup) must not come back.
        self.bib.write_text(
            EXISTING_BIB + "\n@inproceedings{manual2026,\n  title = {{Supercritical} Water Oxidation Reactor Modeling},\n  year = {2026},\n}\n",
            encoding="utf-8",
        )
        self.run_script()
        text = self.bib.read_text(encoding="utf-8")
        self.assertNotIn("doe2026supercritical", text)
        self.assertIn("xu2025cool", text)
        # ...and its missing DOI is filled in from OpenAlex.
        self.assertIn("@inproceedings{manual2026,\n  doi = {10.2514/6.2026-0001},\n  title =", text)
        self.assertIn("DOIs added to existing entries", self.summary.read_text(encoding="utf-8"))
        self.assertEqual(text.count("10.2514/6.2026-0001"), 1)

    def test_only_doi_fill_still_writes(self):
        self.bib.write_text(
            EXISTING_BIB
            + "\n@inproceedings{manual2026,\n  title = {Supercritical water oxidation reactor modeling},\n}\n"
            + "\n@article{have,\n  title = {x},\n  doi = {10.1016/j.combustflame.2025.114000},\n}\n"
            + "\n@misc{have2,\n  title = {y},\n  doi = {10.48550/arxiv.2607.00001},\n}\n",
            encoding="utf-8",
        )
        self.run_script()
        text = self.bib.read_text(encoding="utf-8")
        self.assertNotIn(up.MARKER, text)
        self.assertIn("doi = {10.2514/6.2026-0001}", text)
        self.assertTrue(self.summary.exists())

    def test_title_fingerprint(self):
        self.assertEqual(up.title_fingerprint(r"Cool flame \textit{n}-heptane \& soot"), up.title_fingerprint("Cool Flame n-Heptane & Soot"))
        self.assertNotEqual(up.title_fingerprint("Cool flames"), up.title_fingerprint("Hot flames"))

    def test_datacite_doi_falls_back_to_openalex_single_work(self):
        # arXiv DOIs are registered with DataCite, so Crossref has nothing; OpenAlex's /works/doi: does.
        code, fetch = self.run_script("--doi", "10.48550/arXiv.2607.00001")
        self.assertEqual(code, 0)
        self.assertIn("@misc{xu2026flame,", self.bib.read_text(encoding="utf-8"))
        self.assertTrue(any("/works/doi:10.48550/arxiv.2607.00001" in c for c in fetch.calls))

    def test_unknown_doi_fails_loudly(self):
        code, _ = self.run_script("--doi", "10.9999/does-not-exist")
        self.assertEqual(code, 1)
        self.assertEqual(self.bib.read_text(encoding="utf-8"), EXISTING_BIB)

    def test_semicolon_doi_is_not_split(self):
        _, fetch = self.run_script("--doi", "10.1002/(SICI)1097-0258(19980815/30)17:15/16<1661::AID-SIM968>3.0.CO;2-2")
        self.assertTrue(any("3.0.co%3B2-2" in c or "3.0.co;2-2" in c for c in fetch.calls))

    def test_journal_version_of_existing_preprint_is_proposed_and_flagged(self):
        self.bib.write_text(
            EXISTING_BIB + "\n@misc{xu2024pre,\n  title = {Cool flame n-heptane droplets \\& soot},\n  doi = {10.2139/ssrn.1},\n}\n",
            encoding="utf-8",
        )
        self.run_script()
        text = self.bib.read_text(encoding="utf-8")
        self.assertIn("@article{xu2025cool,", text)
        self.assertIn("same title as existing `xu2024pre`", self.summary.read_text(encoding="utf-8"))

    def test_preprint_doi_is_not_filled_into_hand_entered_article(self):
        self.bib.write_text(
            EXISTING_BIB + "\n@article{hand2026,\n  title = {Flame segmentation with foundation models},\n  journal = {Fuel},\n}\n",
            encoding="utf-8",
        )
        self.run_script()
        text = self.bib.read_text(encoding="utf-8")
        self.assertNotIn("@article{hand2026,\n  doi", text)
        self.assertIn("@misc{xu2026flame,", text)
        self.assertIn("same title as existing `hand2026`", self.summary.read_text(encoding="utf-8"))

    def test_crossref_inbook_and_entities(self):
        fetch = FakeFetch()
        fetch.extra_openalex = [
            {
                "id": "https://openalex.org/W9",
                "doi": "https://doi.org/10.1007/978-3-030-00000-0_5",
                "title": "Droplets in low gravity",
                "publication_year": 2026,
                "type": "book-chapter",
                "authorships": [
                    {"author_position": "first", "author": {"id": "A1", "display_name": "Yuhao Xu", "orcid": ORCID}, "institutions": [None]}
                ],
            }
        ]
        fetch.crossref_extra = {
            "10.1007/978-3-030-00000-0_5": "@inbook{Xu_2026, title={Droplets in low gravity at Re &lt; 1}, "
            "booktitle={Energy &amp; Fuels Handbook}, publisher={Springer}, author={Xu, Yuhao}, year={2026}}"
        }
        self.config.write_text(f'orcid: "{ORCID}"\nvenue_abbreviations:\n  "Energy & Fuels Handbook": "EFH"\n', encoding="utf-8")
        self.run_script(fetch=fetch)
        flat = re.sub(r" +", " ", self.bib.read_text(encoding="utf-8"))
        self.assertIn("@incollection{xu2026droplets,", flat)
        self.assertIn("title = {Droplets in low gravity at Re < 1}", flat)
        self.assertIn(r"booktitle = {Energy \& Fuels Handbook}", flat)
        self.assertIn("abbr = {EFH}", flat)

    def test_near_identical_title_gets_the_doi(self):
        # CV working title vs. published title: fill the DOI instead of adding a duplicate.
        self.bib.write_text(
            EXISTING_BIB
            + "\n@article{cv2025,\n  title = {Cool Flames of n-Heptane Droplets and Soot},\n  year = {2025},\n}\n"
            + "\n@inproceedings{cv2025conf,\n  title = {Cool flame n-heptane droplets and soot},\n  year = {2024},\n  doi = {10.1/x},\n}\n",
            encoding="utf-8",
        )
        self.run_script("--doi", "10.1016/j.combustflame.2025.114000")
        text = self.bib.read_text(encoding="utf-8")
        self.assertIn("@article{cv2025,\n  doi = {10.1016/j.combustflame.2025.114000},", text)
        self.assertNotIn("xu2025cool", text)
        self.assertIn("Check that each pair of titles is the same paper", self.summary.read_text(encoding="utf-8"))

    def test_similar_but_different_title_is_not_merged(self):
        self.bib.write_text(EXISTING_BIB + "\n@article{other2025,\n  title = {Hot flame n-octane sprays and smoke},\n  year = {2025},\n}\n", encoding="utf-8")
        self.run_script("--doi", "10.1016/j.combustflame.2025.114000")
        text = self.bib.read_text(encoding="utf-8")
        self.assertIn("@article{xu2025cool,", text)
        self.assertNotIn("@article{other2025,\n  doi", text)

    def test_key_taken_in_another_bib_file_is_not_reused(self):
        (self.dir / "presentations.bib").write_text("@inproceedings{xu2025cool,\n  title = {A talk},\n  year = {2025},\n}\n", encoding="utf-8")
        self.run_script()
        text = self.bib.read_text(encoding="utf-8")
        self.assertIn("@article{xu2025coola,", text)
        self.assertNotIn("@article{xu2025cool,", text)

    def test_dry_run_changes_nothing(self):
        self.run_script("--dry-run")
        self.assertEqual(self.bib.read_text(encoding="utf-8"), EXISTING_BIB)

    def test_api_key_is_sent_when_set(self):
        import os

        os.environ["OPENALEX_API_KEY"] = "secret123"
        try:
            _, fetch = self.run_script("--dry-run")
        finally:
            del os.environ["OPENALEX_API_KEY"]
        openalex = [h for c, h in zip(fetch.calls, fetch.headers) if c.startswith(up.OPENALEX)]
        self.assertTrue(openalex and all(h.get("Authorization") == "Bearer secret123" for h in openalex))
        self.assertFalse(any("secret123" in c for c in fetch.calls))

    def test_add_by_doi_skips_the_orcid_scan(self):
        _, fetch = self.run_script("--doi", "https://doi.org/10.1016/J.COMBUSTFLAME.2025.114000, 10.1000/old.1")
        self.assertFalse(any("filter=" in c for c in fetch.calls))
        text = self.bib.read_text(encoding="utf-8")
        self.assertEqual(text.count("@article{xu2025cool,"), 1)
        self.assertEqual(text.count("old2019"), 1)


if __name__ == "__main__":
    unittest.main()
