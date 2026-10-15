"""Approval policies are application rules, not model decisions."""

from __future__ import annotations

from typing import Any, Protocol


class ApprovalPolicy(Protocol):
    def allow(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        ...


class DenyAll:
    """Safe default for tools marked as requiring approval."""

    def allow(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        return False


class ConsoleApproval:
    """Ask the person at the terminal before one side-effecting action."""

    def allow(self, tool_name: str, arguments: dict[str, Any]) -> bool:
        answer = input(f"允许执行 {tool_name}，参数 {arguments!r}？[y/N] ")
        return answer.strip().lower() in {"y", "yes"}
