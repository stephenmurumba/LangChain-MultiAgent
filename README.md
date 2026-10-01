# LangChain Multi-Agent Research Assistant

A Streamlit-based research assistant that orchestrates multiple AI agents to search the web, evaluate source quality, extract article content, draft a research report, critique it, and revise the final output.

## Overview

This project demonstrates a practical multi-agent workflow powered by LangChain and LLMs. It helps users:

- Research a topic using live web search
- Identify a relevant source and scrape its content
- Draft a structured report from verified findings
- Review the draft for factual gaps and weak reasoning
- Revise the report into a cleaner final version

The application is designed as a lightweight, interactive research workspace for exploring current information quickly and iteratively.

## Features

- Multi-step research pipeline with specialized agents
- Web search integration via Tavily
- Source scraping and content extraction with BeautifulSoup, Readability, and Trafilatura
- Structured drafting and critique flow using LangChain prompt chains
- Streamlit web interface for hands-on interaction
- Markdown report generation for download and review

## Architecture

The project is organized as follows:

```text
LangChain-MultiAgent/
├── app.py                  # Streamlit UI and session orchestration
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agents.py       # LLM agents and prompt chains
│   ├── pipelines/
│   │   ├── __init__.py
│   │   └── pipeline.py     # Research workflow orchestration
│   └── tools/
│       ├── __init__.py
│       └── tool.py         # Search and scrape tool definitions
├── __init__.py
└── .env                    # Local secret configuration (not committed)
```

## Workflow

The research process follows this sequence:

1. Search agent gathers recent and relevant findings
2. Reader agent selects an important source and extracts article content
3. Writer chain produces an initial research draft
4. Critic chain evaluates the draft for quality and gaps
5. Writer chain revises the final report

This creates a feedback loop similar to a research editor and analyst team working together.

## Tech Stack

- Python
- Streamlit
- LangChain
- LangChain Perplexity
- Tavily Search API
- BeautifulSoup
- readability-lxml
- trafilatura

## Prerequisites

Before running the project, make sure you have:

- Python 3.10 or newer
- A Tavily API key
- A Perplexity API key
- An active internet connection

## Environment Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/LangChain-MultiAgent.git
cd LangChain-MultiAgent
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:

```env
PERPLEXITY_API_KEY=your_perplexity_api_key
TAVILY_API_KEY=your_tavily_api_key
```

> Never commit your `.env` file to version control.

## Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Usage

1. Enter a research topic in the app
2. Click the research button
3. Wait for the agent pipeline to complete
4. Review the final report and intermediate findings
5. Download the generated markdown report if needed

The app is designed for information gathering and structured writing, especially for current events, industry analysis, and fact-based research tasks.

## Important Notes

- Search quality depends on the reliability of your API keys and the availability of live sources
- Web scraping may be blocked by some sites, so some pages may return partial or limited content
- The workflow is best suited for research synthesis rather than legal, medical, or highly regulated advice
- The generated output should always be reviewed for factual accuracy and source quality

## Project Goals

This project was built to:

- showcase LangChain multi-agent orchestration
- combine retrieval, extraction, writing, and critique steps
- make research workflows more interactive and transparent
- provide a starting template for AI-assisted research applications

## License

This project does not currently include a formal license file. If you plan to reuse or distribute it commercially, add a license before doing so.

## Contributing

Contributions are welcome. If you want to improve the project:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request with a clear summary

## Future Improvements

- Add user-configurable model selection
- Support multiple report output formats
- Add source citation formatting
- Improve error handling for blocked or unsupported pages
- Add conversation memory and follow-up research threads
- Include export options such as PDF or DOCX

## Contact

For questions or collaboration opportunities, please reach out through the project repository or your preferred contact channel.
