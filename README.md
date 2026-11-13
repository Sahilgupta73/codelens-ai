# CodeLens AI — Codebase & Debugging Assistant

CodeLens AI helps developers understand Python projects and investigate
errors using Retrieval-Augmented Generation (RAG) and a tool-using AI agent.

It retrieves relevant source code, generates explanations, and suggests
fixes with file references. It does not automatically edit or execute code.

## Features

- Index a local Python project.
- Ask questions about the codebase.
- Retrieve relevant code using semantic search.
- Investigate errors with a LangGraph agent.
- View requested tools during an investigation.
- Generate answers with source references.
- Keep the latest debugging result while switching interface modes.
- Download debugging reports as Markdown files.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Interface | Streamlit |
| LLM access | Groq through ChatGroq |
| LLM integration and tools | LangChain |
| Agent orchestration | LangGraph |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector database | Chroma |
| Environment configuration | python-dotenv |
| Demo tests | pytest |

The embedding model runs locally. Retrieved code snippets and questions
are sent to Groq when generating answers.

## How It Works

### Repository indexing

1. Read supported files from the selected folder.
2. Exclude hidden files, virtual environments, and other skipped folders.
3. Split file contents into overlapping token-based chunks.
4. Preserve file paths and source line numbers.
5. Generate embeddings and save the chunks in Chroma.

Each repository has a separate collection. Refreshing the index rebuilds
that repository's generated collection without changing its source files.

### Ask Codebase mode

1. Receive a question.
2. Retrieve three relevant code chunks.
3. Send the question and retrieved evidence to the LLM.
4. Display the answer and retrieved source locations.

### Debug Error mode

The agent chooses from three read-only tools:

| Tool | Purpose |
|---|---|
| list_files | List supported, non-empty repository files |
| search_code | Search indexed code by meaning |
| read_file | Read a bounded range of source lines |

LangGraph repeats the model-and-tool cycle until the agent answers or
reaches its four-tool-call limit.

## Main Files

| File | Purpose |
|---|---|
| app.py | Streamlit interface |
| src/loader.py | Read supported repository files |
| src/chunker.py | Create token-based chunks with source locations |
| src/embeddings.py | Initialize the local embedding model |
| src/indexer.py | Build and open Chroma collections |
| src/rag.py | Generate answers from retrieved code |
| src/tools.py | Define read-only agent tools |
| src/agent.py | Build the LangGraph investigation workflow |
| demo_project/calculator.py | Small demonstration project |
| tests/test_calculator.py | Tests for the corrected calculator |

## Setup on Windows

### 1. Open the project

Open the project folder in VS Code and open a PowerShell terminal.

### 2. Create a virtual environment

```powershell
py -3.12 -m venv .venv
```

### 3. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The first embedding-model run requires internet access to download
the model.

### 4. Configure Groq

Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Use a model available to your account that supports tool calling.
Do not commit your actual `.env` file or API key.

### 5. Start the app

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Open the local URL printed in the terminal.

## Usage

1. Enter the full path of a local project in the sidebar.
2. Click **Index / Refresh project**.
3. Select **Ask Codebase** or **Debug Error**.
4. Enter a question or problem description.
5. Review the answer and compare its references with the source code.

Refresh the index after changing project files.

### Example questions

- How does this project load its API key?
- Which folders does the repository loader skip?
- How does calculate_average handle an empty list?
- Why does this function raise IndexError?
- Where is the payment gateway configured?

The last question tests how the assistant handles missing evidence when
used with the calculator demo.

## Running the Demo Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_calculator.py -v
```

The calculator test suite contains nine cases covering:

- Average calculation.
- Empty-list handling.
- Percentage discounts.
- Last-item retrieval.

The corrected demo is expected to pass all nine cases.
These tests verify calculator behaviour, not the accuracy of the AI agent.

## Manual Agent Evaluation

Three scenarios were manually reviewed during development:

| Scenario | Finding |
|---|---|
| Empty-list handling | Correctly explained ValueError; citation wording improved |
| Discount calculation | Correct numerical explanation; exact output formatting and line references needed review |
| Missing payment configuration | Scope wording improved, but the model still incorrectly described settings.py as unsupported |

This is a small qualitative evaluation, not a measured overall accuracy
score. Generated citations and conclusions require verification.

Changes made during evaluation included:

- Requesting filenames and line ranges in citations.
- Distinguishing inferred output from executed results.
- Clarifying that the file inventory is partial.
- Asking the agent to acknowledge missing evidence.
- Avoiding unnecessary fixes when the code is already correct.

## Supported Files

The current loader accepts:

- `.py`
- `.md`
- `requirements.txt`
- `pyproject.toml`

It skips hidden files, selected generated folders, linked files,
oversized files, and files it cannot decode as UTF-8.

A normal, non-empty `settings.py` is supported.
Hidden `.env` files and YAML configuration files are not inspected.

## Limitations

- Answers and citations may be incorrect.
- Semantic retrieval can miss relevant code or exact identifiers.
- The embedding model is a general text model, not a specialized code model.
- The index must be refreshed after source changes.
- Each question is independent; displayed chat history is not passed
  to the model as conversation memory.
- Debugging results are stored in the current Streamlit session.
  Reloading the browser or restarting the server can clear them.
- The agent cannot inspect installed packages or the runtime environment.
- Dependency declarations do not prove that a package is installed.
- The agent has a four-tool-call investigation budget.
- The agent does not apply patches or execute tests.
- The exported report does not include complete tool traces.
- This version is intended for local, single-user use.

## Privacy

- Keep API keys in `.env`, excluded from Git.
- Do not paste secrets into questions or tracebacks.
- Source files can contain hard-coded secrets even when `.env` is excluded.
- Retrieved snippets are sent to Groq for answer generation.
- Chroma stores indexed source content locally in `chroma_db`.
- Review downloaded reports before sharing them.

## Future Improvements

- Exact identifier and keyword search alongside semantic retrieval.
- Function-aware chunking.
- Citation validation against retrieved evidence.
- A larger, repeatable agent evaluation dataset.
- Exported tool traces for easier review.
- Patch previews with explicit user approval.
- Isolated test execution.