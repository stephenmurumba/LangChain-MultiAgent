from typing import Any

from langchain_core.messages import HumanMessage

from src.agents import (
    build_read_write_agent,
    build_search_agent,
    critic_chain,
    prompt_chain,
)


def _content_to_text(content: Any) -> str:
    """Convert LangChain message content into a clean string."""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")

                if isinstance(text, str):
                    text_parts.append(text)

        return "\n".join(text_parts).strip()

    return str(content).strip()


def _get_final_agent_message(agent_result: dict[str, Any]) -> str:
    """Extract the final assistant message from an agent invoke result."""

    messages = agent_result.get("messages", [])

    if not messages:
        return "No response was returned by the agent."

    return _content_to_text(messages[-1].content)


def research_pipeline(topic: str) -> dict[str, Any]:
    """
    Run a multi-agent research workflow.

    Workflow:
    1. Search agent finds recent/reliable information.
    2. Reader agent selects and scrapes a relevant source.
    3. Writer chain drafts a report.
    4. Critic chain evaluates accuracy, structure, and gaps.
    5. Writer chain produces a final improved report.

    Returns:
        A dictionary containing research state, draft, critique, and final report.
    """

    topic = topic.strip()

    if not topic:
        return {
            "success": False,
            "error": "Please provide a research topic.",
            "topic": "",
        }

    state: dict[str, Any] = {
        "success": False,
        "topic": topic,
        "search_result": "",
        "scraped_content": "",
        "draft_report": "",
        "critique": "",
        "final_report": "",
        "error": None,
    }

    try:
        print("\n" + "=" * 60)
        print("STEP 1: Search agent is working...")
        print("=" * 60)

        search_agent = build_search_agent()

        search_result = search_agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            f"Find recent, reliable, and detailed information about: "
                            f"{topic}\n\n"
                            "Use web search. Return a concise research brief containing:\n"
                            "1. Key current findings\n"
                            "2. Important facts and figures\n"
                            "3. A list of the most relevant source URLs\n"
                            "4. Publication dates when available\n"
                            "5. Any conflicting claims or uncertainty"
                        )
                    )
                ]
            }
        )

        state["search_result"] = _get_final_agent_message(search_result)

        print("\nSearch completed.")
        print(state["search_result"][:1_500])

        if not state["search_result"]:
            raise ValueError("The search agent returned an empty result.")

        print("\n" + "=" * 60)
        print("STEP 2: Reader agent is scraping top resources...")
        print("=" * 60)

        reader_agent = build_read_write_agent()

        reader_message = (
            f"Research topic: {topic}\n\n"
            "Below are web-search findings. Select the single most relevant, "
            "credible, publicly accessible URL. Use the URL scraping tool to "
            "extract deeper content from it.\n\n"
            "Return:\n"
            "1. The selected URL\n"
            "2. Why the source is credible and relevant\n"
            "3. The extracted article content or a detailed factual summary\n"
            "4. Important dates, names, numbers, claims, and caveats\n\n"
            f"Search results:\n{state['search_result'][:8_000]}"
        )

        reader_result = reader_agent.invoke(
            {
                "messages": [
                    HumanMessage(content=reader_message)
                ]
            }
        )

        state["scraped_content"] = _get_final_agent_message(reader_result)

        print("\nScraping completed.")
        print(state["scraped_content"][:1_500])

        if not state["scraped_content"]:
            state["scraped_content"] = (
                "No additional source content was returned. "
                "Write the report using the search findings and clearly "
                "state any uncertainty."
            )

        print("\n" + "=" * 60)
        print("STEP 3: Writer chain is creating the first report draft...")
        print("=" * 60)

        draft_result = prompt_chain.invoke(
            {
                "topic": state["topic"],
                "search_result": state["search_result"],
                "scraped_content": state["scraped_content"],
                "critique": "No critique yet. Create the initial draft.",
            }
        )

        state["draft_report"] = _content_to_text(draft_result)

        print("\nDraft report completed.")
        print(state["draft_report"][:1_500])

        if not state["draft_report"]:
            raise ValueError("The writer chain returned an empty draft.")

        print("\n" + "=" * 60)
        print("STEP 4: Critic chain is reviewing the draft...")
        print("=" * 60)

        critique_result = critic_chain.invoke(
            {
                "topic": state["topic"],
                "search_result": state["search_result"],
                "scraped_content": state["scraped_content"],
                "draft_report": state["draft_report"],
            }
        )

        state["critique"] = _content_to_text(critique_result)

        print("\nCritique completed.")
        print(state["critique"][:1_500])

        if not state["critique"]:
            state["critique"] = (
                "No separate critique was generated. Improve clarity, factual "
                "precision, source attribution, and uncertainty statements."
            )

        print("\n" + "=" * 60)
        print("STEP 5: Writer chain is revising the final report...")
        print("=" * 60)

        final_result = prompt_chain.invoke(
            {
                "topic": state["topic"],
                "search_result": state["search_result"],
                "scraped_content": state["scraped_content"],
                "critique": (
                    f"Original draft:\n{state['draft_report']}\n\n"
                    f"Critic feedback:\n{state['critique']}\n\n"
                    "Rewrite and improve the report. Correct unsupported claims, "
                    "retain useful evidence, identify uncertainty, and include "
                    "the source URLs provided by the research agents."
                ),
            }
        )

        state["final_report"] = _content_to_text(final_result)

        if not state["final_report"]:
            state["final_report"] = state["draft_report"]

        state["success"] = True

        print("\n" + "=" * 60)
        print("RESEARCH PIPELINE COMPLETED")
        print("=" * 60)

        return state

    except Exception as exc:
        state["error"] = f"{type(exc).__name__}: {exc}"

        print("\n" + "=" * 60)
        print("RESEARCH PIPELINE FAILED")
        print("=" * 60)
        print(state["error"])

        return state
    