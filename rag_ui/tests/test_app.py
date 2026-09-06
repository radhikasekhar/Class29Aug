from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_chat_ui_renders_controls_and_starts_empty() -> None:
    app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py")).run()

    assert not app.exception
    assert app.selectbox(key="provider").value == "Ollama"
    assert app.slider(key="top_k").value == 8
    assert app.session_state["messages"] == []