<?php
session_start(); // Démarrage de la session
require_once 'config.php'; // On inclut la connexion à la base de données

// Vérification si les champs email et password sont présents
if(!empty($_POST['email']) && !empty($_POST['password'])) {
    // Patch XSS
    $email = htmlspecialchars($_POST['email']);
    $password = htmlspecialchars($_POST['password']); // Renamed variable to avoid conflict

    $check = $bdd->prepare('SELECT id,email,password,name FROM users WHERE email = ?');
    $check->execute(array($email));
    $data = $check->fetch();
    $row = $check->rowCount();
    if($row > 0)
        {
            // Si le mail est bon niveau format
            if(filter_var($email, FILTER_VALIDATE_EMAIL))
            {
               // Si le mot de passe est le bon
                if(password_verify($password, $data['password']))
                {
                    // On créer la session et on redirige sur landing.php
                    $_SESSION['user'] = $data['id'];
                    $_SESSION['name'] = $data['name'];
                    header('Location: userIndex.php?reg_err=success');
                    die();
                }else{ header('Location:login.php?login_err=password'); die(); 
                }
            }else{ header('Location:login.php?login_err=email'); die(); 
            }
        }else{ header('Location:login.php?login_err=already'); die(); 
        }
    }else{ header('Location:login.php'); die();}

    
   
?>
