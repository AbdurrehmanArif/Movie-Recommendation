import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# STYLES (Netflix-like dark theme)
# =============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Netflix+Sans:wght@400;700&display=swap');

* {
    font-family: 'Netflix Sans', sans-serif;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #141414 !important;
    color: #ffffff !important;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1400px;
    background-color: #141414 !important;
}

[data-testid="stSidebar"] {
    background-color: #000000 !important;
    border-right: 1px solid #333;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

.movie-title {
    font-size: 0.9rem;
    line-height: 1.15rem;
    height: 2.3rem;
    overflow: hidden;
    color: #ffffff !important;
    text-align: center;
    margin-top: 8px;
}

.movie-card {
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    background: #333;
    margin: 5px;
}

.movie-card:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 16px rgba(0,0,0,0.8);
}

.movie-poster {
    width: 100%;
    height: auto;
    display: block;
}

.row-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 20px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.search-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.details-section {
    background: #1a1a1a;
    padding: 30px;
    border-radius: 15px;
    margin: 20px 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.stButton>button {
    background-color: #e50914 !important;
    color: white !important;
    border: none !important;
    border-radius: 5px !important;
    padding: 10px 20px !important;
    font-weight: bold !important;
    transition: background-color 0.3s ease !important;
}

.stButton>button:hover {
    background-color: #f40612 !important;
}

.stTextInput>div>div>input {
    background-color: #333 !important;
    color: white !important;
    border: 1px solid #555 !important;
    border-radius: 5px !important;
}

.stSelectbox>div>div>select {
    background-color: #333 !important;
    color: white !important;
    border: 1px solid #555 !important;
    border-radius: 5px !important;
}

.stSlider>div>div>div {
    background: linear-gradient(90deg, #e50914, #ff6b6b) !important;
}

[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
    color: #ffffff !important;
}

.small-muted {
    color: #cccccc !important;
    font-size: 0.92rem;
}

.card {
    border: 1px solid #333;
    border-radius: 16px;
    padding: 20px;
    background: #1a1a1a;
    box-shadow: 0 4px 8px rgba(0,0,0,0.5);
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (single-file pages)
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)  # short cache for autocomplete
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                if poster:
                    st.image(poster, width='stretch')
                else:
                    st.write("🖼️ No poster")

                if st.button("Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

                st.markdown(
                    f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True
                )


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                }
            )
    return cards


# =============================
# IMPORTANT: Robust TMDB search parsing
# Supports BOTH API shapes:
# 1) raw TMDB: {"results":[{id,title,poster_path,...}]}
# 2) list cards: [{tmdb_id,title,poster_url,...}]
# =============================
def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    # A) If API returns dict with 'results'
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                }
            )

    # B) If API returns already as list
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            # might be {tmdb_id,title,poster_url}
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                }
            )
    else:
        return [], []

    # Word-match filtering (contains)
    matched = [x for x in raw_items if keyword_l in x["title"].lower()]

    # If nothing matched, fallback to raw list (so never blank)
    final_list = matched if matched else raw_items

    # Suggestions = top 10 labels
    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    # Cards = top N
    cards = [
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
        for x in final_list[:limit]
    ]
    return suggestions, cards


# =============================
# SIDEBAR (clean)
# =============================
with st.sidebar:
    st.markdown("## 🎬 Menu")
    if st.button("🏠 Home"):
        goto_home()

    st.markdown("---")
    st.markdown("### 🏠 Home Feed (only home)")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    grid_cols = st.slider("Grid columns", 4, 8, 6)

# =============================
# HEADER
# =============================
st.title("🎬 Movie Recommender")
st.markdown(
    "<div class='small-muted'>Type keyword → dropdown suggestions + matching results → open → details + recommendations</div>",
    unsafe_allow_html=True,
)
st.divider()

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title (keyword)", placeholder="Type: avenger, batman, love..."
    )

    st.divider()

    # SEARCH MODE (Autocomplete + word-match results)
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                # Dropdown
                if suggestions:
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0)

                    if selected != "-- Select a movie --":
                        # map label -> id
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("### Results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    # HOME FEED MODE
    st.markdown(f"### 🏠 Home — {home_category.replace('_',' ').title()}")

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    # Top bar
    a, b = st.columns([3, 1])
    with a:
        st.markdown("### 📄 Movie Details")
    with b:
        if st.button("← Back to Home"):
            goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Layout: Poster LEFT, Details RIGHT
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if data.get("poster_url"):
            st.image(data["poster_url"], width='stretch')
        else:
            st.write("🖼️ No poster")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"## {data.get('title','')}")
        release = data.get("release_date") or "-"
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "-"
        st.markdown(
            f"<div class='small-muted'>Release: {release}</div>", unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='small-muted'>Genres: {genres}</div>", unsafe_allow_html=True
        )
    st.markdown("---")
    st.markdown("### Overview")
    st.write(data.get("overview") or "No overview available.")

    # Trailer Section
    if data.get("trailer_url"):
        st.markdown("### 🎥 Trailer")
        trailer_url = data["trailer_url"]
        # Safe video ID extraction: Handle '&' in URL properly
        video_id = trailer_url.split("v=")[-1].split("&")[0]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        st.video(embed_url)
    else:
        st.markdown("### 🎥 Trailer")
        st.info("Trailer not available")

    # Watch Providers Section
    if data.get("watch_providers"):
        st.markdown("### 📺 Where to Watch")
        providers = data["watch_providers"]
        # Assuming US for simplicity, can be extended
        us_providers = providers.get("US", {})
        if us_providers:
            for provider_type, prov_list in us_providers.items():
                if prov_list:
                    st.markdown(f"**{provider_type.title()}:**")
                    for p in prov_list:
                        logo = p.get("logo_path")
                        name = p.get("provider_name", "Unknown")
                        if logo:
                            st.markdown(f'<img src="https://image.tmdb.org/t/p/w92{logo}" alt="{name}" style="height:30px; margin-right:10px;"> {name}', unsafe_allow_html=True)
                        else:
                            st.markdown(f"- {name}")
        else:
            st.info("Watch providers not available for your region.")

    st.markdown("</div>", unsafe_allow_html=True)

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(data["backdrop_url"], width='stretch')

    st.divider()
    st.markdown("### ✅ Recommendations")

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### 🔎 Similar Movies (TF-IDF)")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("#### 🎭 More Like This (Genre)")
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")