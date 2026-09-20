import os
from urllib.parse import urlparse, parse_qs

import streamlit as st
from dotenv import load_dotenv

import requests
from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEndpoint
)

from langchain_core.messages import (
    HumanMessage,
    AIMessage
)

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()



st.set_page_config(
    page_title="StudyTube",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
#
# Design idea: a study notebook.
#   - graph-paper background
#   - navy ink for text, blue for actions
#   - a yellow highlighter used ONLY on the section headings
#     of the generated notes (the one memorable detail)
# ============================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap');

    :root {
        --paper:      #f5f7fa;
        --grid:       #e6ebf3;
        --card:       #ffffff;
        --ink:        #16223b;
        --ink-soft:   #4a5672;
        --muted:      #7b869e;
        --line:       #d8dfec;
        --blue:       #2b4bd6;
        --blue-dark:  #2039a8;
        --blue-tint:  #eaf0ff;
        --highlight:  #ffe27a;

        --font-ui:    "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
        --font-read:  "Newsreader", Georgia, "Times New Roman", serif;

        color-scheme: light;
    }


    /* -------------------------------------------------------
       GLOBAL
    ------------------------------------------------------- */

    html, body, .stApp {
        font-family: var(--font-ui);
        color: var(--ink);
    }

    .stApp {
        background-color: var(--paper);
        background-image:
            linear-gradient(var(--grid) 1px, transparent 1px),
            linear-gradient(90deg, var(--grid) 1px, transparent 1px);
        background-size: 32px 32px;
        background-attachment: fixed;
    }

    .block-container {
        max-width: 1040px;
        padding-top: 3.5rem;
        padding-bottom: 6rem;
    }

    /* Remove default Streamlit clutter */

    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }


    /* -------------------------------------------------------
       HERO
    ------------------------------------------------------- */

    .hero {
        margin-bottom: 2rem;
    }

    .hero-title {
        font-family: var(--font-ui);
        font-size: 4.2rem;
        font-weight: 800;
        letter-spacing: -0.045em;
        line-height: 1;
        color: var(--ink);
        margin: 0 0 0.9rem 0;
    }

    .hero-subtitle {
        font-family: var(--font-read);
        font-size: 1.3rem;
        line-height: 1.5;
        color: var(--ink-soft);
        max-width: 34rem;
        margin: 0;
    }


    /* -------------------------------------------------------
       CARDS (bordered containers)
    ------------------------------------------------------- */

    .st-key-inputcard,
    .st-key-statscard,
    .st-key-notescard {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: 0 1px 0 rgba(22, 34, 59, 0.04),
                    0 12px 32px -18px rgba(22, 34, 59, 0.25);
        padding: 1.1rem 1.2rem;
    }

    .st-key-notescard {
        padding: 1.4rem 2rem 1.8rem 2rem;
    }


    /* -------------------------------------------------------
       INPUT
    ------------------------------------------------------- */

    div[data-testid="stTextInput"] label {
        color: var(--ink-soft);
        font-weight: 600;
        font-size: 0.9rem;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background: var(--paper) !important;
        border-color: var(--line) !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        min-height: 52px;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 3px rgba(43, 75, 214, 0.15);
    }

    div[data-testid="stTextInput"] input {
        background: transparent !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink);
        caret-color: var(--blue);
        font-family: var(--font-ui);
        font-size: 1rem;
        padding: 0.85rem 1rem;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted);
        opacity: 1;
    }


    /* -------------------------------------------------------
       BUTTONS
    ------------------------------------------------------- */

    .stButton > button {
        font-family: var(--font-ui);
        border-radius: 12px;
        border: 1px solid var(--blue);
        background: var(--blue);
        color: #ffffff;
        font-weight: 600;
        font-size: 0.98rem;
        min-height: 52px;
        transition: background 0.15s ease, border-color 0.15s ease;
    }

    /* keep button labels in the UI font, not the reading serif */
    .stButton > button p {
        font-family: var(--font-ui) !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        line-height: 1.2 !important;
        color: #ffffff !important;
    }

    .stButton > button:hover {
        background: var(--blue-dark);
        border-color: var(--blue-dark);
        color: #ffffff;
    }

    .stButton > button:focus-visible {
        outline: 3px solid rgba(43, 75, 214, 0.35);
        outline-offset: 2px;
    }

    /* the "analyze another" button is secondary */
    .st-key-reset .stButton > button {
        background: transparent;
        color: var(--ink);
        border: 1px solid var(--line);
    }

    .st-key-reset .stButton > button:hover {
        background: var(--card);
        border-color: var(--ink-soft);
        color: var(--ink);
    }

    .st-key-reset .stButton > button p {
        color: var(--ink) !important;
    }


    /* -------------------------------------------------------
       HEADINGS
    ------------------------------------------------------- */

    h1, h2, h3 {
        font-family: var(--font-ui) !important;
        color: var(--ink) !important;
        letter-spacing: -0.02em;
    }

    h3 {
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }

    /* Section headings inside the generated notes get the
       highlighter treatment */

    [data-testid="stMarkdownContainer"] h2 {
        display: inline-block;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        margin-top: 1.6rem !important;
        padding: 0 0.35rem;
        margin-left: -0.35rem;
        background: linear-gradient(
            transparent 58%,
            var(--highlight) 58%,
            var(--highlight) 92%,
            transparent 92%
        );
    }


    /* -------------------------------------------------------
       READING TEXT (notes, transcript)
    ------------------------------------------------------- */

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        font-family: var(--font-read);
        font-size: 1.12rem;
        line-height: 1.72;
        color: var(--ink);
    }

    [data-testid="stMarkdownContainer"] li {
        margin-bottom: 0.3rem;
    }

    [data-testid="stMarkdownContainer"] strong {
        font-weight: 600;
        color: var(--ink);
    }

    [data-testid="stMarkdownContainer"] code {
        background: var(--blue-tint);
        color: var(--blue-dark);
        border-radius: 6px;
        padding: 0.1rem 0.4rem;
        font-size: 0.92em;
    }


    /* -------------------------------------------------------
       DIVIDERS
    ------------------------------------------------------- */

    hr {
        border-color: var(--line);
        margin-top: 2.4rem;
        margin-bottom: 2.4rem;
    }


    /* -------------------------------------------------------
       VIDEO
    ------------------------------------------------------- */

    [data-testid="stVideo"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--line);
        box-shadow: 0 16px 36px -22px rgba(22, 34, 59, 0.45);
    }


    /* -------------------------------------------------------
       STATS PANEL
    ------------------------------------------------------- */

    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 0.85rem 0;
        border-bottom: 1px solid var(--line);
    }

    .stat-row:last-child {
        border-bottom: none;
    }

    .stat-label {
        color: var(--ink-soft);
        font-size: 0.95rem;
    }

    .stat-value {
        font-weight: 700;
        font-size: 1.35rem;
        letter-spacing: -0.02em;
        color: var(--ink);
    }

    .panel-title {
        font-weight: 700;
        font-size: 1.15rem;
        margin: 0.3rem 0 0.2rem 0;
        color: var(--ink);
    }

    .panel-text {
        font-family: var(--font-read);
        color: var(--ink-soft);
        font-size: 1.05rem;
        line-height: 1.55;
        margin: 0 0 0.6rem 0;
    }


    /* -------------------------------------------------------
       CHAT
    ------------------------------------------------------- */

    [data-testid="stChatMessage"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }

    /* user messages get a soft blue tint */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: var(--blue-tint);
        border-color: #cfdaf8;
    }

    [data-testid="stChatMessage"] p {
        line-height: 1.7;
    }

    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"] {
        background: var(--paper) !important;
    }

    [data-testid="stChatInput"] {
        border-radius: 14px;
        border-color: var(--line) !important;
        background: var(--card) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink);
        font-family: var(--font-ui);
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--muted) !important;
        -webkit-text-fill-color: var(--muted);
        opacity: 1;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--blue);
        box-shadow: 0 0 0 3px rgba(43, 75, 214, 0.15);
    }


    /* -------------------------------------------------------
       EXPANDERS
    ------------------------------------------------------- */

    [data-testid="stExpander"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        overflow: hidden;
    }

    [data-testid="stExpander"] summary {
        font-weight: 600;
        color: var(--ink);
    }


    /* -------------------------------------------------------
       ALERTS / CAPTIONS
    ------------------------------------------------------- */

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted);
        font-size: 0.92rem;
    }

    .muted {
        color: var(--muted);
        font-size: 0.85rem;
    }


    /* -------------------------------------------------------
       MOBILE
    ------------------------------------------------------- */

    @media (max-width: 768px) {

        .block-container {
            padding-top: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-title {
            font-size: 3rem;
        }

        .hero-subtitle {
            font-size: 1.1rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        * { transition: none !important; }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD MODELS
# ============================================================

@st.cache_resource
def load_models():

    hf_token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]

    qwen_llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen3-8B",
        temperature=0.4,
        max_new_tokens=1500,
        huggingfacehub_api_token=hf_token
    )

    qwen = ChatHuggingFace(llm=qwen_llm)

    llama_llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        task="text-generation",
        temperature=0.3,
        max_new_tokens=700,
        huggingfacehub_api_token=hf_token
    )

    llama = ChatHuggingFace(llm=llama_llm)

    return qwen, llama


