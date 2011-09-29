#!/usr/bin/perl
#
# (c) 2002 Robert Wood <rob@empathymp3.co.uk>
#
# $Id: proxygraphs.cgi 3482 2009-08-21 18:50:24Z eoberlander $
#

# Add entry in menu
# MENUENTRY status 050 "ssproxy graphs" "proxy access graphs" haveProxy
#
# Make sure translation exists $Lang::tr{'ssproxy graphs'}

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require "/usr/lib/ipcop/lang.pl";
require "/usr/lib/ipcop/header.pl";

my @graphs = ();

&Header::showhttpheaders();

my $dir       = "/home/httpd/html/sgraph";
my $sgraphdir = "/home/httpd/html/sgraph";

&Header::openpage($Lang::tr{'proxy access graphs'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'proxy access graphs'});

if (open(IPACHTML, "$sgraphdir/index.html")) {
    my $skip = 1;
    while (<IPACHTML>) {
        $skip = 1 if /^<HR>$/;
        if ($skip) {
            $skip = 0 if /<H1>/;
            next;
        }
        s/<IMG SRC=([^"'>]+)>/<img src='\/sgraph\/$1' alt='Graph' \/>/;
        s/<HR>/<hr \/>/g;
        s/<BR>/<br \/>/g;
        s/<([^>]*)>/\L<$1>\E/g;
        s/(size|align|border|color)=([^'"> ]+)/$1='$2'/g;
        # strip out size=-1 from font tags
        s/ size=\'-1\'//g;
        print;
    }
    close(IPACHTML);
}
else {
    print $Lang::tr{'no information available'};
}

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
