import json
from sales_tools import summarize_sales, get_top_product, average_sales, filter_by_region, sales_trend, total_sales_by_region
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

file = 'sales_data.csv'
region = 'North'
console = Console()

# Map tool names to functions and default parameter values
tool_functions = {
    "summarize_sales": (summarize_sales, {"file": file}),
    "get_top_product": (get_top_product, {"file": file}),
    "average_sales": (average_sales, {"file": file}),
    "filter_by_region": (filter_by_region, {"file": file, "region": region}),
    "sales_trend": (sales_trend, {"file": file}),
    "total_sales_by_region": (total_sales_by_region, {"file": file, "region": region}),
}

# Load tool descriptions
with open('sales_tools_description.json', 'r') as f:
    tools_desc = json.load(f)

def tool_panel(tool_name, description, param_names, params, result, color):
    table = Table(show_header=True, header_style="bold")
    table.add_column("Parameter", style="bold")
    table.add_column("Value", style="italic")
    for k in param_names:
        v = params.get(k, "")
        table.add_row(str(k), str(v))
    panel_content = Group(
        f"[bold underline]Tool Name:[/bold underline] {tool_name}\n"
        f"[bold]Description:[/bold] {description}\n"
        f"[bold]Parameters:[/bold] {', '.join(param_names)}\n",
        table,
        f"\n[white]{result}[/white]"
    )
    return Panel.fit(
        panel_content,
        title=f"[{color}]{tool_name}[/{color}]",
        border_style=color
    )

colors = ["green", "blue", "magenta", "yellow", "cyan"]

for idx, tool in enumerate(tools_desc):
    name = tool["name"]
    desc = tool["description"]
    param_names = tool["parameters"]
    params = tool_functions[name][1]
    func = tool_functions[name][0]
    # Prepare arguments for the function
    func_args = [params[p] for p in param_names]
    result = func(*func_args)
    color = colors[idx % len(colors)]
    console.print(tool_panel(name, desc, param_names, params, result, color))
