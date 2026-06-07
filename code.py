import streamlit as st
import feedparser
import re
import urllib.parse
from urllib.parse import urlparse
from newspaper import Article
import nltk
# Download the lightweight text processor required for the summarizer
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
# Page Config
st.set_page_config(page_title="Tech News Digest", layout="wide", initial_sidebar_state="expanded")
# -------- CUSTOM CSS FOR MINIMAL/PROFESSIONAL UI --------
# -------- REFINED CSS: NO DISPLACEMENT --------
# -------- CSS: LOCKED SIDEBAR + CENTERED CONTENT --------
# -------- FINAL OVERLAP FIX CSS --------
# -------- FULL HEIGHT SIDEBAR & BLACK TEXT FIX --------
# -------- FINAL STABLE UI ADJUSTMENT --------
st.markdown("""
    <style>
    /* 1. GLOBAL & MAIN FRAME TEXT COLOR */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #dbd9d9 !important;
    }
    /* Force all text in the main area to be Black */
    [data-testid="stMain"] p,
    [data-testid="stMain"] div,
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] span {
        color: #000000 !important;
    }
    /* Hide the top black header strip */
    header[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0px !important;
    }
    /* 2. SIDEBAR: FULL HEIGHT & LOCKED */
    [data-testid="stSidebar"] {
        background-color: #2C3947 !important;
        min-width: 300px !important;
        width: 300px !important;
        height: 100vh !important; /* Forces it to bottom of screen */
        position: fixed !important;
        top: 0;
        left: 0;
        visibility: visible !important;
        transform: none !important;
        z-index: 9999; /* Keeps it above other layers */
    }
    [data-testid="stMain"] {
    margin-left: 300px !important;  /* match sidebar width */
    padding: 2rem 2rem 2rem 2rem;
    max-width: calc(100vw - 320px); /* prevents overflow */
}
            section.main > div {
    max-width: 100% !important;
    overflow-x: hidden !important;
}
    /* Hide the sidebar collapse arrow */
    button[data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    /* 3. SIDEBAR TEXT COLOR (Must stay White) */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }
    /* 4. MAIN TITLES */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin-top: -1rem;
        color: #000000 !important;
    }
    .sub-title {
        text-align: center;
        font-size: 1.1rem;
        color: #444444 !important;
        margin-bottom: 2rem;
    }
    /* 5. ARTICLE CARDS (Solid border and white background) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #edebeb !important;
        border: 1.5px solid #000000 !important;
        border-radius: 15px !important;
    }
    /* 6. EXPANDERS (Summary Box) */
    [data-testid="stExpander"] {
    background-color: #ded9d9 !important;
    border: 1px solid #000000 !important;
    border-radius: 8px !important;
}

[data-testid="stExpander"] details {
    background-color: #ded9d9 !important;
}

[data-testid="stExpander"] summary {
    background-color: #ded9d9 !important;
    color: #000000 !important;
}

    /* Ensure summary text inside is black */
    .st-expander p, .st-expander div {
        color: #000000 !important;
    }
    /* 7. BUTTON STYLING */
    div.stButton > button:first-child {
        background-color: transparent;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# -------- SIDEBAR: REFINE --------
st.sidebar.markdown("### ⚙️ Refine")
st.sidebar.write("Customize your news feed.")
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Search Titles", placeholder="e.g., OpenAI, chip...")



tech_keywords = [

    "AI", "Cloud", "Cybersecurity",

    "Apple", "Google", "Microsoft", "Startup", "Crypto", "Semiconductor"

]

selected_keywords = st.sidebar.multiselect("🏷️ Topics", tech_keywords)



# -------- MAIN PAGE --------

st.markdown("<div class='main-title'> Tech News Digest</div>", unsafe_allow_html=True)

st.markdown("<div class='sub-title'>ML Based Tech News Dashboard</div>", unsafe_allow_html=True)



# -------- HELPER FUNCTIONS --------

def clean_title(title):

    title = title.lower().strip()

    title = re.sub(r'[^\w\s]', '', title)

    title = re.sub(r'\s+', ' ', title)

    return title.strip()



def clean_link(link):

    parsed = urlparse(link)

    return parsed.scheme + "://" + parsed.netloc + parsed.path



##@st.cache_data(show_spinner=False)

def get_full_article_and_summary(url):

    """

    Returns (full_text, summary, is_accessible).

    is_accessible=False when article is paywalled/blocked/too short.

    """

    try:

        article = Article(url)

        article.download()

        article.parse()

        article.nlp()

        full_text = article.text

        summary = article.summary

        if len(full_text) < 200:

            return "", "", False  # Paywalled or blocked

        return full_text, summary, True

    except Exception:

        return "", "", False  # Download/parse failure = treat as blocked



def is_article_accessible(url):

    """Returns True only if the article has enough readable content."""

    _, _, accessible = get_full_article_and_summary(url)

    return accessible



# -------- RSS FEEDS — No Google News --------

rss_feeds = {

    "Economic Times Tech": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",

    "The Hindu Tech": "https://www.thehindu.com/sci-tech/technology/feeder/default.rss",

    "Mint Tech": "https://www.livemint.com/rss/technology",

    "TechCrunch": "https://techcrunch.com/feed/",

    "ZDNET": "https://www.zdnet.com/news/rss.xml",

    "VentureBeat": "https://venturebeat.com/feed/",

    "The Verge": "https://www.theverge.com/rss/index.xml"

}



# -------- COLLECT ARTICLES --------

all_entries = []

seen = set()



for source, url in rss_feeds.items():

    feed = feedparser.parse(url)

    for entry in feed.entries[:15]:

        raw_title = entry.get("title", "No title")

        raw_link = entry.get("link", "#")

        published = entry.get("published", "No date")



        normalized_title = clean_title(raw_title)

        normalized_link = clean_link(raw_link)

        identifier = (normalized_title, normalized_link)



        if identifier in seen:

            continue



        seen.add(identifier)

        all_entries.append({

            "title": raw_title.strip(),

            "link": raw_link,

            "published": published,

            "source": source

        })



# -------- FILTER BY KEYWORD + SEARCH --------

filtered_entries = []



for news in all_entries:

    title_lower = news["title"].lower()



    matches_search = True

    if search_query:

        matches_search = search_query.lower() in title_lower



    matches_keyword = True

    if selected_keywords:

        matches_keyword = any(kw.lower() in title_lower for kw in selected_keywords)



    if matches_search and matches_keyword:

        filtered_entries.append(news)



filtered_entries = filtered_entries[:50]



# -------- DISPLAY --------

st.write("---")

st.markdown(f"### 🧾 {len(filtered_entries)} articles found.")



if len(filtered_entries) > 0:

    if st.button("Summarize Filtered News"):

        st.write("---")



        accessible_entries = []

        skipped = 0



        # Pre-screen all articles for accessibility before rendering any cards

        check_placeholder = st.empty()

        check_placeholder.info("⏳ Checking article accessibility, please wait...")



        for news in filtered_entries:

            full_text, summary, accessible = get_full_article_and_summary(news["link"])



            if accessible:

                news["full_text"] = full_text

                news["summary"] = summary

                accessible_entries.append(news)

            else:

                skipped += 1

                print(f"[BLOCKED] {news['title']} | {news['link']}")  # ← add this



        check_placeholder.empty()



        # ← REMOVE the st.warning line below entirely:

        # if skipped > 0:

        #     st.warning(f"⚠️ {skipped} article(s) skipped — paywalled or inaccessible.")



        # ← ADD this print to terminal instead:

        print(f"\n{'='*60}")

        print(f"[SUMMARY] Total fetched: {len(filtered_entries)}")

        print(f"[SUMMARY] Accessible:    {len(accessible_entries)}")

        print(f"[SUMMARY] Blocked/Skipped: {skipped}")

        print(f"{'='*60}\n")

        if not accessible_entries:

            st.error("No accessible articles found. All results are behind paywalls or blocked.")

        else:

            st.markdown(f"### ✅ Showing  accessible articles.")



            col1, col2 = st.columns(2)



            for i, news in enumerate(accessible_entries):

                with (col1 if i % 2 == 0 else col2):

                    with st.container(border=True):

                        st.subheader(news["title"])

                        st.caption(f"📅 {news['published']} | 📰 {news['source']}")

                        st.markdown(f"🔗 [Read Full Article Here]({news['link']})")



                        with st.expander("🔎 View Summary"):

                            with st.spinner("Summarizing..."):

                                summary = news.get("summary", "")

                                full_text = news.get("full_text", "")

                                if not summary.strip():

                                    st.write(full_text[:300] + "... (summary unavailable)")

                                else:

                                    st.write(summary)

else:

    st.info("No articles match your search or keyword filters. Try clearing them!")