import requests
import json
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from sales_tools import summarize_sales, get_top_product, average_sales, filter_by_region, sales_trend

model_name = "llama3.1:latest"
model_url_generate = "http://localhost:11434/api/generate"

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
        history_str += f"User: {u}\nAgent: {a}\n"
    return f"""
You are an AI assistant with access to the following:

[Grounding Context]
{context}

[User Profile]
{user_profile}

[Available Sales Tools]
{tools_info}

File name: {file}

[Conversation History]
{history_str}

Your job is to help the user complete their overall task, breaking it into steps if needed. 
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

User's overall query:
{user_query}

Current message:
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

def try_execute_tool(tool_name, params):
    try:
        if tool_name not in tool_functions:
            return f"Tool '{tool_name}' not found."
        func = tool_functions[tool_name]
        if tool_name == "filter_by_region":
            return func(params.get("file", file), params.get("region", region))
        else:
            return func(params.get("file", file))
    except Exception as e:
        return f"Error executing tool: {e}"

if __name__ == "__main__":
    console = Console()
    console.print(f"[bold blue]USING MODEL[/bold blue]\n", justify="center")
    console.print(f"\n[bold white on blue]   {model_name}  [/bold white on blue]", justify="center")
    console.rule("[bold green]AgentX Demo: Grounding + Tools + Memory + Context + Multi-step Reasoning")

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
                    tool_result = try_execute_tool(tool_name, params)
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