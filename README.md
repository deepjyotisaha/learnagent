# 🤖 AI4All - Hands-on: Fundamentals of LLM & Agents

Welcome to the **AI4All - Hands-on - Fundamentals of LLM & Agents** project! This repository demonstrates how to build, ground, and extend LLM-powered agents with tool use, memory, and multi-step reasoning, including integration with the Model Context Protocol (MCP).

---


## 📂 Project Structure & Conceptual Build-up

The project is organized to help you learn and experiment with LLM agents step by step, from the simplest to the most advanced. Here’s the recommended order:

| File/Folder                        | Concept/Stage                                                                                 |
|------------------------------------|----------------------------------------------------------------------------------------------|
| `helloworld.py`                    | 🟢 **Hello World**: Minimal LLM call, basic prompt/response.                                 |
| `ollama_run_pretrained.py`         | 🟢 **Pretrained LLM**: Use a base LLM for simple Q&A.                                        |
| `ollama_run_finetuned.py`          | 🟡 **Fine-tuned LLM**: Use a fine-tuned LLM for improved task performance.                   |
| `ollama_run_no_grounding.py`       | 🟡 **No Grounding**: LLM agent without external context.                                     |
| `ollama_run_grounding.py`          | 🟠 **Grounding**: Add external context (e.g., policies) to LLM agent.                        |
| `ollama_run_sales_tools.py`        | 🟠 **Tool Use**: LLM agent can call Python sales tools for data analysis.                    |
| `ollama_run_user_memory.py`        | 🟠 **User Memory**: Add persistent user profile/memory to agent.                             |
| `ollama_run_agentx.py`             | 🟣 **AgentX**: Full agent with LLM, tools, memory, context, and multi-step reasoning.        |
| `ollama_run_agentx_mcp.py`         | 🟣 **AgentX + MCP**: AgentX with dynamic MCP tool discovery and execution.                   |
| `ollama_run_mcp_try.py`            | 🧪 **MCP Client Example**: Example/test client for MCP tool invocation and debugging.         |
| `mcp_calculator_server.py`         | 🧮 **MCP Calculator Server**: Exposes calculator tools (add, subtract, multiply, divide).    |
| `sales_tools.py`                   | 🛠️ **Sales Tools**: Python functions for sales data analysis.                               |
| `test_sales_tools.py`              | 🧪 **Sales Tools Tests**: Unit tests for sales tools.                                        |
| `sales_tools_description.json`     | 📝 **Sales Tools Metadata**: Descriptions and parameters for each sales tool.                |
| `sales_data.csv`                   | 📊 **Sales Data**: Example sales data for use with sales tools.                              |
| `ikea_return_policy.txt`           | 📄 **Grounding Context**: Example context for grounding agent responses.                     |
| `user_profile.txt`                 | 👤 **User Profile**: Example user memory/profile for the agent.                              |
| `requirements.txt`                 | 📦 **Dependencies**: All required Python dependencies for this project.                      |
| `AI4All - Hands-on - Fundamentals of LLM & Agents.code-workspace` | VS Code workspace settings.                             |
| `__pycache__/`                     | Python bytecode cache (auto-generated).                                                      |


---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd "AI4All - Hands-on - Fundamentals of LLM & Agents"
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the MCP Calculator Server (if using MCP tools)
```bash
python mcp_calculator_server.py
```
Note: The MCP server is started by the agent, you don't need to start it when using with the agent.

### 4. Run the Agent
 **Standard agent with local tools:**
  ```bash
  python ollama_run_agentx.py
  ```
 **Agent with local and MCP tools:**
  ```bash
  python ollama_run_agentx_mcp.py
  ```

### 5. Interact!
- Follow the prompts in the terminal.
- Try queries like:
  - "What is the sum of 5 and 7?"
  - "Show me the sales trend for the North region."
  - "Add 10 and 20 using the calculator tool."

---

## 🛠️ Key Features
- **LLM-powered agent** with context, memory, and tool use
- **Dynamic tool discovery** via MCP protocol
- **Sales analytics tools** for CSV data
- **Calculator tools** (add, subtract, multiply, divide) via MCP
- **Rich terminal UI** with [Rich](https://github.com/Textualize/rich)

---


## 📄 File Details

- **helloworld.py**: Test if Python is installed.
- **ollama_run_pretrained.py**: Use a base LLM for simple Q&A.
- **ollama_run_finetuned.py**: Use a fine-tuned LLM for improved task performance.
- **ollama_run_no_grounding.py**: LLM agent without external context.
- **ollama_run_grounding.py**: Add external context (e.g., policies) to LLM agent.
- **ollama_run_sales_tools.py**: LLM agent can call Python sales tools for data analysis.
- **ollama_run_user_memory.py**: Add persistent user profile/memory to agent.
- **ollama_run_agentx.py**: Full agent with LLM, tools, memory, context, and multi-step reasoning.
- **ollama_run_agentx_mcp.py**: AgentX with dynamic MCP tool discovery and execution.
- **ollama_run_mcp_try.py**: Example/test client for MCP tool invocation and debugging.
- **mcp_calculator_server.py**: MCP server exposing calculator tools (add, subtract, multiply, divide) via stdio.
- **sales_tools.py**: Implements sales data analysis tools (summarize, filter, trend, total by region, etc.).
- **test_sales_tools.py**: Unit tests for sales tools.
- **sales_tools_description.json**: Descriptions and parameters for each sales tool.
- **sales_data.csv**: Example sales data for use with sales tools.
- **ikea_return_policy.txt**: Example grounding context for the agent.
- **user_profile.txt**: Example user memory/profile for the agent.
- **requirements.txt**: All required Python dependencies for this project.

---

## 🧑‍💻 Authors & Credits
- Project by Deepjyoti Saha
- Built with [Rich](https://github.com/Textualize/rich), [MCP](https://github.com/microsoft/mcp), and Python 3.8+

---

## 📜 License
This project is licensed under the MIT License.

---

Enjoy exploring LLM agents and tool use! 🤖✨
