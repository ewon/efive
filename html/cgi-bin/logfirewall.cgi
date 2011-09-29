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
# along with IPCop.  If not, see <http://www.gnu.org/licenses/>.
#
# (c) The SmoothWall Team
# Copyright (c) 2001-2011 The IPCop Team
#
# $Id: logfirewall.cgi 5809 2011-08-18 14:30:25Z owes $
#
# July 28, 2003 - Darren Critchley - darren@kdi.ca
#	- added source mac adapter to layout
#

# Add entry in menu
# MENUENTRY logs 040 "firewall logs" "firewall log viewer"
#
# Make sure translation exists $Lang::tr{'firewall logs'} $Lang::tr{'firewall log viewer'}

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

use POSIX();

my %cgiparams    = ();
my %logsettings  = ();
my $errormessage = '';

my @now  = localtime();
my $dow  = $now[6];
my $doy  = $now[7];
my $tdoy = $now[7];
my $year = $now[5] + 1900;

$cgiparams{'DAY'}    = $now[3];
$cgiparams{'MONTH'}  = $now[4];
$cgiparams{'ACTION'} = '';

&General::getcgihash(\%cgiparams);
$logsettings{'LOGVIEW_REVERSE'}  = 'off';
$logsettings{'LOGVIEW_VIEWSIZE'} = 150;
&General::readhash('/var/ipcop/logging/settings', \%logsettings);

my $start = ($logsettings{'LOGVIEW_REVERSE'} eq 'on') ? 0x7FFFF000 : 0;    #index of firts line number to display

if ($ENV{'QUERY_STRING'} && $cgiparams{'ACTION'} ne $Lang::tr{'update'}) {
    my @temp = split(',', $ENV{'QUERY_STRING'});
    $start              = $temp[0];
    $cgiparams{'MONTH'} = $temp[1];
    $cgiparams{'DAY'}   = $temp[2];
}

my @temp_then = ();
if ($ENV{'QUERY_STRING'} && $cgiparams{'ACTION'} ne $Lang::tr{'update'}) {
    @temp_then = split(',', $ENV{'QUERY_STRING'});
    $start                = $temp_then[0];
    $cgiparams{'MONTH'}   = $temp_then[1];
    $cgiparams{'DAY'}     = $temp_then[2];
    $cgiparams{'SECTION'} = $temp_then[3];
}

if (!($cgiparams{'MONTH'} =~ /^(0|1|2|3|4|5|6|7|8|9|10|11)$/)
    || !($cgiparams{'DAY'} =~
        /^(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31)$/))
{
    $cgiparams{'DAY'}   = $now[3];
    $cgiparams{'MONTH'} = $now[4];
}
elsif ($cgiparams{'ACTION'} eq '>>') {
    @temp_then = &General::calculatedate($year, $cgiparams{'MONTH'}, $cgiparams{'DAY'}, 1);
    $year               = $temp_then[5]+1900;
    $cgiparams{'MONTH'} = $temp_then[4];
    $cgiparams{'DAY'}   = $temp_then[3];
}
elsif ($cgiparams{'ACTION'} eq '<<') {
    @temp_then = &General::calculatedate($year, $cgiparams{'MONTH'}, $cgiparams{'DAY'}, -1);
    $year               = $temp_then[5]+1900;
    $cgiparams{'MONTH'} = $temp_then[4];
    $cgiparams{'DAY'}   = $temp_then[3];
}
else {
    @temp_then = &General::validatedate(0, $cgiparams{'MONTH'}, $cgiparams{'DAY'});
    $year               = $temp_then[5]+1900;
    $cgiparams{'MONTH'} = $temp_then[4];
    $cgiparams{'DAY'}   = $temp_then[3];
}

# Date to display 
my $date;
$date = sprintf("%d-%02d-%02d", $year, $cgiparams{'MONTH'}+1, $cgiparams{'DAY'});

my $monthstr = $General::shortMonths[ $cgiparams{'MONTH'} ];
my $daystr = $cgiparams{'DAY'} == 0 ? '..' : $cgiparams{'DAY'} <= 9 ? " $cgiparams{'DAY'}" : "$cgiparams{'DAY'}";

my $lines = 0;
my @log   = ();

my $loop    = 1;
my $filestr = 0;
my $lastdatetime;    # for debug
my $search_for_end = 0;
my $day_extension = ($cgiparams{'DAY'} == 0 ? 1: $cgiparams{'DAY'});

