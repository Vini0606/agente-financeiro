import asyncio
from pathlib import Path
from typing import Any
from agents import Agent, Runner, RunConfig, trace
from tools import create_tools

class FinancialExpenseAgent:
    """
    Agente de IA para coleta de despesas de funcionários com comprovantes.
    
    Responsabilidades:
    - Coletar dados de despesas via chat
    - Gerenciar comprovantes de despesas
    - Estruturar dados em tabela
    - Persistir dados em diretório específico
    """
    
    def __init__(
        self,
        name: str = "Agente Financeiro",
        instructions: str = None,
        output_directory: str = "./data/expenses",
        model: str = "gpt-4o-mini",
    ):
        """
        Inicializa o agente financeiro com todas as configurações.
        
        Args:
            name: Nome do agente
            instructions: Instruções personalizadas do agente
            output_directory: Diretório onde salvar comprovantes e dados
            model: Modelo OpenAI a ser utilizado
        """
        self.name = name
        self.output_directory = Path(output_directory)
        self.model = model
        self.expenses_data = []
        
        # Criar diretório de saída se não existir
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Instruções padrão do agente
        if instructions is None:
            instructions = """Você é um assistente financeiro especializado em coletar dados de despesas 
                              de funcionários. Seu objetivo é:

                              1. Solicitar informações sobre despesas: funcionário, categoria, valor, data e descrição
                              2. Armazenar os comprovantes enviados pelos usuários
                              3. Gerar um relatório estruturado com todos os dados coletados
                              4. Manter um histórico organizado das despesas

                              Sempre seja cortês, claro e preciso ao solicitar informações. Confirme os dados antes de persistir."""
        
        self.instructions = instructions
        self.agent = self.create_agent()
        
    def create_agent(self) -> Agent:
        """
        Cria e retorna uma instância do agente com as configurações definidas.
        
        Returns:
            Agent: Instância do agente configurada
        """
        # Criar ferramentas a partir do módulo tools
        tools = create_tools(self)
        
        agent = Agent(
            name=self.name,
            instructions=self.instructions,
            model=self.model,
            tools=tools,
        )
        
        return agent
    
    async def run_with_history(
        self,
        user_input: str,
        history: list[dict] = None,
    ) -> dict[str, Any]:
        """
        Executa o agente com entrada do usuário e histórico da conversa.
        
        Args:
            user_input: Entrada do usuário
            history: Histórico de conversas anterior (lista de dicts com 'role' e 'content')
            
        Returns:
            Dicionário com resultado da execução
        """
        # Construir input list com histórico
        if history is None:
            history = []
        
        input_list = history.copy() if history else []
        input_list.append({"role": "user", "content": user_input})
        
        # Executar com Runner
        run_config = RunConfig(
            workflow_name="Expense Collection",
            trace_include_sensitive_data=True,
        )
        
        result = await Runner.run(
            self.agent,
            input=input_list,
            run_config=run_config,
        )
        
        return {
            "output": result.final_output,
            "input_list": result.to_input_list(),
            "all_items": result.new_items,
        }
    
    async def run_with_trace(
        self,
        user_input: str,
        history: list[dict] = None,
        trace_name: str = "Financial Expense Workflow",
        group_id: str = None,
    ) -> dict[str, Any]:
        """
        Executa o agente com tracing configurado da OpenAI.
        
        Args:
            user_input: Entrada do usuário
            history: Histórico de conversas anterior
            trace_name: Nome do workflow para tracing
            group_id: ID do grupo para agrupar múltiplas execuções
            
        Returns:
            Dicionário com resultado da execução
        """
        # Usar trace context manager para rastrear a execução
        with trace(workflow_name=trace_name, group_id=group_id) as current_trace:
            # Construir input list com histórico
            if history is None:
                history = []
            
            input_list = history.copy() if history else []
            input_list.append({"role": "user", "content": user_input})
            
            # Configurar run com tracing
            run_config = RunConfig(
                workflow_name=trace_name,
                trace_id=None,  # Deixar gerar automaticamente
                group_id=group_id,
                trace_include_sensitive_data=True,
                trace_metadata={
                    "application": "financial_agent",
                    "version": "1.0.0",
                },
            )
            
            # Executar o runner dentro do contexto de trace
            result = await Runner.run(
                self.agent,
                input=input_list,
                run_config=run_config,
            )
            
            return {
                "output": result.final_output,
                "input_list": result.to_input_list(),
                "all_items": result.new_items,
                "trace_id": current_trace.trace_id if hasattr(current_trace, 'trace_id') else None,
            }

# === EXEMPLO DE USO ===

async def main():
    """Demonstração do uso do agente financeiro."""
    
    # Criar instância do agente
    agent = FinancialExpenseAgent(
        name="Assistente Financeiro",
        output_directory="./data/expenses",
        model="gpt-4o-mini",
    )
    
    print("=== Agente Financeiro Inicializado ===\n")
    
    # Exemplo 1: Execução simples com run_with_history
    print("--- Teste 1: run_with_history ---")
    result = await agent.run_with_history(
        user_input="Olá! Gostaria de registrar uma despesa de transporte no valor de R$50 que tive hoje para ir à reunião."
    )
    print(f"Resposta: {result['output']}\n")
    
    # Exemplo 2: Execução com tracing
    print("--- Teste 2: run_with_trace ---")
    history = result['input_list']  # Usar histórico da conversa anterior
    result_with_trace = await agent.run_with_trace(
        user_input="Gostaria de ver um resumo de todas as despesas que registrei.",
        history=history,
        trace_name="Financial Expense Workflow",
        group_id="session_001",
    )
    print(f"Resposta: {result_with_trace['output']}")
    if result_with_trace.get('trace_id'):
        print(f"Trace ID: {result_with_trace['trace_id']}\n")
    
    # Exemplo 3: Outra conversa com histórico
    print("--- Teste 3: Continuação da conversa ---")
    history = result_with_trace['input_list']
    result = await agent.run_with_history(
        user_input="Pode exportar essas despesas em CSV para eu salvar?",
        history=history,
    )
    print(f"Resposta: {result['output']}\n")
    
    print("=== Testes Concluídos ===")

if __name__ == "__main__":
    # Executar o exemplo
    asyncio.run(main())
