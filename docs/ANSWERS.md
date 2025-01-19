# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

### 1. Environnement virtuel

Pour valider le fonctionnement du pipeline de données, il suffit de lancer le workflow 'Pipeline ETL' dans la section Actions du repo GitHub. On peut suivre les étapes du pipeline grâce aux logs. Le pipeline génère les données sortantes en format csv, les compresse (zip), puis crée un artéfact.

Au niveau du développement local, on peut utiliser un venv pour compartementaliser les dépendances du projet, puis exécuter les fichiers ETL un à un pour valider leur fonctionnement.

### 2.a Développement du pipeline

J'ai choisi de développer un pipeline de type **ETL** (Extraction, Transformation, Chargement). Chaque étape du pipeline est exécutée dans un fichier distinct afin de garantir une séparation des responsabilités et d'avoir un contrôle plus granulaire sur l'exécution des étapes. Voici un résumé des responsabilités des trois fichiers principaux :

#### 1. `extract.py`

Ce fichier est responsable de l'extraction des données depuis l'API (FastAPI). Le processus suivant est réalisé :
- Appel à l'API pour récupérer les données.
- Conversion des données extraites en DataFrames via **pandas**.
- Sérialisation des DataFrames en utilisant **pickle**, ce qui permet de passer les données à l'étape suivante.

#### 2. `transform.py`

Le fichier **`transform.py`** s'occupe de la transformation et du nettoyage des données. Voici les étapes de transformation :

1. **Standardisation des genres** :  
   - Conversion des noms de genres en minuscules.
   - Suppression des espaces superflus.

2. **Nettoyage des durées** :  
   - Conversion des durées des morceaux du format `MM:SS` en secondes.

3. **Gestion des données manquantes** :
   - Remplissage des valeurs manquantes pour le genre et les genres préférés des utilisateurs.
   - Remplissage des valeurs manquantes pour l'artiste et les genres des morceaux.
   - Suppression des lignes contenant des durées ou des timestamps manquants.

4. **Normalisation des données de texte** :  
   - Nettoyage des champs texte (par exemple, `name`, `artist`) en supprimant les caractères non alphanumériques.

5. **Transformation des données d'historique d'écoute** :
   - Conversion des dates en format `datetime`, avec gestion des erreurs.
   - Nettoyage du champ `items` pour garantir qu'il soit une liste.

6. **Normalisation de la durée des morceaux** :  
   - Mise à l'échelle des durées des morceaux entre 0 et 1 si nécessaire.

Une fois les données nettoyées, elles sont sérialisées dans un autre fichier **pickle** pour être utilisées à l'étape suivante.

#### 3. `load.py`

Ce fichier prend le **pickle** des données nettoyées et effectue l'opération suivante :
- Conversion des données en format **CSV**.
- Sauvegarde du fichier CSV dans la racine du projet.

#### Remarque sur l'utilisation de Pickle

- **Pourquoi Pickle** :  
   J'ai choisi d'utiliser le format **pickle** pour stocker les données à chaque étape du pipeline, car cela permet une mise en œuvre rapide et simple. Cette approche est adaptée aux contraintes de temps du test.
  
- **Alternatives pour un environnement de production** :
   - **Parquet** : Idéal pour le traitement de grandes quantités de données, car il est optimisé pour des performances élevées.
   - **Bases de données relationnelles** : Utiliser des bases de données comme **PostgreSQL** ou **MySQL** serait plus robuste et scalable pour un environnement de production.

Ces solutions offrent une meilleure gestion à long terme des données et une meilleure scalabilité.



### 2.b Orchestration du pipeline

Ce pipeline ETL utilise GitHub Actions pour coordonner l'extraction, la transformation et le chargement des données. Les mécanismes clés d'orchestration incluent :

- Déclencheurs : Le pipeline s'exécute automatiquement lors de push sur la branche principale, sur demande via workflow_dispatch, ou quotidiennement à minuit grâce à une tâche CRON.
- Dépendances : Chaque étape dépend de la réussite de l'étape précédente, garantissant l'intégrité du processus via la directive needs.
- Artefacts : Les données intermédiaires (pickles) sont sauvegardées et récupérées entre les étapes grâce à upload-artifact et download-artifact.
- Tolérance aux échecs : Des boucles de réessai avec temporisation sont implémentées dans chaque étape pour assurer la résilience face aux erreurs temporaires.
- Notifications : Une étape finale exécute une notification conditionnelle, quelle que soit la réussite ou l'échec du pipeline (C'est un echo, mais dans le cadre d'une application réelle, on enverrait une notification vers Slack ou une alerte courriel).

