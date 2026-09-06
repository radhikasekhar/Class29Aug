from rag_api.app.settings import Settings


def test_settings_reads_db_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv("DB_HOST", "database.internal")
    monkeypatch.setenv("DB_PORT", "5544")
    monkeypatch.setenv("DB_NAME", "rag_test")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "postgres")

    settings = Settings(_env_file=None)

    assert settings.db_host == "database.internal"
    assert settings.db_port == 5544
    assert settings.db_name == "rag_test"
    assert settings.db_user == "postgres"
    assert "host=database.internal" in settings.database_url