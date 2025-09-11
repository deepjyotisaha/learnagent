


import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

model_type = "ollama"
model_name = "mistral:text"
model_url_generate = "http://localhost:11434/api/generate"
model_url_embed = "http://localhost:11434/api/embeddings"



prompt = "What is the capital of France?"


def generate_response(prompt=prompt, model=model_name):
	payload = {
		"model": model,
		"prompt": prompt
	}
	response = requests.post(model_url_generate, json=payload, stream=True)
	response.raise_for_status()
	output = ""
	for line in response.iter_lines():
		if line:
			import json
			data = line.decode("utf-8")
			obj = json.loads(data)
			output += obj.get("response", "")
	return output

if __name__ == "__main__":
	console = Console()
	console.print(f"[bold blue] USING MODEL[/bold blue]\n", justify="center")
	console.print(f"\n[bold white on blue]   {model_name}  [/bold white on blue]", justify="center")
	#console.print(f"[bold blue]{model_name}[/bold blue]\n", justify="center")
	#console.rule("[bold green]PROMPT TO LLM")
	prompt = Prompt.ask("[bold green]Enter your prompt")
	print("\n")
	console.print(Panel(prompt, title="[bold yellow]LLM Prompt[/bold yellow]", style="bold yellow", border_style="bright_yellow"))
	print("\n")
	result = generate_response(prompt)
	#console.rule("[bold magenta]LLM RESPONSE")
	console.print(Panel(result, title="[bold cyan]LLM Response[/bold cyan]", style="bold cyan", border_style="bright_cyan"))

