---
description: "docs/evals/intent-check.md 켜져야 할 요청 3"
expected_outcome: "intent-check가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-intent-check"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

배포 전에 최종 확인 한번 해 줘. 요구사항 목록이랑 staging 화면 비교해서.
