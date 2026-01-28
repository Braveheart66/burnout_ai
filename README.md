🌙 AI-Powered Organizational Wellbeing Monitor
A full-stack AI application designed to detect early signs of employee burnout while strictly preserving individual privacy. This dual-application system allows employees to track their personal wellbeing and gives managers aggregated, anonymized insights into organizational health.
(Add your image_87714d.png or dashboard screenshot here)

🚀 Key Features
1. 🔒 Privacy-First Architecture
Zero Surveillance: Individual data is hashed and encrypted.
Aggregation Layer: The dashboard only displays data if a minimum threshold of users (configurable) participate, preventing identification of specific individuals.
Separation of Concerns: The "Employee App" and "Manager Dashboard" are completely distinct interfaces.

2. 🧠 AI Risk Prediction
Uses a Random Forest Classifier (Scikit-Learn) to predict burnout risk (Low/Medium/High).
Analyzes factors like sleep quality, cognitive load, engagement, and sentiment.
Fixes "flat scoring" issues by dynamically calculating confidence scores based on class probabilities.

3. 📊 Interactive Analytics
Employee View: Daily trend analysis, personalized recommendations, and immediate risk feedback.
Manager View: Department-level heatmaps, stress trends over time, and participation metrics.
🛠️ Tech Stack
Frontend: Streamlit (Custom CSS Dark Mode)
Database: PostgreSQL (Hosted on Supabase)
Machine Learning: Scikit-Learn, Joblib
Visualization: Plotly Express & Graph Objects
Language: Python 3.11

📂 Project Structure
burnout_ai/
├── src/
│   ├── database.py       # PostgreSQL connection & aggregation logic
│   ├── predictor.py      # ML Model inference logic
│   └── utils.py          # Helper functions (engagement scores, etc.)
├── models/               # Pre-trained .pkl files (RF model, Scaler, Encoder)
├── app_daily.py          # 📱 THE EMPLOYEE APP (Entry point 1)
├── app_dashboard.py      # 📊 THE MANAGER DASHBOARD (Entry point 2)
├── requirements.txt      # Dependencies
└── README.md             # Documentation

⚙️ Local Setup & Installation
1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/burnout-ai-app.git
cd burnout-ai-app

2. Create Virtual Environment
# Windows
python -m venv venv
.\venv\Scripts\activate
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure Secrets
Create a folder .streamlit in the root directory and add a file secrets.toml:

# .streamlit/secrets.toml
# Use the Transaction Pooler (Port 6543) for Streamlit Cloud compatibility
db_url = "postgresql://postgres.project:[PASSWORD]@aws-0-region.pooler.supabase.co:6543/postgres"

5. Run Locally
To run the Employee App:
streamlit run app_daily.py
To run the Manager Dashboard:

streamlit run app_dashboard.py

☁️ Deployment (Streamlit Cloud)
This project is deployed as two separate apps connected to the same repository and database.

Push to GitHub: Ensure your requirements.txt is up to date.

Deploy Employee App:

Create new app on Streamlit Cloud.

Set Main file path: app_daily.py.

Advanced Settings: Paste your db_url into the Secrets box.

Python Version: Select 3.11.

Deploy Dashboard:

Create a second app on Streamlit Cloud.

Set Main file path: app_dashboard.py.

Advanced Settings: Add the same Secrets again.

Python Version: Select 3.11.


🛡️ Database Schema
The system uses a robust PostgreSQL schema with three main tables:

individual_checkouts: Stores raw, encrypted inputs (User ID is hashed).

department_aggregates: Stores pre-calculated averages per department (No PII).

organization_aggregates: Stores global metrics for high-level tracking.

Note: The system currently uses a Supabase Transaction Pooler (Port 6543) to resolve IPv6 connection issues common in serverless environments.


🤝 Contributing
Fork the repository.

Create a feature branch (git checkout -b feature/NewFeature).

Commit your changes.

Push to the branch and open a Pull Request.

License
MIT
