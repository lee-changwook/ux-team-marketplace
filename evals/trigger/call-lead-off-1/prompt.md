---
description: "docs/evals/call-lead.md 켜지면 안 될 요청 1 · docs/evals/tikita-policy.md 켜져야 할 요청 1"
expected_outcome: "tikita-policy가 켜지고 다른 ux-team 스킬은 켜지지 않는다"
tags: ["trigger", "expect-tikita-policy"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

출결 상태에서 지각과 결석은 어떻게 달라?
