# 📝 TODO Console App (Phase I)

A simple, interactive command-line **TODO** application built with Python. This project is part of **Hackathon Phase I** and demonstrates clean architecture, service-based design, and unit testing with pytest.

---

## 📖 Introduction

This console-based TODO application allows users to manage tasks directly from the terminal. Users can:

- Add tasks
- View all tasks
- Update task titles
- Delete tasks
- Toggle task completion status

The application is designed with separation of concerns, keeping the CLI logic, business logic, and data models cleanly separated.

---

## 📁 Project Structure

```csharp
HACKTHON-II-PHASE-I/
├── src/
│   ├── main.py              # CLI entry point
│   ├── todo_service.py      # Business logic for task management
│   ├── models.py            # Task data models
│   ├── pyproject.toml       # Project metadata & dependencies
│   ├── README.md
│   └── uv.lock
├── tests/
│   └── unit/
│       └── test_todo_service.py
├── specs/
│   └── 001-phase-i-console-app/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── data-model.md
│       └── quickstart.md
├── pytest.ini
├── .gitignore
├── CLAUDE.md
└── .python-version
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hackathon-II-phase-I/src
```

### 2. Set Python Version

Ensure you’re using the correct Python version:

```bash
python --version
```

(Version is defined in `.python-version`)

### 3. Create & Activate Virtual Environment (Optional)

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

_or using `uv` (if applicable):_

```bash
uv sync
```

---

## ▶️ Usage

Run the application from the `src` directory:

```bash
uv venv
.venv\Scripts\activate
uv run main.py
```

**Menu Options:**

```markdown
1. Add Task
2. View Task List
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Exit
```

---

## 📄 License

This project is provided for **educational and hackathon purposes**.
License details can be added as needed.
