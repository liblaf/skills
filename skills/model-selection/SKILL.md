---
name: model-selection
description: Find the right model for your use case. Use when you need to choose model and reasoning effort.
---

<!-- ref: <https://artificialanalysis.ai/leaderboards/models> -->
<!-- ref: <https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence> -->

Balance cost and intelligence. The most capable model can be too expensive at scale, and the least expensive model can fall short on quality.

| Model                               | Intelligence Index | Cost per Task | Remark       |
| ----------------------------------- | ------------------ | ------------- | ------------ |
| Claude Opus 5.5 (max with fallback) | 58                 | $10.04        | advisor only |
| GPT-6 Astra (max)                   | 57                 | $6.24         | advisor only |
| GPT-6.1 Sol (max)                   | 55                 | $1.27         |              |
| GPT-6.1 Sol (xhigh)                 | 52                 | $0.76         |              |
| GPT-6.1 Sol (high)                  | 50                 | $0.59         |              |
| GPT-6.1 Sol (medium)                | 46                 | $0.36         |              |
| GPT-6.1 Sol (medium)                | 46                 | $0.36         |              |
| GPT-6.1 Terra (high)                | 42                 | $0.26         |              |
| GPT-6.1 Terra (medium)              | 38                 | $0.17         |              |
| GPT-6.1 Sol (low)                   | 35                 | $0.16         |              |
| GPT-6.1 Terra (low)                 | 29                 | $0.07         |              |
| GPT-6 Luna (medium)                 | 18                 | $0.04         |              |
| GPT-6 Luna (low)                    | 10                 | $0.01         |              |

Treat Routing Weight as a cost multiplier.

| Provider    | Routing Weight |
| ----------- | -------------- |
| Codex       | 1.0            |
| Antigravity | 20.0           |
| OpenRouter  | 50.0           |
