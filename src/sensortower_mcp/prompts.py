#!/usr/bin/env python3
"""
Prompt templates exposed via FastMCP @mcp.prompt
"""

from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage


def register_prompts(mcp: FastMCP) -> None:
    """Register reusable, parameterized prompts for MCP clients."""

    # Intentionally no generic code review prompt; not relevant for this MCP

    @mcp.prompt(
        name="creatives_investigation",
        description="Fetch and summarize ad creatives (SOV, formats, themes)",
        tags={"ads", "creatives"},
        meta={"version": "1.0"},
    )
    def creatives_investigation(
        os: str,
        app_ids: str,
        start_date: str,
        countries: str,
        networks: str,
        ad_types: str,
        end_date: str | None = None,
    ) -> str:
        """Guides the LLM to call get_creatives and summarize insights."""
        hint = (
            "Use the MCP tool get_creatives with the provided arguments. "
            "Summarize: top networks, SOV distribution, dominant creative formats, "
            "common themes/messages, and notable outliers."
        )
        parts = {
            "os": os,
            "app_ids": app_ids,
            "start_date": start_date,
            "countries": countries,
            "networks": networks,
            "ad_types": ad_types,
        }
        if end_date:
            parts["end_date"] = end_date
        return f"{hint}\n\nArgs: {parts}"

    @mcp.prompt(
        name="competitor_snapshot",
        description="Search target, pull metadata/rankings/creatives, summarize position",
        tags={"competition", "summary"},
        meta={"version": "1.0"},
    )
    def competitor_snapshot(
        os: str,
        term: str,
        country: str = "US",
        chart_type: str = "topfreeapplications",
        date: str | None = None,
    ) -> list[PromptMessage | str]:
        """End-to-end guidance to assemble a quick competitor snapshot."""
        msg1 = Message(
            f"Search apps matching '{term}' on {os}. Prefer top results with significant presence.")
        msg2 = Message(
            "For 1-3 top matches: fetch app metadata, category rankings, and top creatives."
        )
        msg3 = Message(
            "Summarize competitor position: downloads/revenue trend (if available), ranking momentum, "
            "creative mix/themes, and risks/opportunities. Include a short recommended next action.")
        return [msg1, msg2, msg3]

    @mcp.prompt(
        name="usage_insights",
        description="Pull active users and highlight MoM deltas and anomalies",
        tags={"usage", "timeseries"},
        meta={"version": "1.0"},
    )
    def usage_insights(
        os: str,
        app_ids: str,
        start_date: str,
        end_date: str,
        countries: str = "US",
        date_granularity: str = "monthly",
        data_model: str = "DM_2025_Q2",
    ) -> str:
        """Guide to call get_usage_active_users and interpret trends succinctly."""
        return (
            "Call get_usage_active_users with the provided args. Then compute MoM deltas, "
            "flag anomalies (sudden spikes/drops), and provide a 3-bullet executive summary."
        )

    @mcp.prompt(
        name="keyword_research",
        description="Run research_keyword and suggest target terms with rationale",
        tags={"aso", "keywords"},
        meta={"version": "1.0"},
    )
    def keyword_research(
        os: str,
        term: str,
        country: str,
        app_id: int | None = None,
        page: int | None = None,
    ) -> str:
        """Guide to pull keyword intel and produce prioritized suggestions."""
        return (
            "Use research_keyword with the args to fetch related terms and difficulty. "
            "Recommend 5-10 target keywords with a short rationale each (traffic vs. difficulty vs. relevance)."
        )

    @mcp.prompt(
        name="prospect_research",
        description="Pre-sales: compile a one-pager from key Sensor Tower signals",
        tags={"presales", "summary"},
        meta={"version": "1.0"},
    )
    def prospect_research(
        os: str,
        term: str,
        countries: str = "US",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[PromptMessage | str]:
        """End-to-end prospect one-pager guidance."""
        return [
            Message(
                "1) Identify targets: search_entities(term, os). Pick 1-3 with meaningful scale."),
            Message(
                "2) Market position: get_top_and_trending/get_top_publishers; get_category_rankings (trend/momentum)."),
            Message(
                "3) Paid UA: get_impressions/impressions_rank (network mix, seasonality), get_creatives (formats/themes)."),
            Message(
                "4) Scale/ROI: get_download_estimates/get_revenue_estimates (geo mix, seasonality)."),
            Message(
                "5) Engagement: get_usage_active_users (+ retention if needed) for MoM deltas/anomalies."),
            Message(
                "6) Organic/ASO: get_keywords, get_reviews, featured stories/apps (strengths/risks)."),
            Message(
                "Output: a one-pager with bullets: Channels, Creative notes, Momentum, Risks, measurement angles."),
        ]

    @mcp.prompt(
        name="channel_gap_analysis",
        description="Find network and creative gaps to target",
        tags={"ads", "gap"},
        meta={"version": "1.0"},
    )
    def channel_gap_analysis(
        os: str,
        app_ids: str,
        start_date: str,
        end_date: str,
        countries: str = "US",
    ) -> str:
        """Guide to quantify paid mix gaps and propose measurable experiments."""
        return (
            "1) Pull get_impressions for the period to quantify network shares and volatility. "
            "2) Pull get_creatives to assess diversity and velocity by network and format. "
            "3) Compare against category peers via get_top_and_trending / top_creatives. "
            "Output: list of network/format gaps and 3 experiment ideas with expected lift and clear measurement tie-in."
        )


