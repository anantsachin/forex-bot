
import sys
import os

# Add backend to path
sys.path.append(os.getcwd() + "/backend")

try:
    from bot.paper_trader import paper_trader
    print("Import successful!")
    print(f"Type of paper_trader: {type(paper_trader)}")
except Exception as e:
    print(f"Import failed: {e}")
