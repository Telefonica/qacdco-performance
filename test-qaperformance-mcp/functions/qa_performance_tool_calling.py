"""
title: QA Performance Tool Calling
author: QA Performance Team
description: Native tool calling for QA Performance analysis via LiteLLM proxy
required_open_webui_version: 0.5.0
based on https://openwebui.com/f/sgodo/native_tool_calling_pipe_2
version: 1.1.0
"""

from abc import ABC, abstractmethod
import inspect
import json
from typing import (
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Any,
    Iterable,
    Literal,
    Mapping,
    NotRequired,
    Optional,
    TypedDict,
    Union,
)
import html
import asyncio
import httpx
from pydantic import BaseModel, Field
from openai import NotGiven, OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)
from openai.types.shared_params.function_definition import FunctionDefinition


# Patched HTTPClient for compatibility
class CustomHTTPClient(httpx.Client):
    def __init__(self, *args, **kwargs):
        kwargs.pop("proxies", None)
        super().__init__(*args, **kwargs)


class ToolSpecParametersProperty(TypedDict):
    description: str
    type: str
    items: NotRequired[dict[str, str]]
    default: NotRequired[Any]
    enum: NotRequired[list[str]]


class ToolSpecParameters(TypedDict):
    properties: dict[str, ToolSpecParametersProperty]
    required: NotRequired[list[str]]
    type: str


class ToolSpec(TypedDict):
    name: str
    description: str
    parameters: ToolSpecParameters


class ToolCallable(TypedDict):
    toolkit_id: str
    callable: Callable
    spec: ToolSpec
    file_handler: bool
    citation: bool


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str


class EventEmitterMessageData(TypedDict):
    content: str


class EventEmitterStatusData(TypedDict):
    description: str
    done: Optional[bool]


class EventEmitterStatus(TypedDict):
    type: Literal["status"]
    data: EventEmitterStatusData


class EventEmitterMessage(TypedDict):
    type: Literal["message"]
    data: EventEmitterMessageData


class Metadata(TypedDict):
    chat_id: str
    user_id: str
    message_id: str


class EventEmitter:
    def __init__(
        self,
        __event_emitter__: Optional[
            Callable[[Mapping[str, Any]], Awaitable[None]]
        ] = None,
    ):
        self.event_emitter = __event_emitter__

    async def emit(
        self, message: Union[EventEmitterMessage, EventEmitterStatus]
    ) -> None:
        if self.event_emitter:
            maybe_future = self.event_emitter(message)
            if asyncio.isfuture(maybe_future) or inspect.isawaitable(maybe_future):
                await maybe_future

    async def status(self, description: str, done: Optional[bool] = None) -> None:
        await self.emit(
            EventEmitterStatus(
                type="status",
                data=EventEmitterStatusData(description=description, done=done),
            )
        )

    async def result(self, summary: str, content: str) -> None:
        await self.emit(
            EventEmitterMessage(
                type="message",
                data=EventEmitterMessageData(
                    content=f'\n<details type="tool_calls" done="true" results="{html.escape(content)}">\n<summary>{summary}</summary>\n{content}\n</details>',
                ),
            )
        )


class ToolCallResult(BaseModel):
    tool_call: ToolCall
    result: Optional[str] = None
    error: Optional[str] = None

    def to_display(self) -> str:
        if self.error:
            return f'\n\n<details>\n<summary>❌ Error: {self.tool_call.name}</summary>\n\n**Error:** {self.error}\n\n</details>\n\n'

        try:
            result_data = json.loads(self.result) if self.result else {}

            return f"""

<details>
<summary>🛠️ Tool: {self.tool_call.name}</summary>

**Parámetros:**
```json
{json.loads(self.tool_call.arguments) if self.tool_call.arguments else {}}
```

**Resultado:**
```json
{result_data}
```

</details>

"""
        except:
            return f"""

<details>
<summary>🛠️ Tool: {self.tool_call.name}</summary>

**Parámetros:** {self.tool_call.arguments}

**Resultado:** {self.result or "Sin resultado"}

</details>

"""


class ToolCallingChunk(BaseModel):
    message: Optional[str] = None
    tool_calls: Optional[Iterable[ToolCall]] = None


class ToolCallingModel(ABC):
    @abstractmethod
    def stream(
        self,
        body: dict,
        __tools__: dict[str, ToolCallable] | None,
    ) -> AsyncIterator[ToolCallingChunk]:
        raise NotImplementedError

    @abstractmethod
    def append_tool_calls(self, body: dict, tool_calls: Iterable[ToolCall]) -> None:
        raise NotImplementedError

    @abstractmethod
    def append_results(self, body: dict, results: Iterable[ToolCallResult]) -> None:
        raise NotImplementedError


