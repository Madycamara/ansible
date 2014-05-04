cat <<EOF | debconf-set-selections
tzdata	tzdata/Zones/Australia	select	
tzdata	tzdata/Zones/US	select	
tzdata	tzdata/Zones/Asia	select	
tzdata	tzdata/Zones/Etc	select	UTC
tzdata	tzdata/Zones/SystemV	select	
tzdata	tzdata/Zones/Arctic	select	
tzdata	tzdata/Zones/Pacific	select	
tzdata	tzdata/Zones/Antarctica	select	
tzdata	tzdata/Zones/Europe	select	Madrid
tzdata	tzdata/Zones/Africa	select	
tzdata	tzdata/Zones/America	select	
tzdata	tzdata/Areas	select	Europe
tzdata	tzdata/Zones/Atlantic	select	
tzdata	tzdata/Zones/Indian	select	
EOF

if [ "$?" == "0" ]; then
	echo -n "OK"
else
	echo -n "ERROR"
fi