while ($loop) {

    # calculate file name
    my $gzindex;
    if (($cgiparams{'MONTH'} eq $now[4]) && ($day_extension eq $now[3])) {
        $filestr = "/var/log/messages";
        $loop = 0;
    }
    else {
        $filestr = sprintf("/var/log/messages-%d%02d%02d", $year, $cgiparams{'MONTH'}+1, $day_extension);
        $filestr = "${filestr}.gz" if -f "${filestr}.gz";
    }

    # now read file if existing
    if (open(FILE, ($filestr =~ /.gz$/ ? "gzip -dc $filestr |" : $filestr))) {

        #&General::log("reading $filestr");
        READ: while (<FILE>) {
            my $line = $_;
            if ($line =~ /^${monthstr} ${daystr} ..:..:.. [\w\-]+ kernel:.*IN=.*$/) {
                # when standard viewing, just keep in memory the correct slice
                # it starts a '$start' and size is $viewport
                # If export, then keep all lines...
                if ($cgiparams{'ACTION'} eq $Lang::tr{'export'}) {
                    $log[ $lines++ ] = "$line";
                }
                else {
                    if ($lines++ < ($start + $logsettings{'LOGVIEW_VIEWSIZE'})) {
                        push(@log, "$line");
                        if (@log > $logsettings{'LOGVIEW_VIEWSIZE'}) {
                            shift(@log);
                        }

                        #} else { dont do this optimisation, need to count lines !
                        #    $datetime = $maxtime; # we have read viewsize lines, stop main loop
                        #    last READ;           # exit read file
                    }
                }
                $search_for_end = 1;    # we find the start of slice, can look for end now
            }
            else {
                if ($search_for_end == 1) {

                    #finish read files when date is over (test month equality only)
                    $line =~ /^(...) (..) ..:..:..*$/;
                    $loop = 0 if (($1 ne $monthstr) || (($daystr ne '..') && ($daystr ne $2)));
                }
            }
        }
        close(FILE);
    }
    $day_extension++;
    if ($day_extension > 31) {
        $loop = 0;
    }
}   # while

#  $errormessage = "$Lang::tr{'date not in logs'}: $filestr $Lang::tr{'could not be opened'}";

if ($cgiparams{'ACTION'} eq $Lang::tr{'export'}) {
    print "Content-type: text/plain\n";
    print "Content-Disposition: attachment; filename=\"ipcop-firewall-$date.log\";\n";
    print "\n";
    print "IPCop firewall log\r\n";
    print "$Lang::tr{'date'}: $date\r\n\r\n";

    # Do not reverse log when exporting
    # if ($logsettings{'LOGVIEW_REVERSE'} eq 'on') { @log = reverse @log; }

    foreach $_ (@log) {
        /^... (..) (..:..:..) [\w\-]+ kernel:.*(IN=.*)$/;
        my $day = $1;
        $day =~ tr / /0/;
        my $time = $cgiparams{'DAY'} ? "$2" : "$day/$2";
        print "$time $3\r\n";

    }
    exit 0;
}

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'firewall log'}, 1, '');

&Header::openbigbox('100%', 'left', '');

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:", 'error');
    print "<font class='base'>$errormessage&nbsp;</font>\n";
    &Header::closebox();
}

&Header::openbox('100%', 'left', "$Lang::tr{'settings'}:");

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr>
	<td width='50%' class='base' nowrap='nowrap'>$Lang::tr{'month'}:&nbsp;
	<select name='MONTH'>
END
    ;
for (my $month = 0; $month < 12; $month++) {
    print "\t<option ";
    if ($month == $cgiparams{'MONTH'}) {
        print "selected='selected' ";
    }
    print "value='$month'>$Lang::tr{$General::longMonths[$month]}</option>\n";
}
print <<END
	</select>
	&nbsp;&nbsp;$Lang::tr{'day'}:&nbsp;
	<select name='DAY'>
END
    ;
print "<option value='0'>$Lang::tr{'all'}</option>\n";
for (my $day = 1; $day <= 31; $day++) {
    print "\t<option ";
    if ($day == $cgiparams{'DAY'}) {
        print "selected='selected' ";
    }
    print "value='$day'>$day</option>\n";
}
print <<END
	</select>
	</td>
	<td width='45%'  align='center'>
		<input type='submit' name='ACTION' title='$Lang::tr{'day before'}' value='&lt;&lt;' />
		<input type='submit' name='ACTION' title='$Lang::tr{'day after'}' value='&gt;&gt;' />
		<input type='submit' name='ACTION' value='$Lang::tr{'update'}' />
		<input type='submit' name='ACTION' value='$Lang::tr{'export'}' />
	</td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/logs-firewall.html' target='_blank'><img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>
    </td>
</tr>
</table>
</form>
END
    ;

&Header::closebox();

&Header::openbox('100%', 'left', "$Lang::tr{'log'}:");
print "<p><b>$Lang::tr{'firewall hits'} $date: $lines</b></p>";

$start = $lines - $logsettings{'LOGVIEW_VIEWSIZE'} if ($start >= $lines - $logsettings{'LOGVIEW_VIEWSIZE'});
$start = 0 if ($start < 0);

my $prev;
if ($start == 0) {
    $prev = -1;
}
else {
    $prev = $start - $logsettings{'LOGVIEW_VIEWSIZE'};
    $prev = 0 if ($prev < 0);
}

my $next;
if ($start == $lines - $logsettings{'LOGVIEW_VIEWSIZE'}) {
    $next = -1;
}
else {
    $next = $start + $logsettings{'LOGVIEW_VIEWSIZE'};
    $next = $lines - $logsettings{'LOGVIEW_VIEWSIZE'} if ($next >= $lines - $logsettings{'LOGVIEW_VIEWSIZE'});
}

