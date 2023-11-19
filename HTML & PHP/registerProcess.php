<?php 
    require_once 'config.php'; // On inclu la connexion à la bdd

    // Si les variables existent et qu'elles ne sont pas vides
    if(!empty($_POST['name']) && !empty($_POST['email']) && !empty($_POST['password']) && !empty($_POST['password_retype']) && !empty($_POST['birthdate']))
    {
        // Patch XSS
        $name = htmlspecialchars($_POST['name']);
        $email = htmlspecialchars($_POST['email']);
        $password = htmlspecialchars($_POST['password']);
        $password_retype = htmlspecialchars($_POST['password_retype']);
        $birthdate = htmlspecialchars($_POST['birthdate']);

        // On vérifie si l'utilisateur existe
        $check = $bdd->prepare('SELECT email, password, name, birthdate,idpf,picprofile FROM users WHERE email = ?');
        $check->execute(array($email));
        $data = $check->fetch();
        $row = $check->rowCount();

        $email = strtolower($email); // on transforme toute les lettres majuscule en minuscule pour éviter que Foo@gmail.com et foo@gmail.com soient deux compte différents ..
        
        // Si la requete renvoie un 0 alors l'utilisateur n'existe pas 
        if($row == 0){
            if(strlen($name) <= 100){ // On verifie que la longueur du pseudo <= 100
                if(strlen($email) <= 100){ // On verifie que la longueur du mail <= 100
                    if(filter_var($email, FILTER_VALIDATE_EMAIL)){ // Si l'email est de la bonne forme
                        if($password === $password_retype){ // si les deux mdp saisis sont bon

                            // On hash le mot de passe avec Bcrypt, via un coût de 12
                            $cost = ['cost' => 12];
                            $password = password_hash($password, PASSWORD_BCRYPT, $cost);

                            // On insère dans la base de données
                            $insert = $bdd->prepare('INSERT INTO users(email, password, name, birthdate, idpf,picprofile) VALUES(:email, :password, :name, :birthdate, :idpf,:picprofile)');
                            $insert->execute(array(
                                'email' => $email,
                                'name' => $name,
                                'password' => $password,
                                'birthdate' => $birthdate,
                                'idpf' => $idpf,
                                'picprofile' => $picprofile,
                            ));
                            // On redirige avec le message de succès
                            header('Location:login.php?reg_err=success');
                            die();
                        }else{ header('Location: login.php?reg_err=email'); die();}
                    }else{ header('Location: login.php?reg_err=email_length'); die();}
                }else{ header('Location: login.php?reg_err=password'); die();}
            }else{ header('Location: login.php?reg_err=pseudo_length'); die();}
        }else{ header('Location: login.php?reg_err=already'); die();}
    }
?>
