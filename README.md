# NutriSage AI 🥗
### Intelligent Personalized Health & Nutrition Assistant

NutriSage AI is a premium, modular Web Application designed for personalized wellness. It integrates mathematical physiological calculators, a custom calorie-calibrated Indian meal planner, and an intelligent AI Nutrition Coach that references verified health guidelines to provide grounded, evidence-based answers.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python**: Version 3.9, 3.10, or 3.11 is recommended.
- **Google AI Studio API Key**: Required for RAG synthesis.

### 2. Environment Setup

Clone or navigate to the project directory and create a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (Command Prompt/PowerShell):
.\.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Configuration

1. Copy the `.env.template` file to `.env`:
   ```bash
   cp .env.template .env
   ```
2. Open `.env` and enter your Google AI Studio Gemini API key:
   ```env
   GEMINI_API_KEY=yourActualKeyHere...
   ```
   *Note: If the key is not set in `.env`, you can also input it directly in the app's sidebar during execution.*

### 4. Running the Dashboard

Launch the Streamlit app:

```bash
streamlit run src/app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🛠️ Project Architecture

```text
nutrisage-ai/
├── data/
│   ├── raw_documents/        # Upload your nutrition PDFs here
│   └── vector_db/            # Local SQLite/ChromaDB persistence directory
├── src/
│   ├── __init__.py
│   ├── config.py             # App-wide paths, model specifications, & environmental variables
│   ├── health_utils.py       # Mathematical calculators (BMI, BMR, TDEE)
│   ├── meal_planner.py       # Macro breakdowns and custom meal templates
│   ├── rag_engine.py         # PDF parsing, ChromaDB, and Google AI Studio Gemini QA chains
│   └── app.py                # Streamlit UI design, graphs, and chat views
```

---

## 📖 Features

1. **Health Assessment**: Inputs your age, gender, height, weight, and activity level to compute:
   - **BMI** (Body Mass Index) with health category classifications.
   - **BMR** (Basal Metabolic Rate) using the Mifflin-St Jeor equation.
   - **TDEE** (Total Daily Energy Expenditure) to define your active daily caloric requirements.
2. **Meal Planner**: Adjusts TDEE daily requirements for Weight Loss, Maintenance, or Weight Gain, generates carbohydrate, protein, and fat allocations, and outputs daily food suggestions (Breakfast, Lunch, Snacks, Dinner) for Vegetarian or Non-Vegetarian choices.
3. **AI Nutrition Coach**:
   - Analyzes guidelines in real-time to answer queries.
   - Refers to verified local guides (like the ICMR-NIN 2024 Dietary Guidelines) to synthesize grounded, evidence-based responses.
   - Provides verified citations with every answer to ensure safety and precision.
