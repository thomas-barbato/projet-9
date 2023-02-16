# OC Projet 9 - LITReview
## Développez une application Web en utilisant Django
#### Site Web servant à demander et publier des critiques de livres et de documents.

##### Un utilisateur peut :

- Se connecter et s’inscrire – le site ne doit pas être accessible à un utilisateur non connecté
- Consulter un flux contenant les derniers tickets et les commentaires des utilisateurs qu'il suit, classés par ordre chronologique, les plus récents en premier ; 
- Créer de nouveaux tickets pour demander une critique sur un livre/article ;
- Créer des critiques en réponse à des tickets ;
- Créer des critiques qui ne sont pas en réponse à un ticket. Dans le cadre d'un processus en une étape, l'utilisateur créera un ticket puis un commentaire en réponse à son propre ticket
- Voir, modifier et supprimer ses propres tickets et commentaires
- Suivre les autres utilisateurs en entrant leur nom d'utilisateur
- Voir qui il suit et suivre qui il veut
- Cesser de suivre un utilisateur

##### Installation:

1. Installer la derniere version de python, disponible ici :
https://www.python.org/downloads/

2. Importer le projet depuis git:
`git clone https://github.com/thomas-barbato/projet-9.git`

3. Créer un environnement virutel:
`python3 -m venv /path/to/new/virtual/environment`
 Ou `python -m virtualenv venv`

4. Activer l'environnement virtuel:
1.`cd Venv\Scripts\ ; .\activate.bat ;`
2.`cd .. `
3.`cd .. `

5. Installer les dépendances:
`pip install -r requirements.txt`

6. lancer le serveur:
`python manage.py runserver`


