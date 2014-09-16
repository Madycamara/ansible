#!/usr/bin/php
<?php

require 'ejabberd_external_auth.php';

class MyAuth extends EjabberdExternalAuth {
	protected function authenticate($user, $server, $password) {
		require_once 'PasswordHash.php';
		$salt='c55e35033be1c6b58abba66ee697b3';
		$forcePortable = (CRYPT_BLOWFISH != 1);
		$hasher = new PasswordHash(8, $forcePortable);
		if($this->exists($user, $server)){
			$query=$this->db()->prepare('SELECT * FROM oc_users WHERE uid=CONCAT(?,"@",?)');
			$query->execute(array($user,$server));
			$dbpass=$query->fetch();
			$this->log('Received SQL pass: '.$dbpass['password'].'=||= Received user pass: '.$password);
			if(count($dbpass)>0){
				if($hasher->CheckPassword($password . $salt, $dbpass['password'])){
					return true;
				}
			}
		}
		return false;
	}

	protected function exists($user, $server) {
		$query=$this->db()->prepare('SELECT * FROM oc_users WHERE uid=CONCAT(?,"@",?)');
		$query->execute(array($user,$server));
		$count=$query->fetch();
		if(count($count)>0){return true;}

		return false;
	}

}

require 'conf_auth.php';
$pdo = new PDO('mysql:dbname='.$dbname.';host='.$dbhost,$dbuser,$dbpass);
new MyAuth($pdo, '/var/log/ejabberd/mysql.log');
