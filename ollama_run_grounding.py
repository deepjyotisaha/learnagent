import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

model_type = "ollama"
#model_name = "mistral"
model_name = "llama3.1:latest"
model_url_generate = "http://localhost:11434/api/generate"
model_url_embed = "http://localhost:11434/api/embeddings"

# Load external knowledge from file
with open('ikea_return_policy.txt', 'r') as file:
    grounding_blurb = file.read()

#prompt = "What is the return policy of IKEA? What categories can I exchange and within how many days?"

def generate_llm_prompt(user_prompt):
    return f"""
    You are an AI assistant. Your job is to answer user's question correctly.

    Use ONLY the following information to answer the question accurately. Don't assume any information beyond this to provide the answer. If the information is not present, simply state that you don't know the answer. Do not make up any answers.

    Context:
    {grounding_blurb}

    User's Question:
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
			import json
			data = line.decode("utf-8")
			obj = json.loads(data)
			output += obj.get("response", "")
	return output

if __name__ == "__main__":
	console = Console()
	console.print(f"[bold blue] USING MODEL[/bold blue]\n", justify="center")
	console.print(f"\n[bold white on blue]   {model_name}  [/bold white on blue]", justify="center")
	print("\n")
	user_prompt = Prompt.ask("[bold yellow]Enter your prompt")
	print("\n")
	final_prompt = generate_llm_prompt(user_prompt)
	console.print(Panel(final_prompt, title="[bold cyan]LLM Prompt[/bold cyan]", style="bold cyan", border_style="bright_cyan"))
	print("\n")
	result = generate_response(final_prompt)
	console.print(Panel(result, title="[bold cyan]LLM Response[/bold cyan]", style="bold cyan", border_style="bright_cyan"))

