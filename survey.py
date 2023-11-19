# Création du questionnaire pour évaluer l'aversion au risque d'un investisseur

def evaluate_risk_aversion():
    questions = [
        "1. Quel est votre âge ?\n   a) Moins de 30 ans\n   b) 30-50 ans\n   c) Plus de 50 ans",
        "2. Quelle est votre expérience en matière d'investissement ?\n   a) Débutant\n   b) Intermédiaire\n   c) Expérimenté",
        "3. Quel est votre horizon d'investissement ?\n   a) Court terme (moins de 5 ans)\n   b) Moyen terme (5-10 ans)\n   c) Long terme (plus de 10 ans)",
        "4. Quel pourcentage de votre investissement êtes-vous prêt à perdre pour obtenir de meilleurs rendements ?\n   a) Moins de 10%\n   b) 10-30%\n   c) Plus de 30%",
        "5. Comment réagiriez-vous si vos investissements perdaient 10% de leur valeur en un court laps de temps ?\n   a) Acheter plus\n   b) Ne rien changer\n   c) Vendre tous les investissements"
        "6. Envisagez-vous des investissements alternatifs (comme les cryptomonnaies, l'immobilier, les matières premières, etc.) ?\n a) Non, je préfère les investissements traditionnels\n b) Oui, mais seulement une petite partie de mon portefeuille\n c) Oui, je suis ouvert à une proportion significative dans des investissements alternatifs."
        "7. Si un investissement ne performe pas comme prévu après un an, quelle serait votre action ?\n a) Vendre immédiatement pour limiter les pertes.\n b) Réévaluer la situation, mais probablement maintenir l'investissement.\n c) Garder l'investissement car je crois aux bénéfices à long terme."
        "8. Lequel des énoncés suivants décrit le mieux vos connaissances en matière de placement?\n a) Mes connaissances des placements et des marchés financiers sont limitées. Vous informer sur les questions financières ne fait pas partie de vos priorités. Par exemple, vous ne pourriez pas expliquer la différence entre des actions, des obligations et des fonds communs de placement.\n b)Je possède certaines connaissances des placements et des marchés financiers. Vous pourriez expliquer la différence entre les placements énumérés plus haut.\n Je possède de solides connaissances des placements.\n En plus de pouvoir différencier les placements émunérés plus haut, vous connaissez les marchés boursiers, les frais des placements et les principes de diversification. Vous connaissez très bien les risques des différents placements."
        "9. Quel est votre objectif principal en investissant ?\n a) Préserver le capital et maintenir une croissance stable.\nb) Équilibrer la croissance et la sécurité, avec une approche modérée.\nc) Chercher une croissance élevée, même si cela signifie un risque plus grand."
        "10.Face à une nouvelle tendance d'investissement très populaire, comme une bulle spéculative, quelle serait votre approche ?\na) Éviter complètement, trop risqué à mon goût.\nb) Investir une petite somme pour ne pas rater une opportunité potentielle.\nc) Investir de manière significative, en espérant réaliser un gros profit."
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
        5: 2,  # Poids pour la question 5
        6: 2,
        7: 1,
        8: 2,
        9: 1,
        10: 1,

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
    if score <5:
        return "Très prudent"
    elif 5 <= score < 10:
        return "Prudent"
    elif 10 <= score < 15:
        return "Equilibré"
    elif 15 <= score < 20:
        return "Croissance"
    elif score >= 20:
        return "Très dynamique"