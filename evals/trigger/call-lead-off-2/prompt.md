---
description: "docs/evals/call-lead.md 켜지면 안 될 요청 2 · docs/evals/hello-ux-team.md 켜지면 안 될 요청 3"
expected_outcome: "kickoff가 켜지고 다른 ux-team 스킬은 켜지지 않는다 (tikita-policy는 함께 켜져도 된다)"
tags: ["trigger", "expect-kickoff"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

프로젝트 배정됐어, 상위 태스크 만들어 줘
