---
description: "docs/evals/handoff-check.md 켜져야 할 요청 1"
expected_outcome: "handoff-check가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-handoff-check"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

개발에 넘기기 전에 확인해 줘. 요구사항 목록이랑 프로토타입 HTML 첨부할게.
