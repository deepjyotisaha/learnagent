import requests
import json
import asyncio
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from sales_tools import summarize_sales, get_top_product, average_sales, filter_by_region, sales_trend
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.session import ClientSession

#pip install -r requirements.txt

model_name = "llama3.1:latest"
model_url_generate = "http://localhost:11434/api/generate"

#Get me the sales for relevant region, and let me know in how many days can I return stuff from IKEA

#Add RAG
#Add MCP
#Show full integration if possible
# Show conceptual MCP and Multi Agent

# Load grounding context
with open('ikea_return_policy.txt', 'r') as f:
    grounding_blurb = f.read()

# Load sales tools descriptions
with open('sales_tools_description.json', 'r') as f:
    tools_desc = json.load(f)


async def get_mcp_tools():
    math_server_params = StdioServerParameters(
        command="python",
        args=["mcp_calculator_server.py"]
    )
    async with stdio_client(math_server_params) as (math_read, math_write):
        async with ClientSession(math_read, math_write) as math_session:
            await math_session.initialize()
            tools_result = await math_session.list_tools()
            math_tools = tools_result.tools
            # Attach session to each tool for later invocation
            for tool in math_tools:
                tool.server_session = math_session
            return math_tools

# Load user profile (memory)
with open('user_profile.txt', 'r') as f:
    user_profile = f.read()

file = 'sales_data.csv'
region = 'North'


tool_functions = {
    "summarize_sales": summarize_sales,
    "get_top_product": get_top_product,
    "average_sales": average_sales,
    "filter_by_region": filter_by_region,
    "sales_trend": sales_trend,
}

def generate_system_prompt(context, user_profile, tools_desc, history, user_query, current_message):
    tools_info = ""
    for tool in tools_desc:
        tools_info += (
            f"Tool Name: {tool['name']}\n"
            f"Description: {tool['description']}\n"
            f"Parameters: {', '.join(tool['parameters'])}\n\n"
        )
    history_str = ""
    for i, (u, a) in enumerate(history):
        step_num = i + 1
        history_str += f"Step {step_num}:\nUser: {u}\nAgent: {a}\n"
    return f"""
You are an AI assistant and your task is to complete the user's query.

The user's query is: 
{user_query}

You have access to the following:

[Available Sales Tools]
{tools_info}
File name: {file}

[User Profile]
{user_profile}

[Grounding Context]
{context}

[Conversation History]
{history_str}

You break down user's query into steps if needed. 
For each step, decide if you need to use a tool, reference the context, or use user memory. 
If you use a tool, respond ONLY with a JSON object:
{{
  "tool": "<tool_name>",
  "parameters": {{"param1": "value1", ...}},
  "next_step": "<What to do next or ask the user next>"
}}
If the task is complete, respond with:
{{
  "complete": true,
  "final_answer": "<your final answer to the user's overall query>"
}}
Otherwise, answer directly and suggest the next step.

Latest user input:
{current_message}
"""

def generate_response(prompt, model=model_name):
    payload = {
        "model": model,
        "prompt": prompt
    }
    response = requests.post(model_url_generate, json=payload, stream=True)
    response.raise_for_status()
    output = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            try:
                obj = json.loads(data)
                output += obj.get("response", "")
            except Exception:
                continue
    return output


async def try_execute_tool(tool_name, params, mcp_tools):
    try:
        # Sales tools
        if tool_name in tool_functions:
            func = tool_functions[tool_name]
            if tool_name == "filter_by_region":
                return func(params.get("file", file), params.get("region", region))
            else:
                return func(params.get("file", file))
        # MCP calculator tools
        mcp_tool_names = [tool.name for tool in mcp_tools]
        if tool_name in mcp_tool_names:
            tool = next((t for t in mcp_tools if t.name == tool_name), None)
            if tool:
                # Prepare arguments in order
                param_list = [params.get(p, 0) for p in tool.parameters]
                result = await tool(*param_list)
                return result
        return f"Tool '{tool_name}' not found."
    except Exception as e:
        return f"Error executing tool: {e}"


async def main():
    console = Console()
    console.print(f"[bold blue]USING MODEL[/bold blue]\n", justify="center")
    console.print(f"\n[bold white on blue]   {model_name}  [/bold white on blue]", justify="center")
    console.rule("[bold green]AgentX Demo: Grounding + Tools + Memory + Context + Multi-step Reasoning")

    # Load MCP tools
    mcp_tools = await get_mcp_tools()
    # Load sales tools descriptions
    with open('sales_tools_description.json', 'r') as f:
        tools_desc = json.load(f)
    # Add MCP tool descriptions
    for tool in mcp_tools:
        # Try to get parameter names robustly
        param_names = []
        if hasattr(tool, 'parameters') and isinstance(tool.parameters, list):
            param_names = tool.parameters
        elif hasattr(tool, 'param_names') and isinstance(tool.param_names, list):
            param_names = tool.param_names
        elif hasattr(tool, 'model_dump'):
            # For pydantic v2+ objects
            dump = tool.model_dump()
            param_names = dump.get('parameters', []) or dump.get('param_names', [])
        tools_desc.append({
            "name": tool.name,
            "description": getattr(tool, 'description', ''),
            "parameters": param_names
        })

    # Load user profile (memory)
    with open('user_profile.txt', 'r') as f:
        user_profile = f.read()

    # Load grounding context
    with open('ikea_return_policy.txt', 'r') as f:
        grounding_blurb = f.read()

    file = 'sales_data.csv'
    region = 'North'

    history = []
    loop_num = 1

    user_query = Prompt.ask("[bold yellow]Enter your overall task or question for the AI")
    current_message = user_query  # Start with the overall query as the first message

    while True:
        console.print(f"\n[bold yellow]--- Loop {loop_num} ---[/bold yellow]\n")
        system_prompt = generate_system_prompt(
            grounding_blurb, user_profile, tools_desc, history, user_query, current_message
        )
        console.print(Panel(system_prompt, title="[bold cyan]System Prompt[/bold cyan]", border_style="cyan"))
        response = generate_response(system_prompt)
        #console.print(Panel(response, title=f"Agent Step {loop_num}", style="bold green"))
        console.print(Panel(response, title="[bold magenta]LLM Response[/bold magenta]", border_style="magenta"))

        # Try to parse as JSON for tool call
        try:
            resp_json = json.loads(response)
            if resp_json.get("complete"):
                console.print(Panel(resp_json["final_answer"], title="Final Answer", style="bold blue"))
                break
            elif "tool" in resp_json:
                tool_name = resp_json["tool"]
                params = resp_json.get("parameters", {})
                tool_result = await try_execute_tool(tool_name, params, mcp_tools)
                history.append((current_message, f"Tool {tool_name} result: {tool_result}"))
                current_message = resp_json.get("next_step", "")
            else:
                # Not a tool call, just add to history and ask user for next input
                history.append((current_message, response))
                current_message = Prompt.ask("[bold yellow]What would you like to do next?")
        except Exception:
            # Not JSON, treat as normal response
            history.append((current_message, response))
            current_message = Prompt.ask("[bold yellow]What would you like to do next?")

        loop_num += 1


if __name__ == "__main__":
    asyncio.run(main())