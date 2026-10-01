import streamlit as st

from src.pipelines import research_pipeline


st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialise_session_state():
    """Set default Streamlit session-state values."""

    defaults = {
        "pipeline_result": None,
        "last_topic": "",
        "pipeline_running": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_research():
    """Clear the current research session."""

    st.session_state.pipeline_result = None
    st.session_state.last_topic = ""
    st.session_state.pipeline_running = False


def create_markdown_download(result: dict) -> str:
    """Create a Markdown report for download."""

    topic = result.get("topic", "Untitled Research")
    search_result = result.get("search_result", "")
    scraped_content = result.get("scraped_content", "")
    draft_report = result.get("draft_report", "")
    critique = result.get("critique", "")
    final_report = result.get("final_report", "")

    return f"""# Research Report

## Topic

{topic}

## Final Report

{final_report}

---

## Search-Agent Findings

{search_result}

---

## Reader-Agent Source Analysis

{scraped_content}

---

## First Draft

{draft_report}

---

## Critic Feedback

{critique}
"""


initialise_session_state()


st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 750;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1.05rem;
            margin-bottom: 1.6rem;
        }

        .stage-card {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #ffffff;
        }

        .success-banner {
            padding: 0.8rem 1rem;
            border-radius: 8px;
            background-color: #dcfce7;
            color: #166534;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Research workspace")

    st.markdown(
        """
        This application runs a multi-agent research workflow:

        1. **Search agent** — finds recent sources
        2. **Reader agent** — selects and scrapes a source
        3. **Writer chain** — creates a report
        4. **Critic chain** — reviews the draft
        5. **Writer chain** — revises the final report
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear research",
        use_container_width=True,
        help="Remove the current report and all intermediate agent results.",
    ):
        clear_research()
        st.rerun()

    st.divider()

    # st.caption(
    #     "Ensure your `.env` file contains valid `PERPLEXITY_API_KEY` "
    #     "and `TAVILY_API_KEY` values."
    # )

    # st.caption(
    #     "Do not commit your `.env` file to GitHub because it contains secrets."
    # )


st.markdown(
    '<div class="main-title">🔎 Multi-Agent Research Assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Search, inspect sources, draft, critique, and refine a research report."
    "</div>",
    unsafe_allow_html=True,
)


with st.form("research_form", clear_on_submit=False):
    topic = st.text_area(
        "What would you like to research?",
        value=st.session_state.last_topic,
        placeholder=(
            "Example: Latest developments, ownership structure, environmental "
            "concerns, and projected economic impact of the Lamu refinery project."
        ),
        height=130,
        max_chars=1_000,
    )

    submitted = st.form_submit_button(
        "🚀 Run research pipeline",
        type="primary",
        use_container_width=True,
    )


if submitted:
    clean_topic = (topic or "").strip()

    if not clean_topic:
        st.warning("Enter a research topic before running the pipeline.")

    else:
        st.session_state.last_topic = clean_topic
        st.session_state.pipeline_running = True

        progress_bar = st.progress(0)
        status_area = st.empty()

        try:
            status_area.info("Step 1 of 5: Search agent is finding current sources...")
            progress_bar.progress(15)

            with st.spinner("Running the multi-agent research pipeline..."):
                result = research_pipeline(clean_topic)

            progress_bar.progress(100)

            st.session_state.pipeline_result = result

            if result.get("success"):
                status_area.success("Research pipeline completed successfully.")
            else:
                status_area.error("The research pipeline finished with an error.")

        except Exception as exc:
            st.session_state.pipeline_result = {
                "success": False,
                "topic": clean_topic,
                "error": f"{type(exc).__name__}: {exc}",
            }

            progress_bar.progress(100)
            status_area.error("The research pipeline encountered an unexpected error.")

        finally:
            st.session_state.pipeline_running = False


result = st.session_state.pipeline_result


if result:
    st.divider()

    if not result.get("success"):
        st.error("Research pipeline failed.")

        st.code(
            result.get("error", "An unknown error occurred."),
            language="text",
        )

        # st.info(
        #     "Check that your API keys are present in `.env`, your installed "
        #     "packages match `requirements.txt`, and custom tool names do not "
        #     "conflict with Perplexity reserved tool names."
        # )

    else:
        st.markdown(
            '<div class="success-banner">✓ Research pipeline completed</div>',
            unsafe_allow_html=True,
        )

        st.markdown("")

        topic_name = result.get("topic", "Research topic")

        st.subheader(f"Final report: {topic_name}")

        final_report = result.get("final_report", "")

        if final_report:
            st.markdown(final_report)
        else:
            st.warning("The pipeline completed but did not return a final report.")

        markdown_report = create_markdown_download(result)

        st.download_button(
            label="⬇️ Download full research report",
            data=markdown_report,
            file_name="research_report.md",
            mime="text/markdown",
            use_container_width=False,
        )

        st.divider()

        st.subheader("Research workflow details")

        tab_search, tab_reader, tab_draft, tab_critic = st.tabs(
            [
                "🔍 Search findings",
                "📄 Source analysis",
                "✍️ First draft",
                "🧠 Critic feedback",
            ]
        )

        with tab_search:
            st.markdown("### Search-agent results")

            search_result = result.get("search_result", "")

            if search_result:
                st.markdown(search_result)
            else:
                st.info("No search-agent result was returned.")

        with tab_reader:
            st.markdown("### Reader-agent extraction")

            scraped_content = result.get("scraped_content", "")

            if scraped_content:
                st.markdown(scraped_content)
            else:
                st.info("No scraped source content was returned.")

        with tab_draft:
            st.markdown("### Writer-agent first draft")

            draft_report = result.get("draft_report", "")

            if draft_report:
                st.markdown(draft_report)
            else:
                st.info("No draft report was returned.")

        with tab_critic:
            st.markdown("### Critic-agent recommendations")

            critique = result.get("critique", "")

            if critique:
                st.markdown(critique)
            else:
                st.info("No critic feedback was returned.")

else:
    st.info(
        "Enter a topic above and select **Run research pipeline** to start "
        "your multi-agent research workflow."
    )

    st.markdown("### Suggested research topics")

    col_one, col_two = st.columns(2)

    with col_one:
        st.markdown(
            """
            - Latest developments in the Lamu refinery project
            - Kenya's AI regulation and data-protection landscape
            - Digital-payment trends in East Africa
            """
        )

    with col_two:
        st.markdown(
            """
            - Renewable-energy investment in Kenya
            - Fibre-optic connectivity projects in East Africa
            - Effects of the African Continental Free Trade Area on Kenyan technology companies
            """
        )
st.divider()

st.markdown(
    """
    <div style="
        text-align: center;
        color: #6b7280;
        font-size: 0.85rem;
        padding: 0.5rem 0 1rem 0;
    ">
        Built with ❤️ by Stephen Murumba using Streamlit, LangChain, Perplexity, and Tavily
    </div>
    """,
    unsafe_allow_html=True,
)        



# """ from src.tools import web_search, search_url

# results = web_search.invoke("Latest news on Dangote Lamu refinery.")
# print(results)

# results = search_url.invoke("https://kenyanwallstreet.com/dangote-kenya-lamu-refinery")
# print(results) """

# """ from src.pipelines import research_pipeline

# result = research_pipeline(
#     "Latest news and developments concerning the Dangote Lamu refinery"
# )

# if result["success"]:
#     print(result["final_report"])
# else:
#     print(f"Pipeline error: {result['error']}") """