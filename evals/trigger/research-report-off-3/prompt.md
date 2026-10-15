---
description: "docs/evals/research-report.md 켜지면 안 될 요청 3"
expected_outcome: "decision-log가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-decision-log"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

미납 안내는 문자 먼저 보내기로 했어. 결정 기록 남겨 줘
