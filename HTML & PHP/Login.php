@model WC_EsigelecVenture.ViewModels.UserViewModel
<head>

    <meta charset="utf-8" />
    <title>Acceuil</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"
          integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <link rel="stylesheet" type="text/css" href="~/css/indexStyle.css">
    <link rel="stylesheet" type="text/css" href="~/css/Connexion.css">
</head>

<body>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-OERcA2EqjJCMA+/3y+gxIOqMEjwtxJY7qPCqsdltbNJuaOe923+mo//f6V8Qbsw3" crossorigin="anonymous">
    </script>
    <header>
        <nav class="navbar navbar-expand-lg">
            <div class="container-fluid">
                <a asp-action="Index" asp-controller="Home" class="animated-link">
                    <img src="~/photo/Logo.png" alt="Logo Esigelec Ventures"
                         class="logo_esigelec">
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarScroll"
                        aria-controls="navbarScroll" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse justify-content-end" id="navbarScroll">
                    <a asp-action="Index" asp-controller="Home" class="animated-link">
                        <span> Home <span>
                    </a>
                    <a asp-action="Create" asp-controller="Users" class="animated-link">
                        <span> Sign up <span>
                    </a>
                    <a href="PageNotreEquipe2.php" class="animated-link">
                        <span> Our Team <span>
                    </a>

                    <a asp-action="Index" asp-controller="Companies" class="animated-link">
                        <span> Market </span>
                    </a>
                    @{
                        var userRoleString = Context.Session.GetString("UserRole");
                        bool.TryParse(userRoleString, out bool userRole);
                    }

                    @if (userRole)
                    {
                        <a asp-controller="Users" asp-action="Index" class="animated-link">
                            <span> User Management <span>
                        </a>

                    }
                    </a>
                    <a href="#contact" class="animated-link">
                        <span> Contact <span>
                    </a>
                </div>
            </div>
        </nav>
    </header>

    <div class="login-container">
        @if (Model.Authentifie)
        {
            <h3>
                Vous êtes déjà authentifié avec le login :
                @Model.User.Login
            </h3>
            @Html.ActionLink("Voulez-vous vous déconnecter ?", "Deconnexion")
        }
        else
        {
            <h2>Connectez-vous</h2>
            using (Html.BeginForm())
            {
               
                <form asp-action="Index" class="login-form">

                    <div class="login-container">
                        <div class="login-form">

                            @Html.LabelFor(m => m.User.Login)
                            <div class="TextBox">
                                @Html.TextBoxFor(m => m.User.Login)
                            </div>
                            @Html.ValidationMessageFor(m => m.User.Login)
                           
                        </div>
                        <div class="login-form">

                            @Html.LabelFor(m => m.User.Pwd)
                            <div class="mdp">
                                @Html.PasswordFor(m => m.User.Pwd)
                            </div>
                            @Html.ValidationMessageFor(m => m.User.Pwd)
                        </div>
                        <input type="submit" value="Se connecter" action="Index">
                    </div>
                </form>
                <br />
            }

        }
    </div>

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

