---

# 🎬 **CineAI: Intelligent Movie Recommendations**

> ⚠️ **Note:** This project is a **work in progress**. Some features are under active development and may change in updates.

CineAI is a modern **AI-powered movie recommendation system** built with **Azure AI Search**, **Azure OpenAI Embeddings**, and **LangChain** for seamless integration.
It delivers **context-aware movie suggestions** through natural language queries ("AI Mood Search") or similarity-based recommendations ("Find Similar Movies").

The front-end is designed in **Streamlit**, featuring a **dark, cinematic, and interactive UI** with custom CSS animations.

---

## ✨ **Features**

### 🧠 AI Mood Search (RAG)

Describe your desired movie *vibe* (e.g.,

> “A dark, gritty neo-noir film set in a rainy city with a cynical detective”)
> and get **highly relevant movie recommendations** based on semantic similarity using **retrieval-augmented generation (RAG)**.

### 🔍 Find Similar Movies

Find movies **most similar** to your favorite titles using **vector distance** between movie embeddings.

### 🧩 Vector Search & Embeddings

* Uses **Azure OpenAI embeddings** to transform movie plots into numerical vectors.
* Performs **efficient similarity search** using **Azure Cosmos DB for NoSQL** with a vector index.

### 🎨 Interactive UI

* Built with **Streamlit** and **custom CSS** for an engaging dark theme.
* Includes **animated “flip cards”** for each movie, revealing synopsis, rating, or full plot summaries interactively.

---

## ⚙️ **Prerequisites**

Before running CineAI, ensure you have:

* **Python 3.8+**
* **Azure Account** with:

  * **Azure OpenAI Service** (for generating embeddings)
  * **Azure Cosmos DB for NoSQL** (for vector search)
* **Movie Dataset** containing:

  * `title`, `genres`, `rating`, `year`, `plot_summary`, `plot_synopsis`, and precomputed **embeddings**
  * Stored in a **Cosmos DB container** configured for vector search

---

## 🚀 **Local Setup and Run**

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Devansh-Patel-2929/Movie-Recommender-using-vector-search.git
cd Movie-Recommender-using-vector-search
```

### 2️⃣ Create and Activate Virtual Environment

```bash
python -m venv venv
# On macOS/Linux
source venv/bin/activate
# On Windows
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root with the following content:

```bash
# .env file
EMBEDDING_MODEL_ENDPOINT="[Your Azure OpenAI Endpoint for Embeddings, e.g., https://your-aoai-instance.openai.azure.com/]"
subscription_key="[Your Azure OpenAI API Key]"
COSMOS_CONNECTION_STRING="[Your Cosmos DB Connection String]"
DATABASE_NAME="[Your Cosmos DB Database Name, e.g., MovieDB]"
CONTAINER_NAME="[Your Cosmos DB Container Name, e.g., MovieData]"
```

> **Note:** The app uses `dotenv` to automatically load environment variables at runtime.

### 5️⃣ Run the Application

```bash
streamlit run ui.py
```

Once started, the app will automatically open in your default web browser.

---

## 🧾 **Project Structure**

```
CineAI/
├── ui.py                   # Streamlit front-end app
├── vector_search.py        # Vector search and embedding logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not to be committed)
├── README.md               # Project documentation
```

---

## 💡 **Tech Stack**

* **Azure OpenAI Service** – for embeddings generation
* **Azure Cosmos DB (NoSQL)** – for vector search
* **LangChain** – for embedding & retrieval orchestration
* **Streamlit** – for front-end UI
* **Python** – for backend and logic

---
<img width="2272" height="1157" alt="Screenshot 2025-10-05 211827" src="https://github.com/user-attachments/assets/b609c12a-4117-4293-87a1-9cf2f5ddb5f4" />
<img width="2293" height="1193" alt="Screenshot 2025-10-05 211813" src="https://github.com/user-attachments/assets/453a4176-ad04-4f4d-9df9-ec0d22b70213" />

## 🧰 **Requirements File**

Include the following (exact versions recommended for reproducibility):

```txt
streamlit==1.37.0
python-dotenv==1.0.1
langchain==0.2.14
langchain-openai==0.1.10
azure-cosmos==4.5.1
azure-ai-formrecognizer==3.3.0
openai==1.35.14
pandas==2.2.2
numpy==1.26.4
```

> **Note:** These versions were used during project creation.
> You may upgrade to the latest releases, but version compatibility is not guaranteed.

---