if ($logsettings{'LOGVIEW_REVERSE'} eq 'on') { @log = reverse @log; }
if ($lines != 0) { &oldernewer(); }

print <<END
<table width='100%'>
<tr>
	<td width='10%' align='center' class='boldbase'><b>$Lang::tr{'time'}</b></td>
	<td width='13%' align='center' class='boldbase'><b>$Lang::tr{'chain'}</b></td>
	<td width='5%' align='center' class='boldbase'><b>$Lang::tr{'iface'}</b></td>
	<td width='5%' align='center' class='boldbase'><b>$Lang::tr{'proto'}</b></td>
	<td width='16%' align='center' class='boldbase'><b>$Lang::tr{'source'}</b></td>
	<td width='10%' align='center' class='boldbase'><b>$Lang::tr{'src port'}</b></td>
	<td width='5%' align='center' class='boldbase'><b>$Lang::tr{'mac address'}</b></td>
	<td width='16%' align='center' class='boldbase'><b>$Lang::tr{'destination'}</b></td>
	<td width='20%' align='center' class='boldbase'><b>$Lang::tr{'dst port'}</b></td>
</tr>
END
    ;

$lines = 0;
foreach $_ (@log) {
    /^... (..) (..:..:..) [\w\-]+ kernel:(.*)(IN=.*)$/;
    my $day = $1;
    $day =~ tr / /0/;
    my $time    = $cgiparams{'DAY'} ? "$2" : "$day/$2";
    my $comment = $3;
    my $packet  = $4;

    $packet =~ /IN=((\w|\-)+)/;
    my $iface = &General::color_devices($1);
    $packet =~ /SRC=([\d\.]+)/;
    my $srcaddr = $1;
    $packet =~ /DST=([\d\.]+)/;
    my $dstaddr = $1;
    $packet =~ /MAC=([\w+\:]+)/;
    my $macaddr = $1;
    my $proto   = ($packet =~ /PROTO=(\w+)/) ? $1 : "-";
    # Set protoname to IGMP, proto 2 can be confusing
    $proto = 'IGMP' if ($proto eq '2');
    my $servi = '';
    my $srcport = '-';
    my $dstport = '-';
    if ($packet =~ /SPT=(\d+)/) {
        $srcport = $1;
        $servi = uc(getservbyport($srcport, lc($proto)));
        if ($servi ne '' && $srcport < 1024) {
            $srcport = "$srcport($servi)";
        }
    }
    if ($packet =~ /DPT=(\d+)/) {
        $dstport = $1;
        $servi = uc(getservbyport($dstport, lc($proto)));
        if ($servi ne '' && $dstport < 1024) {
            $dstport = "$dstport($servi)";
        }
    }

    my @mactemp = split(/:/, $macaddr);
    $macaddr = "$mactemp[6]:$mactemp[7]:$mactemp[8]:$mactemp[9]:$mactemp[10]:$mactemp[11]";
    print "<tr class='table".int(($lines % 2) + 1)."colour'>";
    print <<END

	<td align='center'>$time</td>
	<td align='center'>$comment</td>
	<td align='center'>$iface</td>
	<td align='center'>$proto</td>
	<td align='center'>
	<table width='100%' cellpadding='0' cellspacing='0'><tr>
	<td align='center'><a href='/cgi-bin/ipinfo.cgi?ip=$srcaddr'>$srcaddr</a></td>
	</tr></table>
	</td>
	<td align='center'>$srcport</td>
	<td align='center'>$macaddr</td>
	<td align='center'>
	<table width='100%' cellpadding='0' cellspacing='0'><tr>
	<td align='center'><a href='/cgi-bin/ipinfo.cgi?ip=$dstaddr'>$dstaddr</a></td>
	</tr></table>
	</td>
	<td align='center'>$dstport</td>
</tr>
END
        ;
    $lines++;
}

print "</table>";

&oldernewer();

&Header::closebox();

&Header::closebigbox();

&Header::closepage();

sub oldernewer {
    print <<END
<table width='100%'>
<tr>
END
        ;

    print "<td align='center' width='50%'>";
    if ($prev != -1) {
        print
"<a href='/cgi-bin/logfirewall.cgi?$prev,$cgiparams{'MONTH'},$cgiparams{'DAY'}'>$Lang::tr{'older'}</a>";
    }
    else {
        print "$Lang::tr{'older'}";
    }
    print "</td>\n";

    print "<td align='center' width='50%'>";
    if ($next >= 0) {
        print
"<a href='/cgi-bin/logfirewall.cgi?$next,$cgiparams{'MONTH'},$cgiparams{'DAY'}'>$Lang::tr{'newer'}</a>";
    }
    else {
        print "$Lang::tr{'newer'}";
    }
    print "</td>\n";

    print <<END
</tr>
</table>
END
        ;
}
