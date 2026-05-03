"""
SecureOps Consulting Agent Client
AI-powered security consultant that interacts with MCP servers
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json


@dataclass
class AgentContext:
    """Context for the security consulting agent"""
    client_name: str
    engagement_type: str  # "audit", "pentest", "compliance", etc.
    permissions: List[str]
    session_id: str
    sensitive_data: Dict[str, Any] = None


class SecureOpsAgent:
    """
    AI Security Consultant Agent for SecureOps Consulting
    Demonstrates realistic MCP client interactions
    """
    
    def __init__(self, name: str = "SecureOps AI Consultant"):
        self.name = name
        self.context: Optional[AgentContext] = None
        self.memory: List[Dict[str, Any]] = []
        self.tool_results: List[Dict[str, Any]] = []
        
    def set_context(self, context: AgentContext):
        """Set the operational context for the agent"""
        self.context = context
        self.log(f"Context set: {context.client_name} - {context.engagement_type}")
        
    def log(self, message: str, level: str = "INFO"):
        """Log agent actions"""
        entry = {
            "timestamp": asyncio.get_event_loop().time(),
            "level": level,
            "message": message,
            "context": self.context.client_name if self.context else "None"
        }
        self.memory.append(entry)
        print(f"[{level}] {self.name}: {message}")
        
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP server tool
        This is where vulnerabilities can be exploited
        """
        self.log(f"Calling tool: {tool_name} with params: {params}")
        
        # Simulate tool call - in real implementation, this would use MCP protocol
        result = {
            "tool": tool_name,
            "params": params,
            "status": "pending"
        }
        
        self.tool_results.append(result)
        return result
        
    def analyze_context(self, context_data: str) -> Dict[str, Any]:
        """
        Analyze retrieved context - vulnerable to injection
        """
        self.log(f"Analyzing context data ({len(context_data)} chars)")
        
        # Parse context - this is where MCP06 Intent Subversion can occur
        try:
            parsed = json.loads(context_data) if context_data.startswith("{") else {"raw": context_data}
            return parsed
        except:
            return {"raw": context_data}
            
    def make_decision(self, analysis: Dict[str, Any]) -> str:
        """
        Make security decision based on analysis
        """
        # This is where poisoned tools (MCP03) can influence decisions
        decision = analysis.get("recommendation", "APPROVE")
        self.log(f"Decision made: {decision}", "DECISION")
        return decision
        
    def get_memory_dump(self) -> List[Dict[str, Any]]:
        """
        Return agent memory - can expose secrets (MCP01)
        """
        return self.memory
        
    def clear_context(self):
        """Clear context - important for MCP10 prevention"""
        if self.context:
            self.log(f"Clearing context for {self.context.client_name}")
        self.context = None
        # Note: Memory is NOT cleared - this is a vulnerability