#### ReAct
- "Complex multi-hop questions masquerading as simple one-line queries can make LLMs hallucinate tool calls and cascade errors across steps. ReAct forces the model to reason before acting, and each observation from the real world strengthens the next reasoning step. Chain-of-thought lacks an external feedback loop, there's no observation grounding the reasoning and it produces no auditable trace, so even if you diagnose a failure you have no intervention point to fix it."
- The loop is Thought → Action → Observation → Thought. The Thought is functional not decorative, it's the model's working memory across iterations. The Action gets executed by your code, not the model. The Observation feeds back and grounds the next Thought.
- Thought has roles depending on where in the loop it appears: decomposition at the start, tracking mid-loop, deciding when enough info exists, error correction when an observation was wrong.
- First Thought is the highest hallucination risk — no observations yet, model is working purely from memory. Complex multi-hop questions make this worse.
- HITL works because Thought is auditable. You can't intervene on a black box. The Thought step is what makes the loop inspectable and editable by a human.

#### Multi-agentic raw python issues
- The worst part is whose messages list is whose. Agent 1 has its own messages list growing. Agent 2 has its own. When Agent 2 needs Agent 1's output, do you pass the full messages list? Just the final answer? What if Agent 2 needs to know why Agent 1 made a decision, not just what it returned?
And when Agent 3 needs both Agent 1 and Agent 2's context, do you merge the lists? In what order? What happens to the token count?

#### Langgraph discussion
- in langgraph? i dont know anything about langgraph but if i were to maintain the state in raw. it would be a dicitonary for now, yes i don't have enough knowledge to change the way i store state haha cus this is day 1, but state should have information like the particualr agent's step of reason, the action it took, the result it produced, everything is needed in the context for the next agent to even act coherently. and everything needs to get logged for us to even see what's happening in this abomination of network of agents (the graph of 10 agents talking with eachother sending results across is mind aching better to parse a json log lol). so basically for the next agent to start execution it needs prior agent's state (the context, whether it failed or passed, what it retruned, what was the reasoning step, whether to critic or support it, or to take the action from the state and to continue it? and whether to pivot this to next agent if it's a decision making agent etc...)

#### langraph primitives
1. **State:** A `TypedDict`. Shared memory the entire graph reads from and writes to. Every node gets it, every node can append to it. Reducers handle concurrent writes — add_messages appends instead of overwriting, solving the same shared state bug you fixed in your async eval harness.
2. **Node:** Any Python function that reads state and writes state. Not just agents, could be a validator, a tool executor, a human checkpoint. Agents are built from multiple nodes.
3. **Static edge:** Fixed connection. Always goes A → B.
4. **Conditional edge:** Your Python function reads current state and returns which node to route to next. The model writes its intent into state. Your edge function reads it and routes. Clean separation: model decides intent, your code decides routing.
5. **Compile:** Validates the graph structure before any execution. Catches undefined nodes, missing END paths, broken conditional routes. Locks the graph so it's safe for concurrent execution. Fail fast at definition time not runtime.

#### How loop executes
- The model generates text. code watches the stream. When it sees the Action signal it stops generation, runs the tool, injects the result as Observation, resumes generation. The model never "decides" to stop, code interrupts it.
- Modern APIs moved this to structured JSON tool calls - no string parsing. The model populates a separate field, your code reads it. LangGraph sits on top of this.

#### My ReAct agent:
1. `user query` to `llm_node`. if the query needs: state will accumulate the tool calls, else just accumulates the response.
2. `llm_node` to `routing_logic`. if state has tool calls route towards tool node (read step 3) else route towards `final_node` but interrupts the graph before executing final node. Asks the user approval. If y then resumes the graph and executes the `final_node`, elif n then asks for the modification: modifies the graph state and resumes the graph again, executing the `final_node` (difference is state is updated with the HITL response hence the final response will be different compared to y case)
3. `tool_node`, checks the tool name and executes the tool function appropriately, returns the tool message to the get appended into the state.
4. `tool_node` to `llm_node`, llm sees the appended result from tools, makes either an answer or reasons further more. 
5. depending on the LLM decision whether to call further tools or not, the flow changes. if llm decides to call tool, repeat the flow from step 2's if state has tool calls, else repeat the flow from step 2's state has no tool calls.

#### HITL in my agent:
- HITL mechanically is,
1. The checkpointer saves state at every node, so when the graph pauses, nothing is lost
2. interrupt_before tells the compiler to stop before a named node, the graph halts mid-execution and hands control back to your code
3. `invoke(None, config)` resumes from exactly that point, passing None means "no new input, just continue from where you left off"

#### Failure modes
1. **Infinite Loops:** Agent keeps calling tools without terminating. **Mitigation:** per-invocation step counter in routing logic, hard stops at N steps.
2. **Tool Hallucination:** Agent invents tool names or arguments that don't exist. **Mitigation:** strict manual tool schemas act as a whitelist; model can only call what's explicitly defined.
3. **Context Explosion:** Message history grows until context window fills up across turns. **Mitigation:** threshold check on message length, summarise oldest messages with LLM while preserving system prompt, hard cap summary at 2k tokens.
4. **Cascading Failures:** One bad tool call leads to increasingly wrong reasoning downstream. **Mitigation:** tool output validation at tool node level, return structured error instead of bad data; HITL before high-stakes tool execution.
5. **Overconfidence:** Agent answers confidently from a failed or empty tool result. **Mitigation:** tool output validation checks result quality before passing to LLM; good tool schemas with explicit failure descriptions.
6. **Under-use of Tools:** Agent answers from memory instead of using available tools. **Mitigation:** explicit system prompt instructions on when tools are mandatory; tool descriptions that clearly signal when they should be used.
7. **Goal Drift:** Agent loses track of original goal over many steps. **Mitigation:** structured output schema at each step forcing agent to restate the original goal before acting.