import json

import db
from collectors import github

FAKE_REPO = {
    "id": 42,
    "full_name": "acme/agent-kit",
    "html_url": "https://github.com/acme/agent-kit",
    "description": "Build agents",
    "owner": {"login": "acme"},
    "created_at": "2026-09-20T10:00:00Z",
    "stargazers_count": 1234,
    "forks_count": 56,
    "language": "Python",
    "topics": ["ai-agents"],
}


def test_to_item_maps_fields():
    item = github.to_item(FAKE_REPO)
    assert item["source"] == "github"
    assert item["title"] == "acme/agent-kit"
    assert item["metrics"]["stars"] == 1234


def test_build_query_contains_topic_and_date():
    q = github.build_query("llm", days=7)
    assert q.startswith("topic:llm created:>")


def test_save_items_upserts_instead_of_duplicating():
    conn = db.connect(":memory:")
    item = github.to_item(FAKE_REPO)
    db.save_items(conn, [item])
    item["metrics"]["stars"] = 2000  # the repo got more popular
    db.save_items(conn, [item])
    rows = conn.execute("SELECT metrics FROM items").fetchall()
    assert len(rows) == 1
    assert json.loads(rows[0]["metrics"])["stars"] == 2000


def test_sample_data_loads_and_saves():
    conn = db.connect(":memory:")
    items = github.load_sample()
    assert len(items) > 0
    db.save_items(conn, items)
    assert conn.execute("SELECT COUNT(*) FROM items").fetchone()[0] == len(items)
