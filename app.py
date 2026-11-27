
import streamlit as st
import time
import re
from google.genai import errors

from data_collector import collect_videos
from relevance_filter import filter_videos
from trend_analyzer import analyze_trend


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="TrendRadar",
    page_icon="📡",
    layout="wide"
)


# ==========================================
# UI STYLE
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F5F7FA;
    color: #172033;
}

.block-container {
    max-width: 1440px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #172033 !important;
    letter-spacing: -0.5px;
}

h1 {
    font-size: 36px !important;
    font-weight: 750 !important;
}

h2 {
    font-size: 24px !important;
    font-weight: 700 !important;
}

h3 {
    font-size: 19px !important;
}

.brand {
    font-size: 24px;
    font-weight: 800;
    color: #3549DC;
    letter-spacing: -0.5px;
}

.beta {
    display: inline-block;
    background: #E8EDFF;
    color: #3549DC;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 9px;
    border-radius: 5px;
    margin-left: 10px;
    vertical-align: middle;
}

.section-label {
    font-size: 12px;
    font-weight: 700;
    color: #3549DC;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}

div[data-testid="stForm"] {
    background: white;
    border: 1px solid #E0E5ED;
    border-radius: 12px;
    padding: 24px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 12px;
    border-color: #E0E5ED;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border: 1px solid #E0E5ED;
    border-radius: 10px;
}

[data-testid="stMetricValue"] {
    font-size: 30px !important;
    color: #3549DC !important;
    font-weight: 750 !important;
}

[data-testid="stMetricLabel"] {
    color: #64748B;
}

[data-testid="stFormSubmitButton"] button {
    background: #3549DC !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    min-height: 46px;
    font-weight: 600;
}

[data-testid="stFormSubmitButton"] button:hover {
    background: #2638BC !important;
}

[data-testid="stImage"] img {
    border-radius: 8px;
}

[data-testid="stLinkButton"] a {
    border: 1px solid #DCE2F0;
    color: #3549DC;
    font-weight: 600;
    border-radius: 7px;
}

[data-testid="stTabs"] button {
    font-size: 14px;
    font-weight: 600;
    padding: 12px 18px;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    color: #3549DC;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: #3549DC;
}

[data-testid="stTabs"] [role="tabpanel"] {
    background: white;
    border: 1px solid #E0E5ED;
    border-radius: 10px;
    padding: 24px;
    margin-top: 12px;
}

[data-testid="stMarkdownContainer"] p {
    line-height: 1.65;
}

hr {
    border-color: #E0E5ED !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def format_number(value):

    if value is None:
        return "N/A"

    value = int(value)

    if value >= 1000000:
        return f"{value / 1000000:.2f}M"

    if value >= 1000:
        return f"{value / 1000:.1f}K"

    return str(value)


def clean_title(title):

    title = re.sub(r"#\S+", "", title)
    title = " ".join(title.split())

    if len(title) > 65:
        title = title[:62] + "..."

    return title


def retry_ai(function, *args):

    for attempt in range(3):

        try:
            return function(*args)

        except errors.ServerError as error:

            if error.code != 503 or attempt == 2:
                raise

            time.sleep(10 * (attempt + 1))


def section_header(number, title):

    st.markdown(
        f'<div class="section-label">'
        f'{number} / TRENDRADAR'
        f'</div>',
        unsafe_allow_html=True
    )

    st.header(title)


def split_analysis(analysis):

    pattern = (
        r"(?im)^[ \t]*#{1,6}[ \t]+"
        r"\**([1-5])\.[ \t]+[^\n]+"
    )

    matches = list(re.finditer(pattern, analysis))

    sections = {}

    for index, match in enumerate(matches):

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(analysis)

        content = analysis[start:end].strip()
        content = re.sub(r"\n?---\s*$", "", content)

        sections[int(match.group(1))] = content.strip()

    return sections


def display_remix_ideas(content):

    pattern = (
        r"(?im)^[ \t]*#{1,6}[ \t]+"
        r"\**Idea[ \t]+(\d+)[^\n]*"
    )

    matches = list(re.finditer(pattern, content))

    if not matches:
        st.markdown(content)
        return

    for index, match in enumerate(matches):

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(content)

        title = match.group(0).lstrip("# ").strip("* ")
        body = content[start:end].strip()

        with st.container(border=True):

            st.caption(f"REMIX IDEA / 0{index + 1}")
            st.subheader(title)
            st.markdown(body)


# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div class="brand">
    ◉ TrendRadar
    <span class="beta">BETA 0.1</span>
</div>
""", unsafe_allow_html=True)

st.divider()

st.title("Discover your next viral idea.")

st.markdown(
    "Find trending content. Understand what works. "
    "Make it your own."
)

st.caption(
    "AI-powered trend intelligence for content creators."
)


# ==========================================
# SEARCH FORM
# ==========================================

with st.form("trend_search"):

    col1, col2 = st.columns(2)

    with col1:

        keyword = st.text_input(
            "Trend keyword",
            placeholder="e.g. GRWM, Quiet Luxury, ASMR"
        )

    with col2:

        niche = st.text_input(
            "Your content niche",
            placeholder="e.g. Fashion, Beauty, Lifestyle"
        )

    submitted = st.form_submit_button(
        "Analyze Trend",
        use_container_width=True,
        type="primary"
    )

st.caption(
    "YouTube Data API  ·  Last 7 days  ·  "
    "20 candidates  ·  AI relevance filtering"
)


# ==========================================
# ANALYSIS PIPELINE
# ==========================================

if submitted:

    if not keyword.strip() or not niche.strip():

        st.warning(
            "Please enter both a trend keyword and your niche."
        )

    else:

        st.session_state.pop("trend_result", None)

        try:

            with st.status(
                "Analyzing your trend...",
                expanded=True
            ) as status:

                st.write(
                    "01 / Collecting YouTube data..."
                )

                videos = collect_videos(keyword.strip())

                st.write(
                    f"Collected {len(videos)} candidate videos."
                )

                if not videos:

                    status.update(
                        label="No videos found",
                        state="complete"
                    )

                    st.warning(
                        "Try another trend keyword."
                    )

                else:

                    st.write(
                        "02 / Filtering relevant videos..."
                    )

                    filtered_videos = retry_ai(
                        filter_videos,
                        videos,
                        keyword,
                        niche
                    )

                    st.write(
                        f"Selected {len(filtered_videos)} "
                        "relevant videos."
                    )

                    if not filtered_videos:

                        status.update(
                            label="No relevant videos found",
                            state="complete"
                        )

                        st.warning(
                            "Try a broader keyword or niche."
                        )

                    else:

                        st.session_state["trend_result"] = {
                            "keyword": keyword,
                            "niche": niche,
                            "videos": filtered_videos,
                            "candidate_count": len(videos),
                            "analysis": None
                        }

                        st.write(
                            "03 / Generating personalized insights..."
                        )

                        analysis = retry_ai(
                            analyze_trend,
                            filtered_videos,
                            keyword,
                            niche
                        )

                        st.session_state[
                            "trend_result"
                        ]["analysis"] = analysis

                        status.update(
                            label="Trend analysis complete",
                            state="complete",
                            expanded=False
                        )

        except Exception:

            st.error(
                "The request could not be completed. "
                "Please try again. Your YouTube data "
                "may already be cached."
            )


# ==========================================
# DISPLAY RESULTS
# ==========================================

result = st.session_state.get("trend_result")

if result:

    videos = result["videos"]

    total_views = sum(
        int(v["statistics"].get("viewCount", 0))
        for v in videos
    )

    total_likes = sum(
        int(v["statistics"].get("likeCount", 0))
        for v in videos
    )

    total_comments = sum(
        int(v["statistics"].get("commentCount", 0))
        for v in videos
    )

    st.divider()

    # --------------------------------------
    # SECTION 01: TREND SNAPSHOT
    # --------------------------------------

    section_header("01", "Trend Snapshot")

    st.caption(
        f'{result["keyword"]} / {result["niche"]}'
        ' / Last 7 days'
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Selected Videos",
        len(videos)
    )

    m2.metric(
        "Total Views",
        format_number(total_views)
    )

    m3.metric(
        "Reported Likes",
        format_number(total_likes)
    )

    m4.metric(
        "Reported Comments",
        format_number(total_comments)
    )

    st.caption(
        "Metrics are aggregated from the selected videos."
    )

    st.divider()

    # --------------------------------------
    # SECTION 02: TRENDING VIDEOS
    # --------------------------------------

    section_header("02", "Top Trending Videos")

    st.caption(
        "AI-filtered videos ranked by view count."
    )

    columns = st.columns(len(videos))

    for index, video in enumerate(videos):

        snippet = video["snippet"]
        stats = video["statistics"]

        video_url = (
            "https://www.youtube.com/watch?v="
            + video["id"]
        )

        thumbnail = snippet.get(
            "thumbnails", {}
        ).get(
            "high", {}
        ).get(
            "url"
        )

        with columns[index]:

            with st.container(border=True):

                st.markdown(
                    f"**#{index + 1} TRENDING**"
                )

                if thumbnail:

                    st.image(
                        thumbnail,
                        use_container_width=True
                    )

                st.markdown(
                    "**" + clean_title(
                        snippet["title"]
                    ) + "**"
                )

                st.caption(
                    snippet.get("channelTitle", "")
                )

                st.subheader(
                    format_number(
                        stats.get("viewCount")
                    )
                )

                st.caption("Views")

                st.write(
                    "Likes: "
                    + format_number(
                        stats.get("likeCount")
                    )
                )

                st.write(
                    "Comments: "
                    + format_number(
                        stats.get("commentCount")
                    )
                )

                st.caption(
                    snippet["publishedAt"][:10]
                )

                st.link_button(
                    "Watch Video ↗",
                    video_url,
                    use_container_width=True
                )

                with st.expander("Full title"):

                    st.write(snippet["title"])

    st.divider()

    # --------------------------------------
    # SECTION 03: AI INTELLIGENCE
    # --------------------------------------

    section_header("03", "AI Trend Intelligence")

    st.caption(
        "Explore evidence, content patterns and "
        "personalized creative strategies."
    )

    if result["analysis"]:

        sections = split_analysis(
            result["analysis"]
        )

        
        if len(sections) == 5:

            tab_names = [
                "Trend Overview",
                "Evidence",
                "Viral Mechanism",
                "Meme Formula",
                "Remix Ideas"
            ]

            if "active_analysis_tab" not in st.session_state:
                st.session_state["active_analysis_tab"] = 0

            with st.container(key="analysis_navigation"):

                nav_columns = st.columns(5, gap="small")

                for i, name in enumerate(tab_names):

                    with nav_columns[i]:

                        active = (
                            st.session_state["active_analysis_tab"] == i
                        )

                        if st.button(
                            name,
                            key=f"analysis_nav_{i}",
                            type="primary" if active else "secondary",
                            use_container_width=True
                        ):
                            st.session_state["active_analysis_tab"] = i
                            st.rerun()

            active_tab = st.session_state["active_analysis_tab"]

            with st.container(
                border=True,
                key="analysis_content"
            ):

                if active_tab == 0:

                    st.subheader("Trend Overview")
                    st.markdown(sections[1])

                elif active_tab == 1:

                    st.subheader("Evidence-Based Insights")
                    st.markdown(sections[2])

                elif active_tab == 2:

                    st.subheader("Viral Mechanism")
                    st.markdown(sections[3])

                elif active_tab == 3:

                    st.subheader("Meme Formula")
                    st.markdown(sections[4])

                elif active_tab == 4:

                    st.subheader("Your Personalized Remix Ideas")

                    st.caption(
                        "Three creative concepts tailored "
                        "to your content niche."
                    )

                    display_remix_ideas(sections[5])


            with st.container(border=True):

                st.markdown(result["analysis"])

        st.divider()

        st.download_button(
            "Download Full Trend Report",
            data=result["analysis"],
            file_name="TrendRadar_Report.md",
            mime="text/markdown",
            use_container_width=True
        )

    else:

        st.warning(
            "Video discovery succeeded, but AI analysis "
            "is temporarily unavailable."
        )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "TrendRadar Beta  ·  Powered by YouTube Data API "
    "and Gemini AI"
)

st.caption(
    "Insights are based on selected video metadata, "
    "not direct video viewing. Viral mechanisms "
    "are hypotheses, not guaranteed outcomes."
)


# ==========================================
# TRENDRADAR VISUAL UPGRADE
# ==========================================

st.markdown("""
<style>

:root {
    --brand: #5558E8;
    --navy: #172033;
    --muted: #64748B;
    --surface: #FFFFFF;
    --background: #F5F6FA;
    --border: #E3E7EF;
}

/* Global layout */

.stApp {
    background: #F5F6FA !important;
    color: #172033;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 5rem !important;
    padding-bottom: 3rem !important;
}

[data-testid="stHeader"] {
    background: rgba(245, 246, 250, 0.96);
}

/* Brand identity */

.brand {
    display: flex;
    align-items: center;
    background: #172033;
    color: #FFFFFF !important;
    padding: 18px 24px;
    border-radius: 12px;
    font-size: 25px !important;
    font-weight: 800;
    letter-spacing: -0.8px;
}

.beta {
    background: #343F5C !important;
    color: #C7D2FE !important;
    font-size: 10px !important;
    padding: 5px 9px;
    border-radius: 6px;
}

/* Typography */

h1 {
    font-size: 40px !important;
    font-weight: 800 !important;
    letter-spacing: -1.6px !important;
    line-height: 1.15 !important;
}

h2 {
    font-size: 26px !important;
    font-weight: 750 !important;
    letter-spacing: -0.7px !important;
}

h3 {
    font-size: 19px !important;
    font-weight: 700 !important;
}

.section-label {
    color: #5558E8 !important;
    font-size: 11px !important;
    font-weight: 700;
    letter-spacing: 2px;
}

/* Search panel */

[data-testid="stForm"] {
    background: linear-gradient(
        135deg,
        #172033 0%,
        #303C66 100%
    ) !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 28px !important;
    box-shadow: 0 8px 24px rgba(23,32,51,0.08);
}

[data-testid="stForm"] label,
[data-testid="stForm"] label p {
    color: #E2E8F0 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    color: #172033 !important;
    min-height: 46px;
    font-size: 14px;
}

[data-testid="stTextInput"] input::placeholder {
    color: #94A3B8 !important;
}

[data-testid="stFormSubmitButton"] button {
    background: #6366F1 !important;
    border: none !important;
    color: #FFFFFF !important;
    border-radius: 9px !important;
    min-height: 48px;
    font-size: 15px !important;
    font-weight: 650 !important;
}

[data-testid="stFormSubmitButton"] button:hover {
    background: #818CF8 !important;
}

/* Metric cards */

[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E3E7EF !important;
    border-radius: 14px !important;
    padding: 22px !important;
    box-shadow: 0 3px 10px rgba(23,32,51,0.035);
}

[data-testid="stMetricValue"] {
    color: #172033 !important;
    font-size: 34px !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

[data-testid="stMetricLabel"] p {
    font-size: 12px !important;
    color: #64748B !important;
    font-weight: 600;
}

/* Video cards and content panels */

[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlock"][style*="border"],
[data-testid="stVerticalBlockBorderWrapper"]
> div {
    background: #FFFFFF !important;
    border-radius: 14px !important;
    border-color: #E3E7EF !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    box-shadow: 0 3px 12px rgba(23,32,51,0.035);
}

[data-testid="stImage"] img {
    border-radius: 10px !important;
}

[data-testid="stLinkButton"] a {
    background: #EEF0FF !important;
    color: #5558E8 !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}

[data-testid="stLinkButton"] a:hover {
    background: #E0E4FF !important;
}

/* Analysis navigation */

[data-testid="stTabs"] [role="tablist"] {
    background: #E9ECF4;
    padding: 5px;
    border-radius: 10px;
    gap: 5px;
    border-bottom: none !important;
}

[data-testid="stTabs"] button[role="tab"] {
    padding: 10px 16px !important;
    border-radius: 7px !important;
    color: #64748B !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    background: #172033 !important;
    color: #FFFFFF !important;
}

[data-testid="stTabs"]
button[aria-selected="true"] p {
    color: #FFFFFF !important;
}

[data-testid="stTabs"]
[data-baseweb="tab-highlight"] {
    display: none !important;
}

[data-testid="stTabs"]
[data-baseweb="tab-border"] {
    display: none !important;
}

[data-testid="stTabs"] [role="tabpanel"] {
    background: #FFFFFF !important;
    border: 1px solid #E3E7EF !important;
    border-radius: 14px !important;
    padding: 28px !important;
    margin-top: 16px !important;
}

/* Report readability */

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    line-height: 1.75;
}

[data-testid="stMarkdownContainer"] a {
    color: #5558E8;
}

[data-testid="stCaptionContainer"] p {
    color: #64748B !important;
    font-size: 12px !important;
}

[data-testid="stCode"] {
    border-radius: 10px;
}

[data-testid="stDownloadButton"] button {
    background: #FFFFFF !important;
    border: 1px solid #D8DDF0 !important;
    border-radius: 9px !important;
    color: #5558E8 !important;
    font-weight: 600 !important;
    min-height: 44px;
}

hr {
    border-color: #E3E7EF !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# FINAL TYPOGRAPHY & TAB REFINEMENT
# ==========================================

st.markdown("""
<style>

/* Main section headings */

h2 {
    font-size: 34px !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    line-height: 1.25 !important;
}

/* Secondary headings */

h3 {
    font-size: 24px !important;
    font-weight: 700 !important;
    letter-spacing: -0.4px !important;
    line-height: 1.35 !important;
}

/* Third-level headings */

h4, h5 {
    font-size: 19px !important;
    font-weight: 650 !important;
    line-height: 1.4 !important;
}

/* Section numbers */

.section-label {
    font-size: 12px !important;
    font-weight: 750 !important;
    letter-spacing: 2px !important;
    margin-bottom: 2px !important;
}

/* Tab navigation container */

.stTabs [data-baseweb="tab-list"],
.stTabs [role="tablist"] {
    display: flex !important;
    gap: 8px !important;
    background: #E9ECF4 !important;
    padding: 7px !important;
    border-radius: 12px !important;
    border: none !important;
}

/* Individual tabs */

.stTabs [data-baseweb="tab"],
.stTabs button[role="tab"] {
    flex: 1 0 auto !important;
    min-height: 48px !important;
    padding: 12px 18px !important;
    background: #FFFFFF !important;
    border: 1px solid #E0E5ED !important;
    border-radius: 8px !important;
    color: #475569 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    justify-content: center !important;
    transition: background 0.15s ease;
}

/* Tab text */

.stTabs button[role="tab"] p,
.stTabs [data-baseweb="tab"] p {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: inherit !important;
}

/* Hover state */

.stTabs button[role="tab"]:hover {
    background: #E0E4FF !important;
    color: #5558E8 !important;
}

/* Selected tab */

.stTabs [aria-selected="true"] {
    background: #5558E8 !important;
    border-color: #5558E8 !important;
    color: #FFFFFF !important;
}

.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Remove default red underline */

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
    background: transparent !important;
}

/* Analysis panel headings */

.stTabs [role="tabpanel"] h2,
.stTabs [role="tabpanel"] h3 {
    font-size: 24px !important;
    font-weight: 750 !important;
}

.stTabs [role="tabpanel"] h4,
.stTabs [role="tabpanel"] h5 {
    font-size: 19px !important;
    font-weight: 650 !important;
}

/* Analysis text readability */

.stTabs [role="tabpanel"] p,
.stTabs [role="tabpanel"] li {
    font-size: 16px !important;
    line-height: 1.75 !important;
}

/* Keep video statistics compact */

[data-testid="stColumn"] h3 {
    font-size: 22px !important;
}

/* Improve secondary text contrast */

[data-testid="stCaptionContainer"] p {
    color: #64748B !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# CUSTOM ANALYSIS NAVIGATION
# ==========================================

st.markdown("""
<style>

.st-key-analysis_navigation {
    background: #E9EBF4 !important;
    padding: 8px !important;
    border-radius: 16px !important;
    margin-top: 8px;
    margin-bottom: 16px;
}

.st-key-analysis_navigation button {
    width: 100% !important;
    min-height: 64px !important;
    height: 64px !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 10px 12px !important;
    box-shadow: none !important;
    transition: background 0.15s ease;
}

.st-key-analysis_navigation button p {
    font-size: 15px !important;
    font-weight: 650 !important;
    line-height: 1.4 !important;
    text-align: center !important;
    white-space: normal !important;
}

.st-key-analysis_navigation
button[data-testid="stBaseButton-secondary"] {
    background: #FFFFFF !important;
    color: #475569 !important;
}

.st-key-analysis_navigation
button[data-testid="stBaseButton-secondary"] p {
    color: #475569 !important;
}

.st-key-analysis_navigation
button[data-testid="stBaseButton-primary"] {
    background: #5558E8 !important;
    color: #FFFFFF !important;
}

.st-key-analysis_navigation
button[data-testid="stBaseButton-primary"] p {
    color: #FFFFFF !important;
}

.st-key-analysis_navigation
button[data-testid="stBaseButton-secondary"]:hover {
    background: #DFE3FF !important;
    color: #5558E8 !important;
}

.st-key-analysis_navigation button:focus {
    box-shadow: none !important;
}

.st-key-analysis_content {
    background: #FFFFFF !important;
    border: 1px solid #E3E7EF !important;
    border-radius: 16px !important;
    padding: 28px !important;
}

.st-key-analysis_content h3 {
    font-size: 26px !important;
    font-weight: 750 !important;
    margin-bottom: 12px !important;
}

.st-key-analysis_content p,
.st-key-analysis_content li {
    font-size: 16px !important;
    line-height: 1.75 !important;
}

</style>
""", unsafe_allow_html=True)