J'ai choisi GitHub Actions pour sa simplicité d'utilisation et son intégration native à la gestion de code, ce qui en fait une solution idéale pour ce projet. Cependant, dans le cadre d'un projet en production, des outils comme Apache Airflow ou Prefect seraient plus adaptés. Ils offrent des fonctionnalités avancées telles que la gestion complexe des dépendances, des planifications personnalisées, un suivi en temps réel des exécutions, et une extensibilité accrue.

Pour émuler un pipeline ETL fonctionnel, j'ai intégré le lancement de l'application FastAPI directement dans l'étape d'extraction. Cela permet de valider le pipeline sans nécessiter l'hébergement préalable de l'application.

### 3. Description des tests:

Les tests unitaires sont exécutés par l'entremise du UI de VS Code (Testing tab).

1. test_extract.py : 

- test_extract_tracks, test_extract_users, test_extract_listen_history : Vérifient que les fonctions d'extraction retournent un DataFrame valide, non vide, et contenant les colonnes attendues en simulant les réponses de l'API via fetch_paginated_data.
- test_fetch_paginated_data_error_handling : Valide la gestion des erreurs dans le cas d'une exception HTTP, en s'assurant qu'un DataFrame vide est retourné.

2. test_transform.py :

- test_standardize_genres : Vérifie que les genres des morceaux sont standardisés en minuscule et sans espaces inutiles.
- test_clean_duration : Valide la conversion des durées en secondes, en ajoutant une nouvelle colonne duration_seconds avec les valeurs correctes.
- test_handle_missing_data_user : Vérifie que les valeurs manquantes dans les colonnes gender et favorite_genres des utilisateurs sont remplacées par des valeurs par défaut.
- test_handle_missing_data_track : Teste que les morceaux avec des durées manquantes sont supprimés, tout en gérant les colonnes supplémentaires comme artist.
- test_handle_missing_data_listen_history : S’assure que les entrées de l’historique d’écoute avec des timestamps manquants sont supprimées.

3. test_load.py :
   
- test_save_data_as_csv : Vérifie que la fonction save_data_as_csv crée le répertoire spécifié pour stocker les fichiers CSV en utilisant os.makedirs.
et qu'elle sauvegarde chaque DataFrame dans un fichier CSV avec le bon nom de fichier.
- test_save_data_as_csv_invalid_dataframe : Valide que la fonction save_data_as_csv gère les cas où des objets non-DataFrame sont présents dans les données et qu'elle sauvegarde uniquement les DataFrames valides sans lancer d’exception.

Dans le cadre du développement d'un projet similaire en production, plusieurs tests seraient cruciaux pour garantir la robustesse du système. Par exemple :

- Tests d'intégration : Assurer que les différentes étapes du pipeline (extraction, transformation, chargement) s'enchaînent correctement avec des données réelles provenant de l'API. Cela inclurait la validation de la communication entre le pipeline ETL et la base de données PostgreSQL.

- Tests de charge : Simuler des volumes élevés de données, par exemple en récupérant des millions d'historiques d'écoute, pour observer la manière dont le pipeline gère l'augmentation du volume sans impact sur la performance ou la stabilité.

- Tests de performance : Mesurer les temps d'exécution du pipeline ETL et du calcul des recommandations pour s'assurer que les traitements sont effectués dans un délai acceptable, même avec des données volumineuses.

- Tests de sécurité : Tester l'API FastAPI pour des vulnérabilités comme les injections SQL ou XSS, garantir que les données sensibles (comme les informations utilisateur) sont protégées, et que le pipeline est sécurisé contre les accès non autorisés.

- Tests de résilience : Tester la capacité du système à se remettre d'une défaillance partielle, comme une API qui tombe en panne temporairement ou une interruption dans la base de données, en s'assurant que le pipeline redémarre correctement ou gère les erreurs de manière transparente.

Bien que ces tests dépassent la portée du test technique demandé, j'y ai réfléchi pour m'assurer que le pipeline serait adapté à un environnement de production, où la fiabilité et la scalabilité sont primordiales.

### Étape 4

#### Schéma de la base de données pour les données provenant des trois sources :

Table tracks
- id (PK, INTEGER) : Identifiant unique du morceau.
- name (VARCHAR) : Nom du morceau.
- genres (VARCHAR) : Genres musicaux.
- duration_seconds (INTEGER) : Durée en secondes.
- artist (VARCHAR, facultatif) : Nom de l'artiste.

