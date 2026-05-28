# PPGA Event Scout 🎓

**MCP server** para busca inteligente de congressos, encontros e seminários acadêmicos internacionais, voltado para mestrandos e doutorandos do [PPGA/UCS](https://www.ucs.br/site/pos-graduacao/programas-de-pos-graduacao/administracao/).

Integra o [Claude Desktop](https://claude.ai/download) com a API de busca [Tavily](https://tavily.com) para encontrar eventos acadêmicos relevantes diretamente na conversa com o Claude.

---

## O que o PPGA Event Scout faz?

Com ele, você pode perguntar ao Claude coisas como:

> _"Quais congressos internacionais sobre inovação e sustentabilidade têm call for papers aberto para 2025?"_

> _"Liste os principais congressos de referência em Administração para 2025/2026."_

> _"Existem bolsas ou auxílios de viagem para doutorandos participarem de eventos internacionais na área de gestão?"_

O servidor oferece **4 ferramentas**:

| Ferramenta | O que faz |
|---|---|
| `buscar_eventos` | Busca congressos/seminários por área temática, formato e idioma |
| `buscar_chamadas_trabalhos` | Encontra call for papers abertos por tema |
| `listar_congressos_referencia` | Lista os grandes congressos de referência (AoM, ENANPAD, EURAM…) |
| `buscar_bolsas_eventos` | Busca grants e auxílios de viagem para pós-graduandos |

---

## Pré-requisitos

- **Python 3.10+**
- **Claude Desktop** instalado ([baixar aqui](https://claude.ai/download))
- **Chave de API do Tavily** — crie uma conta gratuita em [tavily.com](https://tavily.com) (plano gratuito já é suficiente para começar)

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/derossimolina/ppga-event-scout.git
cd ppga-event-scout
```

### 2. Crie e ative o ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instale o pacote

```bash
pip install -e .
```

### 4. Configure sua chave do Tavily

Crie um arquivo `.env` na raiz do projeto (nunca commitar):

```bash
cp .env.example .env
```

Edite o `.env` e insira sua chave:

```
TAVILY_API_KEY=tvly-SuaChaveAqui
```

---

## Configuração no Claude Desktop

Abra o arquivo de configuração do Claude Desktop:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Adicione o bloco abaixo dentro de `"mcpServers"` (ajuste o caminho conforme onde você clonou o projeto):

**Windows:**
```json
{
  "mcpServers": {
    "ppga-event-scout": {
      "command": "C:\\caminho\\para\\ppga-event-scout\\.venv\\Scripts\\python.exe",
      "args": ["-m", "ppga_event_scout.server"],
      "env": {
        "TAVILY_API_KEY": "tvly-SuaChaveAqui"
      }
    }
  }
}
```

**macOS / Linux:**
```json
{
  "mcpServers": {
    "ppga-event-scout": {
      "command": "/caminho/para/ppga-event-scout/.venv/bin/python",
      "args": ["-m", "ppga_event_scout.server"],
      "env": {
        "TAVILY_API_KEY": "tvly-SuaChaveAqui"
      }
    }
  }
}
```

> **Dica Windows:** Para descobrir o caminho exato do Python no ambiente virtual, com o `.venv` ativado execute:
> ```powershell
> (Get-Command python).Source
> ```

Após salvar, **reinicie o Claude Desktop**. Um ícone de ferramenta (🔧) aparecerá na interface indicando que o MCP está ativo.

---

## Exemplos de uso

Após a configuração, converse com o Claude normalmente:

```
Busque congressos internacionais remotos ou híbridos sobre inovação e 
empreendedorismo com call for papers aberto para 2025.
```

```
Quero submeter um artigo sobre sustentabilidade em cadeias de suprimentos. 
Que chamadas de trabalhos estão abertas em eventos internacionais?
```

```
Liste os principais congressos internacionais de referência em Administração 
para 2025 e 2026.
```

```
Existe algum auxílio financeiro para doutorandos brasileiros participarem de 
congressos internacionais de gestão?
```

---

## Estrutura do projeto

```
ppga-event-scout/
├── src/
│   └── ppga_event_scout/
│       ├── __init__.py
│       └── server.py        # MCP server principal
├── pyproject.toml           # Metadados e dependências
├── .env.example             # Modelo do arquivo de credenciais
├── .gitignore
└── README.md
```

---

## Desenvolvimento

Para contribuir ou adaptar o servidor:

```bash
# Instalar em modo editável (já feito na instalação)
pip install -e .

# Testar o servidor localmente
python -m ppga_event_scout.server
```

Adicione novas ferramentas no arquivo [`src/ppga_event_scout/server.py`](src/ppga_event_scout/server.py) seguindo o padrão das existentes.

---

## Licença

MIT — livre para uso, adaptação e distribuição.

---

## Contato

Desenvolvido para o **PPGA/UCS — Programa de Pós-Graduação em Administração da Universidade de Caxias do Sul**.

Para dúvidas ou sugestões, abra uma [issue](https://github.com/derossimolina/ppga-event-scout/issues) no repositório.
