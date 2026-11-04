"""
Model Context Protocol (MCP) Tool definitions for Core Banking Integration.
Adheres to standard MCP tool format (name, description, inputSchema).
"""
from typing import Dict, Any, List
from apis.mock_core_banking import banking_service

MCP_CORE_BANKING_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "ValidateAccountAPI",
        "description": "Validates whether the customer account number is active and authorized.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "10-digit customer savings or current account number"
                }
            },
            "required": ["account_number"]
        }
    },
    {
        "name": "ValidateCardAPI",
        "description": "Validates whether the customer credit card number is active.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "card_number": {
                    "type": "string",
                    "description": "Full or masked credit card number"
                }
            },
            "required": ["card_number"]
        }
    },
    {
        "name": "GetAccountBalanceAPI",
        "description": "Retrieves the current available balance and currency for an active account.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "The account number to query"
                }
            },
            "required": ["account_number"]
        }
    },
    {
        "name": "GetCardTransactionsAPI",
        "description": "Fetches recent transaction history for a valid credit card.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "card_number": {
                    "type": "string",
                    "description": "The credit card number"
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Number of recent transactions to return"
                }
            },
            "required": ["card_number"]
        }
    },
    {
        "name": "GetStatementAPI",
        "description": "Retrieves or generates an account statement for a specified month/period.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "The customer account number"
                },
                "period": {
                    "type": "string",
                    "description": "Statement month/year period (e.g. 'April 2026')"
                }
            },
            "required": ["account_number", "period"]
        }
    }
]

def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes an MCP tool call by dispatching to the MockCoreBankingService.
    """
    if tool_name == "ValidateAccountAPI":
        res = banking_service.validate_account(arguments.get("account_number", ""))
        return res.model_dump()
    elif tool_name == "ValidateCardAPI":
        res = banking_service.validate_card(arguments.get("card_number", ""))
        return res.model_dump()
    elif tool_name == "GetAccountBalanceAPI":
        res = banking_service.get_account_balance(arguments.get("account_number", ""))
        return res.model_dump()
    elif tool_name == "GetCardTransactionsAPI":
        res = banking_service.get_card_transactions(
            arguments.get("card_number", ""),
            limit=int(arguments.get("limit", 5))
        )
        return res.model_dump()
    elif tool_name == "GetStatementAPI":
        res = banking_service.get_statement(
            arguments.get("account_number", ""),
            period=arguments.get("period", "")
        )
        return res.model_dump()
    else:
        return {"error": f"Unknown tool: {tool_name}"}

