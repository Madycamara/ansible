#!/usr/bin/php
<?php

require_once 'PasswordHash.php';


define('ERR_PERMFAIL',1);
define('ERR_NOUSER',3);
define('ERR_TEMPFAIL',111);


class doveauth  {
	public $db = null;
	public $hasher = null;
	public $salt = null;
	final public function __construct(PDO $db = null,$salt){
		$this->db=$db;
		$this->salt=$salt;
		$forcePortable = (CRYPT_BLOWFISH != 1);
		$this->hasher=new PasswordHash(8, $forcePortable);
	}

	final protected function db() {
		return $this->db;
	}

	public function auth($user, $password) {
		if($this->exists($user)){
			$query=$this->db()->prepare('SELECT password FROM oc_users WHERE uid=?');
			$query->execute(array($user));
			$dbpass=$query->fetch();
			if(count($dbpass)>0){
				if($this->hasher->CheckPassword($password . $this->salt, $dbpass['password'])){
					echo 'OK'.PHP_EOL;
					return true;
				}
			}
		}
		return false;
	}

	public function exists($user) {
		$query=$this->db()->prepare('SELECT * FROM oc_users WHERE uid=?');
		$query->execute(array($user));
		$count=$query->fetch();
		if(count($count)>0){echo 'OK'.PHP_EOL; return true;}
		return false;
	}
}

array_shift($argv);
$args=$argv;

$pdo = new PDO('mysql:dbname='.$dbname.';host='.$dbhost,$dbuser,$dbpass);
$auth=new doveauth($pdo,'c55e35033be1c6b58abba66ee697b3');
if(count($args)>1){
$auth->auth($args[0],$args[1]);
}else{
$auth->exists($args[0]);
}
