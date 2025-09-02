# Automatiseur Métier Intelligent

## Description
**Automatiseur Métier Intelligent** est un projet de stage visant à enrichir une plateforme **Low-Code/No-Code (LCNC)** avec des nœuds intelligents (actions et triggers).  
Il permet d’automatiser des processus métier en intégrant :  

- Des triggers basés sur des événements ( réception d’email)  
- Des capacités d’IA : OCR, NLP, analyse de sentiments, résumé automatique  
- Des intégrations API pour des services externes ( Calendar)

---
## Exemple de workflow
1. Un email arrive → déclencheur `EmailReceivedTrigger`
2. Extraction du texte avec OCR (si pièce jointe)
3. Analyse NLP pour sentiment
4. Analyse NLP pour résumé  
5.  créer un événement Calendar


## Technologies utilisées
- **Backend :** Python (FastAPI)  
- **Frontend :** React + React Flow  
- **Données :** JSON / SQLite  
- **IA & NLP :** Transformers, OCR libraries  
- **Versioning :** Git + GitHub

---

## Installation et configuration

### 1️⃣ Cloner le dépôt
```bash
git clone https://github.com/sarra-rouahi/Automatiseur-M-tier-Intelligent.git
cd Automatiseur-M-tier-Intelligent
```

### 2️⃣ Créer un environnement virtuel
```bash
python -m venv myenv
myenv\Scripts\activate    # Windows
```

### 3️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurer les secrets
- Créer un fichier `.env` pour stocker les tokens et clés API.  
- ⚠ Ne jamais les committer dans le dépôt.

### 5️⃣ Lancer le backend
```bash
cd backend
uvicorn main:app --reload
```

### 6️⃣ Lancer le frontend
```bash
cd frontend
npm install
npm start
```

---

## Contributions
- Créer une branche pour chaque nouvelle fonctionnalité  
- Soumettre une Pull Request pour valider les changements  
- Respecter la structure existante des nœuds et du projet

---

## Licence
Projet interne / Stage – tous droits réservés

