"""
Módulo com todas as ferramentas (tools) do Agente Financeiro.

Este módulo define as funções de ferramentas que o agente utiliza
para coletar, armazenar e exportar dados de despesas.
"""

import base64
import csv
import json
from datetime import datetime
from typing import Any
from agents import function_tool

def create_tools(agent_instance: Any):
    """
    Cria as ferramentas configuradas para o agente.
    
    Args:
        agent_instance: Instância de FinancialExpenseAgent
        
    Returns:
        list: Lista de ferramentas configuradas
    """
    
    @function_tool
    async def save_expense(
        employee_name: str,
        category: str,
        amount: float,
        date: str,
        description: str,
        receipt_base64: str = None,
    ) -> str:
        """
        Salva uma despesa com seus dados e comprovante.
        
        Args:
            employee_name: Nome do funcionário
            category: Categoria da despesa (transporte, alimentação, etc)
            amount: Valor da despesa em reais
            date: Data da despesa (formato YYYY-MM-DD)
            description: Descrição da despesa
            receipt_base64: Comprovante em base64 (opcional)
            
        Returns:
            Confirmação do salvamento
        """
        expense = {
            "id": len(agent_instance.expenses_data) + 1,
            "employee": employee_name,
            "category": category,
            "amount": amount,
            "date": date,
            "description": description,
            "saved_at": datetime.now().isoformat(),
            "receipt_path": None,
        }
        
        # Salvar comprovante se fornecido
        if receipt_base64:
            receipt_filename = f"receipt_{expense['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            receipt_path = agent_instance.output_directory / receipt_filename
            
            try:
                receipt_data = base64.b64decode(receipt_base64)
                receipt_path.write_bytes(receipt_data)
                expense["receipt_path"] = str(receipt_path)
            except Exception as e:
                return f"Erro ao salvar comprovante: {str(e)}"
        
        agent_instance.expenses_data.append(expense)
        
        # Salvar dados em JSON
        _save_expenses_json(agent_instance)
        
        return f"Despesa registrada com sucesso! ID: {expense['id']}"
    
    @function_tool
    async def get_expense_summary() -> str:
        """
        Retorna um resumo de todas as despesas registradas.
        
        Returns:
            Resumo formatado das despesas
        """
        if not agent_instance.expenses_data:
            return "Nenhuma despesa registrada ainda."
        
        total = sum(e["amount"] for e in agent_instance.expenses_data)
        by_category = {}
        
        for expense in agent_instance.expenses_data:
            cat = expense["category"]
            by_category[cat] = by_category.get(cat, 0) + expense["amount"]
        
        summary = f"Total de despesas: R${total:.2f}\n"
        summary += "Por categoria:\n"
        
        for cat, amount in by_category.items():
            summary += f"  - {cat}: R${amount:.2f}\n"
        
        summary += f"Total de registros: {len(agent_instance.expenses_data)}"
        
        return summary
    
    @function_tool
    async def export_expenses_table(format_type: str = "csv") -> str:
        """
        Exporta as despesas em um formato estruturado.
        
        Args:
            format_type: Formato de exportação ('csv' ou 'json')
            
        Returns:
            Caminho do arquivo exportado
        """
        if not agent_instance.expenses_data:
            return "Nenhuma despesa para exportar."
        
        if format_type == "csv":
            return await _export_to_csv(agent_instance)
        elif format_type == "json":
            return await _export_to_json(agent_instance)
        else:
            return f"Formato '{format_type}' não suportado. Use 'csv' ou 'json'."
    
    return [
        save_expense,
        get_expense_summary,
        export_expenses_table,
    ]

# ===== FUNÇÕES AUXILIARES =====

def _save_expenses_json(agent_instance: Any) -> None:
    """
    Salva os dados de despesas em arquivo JSON.
    
    Args:
        agent_instance: Instância de FinancialExpenseAgent
    """
    json_path = agent_instance.output_directory / "expenses.json"
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(agent_instance.expenses_data, f, indent=2, ensure_ascii=False)

async def _export_to_csv(agent_instance: Any) -> str:
    """
    Exporta despesas para CSV.
    
    Args:
        agent_instance: Instância de FinancialExpenseAgent
        
    Returns:
        Mensagem com caminho do arquivo exportado
    """
    csv_path = agent_instance.output_directory / f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    if not agent_instance.expenses_data:
        return "Nenhuma despesa para exportar."
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "employee", "category", "amount", "date", "description", "receipt_path", "saved_at"]
        )
        writer.writeheader()
        writer.writerows(agent_instance.expenses_data)
    
    return f"Arquivo CSV exportado: {csv_path}"

async def _export_to_json(agent_instance: Any) -> str:
    """
    Exporta despesas para JSON.
    
    Args:
        agent_instance: Instância de FinancialExpenseAgent
        
    Returns:
        Mensagem com caminho do arquivo exportado
    """
    json_path = agent_instance.output_directory / f"expenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    if not agent_instance.expenses_data:
        return "Nenhuma despesa para exportar."
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(agent_instance.expenses_data, f, indent=2, ensure_ascii=False)
    
    return f"Arquivo JSON exportado: {json_path}"
