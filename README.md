# Neoma Venture

**Neoma Venture** is a web application designed as part of a **school project** to help investors build optimized portfolios using advanced **Monte Carlo simulations**. The platform focuses on maximizing returns while minimizing volatility, offering a personalized and data-driven investment experience.

## Features

- **Investor Profiling**: A quiz to assess the investor’s risk tolerance and preferences.
- **Monte Carlo Simulation**: Simulates thousands of scenarios to recommend the best portfolio allocation.
- **User Authentication**: Secure user login and session management powered by a database.
- **Interactive User Interface**: Built with HTML, CSS, and JavaScript for a sleek and responsive design.
- **Dynamic Portfolio Recommendations**: Real-time, tailored recommendations based on the investor's profile.

## Technologies Used

- **Python**: Backend logic and data processing.
- **Flask**: Framework for building scalable web applications.
- **HTML & CSS**: Structuring and styling the user interface.
- **JavaScript**: Enhancing interactivity and user experience.
- **SQL**: Managing and securely storing user data.

## How It Works

1. **User Registration**: Sign up or log in to the platform.
2. **Investor Quiz**: Complete a short quiz to determine your investment profile.
3. **Portfolio Simulation**: Using Monte Carlo methods, the system recommends an optimized portfolio.
4. **Portfolio Analysis**: View detailed analytics on risk, return, and asset allocation.

## Getting Started

To run **Neoma Venture**, follow these steps:

1. **Install Dependencies**  
   Install the required dependencies from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up the Database**  
   - Open **PHPMyAdmin** (e.g., via UwAmp).
   - Use the default username: `root` and password: `root`.
   - Create a database named `neoma_venturedb`.
   - Import all `.sql` files from the `/SQL` directory into the database.

3. **Configure the Database URI**  
   In the `__init__.py` file (inside the `neoma` folder), ensure the database URI matches your setup:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/neoma_venturedb'
   ```
   If using a custom port (e.g., `8889`), update it like this:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:8889/neoma_venturedb'
   ```

4. **Run the Application**  
   Launch the project by executing the `run.py` file:
   ```bash
   python run.py
   ```
   The application will open at: [http://localhost:5000](http://localhost:5000)

## Project Context

This platform was developed as part of a **school project** to demonstrate our ability to build a complete full-stack application. The goal was to combine theoretical knowledge with practical implementation to address real-world problems in the field of finance and investment.

## Future Enhancements

- **Advanced Analytics**: Incorporating more detailed metrics and visualizations for portfolio evaluation.
- **Data Expansion**: Integrating additional data sources for more accurate and diverse simulations.
- **UI/UX Improvements**: Further enhancing user engagement and usability.
