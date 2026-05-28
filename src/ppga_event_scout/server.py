"""PPGA Event Scout — MCP server principal."""

import asyncio
import os
from datetime import datetime

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions, ServerCapabilities
from mcp.types import ToolsCapability
from tavily import TavilyClient

server = Server("ppga-event-scout")
_tavily_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError(
                "TAVILY_API_KEY não definida. "
                "Configure a variável de ambiente antes de iniciar o servidor."
            )
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


def _current_year() -> int:
    return datetime.now().year


def _format_results(title: str, results: dict, excerpt_len: int = 450) -> str:
    items = results.get("results", [])
    if not items:
        return f"# {title}\n\nNenhum resultado encontrado para essa busca."

    lines = [
        f"# {title}",
        f"_Busca realizada em {datetime.now().strftime('%d/%m/%Y')}_\n",
    ]
    for i, r in enumerate(items, 1):
        content = r.get("content", "").strip()
        excerpt = content[:excerpt_len] + ("..." if len(content) > excerpt_len else "")
        lines += [
            f"## {i}. {r.get('title', 'Sem título')}",
            f"**URL:** {r.get('url', '')}",
            f"{excerpt}\n",
        ]
    return "\n".join(lines)


# ── Ferramentas ───────────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="buscar_eventos",
            description=(
                "Busca congressos, encontros e seminários acadêmicos internacionais "
                "relevantes para mestrandos e doutorandos em Administração (PPGA/UCS). "
                "Prioriza eventos remotos e híbridos com chamada de trabalhos aberta."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area_tematica": {
                        "type": "string",
                        "description": (
                            "Área ou tema de pesquisa (ex: inovação, sustentabilidade, "
                            "estratégia, finanças, marketing, comportamento organizacional)"
                        ),
                    },
                    "formato": {
                        "type": "string",
                        "enum": ["remoto", "hibrido", "presencial", "todos"],
                        "description": "Formato preferido do evento.",
                        "default": "todos",
                    },
                    "idioma": {
                        "type": "string",
                        "enum": ["ingles", "portugues", "espanhol", "todos"],
                        "description": "Idioma principal do evento.",
                        "default": "ingles",
                    },
                    "apenas_com_submissao_aberta": {
                        "type": "boolean",
                        "description": "Se true, filtra somente eventos com call for papers aberto.",
                        "default": False,
                    },
                },
                "required": ["area_tematica"],
            },
        ),
        types.Tool(
            name="buscar_chamadas_trabalhos",
            description=(
                "Busca chamadas de trabalhos (call for papers) abertas em congressos "
                "e periódicos internacionais de Administração e áreas correlatas."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tema": {
                        "type": "string",
                        "description": "Tema específico da pesquisa ou do artigo.",
                    },
                    "tipo_trabalho": {
                        "type": "string",
                        "enum": ["artigo", "resumo", "poster", "todos"],
                        "description": "Tipo de submissão desejada.",
                        "default": "todos",
                    },
                },
                "required": ["tema"],
            },
        ),
        types.Tool(
            name="listar_congressos_referencia",
            description=(
                "Lista os principais congressos de referência em Administração "
                "(ex: Academy of Management, ENANPAD, EURAM, BAM) com informações "
                "sobre próximas edições e prazos de submissão."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "escopo": {
                        "type": "string",
                        "enum": ["nacional", "internacional", "todos"],
                        "description": "Escopo geográfico dos congressos.",
                        "default": "internacional",
                    },
                    "area": {
                        "type": "string",
                        "description": (
                            "Subárea de Administração (opcional). "
                            "Ex: gestão pública, empreendedorismo, RH, TI."
                        ),
                    },
                },
            },
        ),
        types.Tool(
            name="buscar_bolsas_eventos",
            description=(
                "Busca bolsas, auxílios de viagem e grants para participação de "
                "pós-graduandos em eventos e congressos acadêmicos internacionais."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Área de pesquisa para filtrar bolsas relevantes.",
                    },
                    "pais_origem": {
                        "type": "string",
                        "description": "País de origem do solicitante (padrão: Brasil).",
                        "default": "Brasil",
                    },
                },
                "required": ["area"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    client = _get_client()
    year = _current_year()
    next_year = year + 1

    if name == "buscar_eventos":
        area = arguments["area_tematica"]
        formato = arguments.get("formato", "todos")
        idioma = arguments.get("idioma", "ingles")
        apenas_aberta = arguments.get("apenas_com_submissao_aberta", False)

        formato_q = {
            "remoto": "virtual online remote",
            "hibrido": "hybrid",
            "presencial": "in-person",
        }.get(formato, "")

        idioma_q = {
            "portugues": "português Brazil",
            "espanhol": "español latinoamerica",
        }.get(idioma, "")

        cfp = "call for papers submission deadline" if apenas_aberta else "conference symposium workshop"

        query = (
            f"international {cfp} {area} management business administration "
            f"{year} {next_year} {formato_q} {idioma_q}"
        ).strip()

        results = client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
        )

        title = f"Eventos em '{area}'" + (f" — {formato.title()}" if formato != "todos" else "")
        return [types.TextContent(type="text", text=_format_results(title, results))]

    elif name == "buscar_chamadas_trabalhos":
        tema = arguments["tema"]
        tipo = arguments.get("tipo_trabalho", "todos")

        tipo_q = {
            "artigo": "full paper",
            "resumo": "abstract",
            "poster": "poster",
        }.get(tipo, "paper abstract")

        query = (
            f"call for papers {tipo_q} {tema} management administration "
            f"research {year} {next_year} submission deadline international"
        )

        results = client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
        )

        return [types.TextContent(
            type="text",
            text=_format_results(f"Chamadas de Trabalhos: {tema}", results),
        )]

    elif name == "listar_congressos_referencia":
        escopo = arguments.get("escopo", "internacional")
        area = arguments.get("area", "")

        if escopo == "nacional":
            query = f"ENANPAD ANPAD congresso nacional administração gestão {year} {next_year} {area}"
        elif escopo == "internacional":
            query = (
                f"Academy of Management EURAM BAM SMS international conference "
                f"management {year} {next_year} {area}"
            )
        else:
            query = f"congress conference administração management {year} {next_year} {area}"

        results = client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
        )

        return [types.TextContent(
            type="text",
            text=_format_results(f"Congressos de Referência — {escopo.title()}", results),
        )]

    elif name == "buscar_bolsas_eventos":
        area = arguments["area"]
        pais = arguments.get("pais_origem", "Brasil")

        query = (
            f"travel grant scholarship funding PhD master student conference "
            f"{area} management {year} {next_year} {pais} international"
        )

        results = client.search(
            query=query,
            search_depth="advanced",
            max_results=8,
        )

        return [types.TextContent(
            type="text",
            text=_format_results(f"Bolsas e Auxílios para Eventos — {area}", results),
        )]

    else:
        raise ValueError(f"Ferramenta desconhecida: {name!r}")


# ── Entrypoint ────────────────────────────────────────────────────────────────

async def _run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ppga-event-scout",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(listChanged=False),
                ),
            ),
        )


def main():
    asyncio.run(_run())


if __name__ == "__main__":
    main()
