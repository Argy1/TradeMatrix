"""Ask Gemini to score a batch of headlines, and trust nothing it returns without checking.

Rules from CLAUDE.md and docs/03: called only from the worker, JSON schema, temperature 0,
validated output. The model gets no tools and cannot take any action; its reply is only read
as numbers and short text.
"""

import json
from collections.abc import Awaitable, Callable, Sequence

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import ValidationError

from app.sentiment.prompts import PROMPT_VERSION, build_prompt
from app.sentiment.schemas import HeadlineSentiment, ToScore, response_schema

# (prompt, response JSON schema) -> the reply text. Tests pass a fake instead of the real API.
Generate = Callable[[str, dict], Awaitable[str]]

ATTEMPTS = 2  # one retry when the service has a hiccup or the reply is not usable


class SentimentError(Exception):
    """Gemini could not be reached, refused the request or kept sending unusable replies."""


class Retryable(Exception):
    """A failure that may be gone on the next try (server error, timeout)."""


def parse_reply(
    reply: str, sent_ids: Sequence[int], symbols: Sequence[str]
) -> list[HeadlineSentiment]:
    """The valid results for headlines we actually sent; everything else is dropped.

    Raises ValueError when the reply as a whole is not the JSON object we asked for.
    """
    data = json.loads(reply)  # JSONDecodeError is a ValueError
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("the reply is not an object with an 'items' list")
    allowed, wanted = set(symbols), set(sent_ids)
    results: dict[int, HeadlineSentiment] = {}
    for raw in data["items"]:
        try:
            item = HeadlineSentiment.model_validate(raw)
        except ValidationError:
            continue  # one bad item (score out of range, unknown event type) loses only itself
        if item.id not in wanted or item.id in results:
            continue  # an id we never sent, or the same id twice
        # Keep only coins we support, in our own order, whatever the model wrote.
        item.assets = [symbol for symbol in symbols if symbol in allowed.intersection(item.assets)]
        results[item.id] = item
    return list(results.values())


def gemini_generate(
    api_key: str, model: str, timeout_ms: int = 30_000
) -> tuple[Generate, genai.Client]:
    """The real call, through Google's official SDK."""
    client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=timeout_ms))

    async def generate(prompt: str, schema: dict) -> str:
        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    # As repeatable as the model allows. Scores can still differ a little
                    # between two calls, one more reason a headline is scored once and stored.
                    temperature=0,
                    response_mime_type="application/json",
                    response_json_schema=schema,
                    # The model gets no tools and may call no functions: it only returns text.
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
        except genai_errors.ServerError as exc:
            raise Retryable(f"Gemini server error {exc.code}") from exc
        except (TimeoutError, httpx.TransportError) as exc:
            # No answer at all (timeout, dropped connection): worth one more try.
            raise Retryable(f"Gemini could not be reached ({type(exc).__name__})") from exc
        except genai_errors.APIError as exc:
            # 4xx: wrong key, unknown model, quota used up. Trying again right away cannot help.
            raise SentimentError(f"Gemini refused the request ({exc.code} {exc.status})") from exc
        return response.text or ""

    return generate, client


class GeminiScorer:
    def __init__(self, generate: Generate, model: str, client: genai.Client | None = None) -> None:
        self.model = model
        self.prompt_version = PROMPT_VERSION
        self._generate = generate
        self._client = client

    @classmethod
    def from_key(cls, api_key: str, model: str) -> "GeminiScorer":
        if not api_key or not model:
            raise ValueError("GEMINI_API_KEY and GEMINI_MODEL are required for sentiment")
        generate, client = gemini_generate(api_key, model)
        return cls(generate, model, client)

    async def score(
        self, headlines: Sequence[ToScore], symbols: Sequence[str]
    ) -> list[HeadlineSentiment]:
        """Scores for the headlines Gemini answered correctly. A headline missing from the
        result simply stays unscored and is sent again on a later run."""
        if not headlines:
            return []
        prompt, schema = build_prompt(headlines, symbols), response_schema(symbols)
        sent_ids = [h.id for h in headlines]
        problem = "no attempt made"
        for _ in range(ATTEMPTS):
            try:
                return parse_reply(await self._generate(prompt, schema), sent_ids, symbols)
            except Retryable as exc:
                problem = str(exc)
            except ValueError as exc:
                problem = f"unusable reply: {exc}"
        raise SentimentError(f"gave up after {ATTEMPTS} attempts: {problem}"[:200])

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aio.aclose()
