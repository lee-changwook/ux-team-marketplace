---
description: "docs/evals/intent-check.md 켜져야 할 요청 1"
expected_outcome: "intent-check가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-intent-check"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

staging 확인해 줘. 출석 내역 화면이 요구사항 목록대로 나왔는지 봐 줘.
