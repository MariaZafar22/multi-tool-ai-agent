"""
 Simple AI Agent with Multiple Tools (Gemini)

Install first:
    pip install google-genai

Get a FREE Gemini API key: https://aistudio.google.com/apikey

Run:
    python ai_agent.py          -> runs the 4 test cases
    python ai_agent.py --chat   -> chat with the agent yourself

Agent loop (we write it ourselves, no framework):
    receive task -> LLM decides -> needs a tool?
        yes -> our code runs the tool -> result goes back to LLM -> repeat
        no  -> LLM writes the final answer
"""

import os
import sys
from getpass import getpass

from google import genai
from google.genai import types

# ---------------------------------------------------------------
# 0. Setup
# ---------------------------------------------------------------
API_KEY = os.environ.get("GEMINI_API_KEY") or getpass("Enter your Gemini API key: ")
MODEL_NAME = "gemini-3.5-flash-lite"  # if this name gives an error, use another Gemini Flash model
MAX_STEPS = 6  # safety limit so the agent can never loop forever
client = genai.Client(api_key=API_KEY)

# ---------------------------------------------------------------
# 1. Fictional data (our "database")
# ---------------------------------------------------------------
PRODUCTS = {
    "laptop": {"price": 850, "description": "14-inch laptop, 16GB RAM, 512GB SSD"},
    "headphones": {"price": 60, "description": "Wireless over-ear headphones"},
    "keyboard": {"price": 35, "description": "Mechanical keyboard, blue switches"},
    "monitor": {"price": 220, "description": "24-inch Full HD monitor"},
}
STOCK = {"laptop": 5, "headphones": 0, "keyboard": 12, "monitor": 3}


# ---------------------------------------------------------------
# 2. Tools (normal Python functions)
# ---------------------------------------------------------------
def get_product_info(product_name: str) -> dict:
    item = PRODUCTS.get(product_name.strip().lower())
    if item is None:
        return {"found": False, "message": f"No product named '{product_name}'."}
    return {"found": True, "product": product_name.lower(), **item}


def check_stock(product_name: str) -> dict:
    qty = STOCK.get(product_name.strip().lower())
    if qty is None:
        return {"found": False, "message": f"No stock record for '{product_name}'."}
    return {"found": True, "product": product_name.lower(), "in_stock": qty > 0, "quantity": qty}


def calculate_total(price: float, quantity: int) -> dict:
    return {"price": price, "quantity": quantity, "total": price * quantity}


# Allow-list: the agent can ONLY run these functions
AVAILABLE_TOOLS = {
    "get_product_info": get_product_info,
    "check_stock": check_stock,
    "calculate_total": calculate_total,
}

# Tool descriptions the LLM reads (name, purpose, parameters)
TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="get_product_info",
        description="Get the price and description of a product from the catalog.",
        parameters=types.Schema(
            type="OBJECT",
            properties={"product_name": types.Schema(type="STRING", description="e.g. laptop")},
            required=["product_name"],
        ),
    ),
    types.FunctionDeclaration(
        name="check_stock",
        description="Check whether a product is in stock and how many units are available.",
        parameters=types.Schema(
            type="OBJECT",
            properties={"product_name": types.Schema(type="STRING", description="e.g. laptop")},
            required=["product_name"],
        ),
    ),
    types.FunctionDeclaration(
        name="calculate_total",
        description="Calculate the total cost for a given unit price and quantity.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "price": types.Schema(type="NUMBER", description="Price of one unit"),
                "quantity": types.Schema(type="INTEGER", description="Number of units"),
            },
            required=["price", "quantity"],
        ),
    ),
]

# ---------------------------------------------------------------
# 3. Agent instructions
# ---------------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are a shopping assistant agent for a small electronics store.
You can use three tools: get_product_info, check_stock and calculate_total.

Rules:
- Use tools whenever you need product prices, stock or totals. Never guess these values.
- A request may need several tools. Use them one after another and use earlier results in later calls.
- Never do price math yourself, use calculate_total.
- If a tool says found=False, tell the user clearly that the information is unavailable.
  Do NOT invent products, prices or stock numbers.
- For general questions that need no tool (greetings, general knowledge), answer directly.
- Keep final answers short and clear.
"""


# ---------------------------------------------------------------
# 4. The agent loop
# ---------------------------------------------------------------
def run_agent(user_request: str) -> str:
    print("\n" + "=" * 60)
    print(f"USER REQUEST: {user_request}")
    print("=" * 60)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[types.Tool(function_declarations=TOOL_DECLARATIONS)],
        # We run the loop ourselves, so turn off the SDK's automatic tool running
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=user_request)])]
    tools_used = []

    for step in range(1, MAX_STEPS + 1):
        response = client.models.generate_content(model=MODEL_NAME, contents=contents, config=config)
        calls = response.function_calls

        # No tool requested -> the LLM is giving the final answer
        if not calls:
            print(f"\n[Step {step}] LLM: no more tools needed -> final answer")
            print(f"TOOLS USED: {tools_used if tools_used else 'none'}")
            print(f"\nFINAL ANSWER:\n{response.text}")
            return response.text

        # Keep the model's tool request in the conversation history
        contents.append(response.candidates[0].content)

        # Our application runs each requested tool
        result_parts = []
        for call in calls:
            args = dict(call.args)
            print(f"\n[Step {step}] LLM chose tool: {call.name}({args})")
            if call.name in AVAILABLE_TOOLS:
                result = AVAILABLE_TOOLS[call.name](**args)
            else:
                result = {"error": f"Unknown tool '{call.name}'"}
            print(f"[Step {step}] Tool result: {result}")
            tools_used.append(call.name)
            result_parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))

        # Send the tool results back to the LLM, then loop again
        contents.append(types.Content(role="user", parts=result_parts))

    msg = "Sorry, I could not finish this task within the step limit."
    print(f"\nFINAL ANSWER:\n{msg}")
    return msg


# ---------------------------------------------------------------
# 5. Test cases
# ---------------------------------------------------------------
TEST_CASES = [
    "Hi! What can you help me with?",  # 1. simple, no tool
    "How much does the keyboard cost?",  # 2. one tool
    "Tell me the price of the laptop, check whether it is available and calculate the price for two units.",  # 3. multiple tools
    "Do you sell a gaming chair? What is its price?",  # 4. unsuccessful case
]

if __name__ == "__main__":
    if "--chat" in sys.argv:
        print("Chat with the agent. Type 'exit' to stop.")
        while True:
            q = input("\nYou: ").strip()
            if q.lower() in ("exit", "quit", ""):
                break
            run_agent(q)
    else:
        for case in TEST_CASES:
            run_agent(case)
