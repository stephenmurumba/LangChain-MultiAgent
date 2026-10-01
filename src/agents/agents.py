import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_perplexity import ChatPerplexity
from src.tools import search_url, scrape_web

load_dotenv(override=True)

# api_key = os.getenv("TAVILY_API_KEY", "").strip()
api_key = os.getenv("PERPLEXITY_API_KEY", "").strip()

# Moel Creation
llm = ChatPerplexity(
    model='openai/gpt-5.5',
    use_responses_api=True,
    timeout=60,
    api_key=api_key # type: ignore
)

# First Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[search_url]
    )
# Second Agent 
def build_read_write_agent():
    return create_agent(
        model=llm,
        tools=[scrape_web]
    )

# writer chain

writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a senior research writer.

Create a well-structured, factual research report based only on the provided search findings and scraped content.

Requirements:
- Use clear Markdown headings.
- Separate verified facts from uncertain claims.
- Include source URLs where available.
- Do not invent facts, statistics, or citations.
- Address the critic feedback when it is provided.
"""
        ),
        (
            "human",
            """
Research topic:
{topic}

Search findings:
{search_result}

Scraped source content:
{scraped_content}

Critique or revision instructions:
{critique}
"""
        ),
    ]
)

prompt_chain = writer_prompt | llm | StrOutputParser()


# critic chain

critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a strict research editor and fact-checking critic.

Review the report against the supplied research materials. Identify:
1. Unsupported or potentially inaccurate claims
2. Missing important information
3. Contradictions or uncertainty
4. Weak source attribution
5. Clarity and structural improvements
6. Specific revisions the writer must make

Do not rewrite the entire report. Give actionable editorial feedback.
"""
        ),
        (
            "human",
            """
Research topic:
{topic}

Search findings:
{search_result}

Scraped source content:
{scraped_content}

Draft report:
{draft_report}
"""
        ),
    ]
)

critic_chain = critic_prompt | llm | StrOutputParser()