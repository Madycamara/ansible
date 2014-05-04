#! /bin/bash
#
# Script per checkejar si la zona horaria és la correcta

PROGPATH=`echo $0 | /bin/sed -e 's,[\\/][^\\/][^\\/]*$,,'`
source $PROGPATH/utils.sh
source $PROGPATH/functions.sh
source $PROGPATH/params.sh

test -f /etc/nagios/check_timezone.conf || Exit $STATE_UNKNOWN "No he pogut trobar /etc/nagios/check_timezone.conf!"
source /etc/nagios/check_timezone.conf

if [ ! -f ${TIMEZONE_FILE} ] ; then
	Exit $STATE_CRITICAL "No s'ha trobat l'arxiu de configuraci&oacute; ${TIMEZONE_FILE}!"
elif [ "${TIMEZONE}" != ` cat $TIMEZONE_FILE ` ] ; then
	Exit $STATE_WARNING "La zona horaria no &eacute;s correcta: "` cat $TIMEZONE_FILE `
else
	Exit $STATE_OK "La zona horaria &eacute;s la correcta: ${TIMEZONE}"
fi
