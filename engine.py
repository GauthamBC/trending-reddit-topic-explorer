"""Pure data logic for Reddit Trend Explorer.

No user IDs or comment bodies are collected or stored. Scores are a snapshot
of attention in the sampled communities, NOT claims of population-level trends.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import math
import re

from regions import KEYWORDS, region_phrases, sport_entity_phrases

# Common filler words. Topic terms are exploratory keyword clusters, not entity recognition.
STOPWORDS = set("""
a an the this that those these of in on at by for from with without to and or but
is are was were be been being has have had did do does will would can could should
i we you he she it they them our us my your their its who what why when where how
which anyone everyone someone something anything everything here's here's here's
more most very much many just about after before while into onto between over under
not no yes if then than as so too also only even still again back there here
new old good bad better best worse worst big small really think thought know
looks look got get getting gets make made makes much first last next right left
now today yesterday tomorrow week month year years days day hours hour one two
three four five six seven eight nine ten all any some another other people person
thread reddit subreddit comments comment discussion discusses discussing question
questions post posted posting opinion opinions official megathread daily weekly
video image photo photos link watch live highlights highlight reaction reactions
anyone else does did was why what this their they when game games match matches
vs versus team teams player players season seasons win wins winning lose lost
fans fan take takes hot top breaking update updates report reports news
""".split())
TOKEN = re.compile(r"[a-z][a-z0-9']{2,}", re.I)


def elapsed_hours(created_utc: float, now: float | None = None) -> float:
    now = now or datetime.now(timezone.utc).timestamp()
    return max(0.1, (now - float(created_utc)) / 3600)


def compute_heat(score: int, comments: int, age_hours: float) -> float:
    """Recent activity proxy; comparable only within one selected window."""
    impact = max(0, score) + max(0, comments) * 3
    return round(100 * math.log1p(impact) / (max(1, age_hours) + 2) ** 0.55, 2)


def normalized_post(post, now=None):
    """Convert a PRAW submission into a minimal serializable record."""
    age = elapsed_hours(post.created_utc, now)
    link = str(getattr(post, "permalink", ""))
    if not re.match(r"^/r/[A-Za-z0-9_]+/comments/[A-Za-z0-9_]+/", link):
        link = ""
    return {
        "id": str(post.id), "title": str(post.title),
        "subreddit": str(post.subreddit.display_name),
        "created_utc": float(post.created_utc),
        "score": int(post.score or 0), "comments": int(post.num_comments or 0),
        "age_hours": round(age, 1),
        "heat": compute_heat(int(post.score or 0), int(post.num_comments or 0), age),
        "flair": str(post.link_flair_text or ""),
        "url": "https://www.reddit.com" + link if link else "",
        "nsfw": bool(post.over_18),
        "stickied": bool(post.stickied),
    }


def refers_to_region(title, flair, region, category=None):
    text = f"{title} {flair}".lower()
    phrases = region_phrases(region)
    if category == "Sports":
        phrases = phrases + sport_entity_phrases(region)
    for phrase in phrases:
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text):
            return True
    return False


def matches_topic(title, flair, category, topic):
    text = f"{title} {flair}".lower()
    if topic in KEYWORDS:
        return any(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text) for w in KEYWORDS[topic])
    if category == "Sports":
        return any(matches_topic(title, flair, category, t) for t in ("NFL", "NBA", "MLB", "NHL", "College sports", "Soccer"))
    if category == "Entertainment":
        return any(matches_topic(title, flair, category, t) for t in ("Movies", "Television", "Music", "Celebrities"))
    if category == "Technology":
        return any(matches_topic(title, flair, category, t) for t in ("AI", "Gaming", "Consumer tech"))
    if category == "News":
        return True  # Local-news community posts can be about almost any subject.
    return True


def region_and_topic_filter(posts, sources, category, topic, region, cutoff_hours):
    """Only keep posts with an explainable locality match.

    Team subreddits are geographically associated with their franchise, not the
    poster's state. Manual communities are NOT presumed local.
    """
    national = region == "United States (national)"
    now = datetime.now(timezone.utc).timestamp()
    output = []
    for post in posts:
        if post["nsfw"] or post["stickied"] or (now - post["created_utc"]) > cutoff_hours * 3600:
            continue
        kind = sources.get(post["subreddit"].lower(), "global")
        topical = matches_topic(post["title"], post["flair"], category, topic)
        if national:
            # Dedicated category/league subs already imply topic.
            if kind in ("global", "team") or topical:
                locality = "National community"
            else:
                continue
        elif kind == "team":
            locality = "Team associated with state"
        elif kind == "local" and topical:
            locality = "Local subreddit + topic match"
        elif refers_to_region(post["title"], post["flair"], region, category) and (
            kind == "global" or topical
        ):
            locality = "Region named in post"
        else:
            continue
        post = dict(post)
        post["locality"] = locality
        output.append(post)
    output.sort(key=lambda p: p["heat"], reverse=True)
    return output


def _tokens(text):
    return [w.lower().strip("'") for w in TOKEN.findall(text) if w.lower() not in STOPWORDS]


def extract_topics(posts, limit=22):
    """Find recurring keywords and adjacent two-word phrases in sampled titles."""
    doc_counts = Counter()
    weighted = defaultdict(float)
    by_term = defaultdict(list)
    subs = defaultdict(set)
    for post in posts:
        # Using titles only avoids processing bodies or author identity.
        words = _tokens(post["title"])
        terms = set(words)
        terms.update(" ".join(words[i:i+2]) for i in range(len(words) - 1))
        # Exclude trivial short phrases and non-semantic constructions.
        terms = {t for t in terms if len(t) > 3 and not t.isnumeric()}
        for term in terms:
            doc_counts[term] += 1
            weighted[term] += max(1, post["heat"])
            by_term[term].append(post)
            subs[term].add(post["subreddit"].lower())
    min_docs = 2 if len(posts) >= 6 else 1
    candidates = [term for term, count in doc_counts.items() if count >= min_docs and count <= max(2, len(posts)*0.80)]
    # Prefer meaningful recurring phrases but avoid automatically discarding single terms.
    candidates.sort(key=lambda term: (math.log1p(weighted[term]) * (1 + .22*(len(subs[term])-1)) *
                                      (1.15 if " " in term else 1), doc_counts[term]), reverse=True)
    results = []
    for term in candidates:
        # Avoid 'anthony' and 'anthony davis' both as adjacent prominent topic nodes.
        if any(term in existing["term"] and (" " in existing["term"]) and term != existing["term"]
               for existing in results):
            continue
        hits = sorted(by_term[term], key=lambda p: p["heat"], reverse=True)
        results.append({
            "term": term, "posts": len(hits), "communities": len(subs[term]),
            "attention": round(sum(p["heat"] for p in hits), 1),
            "links": [{"title": p["title"], "subreddit": p["subreddit"], "url": p["url"], "heat": p["heat"]} for p in hits[:8]],
            "subreddits": dict(Counter(p["subreddit"] for p in hits)),
        })
        if len(results) >= limit:
            break
    return results


def summarize_subreddits(posts):
    grouped = defaultdict(list)
    for post in posts:
        grouped[post["subreddit"]].append(post)
    return sorted([
        {"Subreddit": "r/" + key, "Posts": len(items),
         "Attention": round(sum(p["heat"] for p in items), 1),
         "Avg. comments": round(sum(p["comments"] for p in items)/len(items), 1),
         "Top post": max(items, key=lambda p: p["heat"])["title"]}
        for key, items in grouped.items()
    ], key=lambda row: row["Attention"], reverse=True)