try:

    analyzer_model, chat_model = load_models()

except Exception as e:

    st.error(
        "Could not load the Hugging Face models."
    )

    st.code(str(e))

    st.stop()


# ============================================================
# PROMPT 1 — VIDEO ANALYSIS
# ============================================================

analysis_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
You are an expert video content analyst and study assistant.

Your task is to analyze YouTube video transcripts accurately
and turn them into useful study material.

Rules:
- Base your response on the transcript.
- Do not invent facts or claims.
- Remove filler, repetition and irrelevant conversation.
- Preserve important technical details, examples, formulas
  and definitions.
- If something is unclear or unsupported by the transcript,
  explicitly mention that.
- Organize the information clearly.
- Use simple but technically accurate language.
"""
    ),

    (
        "human",
        """
Analyze the following YouTube video transcript.

TRANSCRIPT
-----------
{transcript}
-----------

Provide the analysis using exactly these sections:

## Overview

Give a concise explanation of what the video is about.

## Key Topics

List and briefly explain the major topics discussed.

## Detailed Summary

Explain the important points while maintaining the logical
flow of the video.

## Key Takeaways

List the most important things a viewer should remember.

## Important Terms & Concepts

Identify important technical terms, concepts, tools,
people or ideas and briefly explain them.

## Questions Answered

