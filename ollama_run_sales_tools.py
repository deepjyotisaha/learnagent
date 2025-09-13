import requests
import json
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from sales_tools import summarize_sales, get_top_product, average_sales, filter_by_region, sales_trend, total_sales_by_region

model_type = "ollama"
model_name = "llama3.1:latest"
model_url_generate = "http://localhost:11434/api/generate"

# Load sales tools descriptions
with open('sales_tools_description.json', 'r') as f:
    tools_desc = json.load(f)

# Example parameter values
file = 'sales_data.csv'
region = 'North'

# Map tool names to functions and default parameter values
tool_functions = {
    "summarize_sales": (summarize_sales, {"file": file}),
    "get_top_product": (get_top_product, {"file": file}),
    "average_sales": (average_sales, {"file": file}),
    "filter_by_region": (filter_by_region, {"file": file, "region": region}),
    "sales_trend": (sales_trend, {"file": file}),
    "total_sales_by_region": (total_sales_by_region, {"file": file, "region": region}),
}

def generate_tool_catalog_prompt(tools_desc, user_prompt):
    tools_info = ""
    for tool in tools_desc:
        tools_info += (
            f"Tool Name: {tool['name']}\n"
            f"Description: {tool['description']}\n"
            f"Parameters: {', '.join(tool['parameters'])}\n\n"
        )
    return f"""
You are an AI assistant that helps with sales data analysis.

Here is a catalog of available tools:
{tools_info}

Given the user's request below, select the most appropriate tool from the catalog, and return a JSON object with the following format:
{{
  "tool": "<tool_name>",
  "parameters": {{"param1": "value1", ...}}
}}

If you need to use the default file, use "file": "sales_data.csv". If a region is needed and not specified, use "region": "North".

User's request:
{user_prompt}
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
            obj = json.loads(data)
            output += obj.get("response", "")
    return output

if __name__ == "__main__":
    console = Console()
    console.print(f"[bold blue]USING MODEL[/bold blue]\n", justify="center")
    console.print(f"\n[bold white on blue]   {model_name}  [/bold white on blue]", justify="center")
    console.rule("[bold green]Sales Tools Demo (LLM Agent)")

    user_prompt = Prompt.ask("[bold yellow]Enter your sales analysis request")

    # Step 1: Let LLM choose tool and parameters
    llm_catalog_prompt = generate_tool_catalog_prompt(tools_desc, user_prompt)
    console.print(Panel(llm_catalog_prompt, title="[bold cyan]LLM Tool Selection Prompt[/bold cyan]", border_style="cyan"))
    llm_tool_response = generate_response(llm_catalog_prompt)
    console.print(Panel(llm_tool_response, title="[bold magenta]LLM Tool Selection Response[/bold magenta]", border_style="magenta"))

    # Step 2: Parse LLM response to get tool and parameters
    try:
        # Extract JSON from LLM response (handle possible text before/after JSON)
        import re
        match = re.search(r"\{[\s\S]*\}", llm_tool_response)
        if not match:
            raise ValueError("No JSON object found in LLM response.")
        tool_json = json.loads(match.group())
        tool_name = tool_json["tool"]
        params = tool_json["parameters"]
    except Exception as e:
        console.print(Panel(f"Failed to parse LLM response: {e}", title="[red]Error[/red]", border_style="red"))
        exit(1)

    # Step 3: Execute the tool
    if tool_name not in tool_functions:
        console.print(Panel(f"Tool '{tool_name}' not found.", title="[red]Error[/red]", border_style="red"))
        exit(1)
    func, default_params = tool_functions[tool_name]
    # Merge default params with LLM params (LLM params take precedence)
    exec_params = default_params.copy()
    exec_params.update(params)
    # Prepare arguments in correct order
    tool_desc = next(t for t in tools_desc if t["name"] == tool_name)
    param_order = tool_desc["parameters"]
    func_args = [exec_params[p] for p in param_order]
    result = func(*func_args)

    # Step 4: Display tool execution and result
    table = Table(show_header=True, header_style="bold")
    table.add_column("Parameter", style="bold")
    table.add_column("Value", style="italic")
    for k in param_order:
        table.add_row(str(k), str(exec_params[k]))
    panel_content = Group(
        f"[bold underline]Tool Name:[/bold underline] {tool_name}\n"
        f"[bold]Description:[/bold] {tool_desc['description']}\n",
        table,
        f"\n[bold green]Result:[/bold green]\n{result}"
    )
    console.print(Panel(panel_content, title=f"[green]{tool_name} Execution[/green]", border_style="green"))

