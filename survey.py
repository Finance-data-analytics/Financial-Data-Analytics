questions = [
    "1. What is your age?\n   a) Under 30\n   b) 30-50 years\n   c) Over 50 years",
    "2. What is your investment experience?\n   a) Beginner\n   b) Intermediate\n   c) Experienced",
    "3. What is your investment horizon?\n   a) Short term (less than 5 years)\n   b) Medium term (5-10 years)\n   c) Long term (more than 10 years)",
    "4. What percentage of your investment are you willing to lose to obtain better returns?\n   a) Less than 10%\n   b) 10-30%\n   c) More than 30%",
    "5. How would you react if your investments lost 10% of their value in a short period of time?\n   a) Buy more\n   b) Make no changes\n   c) Sell all investments",
    "6. Are you considering alternative investments (like cryptocurrencies, real estate, commodities, etc.)?\n   a) No, I prefer traditional investments\n   b) Yes, but only a small portion of my portfolio\n   c) Yes, I am open to a significant proportion in alternative investments.",
    "7. If an investment does not perform as expected after one year, what would be your action?\n   a) Sell immediately to limit losses\n   b) Reevaluate the situation, but probably maintain the investment\n   c) Keep the investment because I believe in long-term benefits",
    "8. Which of the following statements best describes your knowledge of investing?\n   a) My knowledge of investments and financial markets is limited. Informing yourself about financial matters is not one of your priorities. For example, you could not explain the difference between stocks, bonds, and mutual funds.\n   b) I have some knowledge of investments and financial markets. You could explain the difference between the investments listed above.\n   c) I have solid knowledge of investments. In addition to being able to differentiate the investments listed above, you know the stock markets, investment fees, and principles of diversification. You are very familiar with the risks of different investments.",
    "9. What is your main objective in investing?\n   a) Preserve capital and maintain stable growth\n   b) Balance growth and security, with a moderate approach\n   c) Seek high growth, even if it means greater risk.",
    "10. Faced with a very popular new investment trend, like a speculative bubble, what would be your approach?\n   a) Avoid completely, too risky for my taste\n   b) Invest a small amount not to miss a potential opportunity\n   c) Invest significantly, hoping to make a big profit.",
    "11. Do you wish to include cryptocurrencies in your portfolio?\n   a) Yes\n   b) No"
]

scores = {
    'a': 1,
    'b': 2,
    'c': 3
}

weights = {
    1: 0.5,
    2: 1,
    3: 1,
    4: 1.5,
    5: 2,
    6: 2,
    7: 1,
    8: 2,
    9: 1,
    10: 1,
    11: 0  # No weight for question 11, as it sets score to 0 if answered 'b'
}

def evaluate_risk_aversion():
    total_score = 0

    for index, question in enumerate(questions, start=1):
        print(question)
        if index ==11:
            answer = input("Your choice (a, or b): ").lower()
        else:
            answer = input("Your choice (a, b, or c): ").lower()

        if index == 11 and answer == 'b':  # For question 11, if the answer is 'b', set score to 0
            return 50

        if index == 5 and answer == 'c':  # If the answer to question 5 is 'c'
            return 1  # Return 1 (considered critical)

        total_score += scores.get(answer, 0) * weights[index]

    return total_score


def suggest_portfolio(score):
    # Score maximum possible
    max_score = sum(3 * weight for weight in weights.values())

    # Définir les catégories en fonction des pourcentages du score maximum
    if score == 50:
        return "No Crypto"
    elif score == 1:
        return "Beginner"
    elif score <= max_score * 0.2:
        return "Very Conservative"
    elif score <= max_score * 0.4:
        return "Balanced"
    elif score <= max_score * 0.6:
        return "Growth"
    elif score <= max_score * 0.8:
        return "Growth"
    else:
        return "Very Dynamic"
