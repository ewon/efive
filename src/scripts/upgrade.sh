#!/bin/bash
#
# This file is part of the IPCop Firewall.
# (c) Gilles Espinasse
#
# Universal upgrade script
# - called after every restore (from installation or backup)
# - place a call on update only if a new fix was added
# - every change on data include in backup need to be there
#   and not in update setup
#
# $Id: upgrade.sh 5392 2011-02-01 20:41:22Z owes $
#


# Tweak ntp.conf file if NTPd is running (modified in 1.9.11)
TMP=`grep "ENABLED_NTP=on" /var/ipcop/time/settings`
if [ "x$TMP" != "x" ]; then
    /bin/sed -i -e "s+^fudge\s*127\.127\.1\.0.*+fudge  127.127.1.0 stratum 7+" \
                -e "s+^driftfile.*+driftfile /var/log/ntp/drift+" /var/ipcop/time/ntp.conf

    # Modify server restrictions (1.9.18)
    /bin/sed -i -e "s+^restrict default ignore.*+restrict default kod nomodify notrap nopeer noquery+" \
                -e "/^restrict.*mask 255\.255\.255\.255.*/ d" /var/ipcop/time/ntp.conf
fi

# OpenVPN config file, modified in 1.9.11 and 1.9.13
if [ -e /var/ipcop/openvpn/server.conf ]; then
    TMP=`grep "script-security" /var/ipcop/openvpn/server.conf`
    if [ "x$TMP" == "x" ]; then
        echo "script-security 2" >> /var/ipcop/openvpn/server.conf
    fi
    /bin/sed -i -e "s+^client-connect.*+client-connect /usr/local/bin/openvpn.sh+" \
                -e "s+^client-disconnect.*+client-disconnect /usr/local/bin/openvpn.sh+" \
                /var/ipcop/openvpn/server.conf
fi

# OpenVPN-Blue, OpenVPN-Orange and OpenVPN-Red no longer exist, modified in 1.9.12
if [ -e /var/ipcop/firewall/policy ]; then
    /bin/sed -i -e "/OpenVPN-Blue/ d" \
                -e "/OpenVPN-Orange/ d" \
                -e "/OpenVPN-Red/ d" /var/ipcop/firewall/policy
fi

# IPsec, change from KLIPS to NETKEY, modified in 1.9.15
if [ -e /var/ipcop/ipsec/ipsec.conf ]; then
    /bin/sed -i -e "/^interfaces=.*/ d" \
                -e "s/protostack=klips/protostack=netkey/" /var/ipcop/ipsec/ipsec.conf
fi

# Make sure we have IP when RED=PPPoE, modified in 1.9.15
TMP=`grep "RED_1_TYPE" /var/ipcop/ethernet/settings`
if [ "x$TMP" == "xPPPOE" ]; then
    TMP=`grep "RED_1_ADDRESS" /var/ipcop/ethernet/settings`
    if [ "x$TMP" == "x" ]; then
        echo "RED_1_ADDRESS=1.1.1.1" >> /var/ipcop/ethernet/settings
        echo "RED_1_NETADDRESS=1.1.1.0" >> /var/ipcop/ethernet/settings
        echo "RED_1_NETMASK=255.255.255.0" >> /var/ipcop/ethernet/settings
    fi
fi

# dnsmasq config file, modified in 1.9.15
TMP=`grep "listen-address" /var/ipcop/dhcp/dnsmasq.conf`
if [ "x$TMP" != "x" ]; then
    /bin/sed -i -e "/^listen-address.*/ d" /var/ipcop/dhcp/dnsmasq.conf
    echo "except-interface=wan-1" >> /var/ipcop/dhcp/dnsmasq.conf
    echo "except-interface=ppp0" >> /var/ipcop/dhcp/dnsmasq.conf
    echo "except-interface=dmz-1" >> /var/ipcop/dhcp/dnsmasq.conf
fi
# dnsmasq config file, modified in 1.9.18
TMP=`grep "domain-needed" /var/ipcop/dhcp/dnsmasq.conf`
if [ "x$TMP" == "x" ]; then
    echo "domain-needed" >> /var/ipcop/dhcp/dnsmasq.conf
fi

# External access rules no longer possible as INPUT rule, modified in 1.9.18
/bin/sed -i -e "/,INPUT,.*,defaultSrcNet,Red,/{s/,INPUT,/,EXTERNAL,/}" /var/ipcop/firewall/config
