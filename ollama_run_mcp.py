#import os
#from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
#from concurrent.futures import TimeoutError
#from functools import partial
#import logging
#import sys
#from datetime import datetime
#from config import Config
import requests
import json
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from sales_tools import summarize_sales, get_top_product, average_sales, filter_by_region, sales_trend, total_sales_by_region

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
    "total_sales_by_region": total_sales_by_region,
}

def generate_system_prompt(context, user_profile, tools_desc, mcp_tool_desc, history, user_query, current_message):
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

[Available Math Tools in MCP]
{mcp_tool_desc}

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
                output += data
    return output


async def execute_tool_in_mcp(tool_name, params, tools):

    #if response_text.startswith("FUNCTION_CALL:"):
    #_, function_info = response_text.split(":", 1)
    #parts = [p.strip() for p in function_info.split("|")]
    #func_name, params = parts[0], parts[1:]

    print("DEBUG: Executing tool in MCP, Tool name:", tool_name, "Params:", params)

    func_name = tool_name
    params = params 

    # Find the matching tool to get its input schema
    tool = next((t for t in tools if t.name == func_name), None)
    if not tool:
        print(f"DEBUG: Available tools: {[t.name for t in tools]}")
        raise ValueError(f"Unknown tool: {func_name}")

    print(f"DEBUG: Found tool: {tool.name}")
    print(f"DEBUG: Tool schema: {tool.inputSchema}")

    # Get the correct session from the tool
    session = tool.server_session
    if not session:
        raise ValueError(f"No session found for tool: {func_name}")

    # Prepare arguments according to the tool's input schema
    arguments = {}
    schema_properties = tool.inputSchema.get('properties', {})
    print(f"DEBUG: Schema properties: {schema_properties}")

    for param_name, param_info in schema_properties.items():
        print(f"DEBUG: Processing parameter: {param_name} with info {param_info}")
        #if not params:  # Check if we have enough parameters
        #    print
        #    raise ValueError(f"Not enough parameters provided for {func_name}")
        if param_name not in params:
            raise ValueError(f"Missing required parameter: {param_name}")
        value = params[param_name]
        param_type = param_info.get('type', 'string')
        
        print(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")
        
        # Convert the value to the correct type based on the schema
        if param_type == 'integer':
            arguments[param_name] = int(value)
        elif param_type == 'number':
            arguments[param_name] = float(value)
        elif param_type == 'array':
            # Handle array input
            if isinstance(value, str):
                value = value.strip('[]').split(',')
            arguments[param_name] = [int(x.strip()) for x in value]
        else:
            arguments[param_name] = str(value)

    print(f"DEBUG: Final arguments: {arguments}")
    print(f"DEBUG: Calling tool {func_name}")

    try:
        result = await session.call_tool(func_name, arguments=arguments)
        print(f"DEBUG: Raw result: {result}")
        # Get the full result content
        if hasattr(result, 'content'):
            print(f"DEBUG: Result has content attribute")
            # Handle multiple content items
            if isinstance(result.content, list):
                iteration_result = [
                    item.text if hasattr(item, 'text') else str(item)
                    for item in result.content
                ]
            else:
                iteration_result = str(result.content)
        else:
            print(f"DEBUG: Result has no content attribute")
            iteration_result = str(result)
        return iteration_result
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"DEBUG: Exception during call_tool: {e}\n{tb}")
        return f"Error executing tool: {e}"


async def try_execute_tool(tool_name, params, math_tools):
    try:
        if tool_name in tool_functions:
            print(f"DEBUG: Found tool function {tool_name}")
            func = tool_functions[tool_name]
            if tool_name == "filter_by_region" or tool_name == "total_sales_by_region":
                return func(params.get("file", file), params.get("region", region))
            else:
                return func(params.get("file", file))
        else:
            print(f"DEBUG: Tool {tool_name} not found, executing in MCP")
            result = await execute_tool_in_mcp(tool_name, params, math_tools)
            return result
    except Exception as e:
        return f"Error executing tool: {e}"

