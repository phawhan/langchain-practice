"""Scans third-party text (job postings, tool results, facts to remember) for prompt injection and scams.

Plain regex rules: cheap, fast, and impossible to talk out of. They catch common attacks, not every
attack, so this is one layer of defense, never the whole defense.
"""
import re
from dataclasses import dataclass

RULES: dict[str, re.Pattern[str]] = {
    # "ignore all previous instructions", "disregard your rules"
    "instruction_override": re.compile(
        r"\b(ignore|disregard|forget|override)\b.{0,30}\b(previous|above|prior|earlier|all|your)\b.{0,20}"
        r"\b(instructions?|rules?|prompts?|guidelines?)\b", re.IGNORECASE),
    # text that talks to the AI instead of to a human reader
    "addresses_the_ai": re.compile(r"\b(ai assistant|system prompt)\b|^\s*(assistant|system)\s*:", re.IGNORECASE | re.MULTILINE),
    # third-party text has no reason to mention our internal tool names
    "tool_manipulation": re.compile(r"\b(remember_fact|forget_memory|apply_to_job|get_my_profile)\b"),
    # common fake-job scam: "pay a registration fee"
    "payment_request": re.compile(
        r"\b(registration|processing|security|training|joining)\s+(fee|deposit|charge)s?\b"
        r"|\bpay\b.{0,40}(\bfees?\b|\brs\.?|\binr\b|\brupees?\b|₹)", re.IGNORECASE),
    # Indian UPI payment ids, e.g. someone@ybl
    "upi_id": re.compile(r"\b[\w.\-]{2,}@(upi|ybl|ibl|axl|okaxis|oksbi|okicici|okhdfcbank|paytm|apl)\b", re.IGNORECASE),
    # zero-width characters are a classic way to hide text from human reviewers
    "hidden_characters": re.compile("[​‌‍⁠﻿]"),
}


@dataclass(frozen=True)
class Finding:
    rule: str
    excerpt: str


def scan_text(text: str) -> list[Finding]:
    findings = []
    for rule, pattern in RULES.items():
        if match := pattern.search(text):
            findings.append(Finding(rule, text[max(match.start() - 20, 0): match.end() + 20]))
    return findings


def is_suspicious(text: str) -> bool:
    return bool(scan_text(text))
