# Création du questionnaire pour évaluer l'aversion au risque d'un investisseur

def evaluate_risk_aversion():
    questions = [
        "1. Quel est votre âge ?\n   a) Moins de 30 ans\n   b) 30-50 ans\n   c) Plus de 50 ans",
        "2. Quelle est votre expérience en matière d'investissement ?\n   a) Débutant\n   b) Intermédiaire\n   c) Expérimenté",
        "3. Quel est votre horizon d'investissement ?\n   a) Court terme (moins de 5 ans)\n   b) Moyen terme (5-10 ans)\n   c) Long terme (plus de 10 ans)",
        "4. Quel pourcentage de votre investissement êtes-vous prêt à perdre pour obtenir de meilleurs rendements ?\n   a) Moins de 10%\n   b) 10-30%\n   c) Plus de 30%",
        "5. Comment réagiriez-vous si vos investissements perdaient 10% de leur valeur en un court laps de temps ?\n   a) Acheter plus\n   b) Ne rien changer\n   c) Vendre tous les investissements"
    ]

    scores = {
        'a': 1,
        'b': 2,
        'c': 3
    }

    total_score = 0

    # Poids pour chaque question
    weights = {
        1: 0.5,  # Poids pour la question 1
        2: 1,  # Poids pour la question 2
        3: 1,  # Poids pour la question 3
        4: 1.5,  # Poids pour la question 4
        5: 2  # Poids pour la question 5
    }

    total_score = 0
    last_answer_critical = False  # Indicateur si la dernière réponse est critique

    for index, question in enumerate(questions,
                                     start=1):  # Commence à 1 pour correspondre aux clés du dictionnaire des poids
        print(question)
        answer = input("Votre choix (a, b, ou c): ").lower()
        if index == 5 and answer == 'c':  # Si la réponse à la dernière question est 'c'
            last_answer_critical = True  # Active l'indicateur
            break  # Sort de la boucle car les autres réponses ne comptent plus
        total_score += scores.get(answer, 0) * weights[index]  # Accumule le score pondéré

    if last_answer_critical:
        return 0  # Retourne 0 si la dernière réponse est 'c'
    else:
        print(total_score)
        return total_score  # Retourne le score total sinon


def suggest_portfolio(score):
    if score <=6:
        return "Portefeuille à faible risque (par ex. obligations, fonds monétaires)"
    elif 6 <= score <= 10:
        return "Portefeuille à risque modéré (par ex. mixte d'obligations et d'actions)"
    elif score > 10:
        return "Portefeuille à haut risque (par ex. actions, fonds spéculatifs)"