<p align="center">
  <img src="text_logo.svg"/>
</p>

<h1 align="center"></h1>

### Designed for Dedalus Dathathon Castilla-La Mancha

The challenge of this project lies on indentifying cohorts of cronic patients based on a conversational agent.

To use out project:
1. Clone the repository
```bash
git clone https://github.com/kante420/cohort-agent.git
```
 3. Access to the repository
```bash
cd cohort-agent
```
5. Install the requirements
```bash
pip install -r requirements.txt
```
7. Create the database
```bash
python db.setup
python test_sql_node.py
```
9. Execute the code
```bash
streamlit run app.py
```

The app will run by default as localhost on port _8501_.
