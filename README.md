# Reddit Trend Explorer

A deployable **Streamlit + PRAW** project for exploring current Reddit discussions by topic and U.S. state. Built for research and editorial discovery. The graph displays recurring topic terms and communities, with source posts accessible on click.

## Highlights

- Sports: NFL, NBA, MLB, NHL, college sports and soccer; Entertainment: movies, TV, music and celebrities; also News and Technology.
- United States nationwide, 50 states and Washington, D.C.
- 24-hour, 7-day and 30-day lookback options.
- Location-aware data filtering, sortable posts, original Reddit links and CSV exports.
- Interactive network: topic ↔ subreddit with clickable post listings.
- Small API footprint, PRAW read-only, deduplicated submissions and a 20-minute cache.
- No fabricated live activity or secret credentials in the repository.

## Deploy from GitHub to Streamlit Community Cloud

1. Upload **all files and directories** to a new GitHub repository, maintaining the `.streamlit/config.toml` file. Do not upload any real secret credentials.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/), select **Create app**, connect the repository and choose `app.py` as the main file.
3. Under **Advanced settings → Secrets**, paste the PRAW credentials using ONE of the supported formats below. On an existing app you can instead update secrets in app settings.
4. Deploy and select **Run live Reddit scan**. The initial connection requires API access that is valid for this use case.

### Recommended secrets format

```toml
[reddit]
client_id = "your-reddit-app-client-id"
client_secret = "your-reddit-app-client-secret"
user_agent = "script:reddit-trend-explorer:v1.0 (by u/YOUR_REDDIT_USERNAME)"
```

### Existing flat secrets also supported

If another Streamlit PRAW tool already uses the following, **you do not need to rename them**:

```toml
REDDIT_CLIENT_ID = "..."
REDDIT_CLIENT_SECRET = "..."
REDDIT_USER_AGENT = "script:reddit-trend-explorer:v1.0 (by u/YOUR_REDDIT_USERNAME)"
```

Also accepts the common lowercase variants `reddit_client_id`, `reddit_client_secret`, and `reddit_user_agent`, and root keys `client_id`, `client_secret`, `user_agent`.

**Important:** Streamlit Community Cloud secrets are *per app* unless you explicitly provision them to the new app; setting them for an older Streamlit project does not automatically make them available to another deployed project. It is fine to reuse the values through each app's separate Secrets configuration.

## Local development

```bash
python -m pip install -r requirements.txt
# Provide secrets in .streamlit/secrets.toml (copy the .example and fill your own)
streamlit run app.py
```

## How results are derived

1. **Discover candidate subreddits:** the project uses editable category and geographical starter lists in `regions.py`, plus manually entered subreddit names. No automated Reddit community search is required; this keeps API use predictable. Broaden the mapping in `regions.py` if desired.
2. **Collect fresh submissions:** for each subreddit, fetch limited `new()` and `top(time_filter=...)` listings and deduplicate by submission ID. Reddit API limits and permissions apply.
3. **Filter to the selected region:** posts from curated team subreddits have a *team-state association*; posts in local general-purpose subreddits must match the selected topic; global and manual sources must have a region/city reference (or a high-confidence sports franchise alias) in the post title/flair. A Reddit community's posters may live anywhere.
4. **Rank attention:** `100 × ln(1 + max(votes,0) + 3 × comments) / (max(age_hours,1) + 2)^0.55`. This emphasises recent engaging discussions. It **does not measure real growth** because it lacks a historical baseline.
5. **Discover topic labels:** repeat occurrences of unigrams and bigrams from post titles. These terms are preliminary clusters and may contain false positives. Always inspect the underlying source posts.
6. **Visualise:** a self-contained HTML graph uses `vis-network` from a public CDN. The browser requires internet access to this CDN to render the network; all Reddit fetching happens server-side through PRAW.

### Important limitations

- This is **not a comprehensive Reddit search**. A selected community can have more eligible posts than the sample cap. To improve recall, increase communities scanned/posts per listing, keeping API rate limits in mind.
- A state's results are about associated teams, location-specific subreddits or direct geographical references, **not verified sentiment among residents**.
- Broader topics and communities can crowd out niche events; human review is needed before using story angles.
- The graph is a relation graph based on current sampled post titles, unlike SayIt's older cross-community commenter graph.
- If a community is private, inaccessible, misspelled or removed, it is skipped and the dashboard flags this. Missing results are not proof there is no discussion.
- Streamlit Cloud's compute and cache are ephemeral. For *rising trends relative to yesterday*, add durable timed snapshots (e.g., Supabase or a permitted database) and compare changes, rather than interpreting current attention as acceleration.
- PRAW credentials **alone do not grant commercial Reddit data usage rights**. Reddit's API terms may require express approval and an agreement for commercial research, even on an internal dashboard. Review [Reddit's official Data API terms](https://redditinc.com/policies/data-api-terms) and [developer access guidance](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data).

## File layout

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface, tabs and CSV downloads |
| `regions.py` | U.S. states, category communities, geography and keyword filters |
| `reddit_client.py` | Credentials, bounded PRAW collection and errors |
| `engine.py` | Post normalization, geography matching, attention scoring and topics |
| `graph.py` | Interactive node network and post detail panel |
| `.streamlit/config.toml` | Visual theme |
| `.streamlit/secrets.toml.example` | Safe credential template, not actual secrets |
| `tests/test_engine.py` | Offline logic tests |

## Edit a category, team or state

All curated lists are in `regions.py`. Add state-affiliated community names to `TEAM_SUBS`, add regional locations to `LOCAL_SUBS`, and add word signals to `KEYWORDS`. The interface will automatically pick these up on the next code deployment.
