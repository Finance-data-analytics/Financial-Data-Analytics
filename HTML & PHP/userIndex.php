<!DOCTYPE html>
<html lang="fr">
<?php 
    session_start();
    require_once 'config.php'; // ajout connexion bdd 
   // si la session existe pas soit si l'on est pas connecté on redirige
    if(!isset($_SESSION['user'])){
        header('Location:login.php');
        die();
    }
    // On récupere les données de l'utilisateur
    $req = $bdd->prepare('SELECT * FROM utilisateurs WHERE token = ?');
    $req->execute(array($_SESSION['user']));
    $data = $req->fetch();
?>


<head>
    <html lang="fr">
    <meta charset="utf-8" />
    <title>Acceuil</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"
          integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <link rel="stylesheet" type="text/css" href="../CSS/index.css">
    <!-- At the end of your body tag -->
</head>

<body>
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



            <!-- TradingView Widget END -->
            <nav class="navbar navbar-expand-lg">
                <div class="container-fluid">
                    <a href="index.php" asp-controller="Home" class="animated-link">
                        <img src="../pictures/Logo.png" alt="Logo Neoma Ventures" 
                             class="logo_esigelec">
                    </a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarScroll"
                            aria-controls="navbarScroll" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse justify-content-end" id="navbarScroll">
                        <a href="login.php" class="animated-link">
                            <span>
                                <img src="../pictures/account.svg" alt="Description de l'image">
                            </span>
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

    
    <!-- Fin haut de page-->
    <!--Debut de section 1 -->
</script>
        <div class="container-fluid my-5">
            <div class="container">
                <p>
                    <span>
                        Sculpt Your Financial Future with 
                    </span>
                </p>
                <p>
                    <span>
                        Precision Portfolio Crafting
                    </span>
                </p>
            </div>
        </div>
        </p> 
                <div class="col-sm-12 col-lg-5">
                    <h1 style="margin-top: 30%;"></h1>
                    </div>
                <div class="row">
                    <div class="col-sm-12 col-lg-7 element" >
                        <br />
                        <p style="color: #fff; font-size: 30px; padding:1em; color:antiquewhite" id="#gauche">
                        NEOMA VENTURE IS AT THE FOREFRONT OF REVOLUTIONIZING PORTFOLIO MANAGEMENT WITH A FOCUS ON RISK-ADJUSTED STRATEGIES. FOR OVER A DECADE, WE HAVE BEEN INNOVATING IN THE FINANCIAL SERVICES SECTOR, NOW MANAGING OVER $3 BILLION IN ASSETS. OUR UNIQUE APPROACH COMBINES CUTTING-EDGE TECHNOLOGY WITH TAILORED RISK ASSESSMENT TOOLS, ENSURING OUR CLIENTS' PORTFOLIOS ARE OPTIMIZED FOR THEIR INDIVIDUAL RISK TOLERANCE. NEOMA VENTURE PRIDES ITSELF ON ITS ABILITY TO PROVIDE INTELLIGENT, DYNAMIC, AND FORWARD-THINKING INVESTMENT SOLUTIONS. OUR TEAM OF EXPERTS WORKS TIRELESSLY TO IDENTIFY OPPORTUNITIES ACROSS A DIVERSE RANGE OF MARKETS, ENABLING OUR CLIENTS TO ACHIEVE THEIR FINANCIAL GOALS WITH CONFIDENCE.
                        </p>
                    </div>
                    <div class="col-sm-12 col-lg-6 animate-on-scroll" id="droite">
                        <img src="../pictures/imageIphone.png" alt="=Iphone">
                    </div>
                </div>
        </div>
        <p>

    
        <div class="col-sm-12 col-lg-5">
            <h1 style="margin-top: 30%;"></h1>
        </div>
        <div class="icon-grid">
            <div class="icon">
                <img src="../pictures/rocket.svg" alt="=icone" id="SECTION2">
                <i class="fa fa-star"></i>
                <p>NEOMA VENTURE STANDS OUT FOR ITS RAPID AND DYNAMIC UPDATES, CONSTANTLY EVOLVING WITH NEW FEATURES BASED ON VALUED CLIENT FEEDBACK. OUR COMMITMENT TO RESPONSIVENESS ENSURES THAT WE STAY AHEAD IN MEETING OUR CLIENTS' EVOLVING NEEDS IN PORTFOLIO MANAGEMENT.</p>
            </div>
            <div class="icon">
                <img src="../pictures/phone.svg" alt="=icone2">
                <i class="fa fa-heart"></i>
                <p>NEOMA VENTURE SUPPORTS A WIDE ARRAY OF ASSET CLASSES, COVERING MORE THAN 30 GLOBAL CRYPTOCURRENCY AND STOCK TRADING PLATFORMS. ADDITIONALLY, OUR PLATFORM IS FULLY COMPATIBLE WITH ALL MAJOR GLOBAL INDICES AND A DIVERSE RANGE OF COMMODITIES, ENSURING A COMPREHENSIVE INVESTMENT EXPERIENCE.</p>
            </div>
            <div class="icon">
                <img src="../pictures/hub.svg" alt="=icone2">
                <i class="fa fa-smile"></i>
                <p>AT NEOMA VENTURE, WE CREATE SEAMLESS CONNECTIONS BETWEEN COMPANIES AND THEIR CURRENT OR POTENTIAL INVESTORS. STAY INFORMED WITH INSTANT UPDATES ON INVESTOR RELATIONS DIRECTLY THROUGH OUR PLATFORM, ENSURING SMOOTH AND TRANSPARENT COMMUNICATIONS.</p>
            </div>
            <div class="icon">
                <img src="../pictures/euro.svg" alt="=icone2">
                <i class="fa fa-thumbs-up"></i>
                <p>SEARCHING FOR AN ALL-INCLUSIVE SOLUTION FOR STOCK PRICE, CRYPTO INDEX, AND MUTUAL FUND TRACKING? NEOMA VENTURE INTEGRATES ALL THESE FEATURES INTO ONE EFFICIENT, USER-FRIENDLY APPLICATION. SWITCHING BETWEEN MULTIPLE PLATFORMS IS A THING OF THE PAST – WITH NEOMA VENTURE, ALL YOUR INVESTMENT DATA IS ACCESSIBLE IN ONE PLACE!</p>
            </div>
        </div>
        <div class="col-sm-12 col-lg-5">
            <h1 style="margin-top: 30%;"></h1>
        </div>
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
