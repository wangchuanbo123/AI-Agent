"""运行时配置加载测试。"""

from config import Settings


# 验证默认配置使用 GLM Coding Pro 的 OpenAI 兼容接口。
def test_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_COMPATIBLE_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_COMPATIBLE_BASE_URL", raising=False)

    settings = Settings.from_env()

    assert settings.model_provider == "openai_compatible"
    assert settings.openai_compatible_model == "glm-5-turbo"
    assert (
        settings.openai_compatible_base_url
        == "https://api.iruidong.com/v1"
    )
