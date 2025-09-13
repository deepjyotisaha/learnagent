# 🤖 AI4All - Hands-on: Fundamentals of LLM & Agents

Welcome to the **AI4All - Hands-on - Fundamentals of LLM & Agents** project! This repository demonstrates how to build, ground, and extend LLM-powered agents with tool use, memory, and multi-step reasoning, including integration with the Model Context Protocol (MCP).

---

## 📂 Project Structure & File Guide

| File/Folder                  | Description                                                                                   |
|-----------------------------|----------------------------------------------------------------------------------------------|
| `ollama_run_agentx.py`      | Main agent demo: LLM + sales tools + memory + context + multi-step reasoning.                |
| `ollama_run_agentx_mcp.py`  | Agent demo with dynamic MCP tool discovery and execution (calculator tools via MCP server).   |
| `ollama_run_mcp_try.py`     | Example/test client for MCP tool invocation and debugging.                                    |
| `mcp_calculator_server.py`  | MCP server exposing calculator tools (add, subtract, multiply, divide) via stdio.             |
| `sales_tools.py`            | Sales data analysis tools (summarize, filter, trend, total by region, etc.).                 |
| `test_sales_tools.py`       | Unit tests for sales tools.                                                                   |
| `sales_tools_description.json` | Descriptions and parameters for each sales tool.                                            |
| `sales_data.csv`            | Example sales data for use with sales tools.                                                  |
| `ikea_return_policy.txt`    | Example grounding context for the agent.                                                      |
| `user_profile.txt`          | Example user memory/profile for the agent.                                                    |
| `requirements.txt`          | All required Python dependencies for this project.                                            |

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

### 4. Run the Agent
- **Standard agent:**
  ```bash
  python ollama_run_agentx.py
  ```
- **Agent with MCP tools:**
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

- **ollama_run_agentx.py**: Main agent loop with LLM, sales tools, and memory.
- **ollama_run_agentx_mcp.py**: Agent with dynamic MCP tool integration (calculator tools discovered and called at runtime).
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

## 💡 Tips
- Make sure the MCP server is running before starting the agent if you want to use MCP tools.
- You can extend the agent by adding new tools to `sales_tools.py` and updating `sales_tools_description.json`.
- For troubleshooting, check the terminal output and any log files generated.

---

## 🧑‍💻 Authors & Credits
- Project by Deepjyoti Saha
- Built with [Rich](https://github.com/Textualize/rich), [MCP](https://github.com/microsoft/mcp), and Python 3.8+

---

## 📜 License
This project is licensed under the MIT License.

---

Enjoy exploring LLM agents and tool use! 🤖✨