Identify important questions addressed by the video and
provide their answers based on the transcript.

## Limitations / Unclear Points

Mention anything that is unclear, incomplete or ambiguous.
"""
    )
])


# ============================================================
# PROMPT 2 — FOLLOW-UP QUESTIONS
# ============================================================

followup_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
You are a helpful AI assistant answering follow-up questions
about a YouTube video.

You have access to:

1. The original video transcript.
2. An analysis generated from that transcript.
3. The previous conversation with the user.

Your job is to answer the user's questions accurately,
clearly and conversationally.

IMPORTANT RULES:

- Use the transcript and analysis as your primary sources.
- Do not invent information that is not supported by them.
- If the answer cannot be determined from the video,
  clearly say so.
- If the user asks about something mentioned in the video,
  explain it using the video's context.
- You may use general knowledge to clarify a concept,
  but clearly distinguish it from what the video itself said.
- Keep answers proportional to the question.
- Do not repeat the entire video summary unnecessarily.
- When explaining technical concepts, use examples when useful.

VIDEO TRANSCRIPT
----------------
{transcript}
----------------

VIDEO ANALYSIS
---------------
{analysis}
---------------
"""
    ),

    MessagesPlaceholder(
        variable_name="chat_history"
    ),

    (
        "human",
        "{question}"
    )
])


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_video_id(url):

    parsed_url = urlparse(url)

    hostname = parsed_url.hostname

    # youtube.com/watch?v=...
    if hostname in [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com"
    ]:

        if parsed_url.path == "/watch":

            return parse_qs(
                parsed_url.query
            ).get("v", [None])[0]


        # youtube.com/shorts/VIDEO_ID
        if parsed_url.path.startswith("/shorts/"):

            parts = parsed_url.path.strip("/").split("/")

            if len(parts) >= 2:

                return parts[1]


    # youtu.be/VIDEO_ID
    if hostname in [
        "youtu.be",
        "www.youtu.be"
    ]:

        return parsed_url.path.lstrip(
            "/"
        ).split("/")[0]


    return None


