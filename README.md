# 🤖 Multi-Tool AI Agent (Gemini)

A small AI agent that decides **which tools to use**, runs them in a loop, and combines the results into a final answer. Built from scratch with the Gemini API, with no agent framework, to understand how agents work internally.

## 🔍 Chatbot vs Agent
- **Chatbot:** reads a message and replies.
- **Agent:** decides what action is needed, picks a tool, uses it, checks the result, and continues until the task is done.

## ⚙️ Agent Loop
```
receive task -> LLM decides -> tool needed?
    yes -> application runs tool -> result back to LLM -> repeat
    no  -> LLM writes the final answer
```

## 🧰 Tools (fictional data)
| Tool | Purpose |
|---|---|
| `get_product_info(product_name)` | Returns price and description |
| `check_stock(product_name)` | Returns availability and quantity |
| `calculate_total(price, quantity)` | Returns the total cost |

## 🛡️ Safety Design
- Allow-list of tools (`AVAILABLE_TOOLS`): the model can never run arbitrary code.
- `MAX_STEPS` limit stops infinite loops.
- Instructions forbid guessing: if a tool returns `found: False`, the agent says the information is unavailable.

## 🧪 Test Cases
| # | Request | Expected behavior |
|---|---|---|
| 1 | "Hi! What can you help me with?" | Answers directly, no tool |
| 2 | "How much does the keyboard cost?" | Uses 1 tool |
| 3 | "Tell me the price of the laptop, check whether it is available and calculate the price for two units." | Uses 3 tools in sequence |
| 4 | "Do you sell a gaming chair? What is its price?" | Tool finds nothing, agent says it is unavailable |

## ▶️ Run
```bash
pip install -r requirements.txt
# get a free key: https://aistudio.google.com/apikey
$env:GEMINI_API_KEY="your_key"   # Windows (PowerShell)
python ai_agent.py               # runs the 4 test cases
python ai_agent.py --chat        # chat yourself
```

## 🧱 Tech
Python · Gemini API (`google-genai`) · Function Calling · Agent Loop