Table users
- id (PK, INTEGER) : Identifiant unique de l'utilisateur.
- name (VARCHAR) : Nom de l'utilisateur.
- gender (VARCHAR) : Genre de l'utilisateur (par défaut "Unknown Gender").
- favorite_genres (VARCHAR, facultatif) : Genres favoris.

Table listen_history
- id (PK, BIGINT) : Identifiant unique de l'enregistrement.
- user_id (FK vers users.id, INTEGER) : Identifiant de l'utilisateur.
- track_id (FK vers tracks.id, INTEGER) : Identifiant du morceau.
- timestamp (TIMESTAMP) : Heure d'écoute.
- created_at (TIMESTAMP) : Date de création.
- updated_at (TIMESTAMP) : Date de mise à jour.

#### Considérations par rapport au format actuel des données :

- Track History : Si la colonne track_ids est actuellement une liste, il faudra la "normaliser" pour qu'il y ait une ligne par track_id (comme expliqué précédemment). 
- Genres : Les genres peuvent être stockés sous forme de texte ou, pour une extensibilité future, dans des colonnes JSONB dans PostgreSQL si vous souhaitez gérer des genres multiples ou semi-structurés.

#### Système de BD recommandé : PostgreSQL
- Relationnel : Parfait pour gérer les relations entre tracks, users et listen_history.
- JSONB : Stockage flexible des genres et autres métadonnées.
- Performances : Bonnes performances avec de grandes quantités de données.
- Facilité d'intégration : Compatible avec SQLAlchemy et Django ORM pour une gestion fluide.

### Étape 5

Surveillance du pipeline de données :

Pour garantir la fiabilité du pipeline de données, j'utiliserai Apache Airflow pour l'orchestration et Prometheus/Grafana pour le suivi en temps réel.

Métriques clés :

- Taux de succès des tâches : Permet de détecter rapidement les échecs.
- Temps d'exécution : Identifie les goulets d'étranglement.
- Volume de données traitées : Assure une ingestion correcte.
- Erreurs et anomalies : Surveille les données mal formatées.
- Ressources système : Vérifie l'utilisation CPU/mémoire pour éviter les surcharges.

Des alertes automatisées (via Slack ou email) seront mises en place pour notifier les anomalies.

### Étape 6

Pour le système de recommandation, je propose une approche hybride combinant le filtrage collaboratif (par exemple, SVD) et le filtrage basé sur le contenu. Ce choix permet de générer des recommandations personnalisées tout en tenant compte des préférences utilisateurs et des caractéristiques des morceaux.
Les calculs seront automatisés avec Airflow, exécutés quotidiennement pour intégrer les nouvelles données. Les résultats seront ensuite stockés dans une base SQL pour une récupération rapide.

Pour automatiser le calcul des recommandations, je mettrais en place les étapes suivantes :

1. Pipeline ETL (Airflow, scripts Python) :
- Récupération quotidienne des nouvelles données utilisateurs et historiques.
- Transformation et préparation des données.
  
2. Calcul des recommandations (Python, Airflow, MLflow) :
- Utilisation de modèles hybrides (filtrage collaboratif, basé sur le contenu) pour générer les recommandations (ex. combinaison avec un modèle de regression).
- Gestion du cycle de vie des modèles via MLflow
  
3. Stockage des recommandations (Airflow, PostGreSQL) :
- Sauvegarde dans une base PostGreSQL pour un accès rapide et structuré.

### Étape 7

4. Réentrainement Automatique :

- Surveillance continue des performances des modèles via des métriques clés telles que RMSE, précision, rappel, et F1-score.
- Réentrainement automatisé lorsque les performances chutent sous un seuil défini, avec MLflow pour la gestion des versions de modèles et le suivi des expériences.
- Airflow orchestre le pipeline de réentrainement selon un calendrier ou déclencheur basé sur les métriques de performance.

5. Monitoring et Alertes :
- Prometheus et Grafana sont utilisés pour surveiller les métriques critiques : temps d'exécution des recommandations, qualité des recommandations (via precision, rappel, F1-score), taux de clics (CTR) et taux de conversion pour mesurer l'efficacité du modèle, latence des recommandations et temps de réponse.
- Des alertes automatiques sont déclenchées en cas de baisse significative des performances ou d'anomalies dans les données (par exemple, perte de diversité ou couverture des recommandations), permettant une réaction rapide via Slack, email, ou autres moyens.

Cette approche garantit que le système de recommandation reste performant, réactif aux évolutions des données utilisateurs, et facilement maintenable avec un suivi continu des métriques clés.