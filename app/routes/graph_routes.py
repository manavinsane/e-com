from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.graph.graph import agent_graph  # adjust import if graph.py is elsewhere

router = APIRouter(prefix="/graph", tags=["graph"])

class AgentQuery(BaseModel):
    query: str

@router.post("/query")
async def run_agent(query: AgentQuery):
    """
    Exposes the LangGraph agent as an API endpoint.
    """
    try:
        # Create a message input for the agent
        state_input = {"messages": [HumanMessage(content=query.query)]}

        # Run the graph (this runs reasoning + tool calls)
        result = agent_graph.invoke(state_input)

        # Extract final model message
        final_message = result["messages"][-1].content

        return {"response": final_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))