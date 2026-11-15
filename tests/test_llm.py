from backend.llm import get_setting


def test_environment_variable_wins(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".streamlit").mkdir()
    (tmp_path / ".streamlit" / "secrets.toml").write_text('LLM_MODEL = "from-file"')
    monkeypatch.setenv("LLM_MODEL", "from-env")

    assert get_setting("LLM_MODEL") == "from-env"


def test_falls_back_to_secrets_file(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".streamlit").mkdir()
    (tmp_path / ".streamlit" / "secrets.toml").write_text('LLM_MODEL = "from-file"')
    monkeypatch.delenv("LLM_MODEL", raising=False)

    assert get_setting("LLM_MODEL") == "from-file"


def test_default_when_setting_is_missing(monkeypatch, tmp_path):
    # Empty folder: no environment variable and no secrets file (like CI)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    assert get_setting("LLM_MODEL", "default-model") == "default-model"
