"""运行时配置加载测试。"""

from config import Settings


# 验证默认配置适合本地 Ollama 开发。
def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    settings = Settings.from_env()

    assert settings.model_provider == "ollama"
    assert settings.ollama_model == "qwen3:4b"