class LiteLLMToolCallingModel(ToolCallingModel):
    """Tool calling model that works with LiteLLM proxy"""

    def __init__(self, client: OpenAI, model_id: str):
        self.client = client
        self.model_id = model_id

    async def stream(
        self,
        body: dict,
        __tools__: dict[str, ToolCallable] | None,
    ) -> AsyncIterator[ToolCallingChunk]:
        tools = self._map_tools(__tools__)
        messages: list[ChatCompletionMessageParam] = body["messages"]

        tool_calls_map: dict[str, ToolCall] = {}
        last_tool_call_id: Optional[str] = None

        # Create completion with tools
        for chunk in self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            stream=True,
            tools=tools or NotGiven(),
            temperature=0.3,  # Más creatividad para respuestas completas
        ):
            delta = chunk.choices[0].delta
            finish_reason = chunk.choices[0].finish_reason

            # Stream content
            if delta.content:
                yield ToolCallingChunk(message=delta.content)

            # Handle tool calls
            for tool_call in delta.tool_calls or []:
                tool_call_id = tool_call.id or last_tool_call_id
                last_tool_call_id = tool_call_id

                if not tool_call_id:
                    continue

                if tool_call_id not in tool_calls_map:
                    tool_calls_map[tool_call_id] = ToolCall(
                        id=tool_call_id, name="", arguments=""
                    )

                if tool_call.function:
                    if tool_call.function.name:
                        tool_calls_map[tool_call_id].name = tool_call.function.name
                    if tool_call.function.arguments:
                        tool_calls_map[
                            tool_call_id
                        ].arguments += tool_call.function.arguments

            if finish_reason:
                if tool_calls_map:
                    yield ToolCallingChunk(tool_calls=tool_calls_map.values())
                return

    def append_results(self, body: dict, results: Iterable[ToolCallResult]):
        if "messages" in body:
            for result in results:
                body["messages"].append(self._map_result(result))

    def append_tool_calls(self, body: dict, tool_calls: Iterable[ToolCall]):
        if "messages" in body and tool_calls:  # Solo agregar si hay tool_calls
            tool_calls_list = list(tool_calls)
            if not tool_calls_list:  # Verificación adicional
                return

            tool_call_message = {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": tool_call.arguments,
                        },
                    }
                    for tool_call in tool_calls_list
                ],
            }

            if body["messages"][-1]["role"] == "assistant":
                body["messages"][-1]["tool_calls"] = tool_call_message["tool_calls"]
            else:
                body["messages"].append(tool_call_message)

    def append_assistant_message(self, body: dict, message: str) -> None:
        if "messages" in body:
            body["messages"].append(
                {
                    "role": "assistant",
                    "content": message,
                }
            )

    def _map_result(self, result: ToolCallResult) -> dict[str, str]:
        if result.error:
            return {
                "role": "tool",
                "tool_call_id": result.tool_call.id,
                "content": f"Error: {result.error}",
            }
        return {
            "role": "tool",
            "tool_call_id": result.tool_call.id,
            "content": result.result or "",
        }

    def _map_tools(
        self, tool_specs: dict[str, ToolCallable] | None
    ) -> list[ChatCompletionToolParam]:
        openai_tools: list[ChatCompletionToolParam] = []
        for tool in tool_specs.values() if tool_specs else []:
            function_definition: FunctionDefinition = {
                "name": tool["spec"]["name"],
                "description": tool["spec"].get("description"),
                "parameters": tool["spec"].get("parameters"),  # type: ignore
            }
            openai_tools.append(
                {
                    "type": "function",
                    "function": function_definition,
                }
            )
        return openai_tools


