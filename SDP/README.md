# 🌧️ Smart Rainwater Harvesting & Energy Estimation System

## 📌 Overview

This project focuses on building an intelligent system to **estimate rainwater harvesting potential and energy generation** using machine learning models.
It helps in analyzing rainfall data and water quality parameters to make better environmental and resource management decisions.

---

## 🚀 Features

* 📊 Predicts **harvestable rainwater quantity**
* ⚡ Estimates **energy generation potential**
* 💧 Water quality analysis (pH, turbidity, TDS)
* 🖥️ User-friendly interface using PyQt5
* 🤖 Machine Learning models for accurate predictions

---

## 🏗️ Project Structure

```
SDP/
│
├── dataset/                # (Not included - download separately)
├── Models/                 # (Not included - download separately)
│   ├── model_code.ipynb    # Model training notebook
│
├── UI/
│   └── app.py              # Main application
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/Smart-Rainwater-Harvesting-Energy-Estimation-System.git
cd Smart-Rainwater-Harvesting-Energy-Estimation-System
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📂 Dataset & Model Files

⚠️ Due to size limitations, datasets and trained model files (`.pkl`) are **not included in this repository**.

👉 Download them from:

* 📁 Dataset: *((https://drive.google.com/drive/folders/1a6ehZKOH7z2UNxhAF0hOqOTJM02GC4qH?usp=drive_link))*
* 🤖 Models: *((https://drive.google.com/drive/folders/1PjnqPUl5Lh7H2EUOcgMLQe8WveOjjKwc?usp=drive_link))*

### After downloading:

Place them in the following structure:

```
SDP/
├── dataset/
├── Models/
```

---

## ▶️ How to Run

```bash
cd UI
python app.py
```

---

## 🧠 Machine Learning Models Used

* Regression models for rainfall prediction
* Water quality prediction models
* Trained using Scikit-learn

---

## 🛠️ Technologies Used

* Python 🐍
* Pandas & NumPy
* Scikit-learn
* PyQt5 (GUI)

---
