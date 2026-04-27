from unittest.mock import MagicMock, patch

from fsc.providers.deepseek import DeepSeekProvider


def test_deepseek_generate_sends_chat_completions():
  provider = DeepSeekProvider(api_key="test-key")
  mock_response = MagicMock()
  mock_response.status_code = 200
  mock_response.json.return_value = {
    "choices": [{"message": {"content": "generated spec"}}]
  }

  with patch.object(provider._client, "post", return_value=mock_response) as mock_post:
    result = provider.generate("system prompt", "user prompt")

  mock_post.assert_called_once()
  args, kwargs = mock_post.call_args
  url = args[0] if args else kwargs.get("url", "")

  assert url.endswith("/chat/completions")

  payload = kwargs.get("json", {})

  assert payload["model"] == "deepseek-chat"
  assert len(payload["messages"]) == 2  # noqa: PLR2004
  assert payload["messages"][0]["role"] == "system"
  assert payload["messages"][0]["content"] == "system prompt"
  assert payload["messages"][1]["role"] == "user"
  assert payload["messages"][1]["content"] == "user prompt"
  assert result == "generated spec"
