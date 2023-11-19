<!DOCTYPE html>
<html lang="fr">

<head>
    <html lang="fr">
    <meta charset="utf-8" />
    <title>Acceuil</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"
          integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <link rel="stylesheet" type="text/css" href="../CSS/home.css">
    

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
                    <a asp-action="Index" asp-controller="Home" class="animated-link">
                        <img src="../pictures/Logo.png" alt="Logo Neoma Ventures" 
                             class="logo_esigelec">
                    </a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarScroll"
                            aria-controls="navbarScroll" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse justify-content-end" id="navbarScroll">

                        <a asp-action="Index" asp-controller="Login" class="animated-link">
                            <span> Login </span>
                        </a>
                        <a asp-action="Create" asp-controller="Users" class="animated-link">
                            <span> Sign Up </span>
                        </a>
                        <a href="PageNotreEquipe2.php" class="animated-link">
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
    <div class="container-fluid my-5">
        <div class="ContainerTexteBody animated">
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


    <div class="col-sm-12 col-lg-5">
        <h1 style="margin-top: 30%;"></h1>
    </div>
    <div class="row">
        <div class="col-sm-12 col-lg-7">
            <br />
            <p style="color: #fff; font-size: 30px; padding:1em; color:antiquewhite" id="#gauche">
                ESIGELEC VENTURES HAS BEEN CULTIVATING NEW SEGMENTS OF THE VENTURE CAPITAL MARKET FOR OVER TWENTY YEARS. TODAY, WE MANAGE OVER $5 BILLION IN INSTITUTIONAL CAPITAL AND SUPPORT FOUNDERS, GENERAL PARTNERS AND INSTITUTIONS ACROSS THE PRIVATE TECHNOLOGY ECOSYSTEM. OUR FUNDS INVEST IN COMPANIES AND VENTURE CAPITAL PARTNERSHIPS DIRECTLY OR THROUGH SECONDARY TRANSACTIONS.
            </p>
        </div>
        <div class="col-sm-12 col-lg-6" id="droite">
            <img src="~/photo/imageIphone.png" alt="=Iphone">
        </div>
    </div>
    <div class="col-sm-12 col-lg-5">
        <h1 style="margin-top: 30%;"></h1>
    </div>
    <div class="icon-grid">
        <div class="icon">
            <img src="~/photo/rocket.svg" alt="=icone">
            <i class="fa fa-star"></i>
            <p>ESIGELEC VENTURES IS KNOWN FOR ITS FAST AND CONTINUOUS UPDATES AND ADDING NEW FEATURES BASED ON POPULAR USER REQUESTS.</p>
        </div>
        <div class="icon">
            <img src="~/photo/phone.svg" alt="=icone2">
            <i class="fa fa-heart"></i>
            <p>ESIGELEC Ventures supports more than 300 cryptocurrency and stock trading platforms worldwide. In addition, ESIGELEC Ventures is compatible with all major indices and commodities.</p>
        </div>
        <div class="icon">
            <img src="~/photo/hub.svg" alt="=icone2">
            <i class="fa fa-smile"></i>
            <p>With ESIGELEC Ventures, we draw a direct line between companies and their (potential) investors. Receive instant news about investor relations via Esigelec Ventures. In all fluidity.</p>
        </div>
        <div class="icon">
            <img src="~/photo/euro.svg" alt="=icone2">
            <i class="fa fa-thumbs-up"></i>
            <p>If you are looking for the best stock price tracker, crypto index tracker, fund tracker (mutual funds),... or even more? ESIGELEC Ventures combines them all in one sublime and intuitive application! No need to switch between different platforms and applications. All your investments at a glance!</p>
        </div>
    </div>
    <div class="col-sm-12 col-lg-5">
        <h1 style="margin-top: 30%;"></h1>
    </div>



    <script src="js/main.js"></script>

</body>

<footer>

    <div class="container-fluid">
        <div class="row">
            <h1>En savoir plus</h1>
            <div class="mention col-lg-4">
                <h3>Condition Générales de Ventes</h3>
                <p>
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Nihil necessitatibus illum nobis,
                    maiores
                    quisquam id! Repellendus quia totam dolor, dolorum, reprehenderit dignissimos ea dolore magnam
                    aliquid non, accusamus nemo hic.
                </p>
            </div>
            <div class="mention col-lg-4">
                <h3>Politique de Guestion des Cookies</h3>
                <p>
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Fugit quisquam, excepturi cupiditate
                    nisi
                    eaque
                    consequatur quidem.
                </p>
            </div>
            <div class="mention col-lg-4">
                <h3>Politique de protection des données</h3>
                <p>
                    Lorem ipsum dolor sit amet consectetur adipisicing elit. Nobis blanditiis eius eum laborum
                    laboriosam
            </div>
        </div>
        <p id="contact">Contact : 0617108406 | &copy; 2023, ESIGELEC</p>
    </div>
</footer>




</html>
