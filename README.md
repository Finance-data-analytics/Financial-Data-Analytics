Neoma Venture
Neoma Venture is a web application designed as part of a school project to help investors build optimized portfolios using advanced Monte Carlo simulations. The platform focuses on maximizing returns while minimizing volatility, offering a personalized and data-driven investment experience.

Features
Investor Profiling: Users take a short quiz to assess their risk tolerance and investment preferences.
Monte Carlo Simulation: Generates optimal portfolios by simulating thousands of possible scenarios, ensuring the best risk-return balance.
User Authentication: Secure user login and session management powered by a database.
Interactive User Interface: Built with HTML, CSS, and JavaScript for a sleek and responsive design.
Dynamic Portfolio Recommendations: Real-time analysis and tailored recommendations based on user inputs.
Technologies Used
Python: Backend logic and data processing.
Flask: Framework for building scalable web applications.
HTML & CSS: Structuring and styling the user interface.
JavaScript: Adding interactivity and enhancing user experience.
SQL: Managing and storing user data securely.
How It Works
Users sign up or log in to the platform.
They complete a quiz to determine their investor profile.
The platform uses Monte Carlo simulations to generate an optimal portfolio tailored to the user's profile.
Users can view detailed portfolio analytics, including risk and return metrics.
Getting Started
To run Neoma Venture:

Install the required dependencies listed in requirements.txt using:
bash
Copier le code
pip install -r requirements.txt
Set up the database in PHPMyAdmin:
Username: root
Password: root
Create a database named neoma_venturedb.
Import the SQL files from the /SQL directory.
Verify the database URI in __init__.py:
python
Copier le code
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/neoma_venturedb'
If using a custom port, update accordingly (e.g., localhost:8889).
Run the application:
bash
Copier le code
python run.py
Access the platform at http://localhost:5000.
Project Context
This platform was developed as part of a school project to showcase our ability to design and build a full-stack application with advanced data analytics and portfolio optimization features. The focus was on applying theoretical knowledge to a real-world problem in the domain of finance and investment.

Future Enhancements
Adding advanced analytical tools for portfolio evaluation.
Expanding data sources for more accurate simulations.
Enhancing UI/UX for better user engagement.

[README.md.docx](https://github.com/Finance-data-analytics/Financial-Data-Analytics/files/14347390/README.md.docx)
