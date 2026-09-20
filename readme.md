# 🎧 StudyTube — YouTube Transcript Reader & AI Study Assistant

StudyTube is a Streamlit-based AI web application that turns YouTube videos into structured study material and lets users ask follow-up questions about the video.

The application extracts the transcript of a YouTube video, analyzes it using a Hugging Face language model, and provides an interactive chat interface where users can ask questions grounded in the video's transcript and generated analysis.

---

## ✨ Features

- 🎥 **YouTube Video Input**
  - Accepts YouTube video URLs.
  - Supports standard YouTube URLs, shortened `youtu.be` URLs, and YouTube Shorts.

- 📝 **Automatic Transcript Extraction**
  - Retrieves available transcripts using `youtube-transcript-api`.
  - Converts transcript segments into a single text representation for processing.

- 🧠 **AI-Powered Video Analysis**
  - Uses **Qwen3-8B** through Hugging Face.
  - Converts raw transcripts into structured study material.

- 📚 **Structured Study Notes**
  - Each analyzed video is organized into:
    - Overview
    - Key Topics
    - Detailed Summary
    - Key Takeaways
    - Important Terms & Concepts
    - Questions Answered
    - Limitations / Unclear Points

- 💬 **Follow-Up AI Chat**
  - Users can ask questions about the video after analysis.
  - Uses **Llama 3.1 8B Instruct** for conversational follow-up questions.
  - Maintains conversation history during the current session.

- 🔎 **Transcript Access**
  - The original transcript can be expanded and viewed inside the application.

- ⚡ **Simple Interactive UI**
  - Built entirely with Streamlit.
  - No separate frontend framework or JavaScript application is required.

---

## 🏗️ How It Works

The application follows a simple pipeline:

```text
                YouTube URL
                     │
                     ▼
             Extract Video ID
                     │
                     ▼
          Fetch YouTube Transcript
                     │
                     ▼
              Raw Transcript
                     │
                     ▼
             ┌───────────────┐
             │   Qwen3-8B    │
             │ Video Analysis│
             └───────────────┘
                     │
                     ▼
          Structured Video Analysis
                     │
                     ▼
              User asks a question
                     │
                     ▼
        Transcript + Analysis + History
                     │
                     ▼
        ┌──────────────────────────┐
        │ Llama 3.1 8B Instruct    │
        │   Follow-up Assistant     │
        └──────────────────────────┘
                     │
                     ▼
               AI Response