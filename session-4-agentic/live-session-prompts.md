In repository terminal:

uv run python 01_minimal_factory.py --backend opencode "Summarize this project"

uv run python 02_factory_catalog.py analyzer --backend opencode "Analyze backend_runner.py"

uv run python 02_factory_catalog.py planner --backend opencode "Plan logging for backend_runner.py"

uv run python 02_factory_catalog.py fixer --backend opencode "Implement the plan and add logging to backend_runner.py"

Open another terminal window and run:
opencode
- you can change the model by typing /models to chat window and selecting the model you prefer
- you can ask any questions in there

uv run python 03_resumable_factory.py start --backend opencode "Find logging gaps in backend_runner.py"

uv run python 03_resumable_factory.py resume --backend opencode "Make fixes"