#### ReAct
- "Complex multi-hop questions masquerading as simple one-line queries can make LLMs hallucinate tool calls and cascade errors across steps. ReAct forces the model to reason before acting, and each observation from the real world strengthens the next reasoning step. Chain-of-thought lacks an external feedback loop, there's no observation grounding the reasoning and it produces no auditable trace, so even if you diagnose a failure you have no intervention point to fix it."

#### Multi-agentic raw python issues
- The worst part is whose messages list is whose. Agent 1 has its own messages list growing. Agent 2 has its own. When Agent 2 needs Agent 1's output, do you pass the full messages list? Just the final answer? What if Agent 2 needs to know why Agent 1 made a decision, not just what it returned?
And when Agent 3 needs both Agent 1 and Agent 2's context, do you merge the lists? In what order? What happens to the token count?