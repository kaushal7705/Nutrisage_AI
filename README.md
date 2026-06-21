# NutriSage AI 🥗

### Intelligent Personalized Health & Nutrition Assistant

NutriSage AI is an AI-powered health and nutrition platform designed to support healthier lifestyle choices through personalized physiological analysis, intelligent meal planning, and evidence-based nutrition guidance.

The platform combines health metric calculations, customized Indian meal recommendations, and an AI Nutrition Coach powered by Retrieval-Augmented Generation (RAG) to deliver reliable and grounded nutritional insights.

---

## 🌍 SDG Alignment

### SDG 3: Good Health & Well-Being

NutriSage AI contributes to the United Nations Sustainable Development Goal 3 by:

* Promoting nutrition awareness
* Supporting preventive healthcare
* Encouraging healthier dietary habits
* Providing evidence-based nutrition guidance
* Making personalized wellness assistance more accessible

---

## 🚀 Key Features

### 📊 Health Assessment

Calculate essential physiological metrics:

* Body Mass Index (BMI)
* Basal Metabolic Rate (BMR)
* Total Daily Energy Expenditure (TDEE)
* Healthy weight recommendations

The system helps users understand their nutritional requirements based on personal characteristics and activity levels.

---

### 🍽️ Personalized Indian Meal Planner

Generate customized meal plans based on:

* Weight Loss
* Weight Maintenance
* Weight Gain

Supports:

* Vegetarian Diets
* Non-Vegetarian Diets

Features:

* Daily calorie targets
* Macronutrient allocation
* Meal-wise recommendations
* Protein estimates
* Indian dietary preferences

---

### 🤖 AI Nutrition Coach

An intelligent conversational assistant that:

* Answers nutrition-related questions
* Uses verified nutrition guidelines
* Provides evidence-grounded responses
* Reduces misinformation by retrieving information from trusted reference documents

Example Questions:

* How can I gain healthy weight?
* What are the best vegetarian protein sources?
* How much protein should I consume daily?
* What is a balanced Indian diet?

---

## 🧠 AI & RAG Pipeline

NutriSage AI uses Retrieval-Augmented Generation (RAG) to provide grounded nutrition guidance.

Workflow:

```text
User Question
      ↓
Document Retrieval
      ↓
ChromaDB Vector Search
      ↓
Relevant Nutrition Context
      ↓
Google Gemini
      ↓
Grounded Response
```

This approach helps reduce hallucinations and ensures answers are based on trusted nutrition resources.

---

## 🛠️ Technology Stack

### Frontend

* Streamlit

### Backend

* Python

### AI & RAG

* Google Gemini API
* LangChain
* ChromaDB
* Sentence Transformers

### Data Processing

* PDF Parsing
* Text Chunking
* Vector Embeddings

### Visualization

* Plotly
* Streamlit Components

---

## 📂 Project Architecture

```text
nutrisage-ai/
├── data/
│   ├── raw_documents/
│   └── vector_db/
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── health_utils.py
│   ├── meal_planner.py
│   ├── rag_engine.py
│   └── app.py
│
├── requirements.txt
├── .env
└── README.md
```

---

## 📖 Knowledge Sources

The AI Nutrition Coach references trusted nutrition resources such as:

* ICMR-NIN Dietary Guidelines
* Nutrition and Wellness Reference PDFs
* Evidence-based dietary recommendations

---

## 🔮 Future Enhancements

* Nutrition progress tracking
* Food image recognition
* Personalized fitness recommendations
* Mobile application support
* Multi-language support
* Advanced analytics dashboard

---

## 👨‍💻 Author

**Kaushal Namade**

B.Tech CSE (Data Science)

IPS Academy, Indore

---

## 📜 Disclaimer

NutriSage AI is intended for educational and wellness guidance purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.
