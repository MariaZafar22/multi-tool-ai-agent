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

## 🎬 Sample Output

```
USER REQUEST: Tell me the price of the laptop, check whether it is available
              and calculate the price for two units.

TOOLS USED: ['get_product_info', 'check_stock', 'calculate_total']

FINAL ANSWER:
The laptop is priced at $850 and is currently in stock (5 units available).
The total price for two units is $1,700.
```

---

## 🚀 Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/MariaZafar22/multi-tool-ai-agent.git
cd multi-tool-ai-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set your Gemini API key** (free key: [Google AI Studio](https://aistudio.google.com/apikey))
```powershell
$env:GEMINI_API_KEY="your_key"     # Windows (PowerShell)
```
```bash
export GEMINI_API_KEY="your_key"   # macOS / Linux
```

**4. Run**
```bash
python ai_agent.py          # runs the 4 test cases
python ai_agent.py --chat   # chat with the agent yourself
```

> ⚠️ If you see `404 NOT_FOUND`, change `MODEL_NAME` to another available Gemini Flash model. A `503 UNAVAILABLE` error is temporary, so just retry.

---

## 🧱 Tech Stack

**Python** · **Gemini API** (`google-genai`) · **Function Calling** · **Agent Loop**

---

## 👩‍💻 Author

**Maria Zafar**
GitHub: [@MariaZafar22](https://github.com/MariaZafar22)


