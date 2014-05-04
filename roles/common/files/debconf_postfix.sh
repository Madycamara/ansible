cat <<EOF | debconf-set-selections
postfix	postfix/root_address	string	
postfix	postfix/rfc1035_violation	boolean	false
postfix	postfix/retry_upgrade_warning	boolean	
# Install postfix despite an unsupported kernel?
postfix	postfix/kernel_version_warning	boolean	
postfix	postfix/mydomain_warning	boolean	
postfix	postfix/mynetworks	string	127.0.0.0/8
postfix	postfix/sqlite_warning	boolean	
postfix	postfix/mailbox_limit	string	0
postfix	postfix/relayhost	string	
postfix	postfix/procmail	boolean	true
postfix	postfix/protocols	select	all
postfix	postfix/mailname	string	testans
postfix	postfix/tlsmgr_upgrade_warning	boolean	
postfix	postfix/recipient_delim	string	+
postfix	postfix/main_mailer_type	select	Internet Site
postfix	postfix/destinations	string	$myhostname, localhost.$mydomain, localhost
postfix	postfix/chattr	boolean	false
EOF

if [ "$?" == "0" ]; then
        echo -n "OK"
else
        echo -n "ERROR"
fi
