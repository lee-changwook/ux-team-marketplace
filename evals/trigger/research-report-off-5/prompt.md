---
description: "docs/evals/research-report.md 켜지면 안 될 요청 5"
expected_outcome: "intent-check가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-intent-check"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

staging에 올라간 출결 화면이 의도대로 구현됐는지 봐 줘
