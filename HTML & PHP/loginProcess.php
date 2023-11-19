<?php
session_start(); // Démarrage de la session
require_once 'config.php'; // On inclut la connexion à la base de données

// Vérification si les champs email et password sont présents
if(!empty($_POST['email']) && !empty($_POST['password'])) {
    // Patch XSS
    $email = htmlspecialchars(strtolower($_POST['email']));
    $user_password = htmlspecialchars($_POST['password']); // Renamed variable to avoid conflict

    // Préparation de la requête
    if($stmt = $bdd->prepare("SELECT id, name, email, password FROM users WHERE email = ?")) {
        // Liaison des paramètres
        $stmt->bind_param("s", $email);

        // Exécution de la requête
        if($stmt->execute()) {
            // Liaison des résultats
            $stmt->bind_result($id, $name, $courriel, $db_password); // Corrected variable names
            $stmt->fetch();

            // Vérification du mot de passe
            if(password_verify($user_password, $db_password)) { // Using the correct variables
                // Gestion des rôles et redirection
                $_SESSION['iduser'] = $id;
                $_SESSION['email'] = $email;
                $_SESSION['message'] = "Connexion réussie";
                header('Location: index.php'); // Adjust the redirection as needed
            } else {
                $_SESSION['message'] = "Le mot de passe est invalide";
                header('Location: connexion.php?login_err=password');
            }
        } else {
            $_SESSION['message'] = "aucun compte n'existe avec cette adresse email";
            header('Location: connexion.php?login_err=already');
        }
    }
} else {
    header('Location: index.php'); // Corrected the redirection URL
}
?>
