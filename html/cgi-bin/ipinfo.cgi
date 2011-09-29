#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# (c) 2002 Josh Grubman <jg@false.net> - Multiple registry IP lookup code
#
# $Id: ipinfo.cgi 5024 2010-10-17 22:11:14Z owes $
#

use IO::Socket;
use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

my %cgiparams=();

&Header::showhttpheaders();

&General::getcgihash(\%cgiparams);

$ENV{'QUERY_STRING'} =~s/&//g;
my @addrs = split(/ip=/,$ENV{'QUERY_STRING'});

my %whois_servers = ("RIPE"=>"whois.ripe.net","APNIC"=>"whois.apnic.net","LACNIC"=>"whois.lacnic.net");

&Header::openpage($Lang::tr{'ip info'}, 1, '');

&Header::openbigbox('100%', 'left');
my @lines=();
my $extraquery='';
foreach my $addr (@addrs) {
    next if $addr eq "";

    $extraquery='';
    @lines=();
    my $whoisname = "whois.arin.net";
    my $iaddr = inet_aton($addr);
    my $hostname = gethostbyaddr($iaddr, AF_INET);

    if (!$hostname) { 
        $hostname = $Lang::tr{'lookup failed'}; 
    }

    my $sock = new IO::Socket::INET ( PeerAddr => $whoisname, PeerPort => 43, Proto => 'tcp');
    if ($sock) {
        print $sock "$addr\n";
        while (<$sock>) {
            $extraquery = $1 if (/NetType:\s+Allocated to (\S+)\s+/);
            push(@lines,$_);
        }
        close($sock);

        if ($extraquery) {
            undef (@lines);
            $whoisname = $whois_servers{$extraquery};
            my $sock = new IO::Socket::INET ( PeerAddr => $whoisname, PeerPort => 43, Proto => 'tcp');
            if ($sock) {
                print $sock "$addr\n";
                while (<$sock>) {
                    push(@lines,$_);
                }
            }
            else {
                @lines = ( "$Lang::tr{'unable to contact'} $whoisname" );
            }
        }
    }
    else {
        @lines = ( "$Lang::tr{'unable to contact'} $whoisname" );
    }

    &Header::openbox('100%', 'left', $addr . ' (' . $hostname . ') : '.$whoisname);
    print "<pre>\n";
    foreach my $line (@lines) {
        print &Header::cleanhtml($line,"y");
    }
    print "</pre>\n";

    if (defined($ENV{'HTTP_REFERER'})) {
        # Offer 'back' if there is a referer
        print "<hr /><div align='left'>";
        print "<a href='$ENV{'HTTP_REFERER'}'><img src='/images/back.png' alt='$Lang::tr{'back'}' title='$Lang::tr{'back'}' /></a>";
        print "</div>";
    }

    &Header::closebox();
}

&Header::closebigbox();

&Header::closepage();
