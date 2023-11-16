# Création du questionnaire pour évaluer l'aversion au risque d'un investisseur

def evaluate_risk_aversion():
    questions = [
        "1. Quel est votre âge ?\n   a) Moins de 30 ans\n   b) 30-50 ans\n   c) Plus de 50 ans",
        "2. Quelle est votre expérience en matière d'investissement ?\n   a) Débutant\n   b) Intermédiaire\n   c) Expérimenté",
        "3. Quel est votre horizon d'investissement ?\n   a) Court terme (moins de 5 ans)\n   b) Moyen terme (5-10 ans)\n   c) Long terme (plus de 10 ans)",
        "4. Quel pourcentage de votre investissement êtes-vous prêt à perdre pour obtenir de meilleurs rendements ?\n   a) Moins de 10%\n   b) 10-30%\n   c) Plus de 30%",
        "5. Comment réagiriez-vous si vos investissements perdaient 10% de leur valeur en un court laps de temps ?\n   a) Vendre tous les investissements\n   b) Ne rien changer\n   c) Acheter plus"
    ]

    scores = {
        'a': 1,
        'b': 2,
        'c': 3
    }

    total_score = 0

    for question in questions:
        print(question)
        answer = input("Votre choix (a, b, ou c): ").lower()
        total_score += scores.get(answer, 0)

    return total_score

def suggest_portfolio(score):
    if score <= 5:
        return "Portefeuille à faible risque (par ex. obligations, fonds monétaires)"
    elif 6 <= score <= 10:
        return "Portefeuille à risque modéré (par ex. mixte d'obligations et d'actions)"
    elif score > 10:
        return "Portefeuille à haut risque (par ex. actions, fonds spéculatifs)"