class Pipe:
    class Valves(BaseModel):
        # LiteLLM Configuration
        LITELLM_BASE_URL: str = Field(
            default="http://litellm:4000",
            description="LiteLLM proxy URL"
        )
        LITELLM_API_KEY: str = Field(
            default="sk-1234",
            description="LiteLLM API key"
        )

        # Model Configuration
        MODEL_IDS: list[str] = Field(
            default=["gpt-4"],
            description="List of model IDs to enable"
        )

        # QA Performance specific
        MAX_ITERATIONS: int = Field(
            default=10,
            description="Maximum iterations for analysis"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.type = "manifold"
        self.name = "qa-perf/"

    def pipes(self) -> list[dict]:
        return [
            {"id": model_id, "name": f"QA-Perf {model_id}"}
            for model_id in self.valves.MODEL_IDS
        ]

    def _get_openai_client(self) -> OpenAI:
        """Get OpenAI client configured for LiteLLM proxy"""
        return OpenAI(
            api_key=self.valves.LITELLM_API_KEY,
            base_url=f"{self.valves.LITELLM_BASE_URL}/v1",
            http_client=CustomHTTPClient(),
        )

    async def execute_tool(
        self,
        tool_call: ToolCall,
        tools: dict[str, ToolCallable],
        ev: EventEmitter,
    ) -> ToolCallResult:
        try:
            tool = tools.get(tool_call.name)
            if not tool:
                raise ValueError(f"Tool '{tool_call.name}' not found")

            if tool_call.arguments:
                parsed_args = json.loads(tool_call.arguments)
                await ev.status(f"🔍 Ejecutando {tool_call.name}...")
            else:
                parsed_args = {}

            result = await tool["callable"](**parsed_args)

            await ev.status(f"✅ {tool_call.name} completado")

            return ToolCallResult(
                tool_call=tool_call,
                result=json.dumps(result, ensure_ascii=False),
            )
        except json.JSONDecodeError:
            return ToolCallResult(
                tool_call=tool_call,
                error=f"Failed to parse arguments for tool '{tool_call.name}'",
            )
        except Exception as e:
            return ToolCallResult(
                tool_call=tool_call,
                error=f"Error executing tool '{tool_call.name}': {str(e)}",
            )

    async def pipe(
        self,
        body: dict,
        __metadata__: Metadata,
        __user__: dict | None = None,
        __task__: str | None = None,
        __tools__: dict[str, ToolCallable] | None = None,
        __event_emitter__: Callable[[Mapping[str, Any]], Awaitable[None]] | None = None,
    ) -> AsyncGenerator[str, None]:
        if __task__ == "function_calling":
            return

        # System prompt is configured in OpenWebUI dashboard - no need to modify here

        client = self._get_openai_client()
        model_id = body["model"] or "gpt-4"

        # Clean model ID for LiteLLM
        if "." in model_id:
            model_id = model_id[model_id.find(".") + 1:]

        model = LiteLLMToolCallingModel(client, model_id)
        ev = EventEmitter(__event_emitter__)

        iteration = 0
        while iteration < self.valves.MAX_ITERATIONS:
            iteration += 1
            await ev.status(f"🔄 Análisis iterativo - Iteración {iteration}/{self.valves.MAX_ITERATIONS}")

            tool_calls: list[ToolCall] = []
            message = ""

            # Stream model response
            async for chunk in model.stream(body, __tools__):
                tool_calls = list(chunk.tool_calls) if chunk.tool_calls else tool_calls

                if chunk.message:
                    message += chunk.message
                    yield chunk.message

            if message:
                model.append_assistant_message(body, message)

            if not tool_calls:
                # Obtener la tarea original del primer mensaje del usuario
                original_task = ""
                for msg in body["messages"]:
                    if msg.get("role") == "user":
                        original_task = msg.get("content", "")
                        break

                # Verificación más crítica con contexto de la tarea
                completion_check_messages = body["messages"] + [{
                    "role": "user",
                    "content": f"""¿Completaste totalmente la tarea: "{original_task[:200]}..."?

SI ESTÁ COMPLETA: responde solo "TAREA_COMPLETADA"

SI ESTÁ INCOMPLETA:
⚠️ NUNCA regeneres ni reescribas lo ya hecho
✅ SOLO continúa desde el punto exacto donde se cortó
✅ Agrega únicamente lo que falta para completar"""
                }]

                completion_response = ""
                async for chunk in model.stream({"messages": completion_check_messages}, None):
                    if chunk.message:
                        completion_response += chunk.message

                if "TAREA_COMPLETADA" in completion_response.upper():
                    await ev.status("✅ Análisis completado", done=True)
                    break
                else:
                    # Continuar con la respuesta
                    yield completion_response
                    model.append_assistant_message(body, completion_response)

            if not __tools__:
                yield "\n\n⚠️ No hay herramientas disponibles para consultar datos."
                break

            model.append_tool_calls(body, tool_calls)

            # Execute tools
            await ev.status("🛠️ Ejecutando herramientas...")
            tool_call_results = [
                await self.execute_tool(tool_call, __tools__, ev)
                for tool_call in tool_calls
            ]

            model.append_results(body, tool_call_results)

            # Show tool results in a single block
            if tool_call_results:
                yield "\n\n---\n**🔧 Herramientas ejecutadas:**\n"
                for result in tool_call_results:
                    yield result.to_display()

            await ev.status(f"Iteración {iteration} completada", done=True)

        if iteration >= self.valves.MAX_ITERATIONS:
            yield f"\n\n⚠️ Se alcanzó el límite de {self.valves.MAX_ITERATIONS} iteraciones."

        return
