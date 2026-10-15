---
description: "docs/evals/screen-to-hifi.md 켜져야 할 요청 1"
expected_outcome: "screen-to-hifi가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-screen-to-hifi"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

이 화면 피그마로 떠 줘. staging의 등·하원 내역 화면이고, 기간을 이번 달로 조회한 상태로 떠 줘.
