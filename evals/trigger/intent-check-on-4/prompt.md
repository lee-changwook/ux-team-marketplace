---
description: "docs/evals/intent-check.md 켜져야 할 요청 4"
expected_outcome: "intent-check가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-intent-check"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

staging에 올라간 미납 관리 화면, 기획 의도랑 다른 데 있는지 차이 목록 뽑아 줘.
