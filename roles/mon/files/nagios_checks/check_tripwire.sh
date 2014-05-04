#! /bin/bash
#
# Script per checkejar la integritat de la màquina.
# Depèn de tripwire

TMP=/tmp/twreport.txt.$$
trap "rm -f $TMP; exit 99" HUP INT QUIT TRAP USR1 PIPE TERM

# ATENCIÓ!
#
# Si TW_CMD o TW_EXEC estan definides a /etc/nagios/check_tripwire.conf, 
# els usarà en comptes dels que hi ha aquí. NO CANVÏIS LO D'AQUÍ, fes els
# canvis a /etc/nagios/check_chkrootkit.conf.
#
# Valors per defecte...
SUDO_CMD="/usr/bin/sudo"
TW_CMD="/usr/sbin/tripwire"
TW_OPT="--check -p /etc/tripwire/tw.pol --quiet"

touch $TMP
chmod 600 $TMP

PROGPATH=`echo $0 | /bin/sed -e 's,[\\/][^\\/][^\\/]*$,,'`
source $PROGPATH/utils.sh
source $PROGPATH/functions.sh
source $PROGPATH/params.sh

test -f /etc/nagios/check_tripwire.conf && source /etc/nagios/check_tripwire.conf

[ "X$TW_EXEC" = "X" ] && TW_EXEC="$SUDO_CMD $TW_CMD $TW_OPT"

Test_Command $SUDO_CMD
Test_Command $TW_CMD
Not_Running $TW_CMD

eval $TW_EXEC > $TMP

if ! grep -q "No Error" < $TMP ; then
	EXIT_MSG="S'han trobat errors"
	EXIT=$STATE_CRITICAL
elif [ ` grep "Total violations found:" < $TMP | awk ' { print $4 } ' ` -gt $WARNING_LEVEL ] ; then
	EXIT_MSG="S'han trobat "` grep "Total violations found:" < $TMP | awk ' { print $4 } ' `" errors!"
	EXIT=$STATE_WARNING
else
	EXIT_MSG="Tot OK."
	EXIT=$STATE_OK
fi
> $TMP
Exit $EXIT $EXIT_MSG
