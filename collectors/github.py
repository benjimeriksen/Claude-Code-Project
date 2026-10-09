"""GitHub collector: finds recently active, fast-growing AI repositories.

We call GitHub's Search API, which returns JSON, and convert each repo into
the common "item" shape that db.save_items() understands.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

SEARCH_URL = "https://api.github.com/search/repositories"

# Each query is one "order" we send to GitHub. Topics are tags repo owners add.
TOPICS = ["llm", "ai-agents", "rag", "generative-ai", "mcp"]


def build_query(topic, days=30, min_stars=50):
    """Repos with this topic, created in the last `days` days, with some stars."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    return f"topic:{topic} created:>{since} stars:>{min_stars}"


def to_item(repo):
    """Translate GitHub's JSON for one repo into our common item shape."""
    return {
        "source": "github",
        "external_id": str(repo["id"]),
        "title": repo["full_name"],
        "url": repo["html_url"],
        "description": repo.get("description"),
        "author": repo["owner"]["login"],
        "published_at": repo["created_at"],
        "metrics": {
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
        },
    }


def collect(topics=TOPICS, per_topic=20, days=30):
    """Fetch trending repos for each topic. Returns a list of items."""
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    items = {}  # keyed by id so a repo matching two topics is kept once
    for topic in topics:
        response = requests.get(
            SEARCH_URL,
            headers=headers,
            params={
                "q": build_query(topic, days=days),
                "sort": "stars",
                "order": "desc",
                "per_page": per_topic,
            },
            timeout=30,
        )
        response.raise_for_status()  # turn HTTP errors into Python errors
        for repo in response.json()["items"]:
            items[repo["id"]] = to_item(repo)
    return list(items.values())


def load_sample():
    """Offline mode: read GitHub-shaped JSON from fixtures/ instead of the network.

    The sample goes through the same to_item() as real data, so it exercises
    the real translation code. Descriptions are tagged "[SAMPLE]".
    """
    path = Path(__file__).parent.parent / "fixtures" / "github_sample.json"
    return [to_item(repo) for repo in json.loads(path.read_text())]
