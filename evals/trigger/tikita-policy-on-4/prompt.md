---
description: "docs/evals/tikita-policy.md 켜져야 할 요청 4"
expected_outcome: "tikita-policy가 켜지고 다른 ux-team 스킬은 켜지지 않는다"
tags: ["trigger", "expect-tikita-policy"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

'출결 관리' 화면 정책 글을 쓰는데 예정 · 확인 · 확정 · 신청 조합을 정리해 줘.
