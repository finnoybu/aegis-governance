"""
ACF-1 Full Bundle Generator
Generates detection, validation, and response objects for all 25 ATX-1 v2.0 techniques.
"""
import json
import uuid

def make_id(prefix, name):
    return f"{prefix}--{uuid.uuid5(uuid.NAMESPACE_URL, 'https://aegis-governance.com/acf-1/' + name)}"

TS = "2026-03-26T00:00:00.000Z"

# Detection/validation/response definitions for all 25 techniques
TECHNIQUE_DEFS = {
    "T1001": {
        "detection": ("Identity Validation Failure", "metric", "identity_layer",
                       "invalid_signature OR unknown_principal"),
        "validation": ("Authority Verification", "policy_enforcement",
                        ["principal", "policy"], "principal in authorized_identities"),
        "response": ("Reject Unauthorized Instruction", "prevention", "identity_failure"),
    },
    "T1002": {
        "detection": ("Implicit Authority Inference", "event", "context_layer",
                       "authority_claim_present AND explicit_grant == false"),
        "validation": ("Explicit Authority Check", "policy_enforcement",
                        ["authority_claim", "grant_registry"], "authority_claim in explicit_grants"),
        "response": ("Deny Implicit Authority", "prevention", "authority_not_verified"),
    },
    "T1003": {
        "detection": ("Mass Distribution Under Spoofed Identity", "correlation", "communication_layer",
                       "broadcast_count > threshold AND sender_identity_unverified"),
        "validation": ("Broadcast Authority Validation", "policy_enforcement",
                        ["sender_identity", "broadcast_scope", "policy"], "sender in authorized_broadcasters"),
        "response": ("Block Spoofed Broadcast", "containment", "identity_spoof_detected"),
    },
    "T2001": {
        "detection": ("Scope Deviation", "event", "planner",
                       "planned_action NOT IN declared_scope"),
        "validation": ("Scope Boundary Enforcement", "policy_enforcement",
                        ["task_scope", "planned_action"], "planned_action in task_scope"),
        "response": ("Halt Scope Expansion", "containment", "scope_violation"),
    },
    "T2002": {
        "detection": ("Bulk Operation Volume Anomaly", "metric", "execution_engine",
                       "operation_count > bulk_threshold AND validation_step == false"),
        "validation": ("Bulk Operation Scope Check", "policy_enforcement",
                        ["operation_batch", "scope_limits"], "batch_size <= max_batch AND targets_validated"),
        "response": ("Throttle Bulk Operations", "prevention", "bulk_threshold_exceeded"),
    },
    "T2003": {
        "detection": ("Delegation Fragmentation Pattern", "correlation", "delegation_tracker",
                       "sub_task_count > threshold AND no_single_task_triggers_policy"),
        "validation": ("Aggregate Delegation Intent Check", "consistency_check",
                        ["sub_tasks", "aggregate_intent"], "aggregate_intent in allowed_actions"),
        "response": ("Block Fragmented Delegation", "prevention", "delegation_obfuscation_detected"),
    },
    "T2004": {
        "detection": ("Tool Chain Anomaly", "correlation", "tool_proxy",
                       "sequence_length > threshold AND cross_tool_dependency_detected"),
        "validation": ("Tool Chain Policy Validation", "policy_enforcement",
                        ["tool_sequence", "policy_rules"], "aggregate_effect in allowed_actions"),
        "response": ("Block Unsafe Tool Chain", "prevention", "policy_violation"),
    },
    "T3001": {
        "detection": ("Destructive Operation Attempt", "event", "tool_proxy",
                       "action_type in [delete, overwrite, drop] AND rollback_available == false"),
        "validation": ("Destructive Action Authorization", "policy_enforcement",
                        ["action", "authorization_level"], "authorization_level >= owner"),
        "response": ("Block Destructive Action", "prevention", "unauthorized_destructive_action"),
    },
    "T3002": {
        "detection": ("Cascading Action Pattern", "correlation", "execution_graph",
                       "multiple_linked_actions AND dependency_chain_length > threshold"),
        "validation": ("Cascade Impact Assessment", "anomaly_detection",
                        ["action_graph", "impact_model"], "estimated_impact <= acceptable_threshold"),
        "response": ("Halt Cascading Operations", "containment", "cascade_detected"),
    },
    "T4001": {
        "detection": ("Context Data Exfiltration", "metric", "data_layer",
                       "data_transfer_size > threshold OR sensitive_field_in_output"),
        "validation": ("Data Classification Check", "policy_enforcement",
                        ["output_data", "classification_tags"], "no_sensitive_data_in_output"),
        "response": ("Block Data Exfiltration", "prevention", "sensitive_data_leak"),
    },
    "T4002": {
        "detection": ("Cross-Session Data Access", "event", "memory_layer",
                       "data_source_session != current_session"),
        "validation": ("Session Isolation Check", "consistency_check",
                        ["data_source", "session_boundary"], "data_source.session == current_session"),
        "response": ("Enforce Session Isolation", "prevention", "session_boundary_violation"),
    },
    "T4003": {
        "detection": ("Cross-Domain Data Transfer", "correlation", "data_layer",
                       "source_domain != target_domain AND data_contains_secrets"),
        "validation": ("Domain Boundary Authorization", "policy_enforcement",
                        ["source_domain", "target_domain", "data_classification"], "cross_domain_transfer_authorized"),
        "response": ("Block Cross-Domain Leakage", "prevention", "domain_boundary_violation"),
    },
    "T5001": {
        "detection": ("Execution / Report Mismatch", "correlation", "agent_execution_layer",
                       "reported_success == true AND execution_log.exists == false"),
        "validation": ("Execution Verification Check", "consistency_check",
                        ["execution_log", "task_report"], "execution_log.exists == true"),
        "response": ("Halt Agent on False Completion", "containment", "validation_failure"),
    },
    "T5002": {
        "detection": ("Attribution Fabrication", "correlation", "audit_layer",
                       "claimed_action_source != actual_source"),
        "validation": ("Action Attribution Verification", "integrity_check",
                        ["action_record", "actor_identity"], "action_record.actor == verified_actor"),
        "response": ("Flag Fabricated Attribution", "escalation", "attribution_mismatch"),
    },
    "T5003": {
        "detection": ("Missing Execution Signal", "state", "agent_execution_layer",
                       "expected_execution_report == missing AND timeout_exceeded"),
        "validation": ("Failure Transparency Check", "consistency_check",
                        ["execution_log", "error_log"], "failure_reported OR execution_confirmed"),
        "response": ("Force Failure Reporting", "intervention", "silent_failure_detected"),
    },
    "T6001": {
        "detection": ("Recursive Invocation Loop", "metric", "execution_engine",
                       "call_depth > threshold OR self_invocation_count > limit"),
        "validation": ("Recursion Depth Check", "policy_enforcement",
                        ["call_stack", "depth_limit"], "call_depth <= max_depth"),
        "response": ("Terminate Recursive Loop", "containment", "recursion_limit_exceeded"),
    },
    "T6002": {
        "detection": ("Unbounded Resource Consumption", "metric", "resource_monitor",
                       "api_call_rate > threshold OR compute_usage > budget"),
        "validation": ("Resource Quota Check", "policy_enforcement",
                        ["resource_usage", "quota"], "resource_usage <= allocated_quota"),
        "response": ("Throttle Resource Usage", "prevention", "quota_exceeded"),
    },
    "T7001": {
        "detection": ("Agent Identity Spoofing", "event", "identity_layer",
                       "agent_identity_verification_failed OR duplicate_identity_detected"),
        "validation": ("Agent Identity Verification", "integrity_check",
                        ["agent_id", "credential", "identity_registry"], "agent_id.signature_valid == true"),
        "response": ("Quarantine Spoofed Agent", "containment", "identity_spoof_confirmed"),
    },
    "T7002": {
        "detection": ("Malicious Delegation Injection", "correlation", "delegation_tracker",
                       "new_agent_in_chain AND agent_trust_score < threshold"),
        "validation": ("Delegation Chain Integrity", "integrity_check",
                        ["delegation_chain", "authorized_agents"], "all_agents_in_chain in authorized_set"),
        "response": ("Reject Unauthorized Delegation", "prevention", "delegation_chain_compromised"),
    },
    "T7003": {
        "detection": ("Behavioral Drift Signal", "correlation", "multi_agent_coordinator",
                       "agent_behavior_deviation > baseline_threshold over time_window"),
        "validation": ("Behavioral Baseline Check", "anomaly_detection",
                        ["agent_behavior_log", "baseline_model"], "behavior_within_normal_range"),
        "response": ("Reset Drifted Agent", "intervention", "behavioral_drift_confirmed"),
    },
    "T7004": {
        "detection": ("Consensus Convergence Anomaly", "correlation", "multi_agent_coordinator",
                       "multiple_agents_same_decision AND decision_risk_score > threshold"),
        "validation": ("Consensus Safety Validation", "policy_enforcement",
                        ["agent_decisions", "policy_rules"], "decision_outcome in allowed_actions"),
        "response": ("Break Unsafe Consensus", "intervention", "consensus_violation"),
    },
    "T8001": {
        "detection": ("Memory Integrity Anomaly", "state", "memory_layer",
                       "memory_content_hash != expected_hash OR injection_pattern_detected"),
        "validation": ("Memory Content Validation", "integrity_check",
                        ["memory_snapshot", "integrity_baseline"], "memory_hash == trusted_baseline"),
        "response": ("Restore Clean Memory State", "intervention", "memory_corruption_detected"),
    },
    "T8002": {
        "detection": ("Policy Integrity Failure", "event", "policy_engine",
                       "signature_verification_failed OR unauthorized_policy_modification"),
        "validation": ("Policy Signature Verification", "integrity_check",
                        ["policy_file", "expected_signature"], "policy_signature_valid == true"),
        "response": ("Revert Policy to Last Known Good", "containment", "policy_tamper_detected"),
    },
    "T9001": {
        "detection": ("Unmonitored Execution Context", "state", "monitoring_layer",
                       "action_executed AND monitoring_coverage == false"),
        "validation": ("Monitoring Coverage Check", "consistency_check",
                        ["action_context", "monitoring_scope"], "action_context in monitored_scope"),
        "response": ("Redirect to Monitored Context", "intervention", "monitoring_gap_detected"),
    },
    "T9002": {
        "detection": ("Audit Trail Obfuscation", "correlation", "audit_layer",
                       "audit_completeness_score < threshold OR reconstruction_failure"),
        "validation": ("Audit Reconstructability Check", "integrity_check",
                        ["audit_trail", "execution_log"], "audit_trail.reconstructable == true"),
        "response": ("Flag Non-Reconstructable Actions", "escalation", "audit_obfuscation_detected"),
    },
}

