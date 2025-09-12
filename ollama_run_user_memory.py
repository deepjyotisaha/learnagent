import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

model_name = "llama3.1:latest"
model_url_generate = "http://localhost:11434/api/generate"

# Load user profile (memory)
with open('user_profile.txt', 'r') as f:
    user_profile = f.read()

def generate_memory_prompt(user_profile, user_prompt):
    return f"""
You are an AI assistant that remembers information about the user.

Here is the user's profile:
{user_profile}

Given the user's message below, answer in a way that takes into account the user's profile and preferences.

User's message:
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
    console.rule("[bold green]User Memory Demo")

    user_prompt = Prompt.ask("[bold yellow]Enter your message to the AI")

    memory_prompt = generate_memory_prompt(user_profile, user_prompt)
    console.print(Panel(memory_prompt, title="[bold cyan]LLM Input (With User Memory)[/bold cyan]", border_style="cyan"))

    result = generate_response(memory_prompt)
    console.print(Panel(result, title="[bold magenta]LLM Response[/bold magenta]", border_style="magenta"))