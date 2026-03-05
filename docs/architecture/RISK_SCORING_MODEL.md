# AEGIS Risk Scoring Model

Author: Ken Tannenbaum Project: AEGIS Version: 0.1

## Overview

The risk scoring model provides a structured method for evaluating the
potential impact of capability requests.

Risk evaluation allows the governance engine to make context-aware
decisions.

## Risk Inputs

Risk evaluation considers:

-   actor trust level
-   requested capability type
-   resource sensitivity
-   environmental conditions
-   historical system behavior

## Example Risk Levels

Low Risk

Routine operations with minimal impact.

Moderate Risk

Actions affecting system state but within defined policy.

High Risk

Actions that may significantly alter system integrity.

Critical Risk

Actions that could compromise governance or system security.

## Governance Response

Risk level influences the final decision:

Low → allow

Moderate → allow or constrain

High → constrain or escalate

Critical → deny
