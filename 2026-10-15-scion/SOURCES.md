# Why Anthropic replaced Git: Scion explained (KD Tech Explained, Oct 2026)

Primary source: Anthropic Engineering, "Redesigning source control at Anthropic", 13 Oct 2026
https://www.anthropic.com/engineering/redesigning-source-control

| Claim in the video | Source |
|---|---|
| About 2,500 merges a day in May 2026, over 30,000 a day in September 2026 | Anthropic post |
| Main branch history almost 100 GB; compressed working copy over 25 GB | Anthropic post |
| About 25 million CI checkouts a day; over 600 PB a day if fetched naively | Anthropic post |
| Several hundred internal git mirrors; they outgrew disk and memory and fell behind main | Anthropic post |
| Quote: "The properties that make git excellent for distributed, offline work were actively undermining our ability to scale." | Anthropic post |
| Seven people built Scion and Antique; migration took five months | Anthropic post |
| Commits, rebases and merges on the server; "nothing to push" | Anthropic post |
| Checkouts about two orders of magnitude faster (seconds rather than minutes) | Anthropic post |
| Infrastructure about 200x smaller in CPU and memory than the old git mirroring | Anthropic post |
| Concurrent changes can conflict; caught by post-merge and pre-deploy tests; Claude typically fixes them | Anthropic post |
| Scion is not a general git replacement and is not being released | Anthropic post |

Our own explanations (not claims from Anthropic):
- ShopApp, Priya and Arun are made-up examples.
- "Pull first" and merge conflicts: standard Git behaviour (a push is rejected when the remote branch has moved on; same-line edits conflict).
- The three-case table shows how server-side merging works in principle; the post does not list per-case rules.
- 600 PB a day = about 6.9 TB a second ≈ 1,200 full-HD movies of about 5.5 GB each, every second.
- Why one giant repository: the usual industry reasons (atomic changes across projects, one version of shared code). Anthropic's post does not explain its own choice. Google and Meta also run very large monorepos with their own tooling.
