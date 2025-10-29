from fastapi import APIRouter, Depends, Query, HTTPException
from app.agents.sql_agent import generate_and_execute_select_query, fetch_database_schema
from app.agents.sql_agent import fetch_database_schema, generate_and_execute_select_query, search_web, login_user
# from langchain.agents import AgentExecutor, create_tool_calling_agent
# from langchain.agents.agent_executor import AgentExecutor
from langchain.agents import create_agent


from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from app.db.database import get_session
from sqlmodel import Session
# from sqlmodel import Session

router = APIRouter()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0).bind_tools(
    [fetch_database_schema, generate_and_execute_select_query, search_web])

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a versatile AI assistant that can help with both database queries and general questions.

IMPORTANT: You have built-in knowledge and should answer most questions directly. Only use tools when necessary.

Tool Usage Decision Tree:
1. For DATABASE queries (products, orders, sales, customers, analytics):
   - Use fetch_database_schema first
   - Then use generate_and_execute_select_query

2. For CURRENT/RECENT information (breaking news, today's events, real-time data):
   - Use search_web tool

3. For GENERAL KNOWLEDGE (history, facts, explanations, people's basic info):
   - Answer directly using your knowledge - NO TOOLS NEEDED
   - Examples: "Who is Virat Kohli?", "What is Python?", "Explain SQL"

Remember: Don't use tools unnecessarily. Your knowledge is extensive - use it!"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent_prompt2 = ChatPromptTemplate.from_messages([
    ('system',     """
    Accepts a natural language text in which required login credenntials are there.
    1. Extract login credentials from prompt(key name is username or email, password)
    2. use login api to get token
    3. return appropriate results
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

tools = [search_web, fetch_database_schema, generate_and_execute_select_query, login_user]
agent = create_agent(llm, tools,system_prompt=agent_prompt)
agent2 = create_agent(llm, tools,system_prompt=agent_prompt2)
# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True,
#     handle_parsing_errors=True,
#     max_iterations=5
# )
# agent_executor2 = AgentExecutor(
#     agent=agent2,
#     tools=tools,
#     verbose=True,
#     handle_parsing_errors=True,
#     max_iterations=5
# )

@router.get("/smart-analytic")
def smart_analytic(
    prompt: str = Query(..., description="Ask in plain English, e.g., 'Top 3 most ordered products'")
):
    """
    Accepts a natural language prompt,
    auto-fetches DB schema, generates SQL using LLM, executes it,
    and returns both the query and results.
    """
    try:
        # Step 1: Fetch database schema
        schema = fetch_database_schema.invoke(input={})
        print("Fetched Schema:", list(schema.keys()))

        # Step 2: Generate and execute SQL query
        result = generate_and_execute_select_query.invoke(input={"prompt": prompt, "schema": schema})

        # Step 3: Return the response
        return {
            "query": result.get("query", "N/A"),
            "columns": result.get("columns", []),
            "rows": result.get("rows", []),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/agent/login")
def login_agent(
    prompt: str = Query(..., description="enter your info to authenticate")
):
    """
    Accepts a natural language prompt in which required login credenntials are there.
    1. Extract login credentials from prompt(key name is username or email, password)
    2. use login api to get token
    3. return appropriate results
    """
    try:
        # Invoke the agent - it will decide which tools to call
        result = agent2.invoke({"input": prompt})
        
        # Extract the final output
        output = result.get("output", "")
        
        return {
            "success": True,
            "prompt": prompt,
            "answer": output,
            "tools_used": [step[0].tool for step in result.get("intermediate_steps", [])],
            "intermediate_steps": [
                {
                    "tool": step[0].tool,
                    "tool_input": step[0].tool_input,
                    "output": str(step[1])[:500]  # Truncate for readability
                }
                for step in result.get("intermediate_steps", [])
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/smart-analytics")
def smart_analytics(
    prompt: str = Query(..., description="Ask anything - general questions or database queries")
):
    """
    Accepts a natural language prompt and uses an AI agent to:
    1. Determine if it's a general question or database query
    2. Use web search for general knowledge questions
    3. Use database tools for SQL queries
    4. Return appropriate results
    """
    try:
        # Invoke the agent - it will decide which tools to call
        result = agent.invoke({"input": prompt})
        
        # Extract the final output
        output = result.get("output", "")
        
        return {
            "success": True,
            "prompt": prompt,
            "answer": output,
            "tools_used": [step[0].tool for step in result.get("intermediate_steps", [])],
            "intermediate_steps": [
                {
                    "tool": step[0].tool,
                    "tool_input": step[0].tool_input,
                    "output": str(step[1])[:500]  # Truncate for readability
                }
                for step in result.get("intermediate_steps", [])
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))