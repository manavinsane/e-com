from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
# from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, END, START
from app.core.config import GROQ_API_KEY
from app.api.product import LLM_TOOLS
from langchain_openai import ChatOpenAI

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], "conversation history"]

# model = ChatGroq(
#     model="openai/gpt-oss-120b",
#     api_key=GROQ_API_KEY,
#     temperature=0,
# ).bind_tools(LLM_TOOLS, parallel_tool_calls=False)

model = ChatOpenAI(
    model="gpt-5-nano",
    api_key="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",
    temperature=0,
).bind_tools(LLM_TOOLS, parallel_tool_calls=False)


def call_model(state: dict):
    response = model.invoke(state["messages"])
    # breakpoint()
    return {"messages": [response]}


# tool_node = ToolNode(LLM_TOOLS)

tools_by_name = {tool.name: tool for tool in LLM_TOOLS}

# def tool_node(state: dict):
#     """Performs the tool call"""

#     result = []

#     for tool_call in state["messages"][-1].tool_calls:
#         tool = tools_by_name[tool_call["name"]]
#         observation = tool.invoke(tool_call["args"])
#         # result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
#         tool_msg = ToolMessage(content=observation, tool_call_id=tool_call["id"])
#         # ✅ Append the serialized form
#         # import json
#         # result.append(json.loads(tool_msg.content))
#         # breakpoint()
#         state["messages"].append(tool_msg)  # ✅ correct
    
#     print("----------------> messages:", result)
#     return {"messages": result}

def tool_node(state: dict):
    result = []

    last_message = state["messages"][-1]
    if not getattr(last_message, "tool_calls", None):
        # No tool calls, return state as is
        return {"messages": state["messages"]}

    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        tool_msg = ToolMessage(content=observation, tool_call_id=tool_call["id"])
        # Append tool message to state
        state["messages"].append(tool_msg)
        # Keep track of new messages
        result.append(tool_msg)

    # ✅ Return the updated state
    return {"messages": state["messages"]}

# Router
def route_after_model(state: AgentState):
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        # breakpoint()
        return "tools"
    return END


# graph = StateGraph(AgentState)
# graph.add_node("model", call_model)
# graph.add_node("tools", tool_node)
# graph.set_entry_point("model")

# graph.add_conditional_edges("model", route_after_model)
# graph.add_edge("tools", "model")
graph = StateGraph(AgentState)

graph.add_node("call_model", call_model)
graph.add_node("tools", tool_node)

graph.add_edge(START, "call_model")

graph.add_conditional_edges(
    "call_model",
    route_after_model,
)
graph.add_edge("tools","call_model" )
agent_graph = graph.compile()

# Run test
if __name__ == "__main__":
    query = "List all products"
    result = agent_graph.invoke({"messages": [HumanMessage(content=query)]})
    print(result["messages"][-1].content)
