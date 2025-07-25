import os
import sys
import logging
import asyncio
from pydantic import BaseModel, Field
from typing import List

# Configure logging to see the output from the function
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add project root to path to allow imports from other directories
# This assumes the script is run from the 'triggers' directory or the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from triggers.main import passes_trigger_conditions_check
except ImportError as e:
    print(f"Error: Failed to import necessary modules. Make sure you are running this script from the project's root directory. Details: {e}")
    sys.exit(1)


# --- Mock Data ---
# A simple Pydantic model to mock the `MailMessage` object from `imap_tools`
class MockMailMessage(BaseModel):
    from_: str
    to: List[str] = Field(default_factory=list)
    subject: str
    text: str
    html: str
    uid: str
    date_str: str = "2025-01-01 12:00:00"

async def run_diagnostic():
    """
    Runs a diagnostic test for the LLM trigger condition check.
    """
    print("--- Running Trigger Condition Check Diagnostic ---")

    # 1. CONFIGURE YOUR TEST CASE HERE
    # This data is taken directly from the production logs.
    # ----------------------------------------------------
    mock_msg = MockMailMessage(
        from_="arthur.stockman.me@gmail.com",
        to=["test@example.com"],
        subject="test",
        text="test\r\n\n",
        html="",
        uid="5780", # From production log
        date_str="2025-01-01 12:00:00"
    )

    trigger_conditions = "Create the draft for EVERY incoming email"

    # IMPORTANT: You MUST set your OpenRouter API key as an environment variable
    # In your terminal, run: export OPENROUTER_API_KEY="your_key_here"
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n[ERROR] OPENROUTER_API_KEY environment variable not set.")
        print("Please set it before running the script:")
        print("  export OPENROUTER_API_KEY='your_key_here'")
        return

    # Create a mock trigger with the model
    from agent.models import TriggerModel
    from uuid import uuid4
    
    mock_trigger = TriggerModel(
        agent_uuid=uuid4(),
        trigger_conditions=trigger_conditions,
        filter_rules={},
        model="google/gemini-2.5-flash-preview-05-20:thinking"  # You can change this to test other models
    )
    # ----------------------------------------------------

    print(f"\n[INFO] Using Model: {mock_trigger.model}")
    print(f"[INFO] Trigger Conditions: '{mock_trigger.trigger_conditions}'")
    print(f"[INFO] Email From: {mock_msg.from_}")
    print(f"[INFO] Email Subject: {mock_msg.subject}")
    print(f"[INFO] Email Body: '{mock_msg.text}'")
    print("----------------------------------------------------\n")

    # 2. Run the check
    try:
        # This will call the function from main.py and print its internal logs
        # Note: thread_context=None, message_id="test", agent_name="test" for this diagnostic
        result = await passes_trigger_conditions_check(mock_msg, mock_trigger, None, "test", "test")
        
        print(f"\n--- DIAGNOSTIC RESULT ---")
        print(f"The function returned: {result}")
        print("-------------------------\n")
        
        if result:
            print("✅ The check PASSED. The agent would proceed with this email.")
        else:
            print("❌ The check FAILED. The agent would NOT proceed.")
            print("   Review the logs above to see the raw response from the LLM and any errors.")

    except Exception as e:
        print(f"\n--- SCRIPT EXECUTION ERROR ---")
        print(f"An unexpected error occurred while running the diagnostic script: {e}")
        print("--------------------------------\n")


if __name__ == "__main__":
    asyncio.run(run_diagnostic()) 