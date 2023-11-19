<?php 
    try 
    {
        $bdd = new PDO("mysql:host=localhost;dbname=neoma_venturedb;charset=utf8", "root", "root");
    }
    catch(PDOException $e)
    {
        die('Erreur : '.$e->getMessage());
    }
?>
