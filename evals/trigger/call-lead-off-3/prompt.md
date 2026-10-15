---
description: "docs/evals/call-lead.md 켜지면 안 될 요청 3 · docs/evals/hello-ux-team.md 켜지면 안 될 요청 4 · docs/evals/kickoff.md 켜지면 안 될 요청 4"
expected_outcome: "handoff-check가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-handoff-check"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

넘기기 전에 확인해 줘
