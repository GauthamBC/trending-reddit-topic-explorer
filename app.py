"""Streamlit entry point: Reddit Trend Explorer, PRAW read-only edition."""
from datetime import datetime, timezone
from io import StringIO
import re

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from engine import extract_topics, region_and_topic_filter, summarize_subreddits
from graph import build_graph
from reddit_client import fetch_posts, get_credentials
from regions import CATEGORIES, STATES, candidate_subreddits

st.set_page_config(page_title="Reddit Trend Explorer", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
    .stApp {background: #0b1220; color:#edf3fa}
    [data-testid="stSidebar"] {background: #121c2b; border-right:1px solid #26354c}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#dbe7f5}
    h1,h2,h3{letter-spacing:-.04em}
    h1{font-weight:800!important}
    .block-container{padding-top:2rem;max-width:1500px}
    .eyebrow{color:#5db2fa;font-size:12px;font-weight:800;letter-spacing:2px;text-transform:uppercase}
    .subtext{color:#9caec8;font-size:15px;margin-top:-8px;margin-bottom:16px}
    .metricbox{border:1px solid #2a3a51;background:linear-gradient(125deg,#152235,#101a29);border-radius:14px;padding:20px 21px;min-height:118px}
    .metric-label{font-size:12px;color:#a4b4c9;letter-spacing:.03em}
    .metric-value{font-size:30px;color:white;font-weight:780;line-height:1.5}
    .metric-small{font-size:12px;color:#a4b4c9}
    .stTabs [data-baseweb="tab-list"]{gap:24px}
    .stTabs [data-baseweb="tab"]{font-size:15px;padding:14px 6px}
    div[data-testid="stDataFrame"]{border:1px solid #2d3f55;border-radius:9px}
    .status{background:#101f30;border:1px solid #2a405a;border-radius:10px;padding:13px 15px;color:#b8c8dc;font-size:13px}
    a{color:#79bfff}
</style>""", unsafe_allow_html=True)


@st.cache_data(ttl=1200, show_spinner=False)
def collect(_credentials, candidate_tuple, window, per_sub):
    candidates = [{"name": name, "source": source} for name, source in candidate_tuple]
    return fetch_posts(_credentials, candidates, window=window, per_sub=per_sub)


def metric(label, value, sub):
    st.markdown(f'<div class="metricbox"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-small">{sub}</div></div>', unsafe_allow_html=True)


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8-sig")


with st.sidebar:
    st.markdown('### <span style="color:#68b7ff">◉</span> Trend explorer', unsafe_allow_html=True)
    st.caption("Live Reddit discovery · powered by PRAW")
    st.divider()
    category = st.selectbox("Category", list(CATEGORIES), index=0)
    topic = st.selectbox("Topic", CATEGORIES[category])
    region = st.selectbox("U.S. region or state", ["United States (national)", *list(STATES)], index=list(STATES).index("California") + 1)
    period_label = st.select_slider("Lookback period", options=["Last 24 hours", "Last 7 days", "Last 30 days"], value="Last 24 hours")
    st.divider()
    with st.expander("Advanced scanning options"):
        max_subs = st.slider("Communities to scan", min_value=4, max_value=24, value=15, step=1)
        per_sub = st.slider("Posts per listing / community", min_value=8, max_value=40, value=20, step=4)
        manual = st.text_area("Additional subreddits (optional)", placeholder="lakers, nba, LosAngeles", help="Comma- or newline-separated. These are treated as manual sources and do not automatically prove a geographic link.")
    chosen_custom = [x.strip() for x in re.split(r"[\s,]+", manual) if x.strip()]
    invalid_custom = [x for x in chosen_custom if not re.fullmatch(r"(?:r/)?[A-Za-z0-9_]{2,21}", x)]
    candidates = candidate_subreddits(category, topic, region, [x.removeprefix("r/") for x in chosen_custom if x not in invalid_custom], cap=max_subs)
    with st.expander(f"Communities to scan ({len(candidates)})"):
        for c in candidates:
            st.caption(f"r/{c['name']}  ·  {c['source']}")
    if invalid_custom:
        st.warning("Ignored invalid subreddit names: " + ", ".join(invalid_custom[:5]))
    credentials = get_credentials(st.secrets)
    ready = bool(credentials["client_id"] and credentials["client_secret"])
    if not ready:
        st.error("Reddit credentials missing. Add them to Streamlit secrets (see README).")
    pressed = st.button("↗  Run live Reddit scan", use_container_width=True, type="primary", disabled=not ready)
    st.caption("Uses read-only Reddit API calls. A 20-minute cache limits repeated requests.")
    st.divider()
    st.caption("Location = discussion association, not verified user residence. Trend scores are estimates from sampled post engagement.")

st.markdown('<div class="eyebrow">DISCOVER · ANALYSE · FOLLOW THE CONVERSATION</div>', unsafe_allow_html=True)
st.title("Reddit Trend Explorer")
st.markdown('<div class="subtext">See what communities are discussing across sports, entertainment and more, without guessing subreddit names.</div>', unsafe_allow_html=True)

window_settings = {"Last 24 hours": ("day", 24), "Last 7 days": ("week", 24*7), "Last 30 days": ("month", 24*30)}
period_api, cutoff_hours = window_settings[period_label]
params = {"category": category, "topic": topic, "region": region, "period": period_label, "window": period_api, "cutoff": cutoff_hours, "max_subs": max_subs}

if pressed:
    with st.spinner(f"Scanning {len(candidates)} Reddit communities. This can take a little while..."):
        try:
            result = collect(credentials, tuple((c["name"], c["source"]) for c in candidates), period_api, per_sub)
            fetched, failures, sources = result
            posts = region_and_topic_filter(fetched, sources, category, topic, region, cutoff_hours)
            st.session_state["last_scan"] = {
                "posts": posts, "failures": failures, "sources": sources, "scanned": len(candidates),
                "fetched": len(fetched), "timestamp": datetime.now(timezone.utc).isoformat(), "params": params,
            }
        except Exception as error:
            st.error(f"The Reddit API request could not be completed ({type(error).__name__}). Please check your app credentials, API access and rate limits.")

scan = st.session_state.get("last_scan")
if scan is None:
    st.info("Select a category, topic and state in the sidebar, then choose **Run live Reddit scan**. Nothing is simulated: the results will come from your Reddit API credentials.")
    a, b, c = st.columns(3)
    with a: metric("Categories", "4", "Sports, entertainment, news, tech")
    with b: metric("Geography", "50 states", "Plus D.C. and nationwide")
    with c: metric("Network", "Interactive", "Topics ↔ communities ↔ posts")
    st.markdown("### How the explorer works")
    st.markdown("The scanner starts with curated category and regional communities, collects recent public submissions through PRAW, scores activity, extracts recurring title keywords and creates an interactive topic network. It never claims subreddit participation equals residents of the selected state.")
    st.stop()

scanned_params = scan["params"]
if scanned_params != params:
    st.warning("Your filters have changed since the last scan. The dashboard still shows the previous scan. Click **Run live Reddit scan** to update it.")

posts = scan["posts"]
failures = scan["failures"]
topics = extract_topics(posts)
sub_data = summarize_subreddits(posts)
st.markdown(f'<div class="status">Showing <b>{scanned_params["category"]} / {scanned_params["topic"]} / {scanned_params["region"]}</b> · {scanned_params["period"]} · scanned at {pd.Timestamp(scan["timestamp"]).strftime("%d %b %Y, %H:%M UTC")} · {scan["fetched"]} sampled submissions before relevance filtering.</div>', unsafe_allow_html=True)
st.write("")

col_a,col_b,col_c,col_d = st.columns(4)
with col_a: metric("Relevant posts", f"{len(posts):,}", "Within the selected window")
with col_b: metric("Active communities", f"{len(sub_data):,}", "Appearing in relevant posts")
with col_c: metric("Repeated topics", f"{len(topics):,}", "From post-title phrases")
with col_d: metric("Most discussed", f"{max(posts, key=lambda p: p['comments'])['comments']:,}" if posts else "0", "Comments on top commented post")

if failures:
    with st.expander(f"⚠️  {len(failures)} collection warnings (some communities could not be fetched)"):
        for name, msg in failures:
            st.caption(f"r/{name}: {msg}")

if not posts:
    st.warning("No matching recent posts were found in the scanned sample. Try a wider time window, more communities, a broader topic, or another region. Some states and entertainment categories have limited geographically explicit discussion data.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["◈ Topic network", "↗ Trending topics", "▤ Posts & sources", "▥ Communities & methodology"])
with tab1:
    st.subheader("How the conversation connects")
    st.caption("Drag the graph to explore. Pink nodes are recurring discussion keywords; blue nodes are communities. Click either to open the relevant source posts on the right.")
    if topics:
        components.html(build_graph(posts, topics), height=626, scrolling=False)
    else:
        st.info("Not enough repeated phrases for a connected graph. See the posts tab for individual discussions.")

with tab2:
    st.subheader("Recurring discussion topics")
    st.caption("Ranked by recent activity across sampled posts, not verified audience size, acceleration or cross-platform popularity. Some terms may refer to the same event.")
    if topics:
        topic_df = pd.DataFrame([{"Topic": t["term"].title(), "Mentions": t["posts"], "Communities": t["communities"], "Attention score": t["attention"]} for t in topics])
        st.dataframe(topic_df, hide_index=True, use_container_width=True, height=min(600, 55+35*len(topic_df)))
        chart_df = topic_df.head(12).sort_values("Attention score", ascending=True).set_index("Topic")[["Attention score"]]
        st.bar_chart(chart_df, horizontal=True, height=430)
        selected = st.selectbox("Inspect a topic", [t["term"] for t in topics], format_func=str.title)
        t = next(x for x in topics if x["term"] == selected)
        st.markdown(f"**{t['posts']} sampled posts across {t['communities']} communities**")
        for p in t["links"][:8]:
            if p["url"]:
                st.markdown(f"- [{p['title']}]({p['url']}) · r/{p['subreddit']}")
    else:
        st.info("Not enough recurring terms in this sample. Open the posts tab instead.")

with tab3:
    st.subheader("Posts behind the trends")
    st.caption("Every result has a Reddit source link. The heat score weights votes and comments against post age, and is comparable only within this scan.")
    q1, q2, q3 = st.columns([2, 1, 1])
    with q1: search = st.text_input("Search post titles", placeholder="Team, player, film, news event...")
    with q2: communities = st.multiselect("Communities", sorted({p["subreddit"] for p in posts}), placeholder="All communities")
    with q3: sorting = st.selectbox("Sort posts", ["Attention score", "Comments", "Votes", "Newest"])
    display = [p for p in posts if (not search or search.lower() in p["title"].lower()) and (not communities or p["subreddit"] in communities)]
    keys = {"Attention score":"heat", "Comments":"comments", "Votes":"score", "Newest":"created_utc"}
    display.sort(key=lambda p: p[keys[sorting]], reverse=True)
    if display:
        df = pd.DataFrame([{
            "Title": p["title"], "Community": "r/"+p["subreddit"], "Votes": p["score"],
            "Comments": p["comments"], "Attention": p["heat"],
            "Age (h)": p["age_hours"], "Local evidence": p["locality"], "Post": p["url"],
        } for p in display])
        st.dataframe(df, hide_index=True, use_container_width=True, height=590,
                     column_config={"Title": st.column_config.TextColumn(width="large"),
                                    "Post": st.column_config.LinkColumn("Reddit", display_text="Open ↗"),
                                    "Attention": st.column_config.NumberColumn(format="%.1f"),
                                    "Age (h)": st.column_config.NumberColumn(format="%.1f")})
        st.download_button("↓ Export visible posts (CSV)", data=csv_bytes(df),
                           file_name="reddit_trends_posts.csv", mime="text/csv")
    else:
        st.info("No posts match the search/filter combination.")

with tab4:
    st.subheader("Community activity")
    st.caption("Communities with more posts or engagement may dominate. Do not interpret this as a population-weighted state survey.")
    st.dataframe(pd.DataFrame(sub_data), use_container_width=True, hide_index=True,
                 column_config={"Top post": st.column_config.TextColumn(width="large")})
    st.download_button("↓ Export communities (CSV)", data=csv_bytes(pd.DataFrame(sub_data)),
                       file_name="reddit_trends_communities.csv", mime="text/csv")
    st.subheader("How to interpret the results")
    st.markdown("""- **Source:** Reddit public post metadata via PRAW (OAuth); no comments, author details or personal profiles collected.
- **Coverage:** Curated local, team and broad-category communities, plus optional manual communities. This is a bounded sample, not all Reddit posts.
- **Locality:** Posts in a team community are associated with a state through that team; posts in local communities are included only when their titles or flair match the category; national/manual posts need a region named in the title or flair. This is not verified poster geolocation.
- **Attention score:** `100 × ln(1 + max(votes,0) + 3 × comments) / (max(age_hours,1) + 2)^0.55`. A heuristic, not Reddit's official trending metric.
- **Topics:** Recurring unigrams and two-word phrases from titles. Two topics can represent the same underlying event; review original links before publishing.
- **Not measured:** Unique viewers, public opinion, community demographics, velocity changes between historical snapshots, or independent corroboration.
- **Responsible use:** Commercial API access requires the applicable Reddit approval and licence; respect API rate limits, content deletion and platform terms. Avoid quoting Reddit posts without source checks.
""")

st.caption("Reddit Trend Explorer · Built for editorial discovery · Data provided by Reddit and its communities; Reddit does not endorse this tool.")
