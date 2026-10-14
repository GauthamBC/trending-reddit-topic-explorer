"""Reddit read-only client and bounded on-demand collection."""
import os
import re
import time


def get_credentials(secrets):
    """Support nested PRAW and legacy top-level Streamlit secret names."""
    try:
        source = dict(secrets)
    except (FileNotFoundError, KeyError, AttributeError, RuntimeError):
        source = {}
    nested = source.get("reddit", {})
    def get(*names):
        for name in names:
            v = nested.get(name) if hasattr(nested, "get") else None
            if not v:
                v = source.get(name)
            if not v:
                v = os.getenv(name)
            if v:
                return str(v)
        return ""
    return {
        "client_id": get("client_id", "REDDIT_CLIENT_ID", "reddit_client_id", "CLIENT_ID"),
        "client_secret": get("client_secret", "REDDIT_CLIENT_SECRET", "reddit_client_secret", "CLIENT_SECRET"),
        "user_agent": get("user_agent", "REDDIT_USER_AGENT", "reddit_user_agent", "USER_AGENT") or "script:reddit-trend-explorer:1.0 (read-only dashboard)",
    }


def make_client(credentials):
    import praw  # Deferred so pure logic can be tested without PRAW installed.
    return praw.Reddit(
        client_id=credentials["client_id"], client_secret=credentials["client_secret"],
        user_agent=credentials["user_agent"],
        check_for_async=False,
    )


def fetch_posts(credentials, candidates, window="day", per_sub=18):
    """Fetch bounded subreddit listings. Does not use search scraping or comment data.

    Returns normalized posts, skipped communities, and candidate sources.
    """
    from engine import normalized_post
    reddit = make_client(credentials)
    found = {}
    failures = []
    sources = {item["name"].lower(): item["source"] for item in candidates}
    for item in candidates:
        name = item["name"]
        if not re.fullmatch(r"[A-Za-z0-9_]{2,21}", name):
            failures.append((name, "Invalid subreddit name"))
            continue
        try:
            sub = reddit.subreddit(name)
            # Recent submissions + top submissions within the selected window.
            # Do not request all comments; no author profiles are queried.
            for listing in (sub.new(limit=per_sub), sub.top(time_filter=window, limit=per_sub)):
                for submission in listing:
                    record = normalized_post(submission)
                    found[record["id"]] = record
        except Exception as ex:
            # Keep errors out of the dashboard where they might expose credentials.
            kind = type(ex).__name__
            failures.append((name, f"Fetch failed ({kind})"))
            if kind in ("TooManyRequests", "RateLimitExceeded") or "429" in str(ex):
                failures.append(("API", "Reddit rate limit reached; retry after a short wait"))
                break
            if kind in ("ResponseException", "OAuthException") and ("401" in str(ex)):
                failures.append(("API", "Authentication failed; verify Streamlit secrets and app permissions"))
                break
        # Respect Reddit's rate-limit headers via PRAW; avoid additional waits by default.
    return list(found.values()), failures, sources