async def main():
    console = Console()
    console.print(f"[bold blue]USING MODEL[/bold blue]\n", justify="center")
    console.print(f"\n[bold white on blue]   {model_name}  [/bold white on blue]", justify="center")
    console.rule("[bold green]AgentX Demo: Grounding + Tools + Memory + Context + Multi-step Reasoning")

    #Create session to MCP server and get tools
    math_server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )

    async with stdio_client(math_server_params) as (math_read, math_write):
        print("Connection established, creating session...")
        async with ClientSession(math_read, math_write) as math_session:
            print("Session created, initializing...")
            await math_session.initialize()
            
            # Get available tools
            print("Requesting tool list...")
            tools_result = await math_session.list_tools()
            math_tools = tools_result.tools
            print(f"Math server tools: {len(math_tools)}")
            for tool in math_tools:
                tool.server_session = math_session
            print(f"Successfully retrieved {len(math_tools)} math tools")
            
            try:
                math_tools_description = []
                for i, tool in enumerate(math_tools):
                    try:
                        # Get tool properties
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        
                        # Format the input schema in a more readable way
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'

                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        math_tools_description.append(tool_desc)
                        print(f"Added description for tool: {tool_desc}")
                    except Exception as e:
                        print(f"Error processing tool {i}: {e}")
                        math_tools_description.append(f"{i+1}. Error processing tool")
                
                math_tools_description = "\n".join(math_tools_description)
                print("Successfully created tools description")
            except Exception as e:
                print(f"Error creating tools description: {e}")
                math_tools_description = "Error loading tools"
                
            history = []
            loop_num = 1

            user_query = Prompt.ask("[bold yellow]Enter your overall task or question for the AI")
            current_message = user_query  # Start with the overall query as the first message

            while True:
                console.print(f"\n[bold yellow]--- Loop {loop_num} ---[/bold yellow]\n")
                system_prompt = generate_system_prompt(
                    grounding_blurb, user_profile, tools_desc, math_tools_description, history, user_query, current_message
                )
                console.print(Panel(system_prompt, title="[bold cyan]System Prompt[/bold cyan]", border_style="cyan"))

                llm_response = generate_response(system_prompt)
                console.print(Panel(llm_response, title="[bold magenta]LLM Response[/bold magenta]", border_style="magenta"))

                # Try to parse tool call or completion from LLM response
                try:
                    import re
                    match = re.search(r"\{[\s\S]*\}", llm_response)
                    if match:
                        tool_json = json.loads(match.group())
                        if tool_json.get("complete"):
                            final_answer = tool_json.get("final_answer", "Task complete.")
                            console.print(Panel(final_answer, title="[bold green]Final Answer[/bold green]", border_style="green"))
                            history.append((current_message, final_answer))
                            break
                        elif "tool" in tool_json:
                            tool_name = tool_json.get("tool")
                            params = tool_json.get("parameters", {})
                            print(f"DEBUG: Executing tool {tool_name} with params {params}")
                            tool_result = await try_execute_tool(tool_name, params, math_tools)
                            console.print(Panel(f"Tool: {tool_name}\nParameters: {params}\nResult: {tool_result}",
                                                title="[green]Tool Execution[/green]", border_style="green"))
                            # Add to history and continue with next step
                            agent_reply = f"Tool used: {tool_name}\nResult: {tool_result}"
                            history.append((current_message, agent_reply))
                            # LLM's next_step is a question or instruction for the user
                            next_step = tool_json.get("next_step", "What should I do next?")
                            user_input = Prompt.ask(f"[bold yellow]Agent: {next_step}\nYour reply")
                            current_message = f"{next_step}\nUser: {user_input}"
                        else:
                            # Not a tool or completion, treat as normal reply
                            agent_reply = llm_response
                            history.append((current_message, agent_reply))
                            user_input = Prompt.ask("[bold yellow]Agent: (next step or question above)\nYour reply")
                            current_message = user_input
                    else:
                        # Not a JSON, treat as normal reply
                        agent_reply = llm_response
                        history.append((current_message, agent_reply))
                        user_input = Prompt.ask("[bold yellow]Agent: (next step or question above)\nYour reply")
                        current_message = user_input
                except Exception as e:
                    agent_reply = llm_response + f"\n[red]Error parsing tool call: {e}[/red]"
                    history.append((current_message, agent_reply))
                    user_input = Prompt.ask("[bold yellow]Agent: (next step or question above)\nYour reply")
                    current_message = user_input

                loop_num += 1
                input("\n[bold blue]Press Enter to proceed to the next loop...[/bold blue]\n")


if __name__ == "__main__":
    asyncio.run(main())