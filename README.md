# Document Management Agent

[English](README.md) | 简体中文

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-Agent-blueviolet)
![LLM](https://img.shields.io/badge/LLM-DeepSeek%20%2B%20InternVL3-orange)
![DB](https://img.shields.io/badge/DB-SQLite-green)
![License](https://img.shields.io/badge/License-MIT-green)

An intelligent document analysis system built on a **Large Language Model (LLM) Agent**. Powered by LangChain, the system integrates **natural-language interaction, structured database querying, and document image recognition** into one place: users ask questions in natural language, and the Agent automatically understands the intent, picks the right tool, and returns real results fetched from the database or the vision model.

---

## Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Workflow](#workflow)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Model Fine-tuning](#model-fine-tuning)
- [Tech Stack](#tech-stack)
- [License](#license)

---

## Features

- 💬 **Natural-language interaction**: chat with the agent directly in natural language
- 📊 **Structured data query**: the Agent translates natural language into SQL and queries real data from SQLite (supports aggregations by date/company/item, such as quantity, amount, YoY, MoM, rankings, etc.)
- 🖼️ **Document image recognition**: upload an order/bill image and the Agent invokes a fine-tuned InternVL3 vision model to extract key fields automatically
- 🧭 **Intelligent tool selection**: the main Agent chooses the appropriate tool based on user intent, keeping business logic out of the frontend
- 💾 **Multi-turn conversation**: the `Conversation` module keeps the message history for context-aware follow-up questions
- 🌐 **Web interface**: a local Flask-based web UI supporting text input, image upload, and Markdown rendering

---

## System Architecture

The system follows a layered, modular design consisting of the **UI layer, backend service layer, conversation-management layer, main-agent layer, tool layer, and data-resource layer**:

- **UI layer (Web)**: Flask + vanilla frontend, handles messages, image uploads, and result rendering
- **Backend service layer**: exposes `/chat` and `/clear` HTTP APIs, manages sessions and uploaded files
- **Conversation-management layer**: the `Conversation` class maintains message history for multi-turn dialogs
- **Main-agent layer**: LangChain `create_agent` + DeepSeek LLM, responsible for intent understanding and tool dispatch
- **Tool layer**: `search_orders` (database query) and `parse_order_image` (image recognition)
- **Data-resource layer**: SQLite database + fine-tuned InternVL3 vision model API (deployed on a remote GPU server)

<!-- TODO: place the architecture diagram at docs/images/architecture.png -->
<p align="center">
  <img src="docs/images/architecture.png" alt="System architecture diagram" width="80%">
  <br>
  <em>Figure 1: System architecture diagram</em>
</p>

---

## Workflow

Users submit questions or images through the web frontend. Requests are forwarded by the Flask backend to the `Conversation` module, and the main Agent analyzes the intent and dispatches to the matching tool:

- **Data queries** → `search_orders` converts natural language to SQL and retrieves information from SQLite
- **Image recognition** → `parse_order_image` base64-encodes the image, calls the InternVL3 model API, and extracts key fields

Once a tool finishes, the result goes back to the main Agent, which synthesizes a natural-language answer. The Flask backend packages it as JSON and returns it to the frontend, closing the loop.

<!-- TODO: place the workflow diagram at docs/images/flowchart.png -->
<p align="center">
  <img src="docs/images/flowchart.png" alt="System workflow diagram" width="80%">
  <br>
  <em>Figure 2: System workflow diagram</em>
</p>

<!-- TODO: place the agent workflow diagram at docs/images/agent_workflow.png -->
<p align="center">
  <img src="docs/images/agent_workflow.png" alt="Main agent workflow diagram" width="80%">
  <br>
  <em>Figure 3: Main agent workflow</em>
</p>

<!-- TODO: place the web UI screenshot at docs/images/web_ui.png -->
<p align="center">
  <img src="docs/images/web_ui.png" alt="Web UI" width="80%">
  <br>
  <em>Figure 4: Web interface</em>
</p>

---

## Project Structure

> This tree reflects the public repository. Local data, configuration, and database files that are not published are omitted; the IDE config directory `.idea` is also excluded.

```
Document_management_agent/
├── agent/                          # Agent core
│   ├── chatbot.py                  # Main agent (LangChain + DeepSeek)
│   └── tools/
│       ├── search.py               # search_orders: natural language → SQL → DB query
│       └── vision.py               # parse_order_image: document image recognition
├── web/                            # Web service
│   ├── app.py                      # Flask backend (/chat, /clear APIs)
│   └── index.html                  # Frontend chat page
├── conversation.py                 # Multi-turn conversation management
├── data/                           # Datasets
│   ├── train/                      # Fine-tuning training images
│   ├── val/                        # Fine-tuning validation images
│   └── output_label.xlsx.txt       # Labeled data sample
├── scripts/                        # Utility scripts
│   ├── gen_sharegpt.py             # Generate ShareGPT-format fine-tuning data
│   ├── excel_to_sqlite.py          # Excel → SQLite import
│   ├── api_test.py                 # Vision model API test
│   └── 2base64.py                  # Image → Base64
├── train_2026-09-01-00-13-03/      # LoRA fine-tuning outputs (round 1)
├── train_2026-09-02-02-49-02/      # LoRA fine-tuning outputs (final)
├── sample.json                     # Sample fine-tuning record
├── README.md                       # Project README (English)
├── README.zh-CN.md                 # Project README (Chinese)
├── requirements.txt                # Python dependencies
└── .gitignore
```

---

## Getting Started

### Requirements

- Python 3.10+
- A reachable **DeepSeek API Key**
- A remotely deployed **InternVL3 vision model API** for image recognition (must be reachable from this machine)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create `agent/.env` and set your DeepSeek API Key:

```bash
DEEPSEEK_API_KEY=sk-xxxxxx
```

> Note: the `INTERNVL_API_URL` in `agent/tools/vision.py` (default `http://localhost:5006/v1/chat/completions`) must point to your deployed InternVL3 model service.

### 3. Prepare the database and data

The database and datasets involve business data and are **not included in this repository**. Prepare your own labeled Excel file and rebuild the SQLite database with:

```bash
python scripts/excel_to_sqlite.py
```

The script cleans the labeled data (strips currency symbols and thousand separators, auto-computes the amount field) and imports it into SQLite.

### 4. Start the web service

```bash
python web/app.py
```

Open <http://127.0.0.1:5000> in your browser to start chatting.

**Example questions:**

- "How many orders were there on a specific date?"
- "Top 5 items by total sales amount"
- Upload an image: "Please extract the information from this bill image."

---

## Model Fine-tuning

Document image recognition is built on the **InternVL3-2B** vision model, fine-tuned with **LLaMA-Factory** using **LoRA (SFT)** to better suit bill/document information extraction. After fine-tuning, the model is wrapped into a URL-accessible API service via LLaMA-Factory for the Agent tools to call.

**Fine-tuning highlights:**

| Config | Value |
| --- | --- |
| Base model | `OpenGVLab/InternVL3-2B-hf` |
| Framework | LLaMA-Factory |
| Method | LoRA (`lora_rank=8`, `lora_alpha=16`) |
| Stage | SFT |
| Dataset | ShareGPT format (training / validation) |
| Learning rate | 5e-5 (cosine schedule) |
| Epochs | 4 |
| Precision | bf16 |

**Evaluation results (final model):**

| Metric | Early run | Final model |
| --- | --- | --- |
| BLEU-4 | 30.78 | **60.06** |
| ROUGE-1 | 48.87 | **73.78** |
| ROUGE-2 | 28.25 | **62.08** |
| ROUGE-L | 42.69 | **70.10** |

All metrics improved significantly after fine-tuning; training loss dropped from 0.263 to 0.155.

<!-- TODO: place the training loss / metrics chart at docs/images/training_loss.png -->
<p align="center">
  <img src="docs/images/training_loss.png" alt="Training loss curve and evaluation metrics" width="80%">
  <br>
  <em>Figure 5: Final model training loss curve and evaluation metrics</em>
</p>

---

## Tech Stack

| Category | Technology |
| --- | --- |
| Main Agent | LangChain (`create_agent`), DeepSeek (`deepseek-chat`) |
| Vision model | InternVL3-2B (LoRA fine-tuned with LLaMA-Factory) |
| Backend | Flask |
| Database | SQLite |
| Data processing | pandas, openpyxl |
| Others | python-dotenv, requests, tqdm |

---

## License

[MIT](LICENSE)
