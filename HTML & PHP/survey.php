<!DOCTYPE html>
<html lang="fr">

<head>
    <html lang="fr">
    <meta charset="utf-8" />
    <title>Acceuil</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"
          integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <link rel="stylesheet" type="text/css" href="../CSS/survey.css">
    <!-- At the end of your body tag -->
</head>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-OERcA2EqjJCMA+/3y+gxIOqMEjwtxJY7qPCqsdltbNJuaOe923+mo//f6V8Qbsw3" crossorigin="anonymous">
    </script>
    <!--Debut de haut de page -->
    <header>

        <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
            <div class="tradingview-widget-container__widget"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js">
        {
        "symbols": [
            {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"},
            {"proName": "FOREXCOM:NSXUSD", "title": "US 100"},
            {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"},
            {"proName": "BITSTAMP:ETHUSD", "title": "Ethereum"},
            {"description": "Apple", "proName": "NASDAQ:AAPL"}
        ],
        "showSymbolLogo": false,
        "colorTheme": "dark",
        "isTransparent": true,
        "displayMode": "adaptive",
        "locale": "fr"
        }
        </script>
    </div>
  <!-- TradingView Widget END -->
<body>



            <!-- TradingView Widget END -->
            <nav class="navbar navbar-expand-lg">
                <div class="container-fluid">
                    <a asp-action="Index" asp-controller="Home" class="animated-link">
                        <img src="../pictures/Logo.png" alt="Logo Neoma Ventures" 
                             class="logo_esigelec">
                    </a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarScroll"
                            aria-controls="navbarScroll" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse justify-content-end" id="navbarScroll">
                        <a href="survey.php" class="animated-link">
                            <span> Make your Portfolio </span>
                        </a>
                        <a href="" class="animated-link">
                            <span> Our Team </span>
                        </a>
                        <a asp-action="Stocks" asp-controller="Home" class="animated-link">
                            <span> Stocks </span>
                        </a>
                        <a asp-action="Index" asp-controller="Companies" class="animated-link">
                            <span> Market </span>
                        </a>
                        <a href="#contact" class="animated-link">
                            <span> Contact </span>
                        </a>
                        
                    </div>
                </div>
            </nav>
    </header>

    <div class="container" id="container">
        <div class="form-container sign-up">
            <form>
                <h1>Create Account</h1>
                <span>or use your email for registeration</span>
                <input type="text" placeholder="Name">
                <input type="email" placeholder="Email">
                <input type="password" placeholder="Password">
                <button>Sign Up</button>
            </form>
        </div>
        <div class="form-container sign-in">
            <form>
                <h1>Sign In</h1>
                <span>or use your email password</span>
                <input type="email" placeholder="Email">
                <input type="password" placeholder="Password">
                <a href="#">Forget Your Password?</a>
                <button>Sign In</button>
            </form>
        </div>
        <div class="toggle-container">
            <div class="toggle">
                <div class="toggle-panel toggle-left">
                    <h1>Welcome Back!</h1>
                    <p>Enter your personal details to use all of site features</p>
                    <button class="hidden" id="login">Sign In</button>
                </div>
                <div class="toggle-panel toggle-right">
                    <h1>Hello, Friend!</h1>
                    <p>Register with your personal details to use all of site features</p>
                    <button class="hidden" id="register">Sign Up</button>
                </div>
            </div>
        </div>
    </div>
    <!-- Fin haut de page-->
    <!--Debut de section 1 -->
    <script src="../JS/script.js"> </script>
</body>
<footer>

    <div class="container-fluid">
        <div class="row">
            <h1>Read More</h1>
            <div class="mention col-lg-4">
                <h3>General Terms of Sale</h3>
                <p>
                Our General Terms of Sale outline the agreement between our company and our clients. These terms include information on order processing, delivery procedures, and return policies. We commit to providing high-quality services and products, ensuring customer satisfaction is at the forefront of our operations. Our terms also detail payment methods, warranty information, and the process for handling disputes.
                </p>
            </div>
            <div class="mention col-lg-4">
                <h3>Cookie Management Policy</h3>
                <p>
                Our Cookie Management Policy describes how we use cookies to enhance user experience on our website. We use cookies for website functionality, analytics, and personalized content. Users have the option to manage their cookie preferences, ensuring a balance between personalization and privacy. Our policy provides detailed information on the types of cookies used and how they contribute to a better user experience.
                </p>
            </div>
            <div class="mention col-lg-4">
                <h3>Data Protection Policy</h3>
                <p>
                The Data Protection Policy of our website is dedicated to safeguarding the personal information of our users. We adhere to strict privacy standards and employ robust security measures to protect user data. This policy outlines the types of data we collect, how it is used, and the rights of users regarding their personal information. We are committed to transparency and accountability in all our data handling practices.
            </div>
        </div>
        <p id="contact">Contact :  | &copy; 2023, NEOMA</p>
    </div>
</footer>




</html>
