"""Streamlit UI for the Research Agent — wraps the same tool loop as chat.py."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Allow imports from starter_v0/ when running via `streamlit run app.py`
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import build_artifact_version
from chat import (
    run_model_tool_loop,
    write_transcript,
    trim_history,
    now_iso,
    safe_slug,
    artifact_version_dict,
)

load_lab_env(ROOT)

ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Agent",
    page_icon="🔬",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Cấu hình")

    provider_name = st.selectbox(
        "Provider",
        ["openrouter", "openai", "anthropic", "gemini"],
        index=0,
    )
    version_label = st.selectbox("Version", ["v3", "v2", "v1", "v0"], index=0)
    max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4)
    history_window = st.slider("History window (turns)", 1, 10, 5)

    st.divider()
    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.transcript = None
        st.rerun()

    st.divider()
    st.caption("Tools đang hoạt động:")
    for name in TOOL_FUNCTIONS:
        st.caption(f"• `{name}`")

# ── Load artifacts ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_artifacts(provider_name: str, version_label: str):
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(provider_name)
    artifact_version = build_artifact_version(version_label, system_prompt_path, tools_path)
    return system_prompt, openai_tools, provider, artifact_version, system_prompt_path, tools_path

system_prompt, openai_tools, provider, artifact_version, sp_path, t_path = load_artifacts(
    provider_name, version_label
)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []      # display messages (role + content)
if "history" not in st.session_state:
    st.session_state.history = []       # raw message dicts for model context
if "transcript" not in st.session_state:
    st.session_state.transcript = None  # transcript dict

def ensure_transcript() -> dict:
    if st.session_state.transcript is None:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        tid = f"{safe_slug(version_label)}_{safe_slug(provider_name)}_{timestamp}"
        st.session_state.transcript = {
            "transcript_id": tid,
            **artifact_version_dict(artifact_version),
            "provider": provider_name,
            "model": None,
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
    return st.session_state.transcript

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🔬 Research Agent")
col1, col2, col3 = st.columns(3)
col1.metric("Provider", provider_name)
col2.metric("Version", version_label)
col3.metric("Tools", len(TOOL_FUNCTIONS))

st.divider()

# ── Chat history display ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tool_events"):
            for event in msg["tool_events"]:
                tool_name = event.get("tool", "?")
                args = event.get("args", {})
                result = event.get("result", {})
                with st.expander(f"🔧 `{tool_name}` — xem chi tiết", expanded=False):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.caption("**Args**")
                        st.json(args)
                    with col_b:
                        st.caption("**Result**")
                        st.json(result)

# ── Input ──────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Nhập câu hỏi của bạn...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Build messages for model
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_input},
    ]

    with st.chat_message("assistant"):
        with st.spinner("Agent đang suy nghĩ..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=max_tool_rounds,
                )
                assistant_text = result["assistant_text"]
                tool_events = result.get("tool_events", [])

                st.markdown(assistant_text)

                # Show tool calls inline
                for event in tool_events:
                    tool_name = event.get("tool", "?")
                    args = event.get("args", {})
                    result_data = event.get("result", {})
                    with st.expander(f"🔧 `{tool_name}` — xem chi tiết", expanded=False):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.caption("**Args**")
                            st.json(args)
                        with col_b:
                            st.caption("**Result**")
                            st.json(result_data)

            except Exception as exc:
                assistant_text = f"❌ Lỗi: {type(exc).__name__}: {exc}"
                tool_events = []
                st.error(assistant_text)

    # Update session
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_text,
        "tool_events": tool_events,
    })
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": assistant_text})

    # Save transcript
    transcript = ensure_transcript()
    transcript["turns"].append({
        "turn_index": len(transcript["turns"]) + 1,
        "user": user_input,
        "assistant_text": assistant_text,
        "tool_events": tool_events,
        "ended_at": now_iso(),
    })
    tid = transcript["transcript_id"]
    transcript_path = TRANSCRIPTS_DIR / f"{tid}.transcript.json"
    write_transcript(transcript_path, transcript)
