# WPA LangGraph

A workflow-based article processing system built with LangGraph and LangChain.

## Overview

This system processes articles through a series of steps using a directed graph workflow, leveraging both OpenAI and DeepSeek language models for different processing stages.

## Architecture

The workflow consists of the following nodes:

1. `start` - Initializes the workflow
2. `write_outline` - Generates a structured outline of the article
3. `next_paragraph` - Processes each section of the outline sequentially
4. `top_insights` - Extracts key insights from the article
5. `write_transcript` - Creates a detailed dialogue version
6. `final_review` - Compiles the processed content
7. `fact_checker` - Validates the generated content

## State Management

The system uses a TypedDict-based state management with custom reducers for different data types:

- Strings: Latest value or concatenation
- Lists: Addition or latest value
- Dictionaries: Latest value
- Integers: Latest value

## API Endpoints

- `POST /process` - Process an article
- `GET /graph` - Visualize the workflow graph
- `GET /health` - Health check endpoint

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment Variables in .env

```bash
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key
```

## Usage

Send a POST request:

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"source": "Your article text here"}'
```

## Models Used

- OpenAI GPT-4-mini: Fact checking
- DeepSeek Chat: Article processing and content generation