def fetch_transcript(video_id):
    url = "https://api.freetranscriptapi.com/v1/transcript"

    response = requests.get(
        url,
        params={"video_url": video_id},
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    transcript_segments = data.get("transcript", [])

    if not transcript_segments:
        raise ValueError("No transcript was found for this video.")

    return " ".join(
        segment["text"]
        for segment in transcript_segments
    )


# ============================================================
# SESSION STATE
# ============================================================

if "video_id" not in st.session_state:
    st.session_state.video_id = None

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# HERO
# ============================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-title">StudyTube</div>'
    '<p class="hero-subtitle">'
    'Paste a YouTube link and get clean study notes, '
    'then ask questions about what you watched.'
    '</p>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# URL INPUT
# ============================================================

with st.container(key="inputcard"):

    input_col, button_col = st.columns(
        [4, 1.3],
        gap="small",
        vertical_alignment="center"
    )

    with input_col:

        url = st.text_input(
            "YouTube video",
            placeholder="Paste a YouTube link, e.g. youtube.com/watch?v=...",
            label_visibility="collapsed"
        )

    with button_col:

        analyze_button = st.button(
            "Analyze video",
            use_container_width=True
        )


# ============================================================
# NEW VIDEO BUTTON
# ============================================================

if st.session_state.video_id:

    st.write("")

    with st.container(key="reset"):

        if st.button(
            "Analyze another video"
        ):

            st.session_state.video_id = None
            st.session_state.transcript = None
            st.session_state.analysis = None
            st.session_state.chat_history = []

            st.rerun()


# ============================================================
# PROCESS VIDEO
# ============================================================

if analyze_button:

    if not url.strip():

        st.warning(
            "Paste a YouTube link first."
        )

    else:

        video_id = get_video_id(
            url.strip()
        )

        if not video_id:

            st.error(
                "That doesn't look like a valid YouTube link."
            )

        else:

            try:

                # --------------------------------------------
                # Fetch transcript
                # --------------------------------------------

                with st.spinner(
                    "Fetching the transcript..."
                ):

                    transcript = fetch_transcript(
                        video_id
                    )


                # --------------------------------------------
                # Analyze transcript
                # --------------------------------------------

                with st.spinner(
                    "Reading and analyzing the video..."
                ):

                    prompt = analysis_prompt.invoke({

                        "transcript": transcript

                    })

                    response = analyzer_model.invoke(
                        prompt
                    )


                # --------------------------------------------
                # Store state
                # --------------------------------------------

                st.session_state.video_id = video_id

                st.session_state.transcript = transcript

                st.session_state.analysis = response.content

                st.session_state.chat_history = []

                st.rerun()


            except Exception as e:

                st.error(
                    "Something went wrong while processing "
                    "the video."
                )

                with st.expander(
                    "View error details"
                ):

                    st.code(
                        str(e)
                    )


# ============================================================
# RESULTS
# ============================================================

if st.session_state.analysis:

    st.divider()


    # ========================================================
    # VIDEO + QUICK INFO
    # ========================================================

    left, right = st.columns(
        [1.25, 0.75],
        gap="large"
    )


    with left:

        st.video(
            f"https://www.youtube.com/watch?v="
            f"{st.session_state.video_id}"
        )


    with right:

        word_count = len(
            st.session_state.transcript.split()
        )

        read_minutes = max(
            1,
            round(word_count / 230)
        )

        questions_asked = sum(
            isinstance(m, HumanMessage)
            for m in st.session_state.chat_history
        )

        with st.container(key="statscard"):

            st.markdown(
                '<div class="panel-title">Your notes are ready</div>'
                '<p class="panel-text">'
                'Answers stay grounded in what the video says.'
                '</p>'
                '<div class="stat-row">'
                '<span class="stat-label">Transcript length</span>'
                f'<span class="stat-value">{word_count:,} words</span>'
                '</div>'
                '<div class="stat-row">'
                '<span class="stat-label">Time to read it</span>'
                f'<span class="stat-value">~{read_minutes} min</span>'
                '</div>'
                '<div class="stat-row">'
                '<span class="stat-label">Questions asked</span>'
                f'<span class="stat-value">{questions_asked}</span>'
                '</div>',
                unsafe_allow_html=True
            )


    st.divider()


    # ========================================================
    # ANALYSIS
    # ========================================================

    st.subheader(
        "Study notes"
    )

    with st.container(key="notescard"):

        st.markdown(
            st.session_state.analysis
        )


    # ========================================================
    # TRANSCRIPT
    # ========================================================

    st.write("")

    with st.expander(
        "View original transcript"
    ):

        st.caption(
            "This is the raw transcript retrieved from YouTube."
        )

        st.write(
            st.session_state.transcript
        )


    st.divider()


    # ========================================================
    # CHAT
    # ========================================================

    st.subheader(
        "Ask about the video"
    )

    st.caption(
        "Ask about the concepts, examples or ideas "
        "discussed in the video."
    )


    # --------------------------------------------------------
    # Display previous messages
    # --------------------------------------------------------

    for message in st.session_state.chat_history:

        if isinstance(
            message,
            HumanMessage
        ):

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    message.content
                )


        elif isinstance(
            message,
            AIMessage
        ):

            with st.chat_message(
                "assistant"
            ):

                st.markdown(
                    message.content
                )


    # --------------------------------------------------------
    # Chat input
    # --------------------------------------------------------

    question = st.chat_input(
        "Ask a follow-up question..."
    )


    if question:

        # --------------------------------------------
        # Show user message
        # --------------------------------------------

        with st.chat_message(
            "user"
        ):

            st.markdown(
                question
            )


        # --------------------------------------------
        # Generate response
        # --------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Thinking..."
            ):

                fin2_prompt = followup_prompt.invoke({

                    "transcript":
                        st.session_state.transcript,

                    "analysis":
                        st.session_state.analysis,

                    "chat_history":
                        st.session_state.chat_history,

                    "question":
                        question
                })


                reply = chat_model.invoke(
                    fin2_prompt
                )


                answer = reply.content


                st.markdown(
                    answer
                )


        # --------------------------------------------
        # Save conversation
        # --------------------------------------------

        st.session_state.chat_history.append(
            HumanMessage(
                content=question
            )
        )

        st.session_state.chat_history.append(
            AIMessage(
                content=answer
            )
        )