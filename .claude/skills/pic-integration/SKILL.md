---
name: pic-integration
description: Run an integration study to test components together
args: "[components to test]"
---

# PIC Integration Study

You are running an integration study to test how components work together. Follow this protocol exactly.

## Input

Components to test: `$ARGS`

If no components were specified, ask the user what they want to test together.

## Core Principle

**Integration Over Ablation** - Test ideas together, not in isolation. This skill embodies the NVIDIA Nemotron philosophy of evaluating combined effects.

## When to Use This Skill

Use integration studies when:
1. Multiple components need to work together
2. Individual component tests pass but system behavior is uncertain
3. You want to evaluate combined effects of changes
4. Cross-cutting concerns need validation

## Protocol

### Step 1: Verify Workflow State

Read `.pic/state.json` to check workflow state.

Note: Integration studies can run during any phase, but are most common during Testing.

### Step 2: Generate Study ID

Read existing results in `.pic/integration-results/` to determine the next ID.

Format: `INT-[NNN]` where NNN is zero-padded

### Step 3: Define Integration Scope

Clarify with the user (if not already specified):

1. **Components**: What specific components/modules to include
2. **Interfaces**: What boundaries are being tested
3. **Scenarios**: What usage patterns to validate
4. **Success Criteria**: How to determine if integration works

### Step 4: Create Test Plan

Document the integration test plan:

```markdown
## Integration Test Plan

### Components Under Test
- [Component 1]: [brief description]
- [Component 2]: [brief description]
...

### Interfaces Being Tested
| From | To | Type | Description |
|------|-----|------|-------------|
| [comp1] | [comp2] | [API/event/etc] | [what's exchanged] |

### Test Scenarios

#### Scenario 1: [Name]
- **Description**: [What we're testing]
- **Steps**:
  1. [Step]
  2. [Step]
- **Expected Result**: [What should happen]

#### Scenario 2: [Name]
...

### Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

### Step 5: Spawn Testing Agent

Use the Task tool with `subagent_type: "test-writer"` (the testing PIC's agent type):

**Prompt:**
```
You are running an integration study (INT-[NNN]) for workflow [workflow-id].

## Components to Test
[component list]

## Test Plan
[test plan from Step 4]

## Instructions
1. Execute each test scenario
2. Record results with evidence
3. Note any unexpected behaviors
4. Document failures with reproduction steps
5. Report overall integration health

Return your findings in a structured format.
```

### Step 6: Record Results

Write to `.pic/integration-results/INT-[NNN].md`:

```markdown
# INT-[NNN]: [Title]

**Date**: [ISO date]
**Workflow**: [workflow id]
**Phase**: [current phase]
**Status**: [Pass/Fail/Partial]

## Overview

**Components Tested**: [list]
**Duration**: [how long it took]
**Result**: [summary]

## Test Plan

[From Step 4]

## Results

### Scenario 1: [Name]
- **Status**: [Pass/Fail]
- **Observations**: [What happened]
- **Evidence**: [Logs, outputs, etc.]

### Scenario 2: [Name]
...

## Issues Found

### Issue 1: [Title]
- **Severity**: [Critical/High/Medium/Low]
- **Components Affected**: [list]
- **Description**: [What's wrong]
- **Reproduction**: [How to reproduce]
- **Suggested Fix**: [If known]

## Integration Health

### Working Well
- [What integrates correctly]

### Needs Attention
- [What has problems]

### Recommendations
- [Suggested next steps]

## Conclusion

[Overall assessment of integration status]
```

### Step 7: Update State

Log the integration study:

Append to `.pic/status-log.jsonl`:

```json
{"timestamp": "[ISO]", "event": "integration_study", "id": "INT-[NNN]", "components": "[list]", "result": "[pass/fail/partial]"}
```

### Step 8: Present Results

Display summary to user:

```
## Integration Study Complete

**ID**: INT-[NNN]
**Components**: [list]
**Result**: [Pass/Fail/Partial]

### Summary
[Brief overview of findings]

### Issues Found
[Count and severity breakdown]

### Recommendations
[Key next steps]

Full results saved to: .pic/integration-results/INT-[NNN].md
```

## Integration Study Best Practices

1. **Start Simple** - Test pairs before testing larger groups
2. **Isolate Variables** - Change one thing at a time when diagnosing issues
3. **Document Everything** - Future integrations will benefit from this record
4. **Test Real Scenarios** - Use realistic data and usage patterns
5. **Include Error Cases** - Test what happens when things go wrong

## Error Handling

- If testing agent fails, record partial results
- If components don't exist, report missing dependencies
- Always create the results file, even for failed studies
