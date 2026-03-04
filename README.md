# Agente Financeiro - Coleta de Despesas

Um agente de IA alimentado pelo OpenAI Agents SDK que coleta dados de despesas de funcionários via chat, gerencia comprovantes e estrutura os dados em tabelas.

## 🎯 Funcionalidades

- **Coleta de Despesas**: Solicita informações detalhadas sobre despesas (funcionário, categoria, valor, data, descrição)
- **Gerenciamento de Comprovantes**: Armazena e organiza comprovantes de despesas
- **Estruturação de Dados**: Cria tabelas bem formatadas com todas as informações
- **Exportação**: Exporta dados em CSV e JSON
- **Histórico de Conversa**: Mantém contexto entre múltiplas interações
- **Tracing**: Integração completa com o sistema de traces da OpenAI para debugging

## 📋 Estrutura da Classe

### `FinancialExpenseAgent`

#### Inicialização

```python
agent = FinancialExpenseAgent(
    name: str = "Agente Financeiro",
    instructions: str = None,  # Instruções personalizadas
    output_directory: str = "./data/expenses",
    model: str = "gpt-4o-mini"
)
```

#### Métodos

##### `create_agent() -> Agent`
Cria e retorna uma instância do agente configurada com todas as ferramentas.

##### `run_with_history(user_input: str, history: list) -> dict`
Executa o agente com entrada do usuário e histórico de conversa.

**Parâmetros:**
- `user_input`: A mensagem do usuário
- `history`: Lista de mensagens anteriores (opcional)

**Retorna:**
```python
{
    "output": str,  # Resposta final do agente
    "input_list": list,  # Histórico completo atualizado
    "all_items": list  # Todos os itens gerados
}
```

##### `run_with_trace(user_input: str, history: list, trace_name: str, group_id: str) -> dict`
Executa o agente com tracing completo da OpenAI.

**Parâmetros:**
- `user_input`: A mensagem do usuário
- `history`: Lista de mensagens anteriores (opcional)
- `trace_name`: Nome do workflow para tracing
- `group_id`: ID para agrupar múltiplas execuções

**Retorna:** Mesmo do `run_with_history()` + `trace_id`

## 🔧 Ferramentas Disponíveis

### 1. `save_expense`
Salva uma despesa com dados e comprovante.

**Parâmetros:**
- `employee_name`: Nome do funcionário
- `category`: Categoria (transporte, alimentação, etc)
- `amount`: Valor em reais
- `date`: Data (YYYY-MM-DD)
- `description`: Descrição
- `receipt_base64`: Comprovante em base64 (opcional)

### 2. `get_expense_summary`
Retorna resumo total de despesas por categoria.

### 3. `export_expenses_table`
Exporta despesas em CSV ou JSON.

## 📁 Estrutura de Diretórios

```
data/
└── expenses/
    ├── expenses.json           # Dados em JSON
    ├── expenses_*.csv          # Exportações CSV
    ├── receipt_1_*.pdf         # Comprovantes
    └── ...
```

## 🚀 Exemplos de Uso

### Exemplo Básico

```python
import asyncio
from main import FinancialExpenseAgent

async def main():
    # Criar agente
    agent = FinancialExpenseAgent()
    
    # Registrar despesa simples
    result = await agent.run_with_history(
        user_input="Gostaria de registrar uma despesa de R$50 com transporte"
    )
    print(result["output"])

asyncio.run(main())
```

### Exemplo com Histórico

```python
async def main():
    agent = FinancialExpenseAgent()
    
    # Primeira interação
    result1 = await agent.run_with_history(
        user_input="Olá, quero registrar uma despesa"
    )
    
    # Segunda interação usando histórico
    result2 = await agent.run_with_history(
        user_input="Pode exportar em CSV?",
        history=result1["input_list"]
    )
    
    print(result2["output"])

asyncio.run(main())
```

### Exemplo com Tracing

```python
async def main():
    agent = FinancialExpenseAgent()
    
    # Executar com tracing
    result = await agent.run_with_trace(
        user_input="Registre uma despesa de R$100",
        trace_name="Financial Workflow",
        group_id="session_001"
    )
    
    print(f"Output: {result['output']}")
    print(f"Trace ID: {result['trace_id']}")
    # Visualizar em: https://platform.openai.com/traces

asyncio.run(main())
```

## 🔐 Configuração

### Variáveis de Ambiente

```bash
# Obrigatória
export OPENAI_API_KEY=sk-...

# Opcional - desabilitar tracing
export OPENAI_AGENTS_DISABLE_TRACING=1
```

## 📊 Estrutura de Dados de Despesa

Cada despesa armazenada tem a estrutura:

```json
{
  "id": 1,
  "employee": "João Silva",
  "category": "transporte",
  "amount": 50.00,
  "date": "2024-03-04",
  "description": "Uber para reunião",
  "receipt_path": "./data/expenses/receipt_1_*.pdf",
  "saved_at": "2024-03-04T10:30:00.000000"
}
```

## 🧪 Testes

Execute o arquivo principal para testar o agente:

```bash
python main.py
```

Isso executará 3 testes demonstrando:
1. `run_with_history()` básico
2. `run_with_trace()` com tracing
3. Continuação de conversa com histórico

## 📝 Notas Importantes

- **API Key**: Configure `OPENAI_API_KEY` antes de executar
- **Tracing**: Visualize os traces em https://platform.openai.com/traces
- **Histórico**: Cada `run_with_history()` retorna `input_list` que deve ser passado à próxima chamada
- **Comprovantes**: Envie em base64 para salvar automaticamente
- **Diretórios**: Criados automaticamente se não existirem

## 🔗 Documentação Oficial

- [Agents SDK Documentation](https://openai.github.io/openai-agents-python)
- [OpenAI API Reference](https://developers.openai.com/api/docs)
- [Traces Dashboard](https://platform.openai.com/traces)

## 📜 Licença

MIT
