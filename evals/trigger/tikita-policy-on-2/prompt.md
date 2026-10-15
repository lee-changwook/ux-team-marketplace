---
description: "docs/evals/tikita-policy.md 켜져야 할 요청 2"
expected_outcome: "tikita-policy가 켜지고 다른 ux-team 스킬은 켜지지 않는다"
tags: ["trigger", "expect-tikita-policy"]
max_turns: 4
timeout_seconds: 180
allowed_tools: ["Skill", "Read", "Glob", "Grep"]
---

청구랑 수납이 왜 1:1이 아닌지, 부분 청구 · 부분 결제가 왜 있는지 정책 기준으로 알려 줘.
