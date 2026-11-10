from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

import yaml

# Folder names are intentionally vague to match the tool names students see.
# The imported function names are the underlying implementations (unchanged).
from .clarify.tool import ask_user
from .papers.tool import arxiv_search
from .paper_text.tool import get_arxiv_paper_text
from .timeline.tool import get_user_tweets
from .fetch.tool import read_url
from .format.tool import render_digest
from .policy.tool import search_company_policy
from .social_search.tool import search_tweets
from .send.tool import send_telegram
from .lookup.tool import web_search
# TV2 (Linh): SQLite demo profile/order tools. See docs/TV1_INTEGRATION_NOTES.md.
from .get_my_profile.tool import getMyProfile
from .update_profile.tool import updateProfile
from .preview_order.tool import previewOrder
from .place_order.tool import placeOrder
from .get_order_status.tool import getOrderStatus
from .cancel_order.tool import cancelOrder


def place_order_auto_request_id(preview_id: str = "", **extra) -> dict:
    """Model-facing wrapper for place_order: the model only sends preview_id.

    A new request_id is generated for every call, so the model never has to invent one.
    The UI must NOT use this wrapper when the user approves: it calls placeOrder directly
    with the request_id from pending_action.payload (see docs/TV1_INTEGRATION_NOTES.md).
    """
    return placeOrder(preview_id=preview_id, request_id="REQ-" + secrets.token_hex(8), **extra)


# NOTE (starter_v0): tool names here are intentionally vague. These keys are the
# names the model sees AND the names data/eval_base.json + data/eval_research_extension.json
# match against. If a team renames a tool, it MUST stay in sync across ALL of:
#   artifacts/tools.yaml  ->  this dict  ->  data/eval_base.json + data/eval_research_extension.json
# Otherwise the eval raises "not declared in tools.yaml" or scores every call as a name mismatch.
TOOL_FUNCTIONS = {
    "clarify": ask_user,
    "timeline": get_user_tweets,
    "social_search": search_tweets,
    "lookup": web_search,
    "fetch": read_url,
    "format": render_digest,
    "send": send_telegram,
    "policy": search_company_policy,
    "papers": arxiv_search,
    "paper_text": get_arxiv_paper_text,
    # TV2 (Linh): SQLite demo profile/order tools
    "get_my_profile": getMyProfile,
    "update_profile": updateProfile,
    "preview_order": previewOrder,
    "place_order": place_order_auto_request_id,  # wrapper: auto request_id
    "get_order_status": getOrderStatus,
    "cancel_order": cancelOrder,
}


def load_tool_declarations(path: Path) -> list[dict[str, Any]]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{
        "type": "function",
        "function": {
            "name": item["name"],
            "description": item.get("description", ""),
            "parameters": item.get("parameters", {"type": "object", "properties": {}}),
        },
    } for item in declarations]