# Multi-agent metadata for TA007 techniques
MULTI_AGENT = {
    "T7001": {"coordination_type": "explicit", "propagation_mode": "delegation", "detection_scope": "multi-agent"},
    "T7002": {"coordination_type": "explicit", "propagation_mode": "delegation", "detection_scope": "multi-agent"},
    "T7003": {"coordination_type": "implicit", "propagation_mode": "context", "detection_scope": "multi-agent"},
    "T7004": {"coordination_type": "emergent", "propagation_mode": "context", "detection_scope": "multi-agent"},
}

# Load ATX-1 v2.0 STIX IDs
with open('d:/dev/AEGIS Initiative/aegis-governance/docs/atx/v2/stix/atx-1-bundle.json') as f:
    atx = json.load(f)

atx_stix_ids = {}
for obj in atx['objects']:
    if obj['type'] == 'attack-pattern':
        for ref in obj.get('external_references', []):
            if 'external_id' in ref:
                atx_stix_ids[ref['external_id']] = obj['id']

# Generate bundle
objects = []

for tech_id, defs in TECHNIQUE_DEFS.items():
    slug = tech_id.lower()

    # Detection
    d_name, d_signal, d_source, d_logic = defs["detection"]
    d_slug = f"{slug}-{d_name.lower().replace(' ', '-').replace('/', '-')[:30]}"
    det = {
        "type": "x-acf-detection", "spec_version": "2.1",
        "id": make_id("x-acf-detection", d_slug),
        "created": TS, "modified": TS,
        "name": d_name, "description": f"Detection for {tech_id}: {d_name}",
        "x_acf_signal_type": d_signal,
        "x_acf_log_source": d_source,
        "x_acf_detection_logic": d_logic,
        "x_acf_related_atx": [tech_id]
    }
    if tech_id in MULTI_AGENT:
        det["x_acf_multi_agent"] = MULTI_AGENT[tech_id]
    objects.append(det)

    # Validation
    v_name, v_type, v_signals, v_condition = defs["validation"]
    v_slug = f"{slug}-{v_name.lower().replace(' ', '-').replace('/', '-')[:30]}"
    val = {
        "type": "x-acf-validation", "spec_version": "2.1",
        "id": make_id("x-acf-validation", v_slug),
        "created": TS, "modified": TS,
        "name": v_name, "description": f"Validation for {tech_id}: {v_name}",
        "x_acf_validation_type": v_type,
        "x_acf_required_signals": v_signals,
        "x_acf_expected_condition": v_condition,
        "x_acf_related_atx": [tech_id]
    }
    objects.append(val)

    # Response
    r_name, r_type, r_trigger = defs["response"]
    r_slug = f"{slug}-{r_name.lower().replace(' ', '-').replace('/', '-')[:30]}"
    resp = {
        "type": "x-acf-response", "spec_version": "2.1",
        "id": make_id("x-acf-response", r_slug),
        "created": TS, "modified": TS,
        "name": r_name, "description": f"Response for {tech_id}: {r_name}",
        "x_acf_response_type": r_type,
        "x_acf_trigger": r_trigger,
        "x_acf_related_atx": [tech_id]
    }
    objects.append(resp)

    # Relationships
    target = atx_stix_ids.get(tech_id, f"attack-pattern--unknown-{tech_id}")
    for rel_type, source_id in [("detects", det["id"]), ("validates", val["id"]), ("responds-to", resp["id"])]:
        objects.append({
            "type": "relationship", "spec_version": "2.1",
            "id": f"relationship--{uuid.uuid4()}",
            "created": TS, "modified": TS,
            "relationship_type": rel_type,
            "source_ref": source_id,
            "target_ref": target
        })

bundle = {"type": "bundle", "id": f"bundle--{uuid.uuid4()}", "objects": objects}

outpath = 'd:/dev/AEGIS Initiative/aegis-governance/docs/atx/v2/acf/acf-1-bundle.json'
with open(outpath, 'w') as f:
    json.dump(bundle, f, indent=2)

# Summary
types = {}
for obj in objects:
    types[obj['type']] = types.get(obj['type'], 0) + 1

print(f"ACF-1 v1.0: {sum(types.values())} objects")
for t, c in sorted(types.items()):
    print(f"  {t}: {c}")

unresolved = [o for o in objects if o['type'] == 'relationship' and 'unknown' in o.get('target_ref', '')]
if unresolved:
    print(f"WARNING: {len(unresolved)} unresolved ATX references")
else:
    print("All 25 ATX references resolved")

# Coverage check
covered = set()
for obj in objects:
    if obj['type'] == 'x-acf-detection':
        covered.update(obj['x_acf_related_atx'])
print(f"Detection coverage: {len(covered)}/25 techniques")
