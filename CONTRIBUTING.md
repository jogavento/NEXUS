# Contributing

1. Open an issue for bugs or proposed features.
2. Fork the repository and create a focused branch.
3. Install with `python -m pip install -e ".[dev]"`.
4. Run `pytest` and `ruff check .`.
5. Keep Discord command handlers thin; put gameplay rules in services and SQL in repositories.
6. Never commit tokens, `.env`, server member exports, or production databases.

Pull requests should include a summary, testing notes, and any configuration or migration impact.
