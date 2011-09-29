#!/usr/bin/perl
#
# This file is part of the IPCop Firewall.
#
# IPCop is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# IPCop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IPCop; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# (c) 2006-2009, the IPCop team
#
# $Id: updatelists.pl 3419 2009-08-09 13:50:22Z owes $
#

use strict;
use LWP::UserAgent;
require '/usr/lib/ipcop/general-functions.pl';


my %mainsettings  = ();
$mainsettings{'CHECKUPDATES'} = 'off';
$mainsettings{'PRELOADUPDATES'} = 'off';
&General::readhash('/var/ipcop/main/settings', \%mainsettings);

if (($ARGV[0] eq '--cron') || ($ARGV[0] eq 'cron')) {
    exit 1 unless (-e "/var/ipcop/red/active");

    # Connection is up. Check age of file.
    exit 0 unless (system('find /var/ipcop/red/active -mtime +1 | grep active > /dev/null') == 0);

    # spread the load on the servers by waiting a random length of time...
    my $sleepwait = int(rand(60));
    sleep $sleepwait;
}
elsif (($ARGV[0] eq '--red') || ($ARGV[0] eq 'red')) {
    exit 1 unless (-e "/var/ipcop/red/active");

    exit 0 unless ($mainsettings{'CHECKUPDATES'} eq 'on');
}
else {
    # Test connection up here, to avoid dying later.
    if (! -e "/var/ipcop/red/active") {
        print "RED connection is down.\n";
        exit 1;
    }
}


my @this;
my $return = &General::downloadpatchlist($mainsettings{'PRELOADUPDATES'});
if ($return == 0) {
    # Got it
}
elsif ($return == 1) {
    print "RED connection is down.\n";
}
elsif ($return == 2) {
    print "Could not open available updates file.\n";
}
else {
    print "Could not download the available updates list.\n";
}

exit $return;
