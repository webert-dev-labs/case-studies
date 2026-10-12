import copy
import json
import re
from html import escape
from pathlib import Path

import pytest

import build_site

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def data():
    return build_site.load_data(ROOT / "cases.json")


def test_repository_data_is_valid(data):
    assert data["cases"], "cases.json must list at least one case"


def test_every_case_is_rendered_with_links(data):
    page = build_site.render(data)
    for case in data["cases"]:
        assert f'id="{case["slug"]}"' in page
        assert f'{data["site"]["repo_url"]}/tree/main/{case["path"]}' in page
        assert escape(case["title"]) in page


def test_referenced_files_exist(data):
    for case in data["cases"]:
        assert (ROOT / "docs" / case["image"]).is_file()
        if case.get("demo"):
            assert (ROOT / "docs" / case["demo"]).is_file()
        assert (ROOT / case["path"]).is_dir()


def test_text_is_escaped(data):
    evil = copy.deepcopy(data)
    evil["cases"][0]["title"] = "<script>alert(1)</script>"
    page = build_site.render(evil)
    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_page_has_no_external_resources(data):
    page = build_site.render(data)
    # Only plain links may point outside; nothing is loaded from other hosts.
    assert not re.search(r'(src|srcset)="https?://', page)
    assert "<script" not in page
    # The only <link> allowed is the canonical URL, which loads nothing.
    assert re.findall(r"<link [^>]*>", page) == [
        f'<link rel="canonical" href="{data["site"]["site_url"]}">'
    ]


def test_social_preview_meta(data):
    site = data["site"]
    page = build_site.render(data)
    assert (ROOT / "docs" / site["social_image"]).is_file()
    assert f'<meta property="og:image" content="{site["site_url"]}{site["social_image"]}">' in page
    assert '<meta name="twitter:card" content="summary_large_image">' in page


def test_security_headers(data):
    page = build_site.render(data)
    assert f'<meta http-equiv="Content-Security-Policy" content="{build_site.CSP}">' in page
    assert "default-src 'none'" in build_site.CSP
    assert '<meta name="referrer" content="no-referrer">' in page


def test_published_images_carry_no_text_metadata():
    for png in (ROOT / "docs").rglob("*.png"):
        data = png.read_bytes()
        assert b"tEXt" not in data and b"iTXt" not in data and b"eXIf" not in data, png


def test_page_does_not_advertise_case_count(data):
    # A visible count or a "more coming" line makes a small portfolio look unfinished.
    page = build_site.render(data)
    assert "case study ·" not in page.lower() and "1 case study" not in page
    assert "on the way" not in page
    assert page.count('class="case"') == len(data["cases"])


@pytest.mark.parametrize("field", ["title", "problem", "image"])
def test_missing_field_is_reported(tmp_path, data, field):
    broken = copy.deepcopy(data)
    del broken["cases"][0][field]
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(ValueError, match=field):
        build_site.load_data(path)


def test_duplicate_slug_is_rejected(tmp_path, data):
    dup = copy.deepcopy(data)
    dup["cases"].append(copy.deepcopy(dup["cases"][0]))
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(dup), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        build_site.load_data(path)


def test_image_fit_is_rendered_and_validated(tmp_path, data):
    page = build_site.render(data)
    for case in data["cases"]:
        assert f'class="case-media fit-{case.get("image_fit", "cover")}"' in page
    bad = copy.deepcopy(data)
    bad["cases"][0]["image_fit"] = "stretch"
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="image_fit"):
        build_site.load_data(path)


def test_generated_page_is_up_to_date(data):
    assert (ROOT / "docs" / "index.html").read_text(encoding="utf-8") == build_site.render(data), (
        "docs/index.html is stale: run `python tools/build_site.py`"
    )
