# AEGIS Security Assumptions

Author: Ken Tannenbaum Project: AEGIS Version: 0.1

## Overview

This document defines the assumptions under which the AEGIS system
operates.

Explicitly documenting assumptions ensures the architecture remains
verifiable.

## Core Assumptions

### Kernel Integrity

The operating system kernel is assumed to be trustworthy and
uncompromised.

### Cryptographic Integrity

Cryptographic primitives used for authentication and logging are secure.

### Policy Authenticity

Policies governing capability are authentic and protected from
unauthorized modification.

### Identity Systems

Actors interacting with the system can be authenticated and attributed.

### Governance Engine Isolation

The AEGIS governance engine cannot be bypassed or modified by untrusted
actors.
