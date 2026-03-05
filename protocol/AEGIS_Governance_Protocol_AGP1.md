# AGP‑1: AEGIS Governance Protocol

## Purpose

Define how AI agents propose actions and how governance decisions are evaluated.

## Message Types

ACTION_PROPOSE  
DECISION_RESPONSE  
EXECUTION_RESULT  
ESCALATION_REQUEST

## Decision Types

ALLOW  
DENY  
ESCALATE  
REQUIRE_CONFIRMATION

## Protocol Flow

AI Agent → ACTION_PROPOSE → Governance Engine → DECISION_RESPONSE → Tool Proxy Execution

AGP provides a standard mechanism for governed AI action control.
