from langchain_core.messages import HumanMessage
from src.agent import build_debug_agent

from pathlib import Path

import streamlit as st

from src.indexer import index_repository
from src.rag import answer_question


st.set_page_config(
    page_title="CodeLens AI",
    page_icon="🔎",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parent

# Keep interface data between Streamlit reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_repo" not in st.session_state:
    st.session_state.active_repo = None

if "indexed_repo" not in st.session_state:
    st.session_state.indexed_repo = None

if "index_stats" not in st.session_state:
    st.session_state.index_stats = None

if "debug_result" not in st.session_state:
    st.session_state.debug_result = None

if "debug_activity" not in st.session_state:
    st.session_state.debug_activity = []

st.title("🔎 CodeLens AI")
st.write("Understand your Python project with answers grounded in its code.")
st.caption(
    "Each question is answered independently. "
    "Include function or file names when possible."
)

with st.sidebar:
    st.header("Your repository")

    repo_input = st.text_input(
        "Local project folder",
        value=str(PROJECT_ROOT),
        help="Enter the full path of the project you want to inspect.",
    )

    repo_path = None

    if repo_input.strip():
        try:
            candidate = Path(repo_input.strip()).expanduser().resolve()

            if candidate.is_dir():
                repo_path = str(candidate)
            else:
                st.warning("This folder does not exist.")
        except (OSError, ValueError):
            st.warning("Enter a valid folder path.")

    # Reset the displayed chat when switching repositories.
    if repo_path != st.session_state.active_repo:
        st.session_state.debug_result = None
        st.session_state.debug_activity = []
        st.session_state.active_repo = repo_path
        st.session_state.messages = []
        st.session_state.indexed_repo = None
        st.session_state.index_stats = None

    if st.button(
        "Index / Refresh project",
        disabled=repo_path is None,
    ):
        # Disable questions until indexing finishes successfully.
        st.session_state.indexed_repo = None
        st.session_state.index_stats = None
        st.session_state.messages = []

        try:
            with st.spinner("Reading and indexing code..."):
                _, file_count, chunk_count = index_repository(repo_path)

            st.session_state.indexed_repo = repo_path
            st.session_state.index_stats = {
                "files": file_count,
                "chunks": chunk_count,
            }

        except Exception as error:
            st.error(
                f"Indexing failed ({type(error).__name__}). "
                "Check your folder and embedding model setup."
            )

    if st.session_state.index_stats:
        stats = st.session_state.index_stats
        st.success("Project indexed")
        st.metric("Files", stats["files"])
        st.metric("Chunks", stats["chunks"])

    if st.button("Clear conversation"):
        st.session_state.messages = []

    st.divider()
    st.caption("Refresh the index after changing project files.")
    st.caption(
        "Indexing runs locally. Asking a question sends "
        "retrieved code snippets to Groq."
    )


def show_message(message):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("Retrieved sources"):
                for number, source in enumerate(
                    message["sources"], start=1
                ):
                    st.text(f"[Source {number}] {source}")


# for message in st.session_state.messages:
#     show_message(message)

# ready = (
#     repo_path is not None
#     and st.session_state.indexed_repo == repo_path
# )

# if not ready:
#     st.info("Select a project folder and click 'Index / Refresh project'.")

# question = st.chat_input(
#     "Ask about your code...",
#     disabled=not ready,
#     max_chars=1000,
# )

# if question:
#     user_message = {
#         "role": "user",
#         "content": question,
#     }

#     st.session_state.messages.append(user_message)
#     show_message(user_message)

#     try:
#         with st.spinner("Searching code and generating an answer..."):
#             result = answer_question(repo_path, question)

#         assistant_message = {
#             "role": "assistant",
#             "content": result["answer"],
#             "sources": result["sources"],
#         }

#         st.session_state.messages.append(assistant_message)
#         show_message(assistant_message)

#     except Exception as error:
#         st.error(
#             f"Could not generate an answer ({type(error).__name__}). "
#             "Check your API configuration, internet connection, "
#             "and Groq usage limits, then try again."
#         )

ready = (
    repo_path is not None
    and st.session_state.indexed_repo == repo_path
)

mode = st.radio(
    "Choose a mode",
    ["Ask Codebase", "Debug Error"],
    horizontal=True,
)

if not ready:
    st.info(
        "Select a project folder and click "
        "'Index / Refresh project' first."
    )


# ---------------- ASK CODEBASE ----------------
if mode == "Ask Codebase":
    for message in st.session_state.messages:
        show_message(message)

    question = st.chat_input(
        "Ask about your code...",
        disabled=not ready,
        max_chars=1000,
    )

    if question:
        user_message = {
            "role": "user",
            "content": question,
        }

        st.session_state.messages.append(user_message)
        show_message(user_message)

        try:
            with st.spinner("Searching code and generating an answer..."):
                result = answer_question(repo_path, question)

            assistant_message = {
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"],
            }

            st.session_state.messages.append(assistant_message)
            show_message(assistant_message)

        except Exception as error:
            st.error(
                f"Could not generate an answer "
                f"({type(error).__name__}). "
                "Check your API configuration, connection, "
                "and Groq usage limits."
            )


# ---------------- DEBUG ERROR ----------------
# ---------------- DEBUG ERROR ----------------
else:
    st.subheader("Investigate an error")
    st.write(
        "Describe what you expected, what happened, "
        "and paste the traceback if available."
    )
    st.caption(
        "Remove API keys and passwords before submitting. "
        "The agent suggests fixes but does not edit or execute code."
    )

    with st.form("debug_form"):
        problem = st.text_area(
            "Problem description or traceback",
            height=220,
            max_chars=6000,
            placeholder="Describe the problem or paste a traceback...",
        )

        submitted = st.form_submit_button(
            "Investigate error",
            disabled=not ready,
        )

    if st.button("Clear debugging result"):
        st.session_state.debug_result = None
        st.session_state.debug_activity = []

    if submitted:
        if not problem.strip():
            st.warning("Enter a problem description or traceback.")
        else:
            st.session_state.debug_result = None
            st.session_state.debug_activity = []

            progress_display = st.empty()
            final_answer = None

            try:
                with st.spinner("Agent is investigating..."):
                    agent = build_debug_agent(repo_path)

                    for update in agent.stream(
                        {
                            "messages": [
                                HumanMessage(content=problem.strip())
                            ],
                            "tool_calls_used": 0,
                        },
                        config={"recursion_limit": 20},
                        stream_mode="updates",
                    ):
                        for node_name, data in update.items():
                            for message in data.get("messages", []):

                                if node_name == "assistant":
                                    if message.tool_calls:
                                        for call in message.tool_calls:
                                            st.session_state.debug_activity.append(
                                                "Requested tool: "
                                                + call["name"]
                                            )
                                    else:
                                        final_answer = message.content

                                elif node_name == "tools":
                                    st.session_state.debug_activity.append(
                                        "Tool response received."
                                    )

                                progress_display.text(
                                    "\n".join(
                                        st.session_state.debug_activity
                                    )
                                    or "Preparing an answer..."
                                )

                if final_answer:
                    st.session_state.debug_result = {
                        "problem": problem.strip(),
                        "answer": final_answer,
                        "repository": repo_path,
                    }
                else:
                    st.warning(
                        "No final explanation was returned. "
                        "Try a more specific question."
                    )

            except Exception as error:
                st.error(
                    f"Investigation stopped "
                    f"({type(error).__name__}). "
                    "Check your connection, API settings, "
                    "and Groq usage limits."
                )

            finally:
                progress_display.empty()

    # Display saved information on every rerun.
    if st.session_state.debug_activity:
        with st.expander("Agent activity"):
            st.text(
                "\n".join(st.session_state.debug_activity)
            )

    saved_result = st.session_state.debug_result

    if saved_result:
        st.subheader("Latest investigation")

        with st.expander("Original problem"):
            st.text(saved_result["problem"])

        st.markdown(saved_result["answer"])

        st.caption(
            "Suggested fixes have not been executed "
            "or verified by this app."
        )

        report = (
            "# CodeLens AI — Debugging Report\n\n"
            f"Repository: {saved_result['repository']}\n\n"
            "## Problem\n\n"
            f"{saved_result['problem']}\n\n"
            "## Investigation\n\n"
            f"{saved_result['answer']}\n\n"
            "## Verification status\n\n"
            "Suggested fixes have not been executed or verified "
            "by this app.\n"
        )

        st.download_button(
            label="Download debugging report",
            data=report,
            file_name="codelens_debug_report.md",
            mime="text/markdown",
        )