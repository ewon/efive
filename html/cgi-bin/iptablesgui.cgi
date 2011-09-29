#!/usr/bin/perl
#
################################################################################
#
# IPCop iptables Web-Iface
#
# Copyright (C) 2007 Olaf (weizen_42) Westrik
#
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. 
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
#
# You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110, USA 
#
#
# Dieses Programm ist freie Software. Sie können es unter den Bedingungen der GNU General Public License, wie von der Free Software Foundation veröffentlicht, weitergeben und/oder modifizieren, entweder gemäß Version 2 der Lizenz oder (nach Ihrer Option) jeder späteren Version. 
#
# Die Veröffentlichung dieses Programms erfolgt in der Hoffnung, daß es Ihnen von Nutzen sein wird, aber OHNE IRGENDEINE GARANTIE, sogar ohne die implizite Garantie der MARKTREIFE oder der VERWENDBARKEIT FÜR EINEN BESTIMMTEN ZWECK. Details finden Sie in der GNU General Public License. 
#
# Sie sollten ein Exemplar der GNU General Public License zusammen mit diesem Programm erhalten haben. Falls nicht, schreiben Sie an die Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110, USA.
#
################################################################################
#
# $Id: iptablesgui.cgi 4026 2009-12-19 10:56:49Z owes $
#
# 2007-03 created by weizen_42
#

# Add entry in menu
# MENUENTRY status 080 "IPtables" "IPTables"
#
# Do not translate IPTables

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

use LWP::UserAgent;

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

my $option_table = '';


my %cgiparams=();
$cgiparams{'ACTION'} = '';              # refresh
$cgiparams{'TABLE'} = 'filter';         # filter / mangle / nat / raw
$cgiparams{'CHAIN'} = '';
&General::getcgihash(\%cgiparams);


if ( $cgiparams{'ACTION'} eq $Lang::tr{'refresh'} ) {
}

&Header::showhttpheaders();
&Header::openpage('IPTables', 1, '');
&Header::openbigbox('100%', 'left');

foreach my $table ( ("filter", "mangle", "nat", "raw") ) {
  if ( $cgiparams{'TABLE'} eq $table ) {
    $option_table = $option_table ."<option value='$table' selected='selected'>$table</option>";
  }
  else {
    $option_table = $option_table ."<option value='$table'>$table</option>";
  }
}

&Header::openbox('100%', 'left', 'IPTables:');

print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr>
    <td width='20%' class='base'>Table:</td><td colspan='3'><select name='TABLE'>$option_table</select></td>
</tr><tr>
    <td width='20%' class='base'>Chain:&nbsp;<img src='/blob.gif' alt='*' /></td><td colspan='3'><input type='text' name='CHAIN' value='$cgiparams{'CHAIN'}' size='20' /></td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='comment1button'><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td>
    <td class='button1button'><input type='submit' name='ACTION' value='$Lang::tr{'refresh'}' /></td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/status-iptables.html' target='_blank'><img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>
    </td>
</tr>
</table></form>
<hr />
END
;

my $output = '';
if ($cgiparams{'CHAIN'} eq '') {
    $output = `/usr/local/bin/iptableswrapper $cgiparams{'TABLE'} 2>&1`;
}
else {
    $output = `/usr/local/bin/iptableswrapper chain $cgiparams{'TABLE'} $cgiparams{'CHAIN'} 2>&1`;
}
$output = &Header::cleanhtml($output);

(my @lines) = split(/\n/, $output);

print "<table width='100%'>\n";
foreach my $line ( @lines )
{
    if ($line eq '') {
        print "<tr><td colspan='12'>&nbsp;</td></tr>\n"
    }
    elsif ($line =~ m/^Chain ([A-Z_]+) (.*)$/) {
        print "<tr class='table1colour'><td colspan='12' class='boldbase'><a name='$1'>$1</a> $2</td></tr>\n"
    }
    elsif ($line =~ m/^num + pkts/ ) {
        print "<tr><td>&nbsp;</td><td>num</td><td>pkts</td><td>bytes</td><td>target</td><td>prot</td><td>opt</td><td>in</td><td>out</td><td>src</td><td>dest</td><td>&nbsp;</td></tr>\n"
    }
    elsif ($line =~ m/^([0-9]+)\s+([0-9]+[KMGT]?)\s+([0-9]+[KMGT]?)\s+([A-Z_]+)\s+([a-z]+|[0-9]+)+\s+([a-z-]+)\s+([a-z0-9-:.*]+)\s+([a-z0-9-:.*]+)\s+(!{0,1}[0-9.\/]+)\s+(!{0,1}[0-9.\/]+)+(.*)/) {
        print "<tr><td>&nbsp;</td><td>$1</td><td>$2</td><td>$3</td><td>".&formattarget($4)."</td><td>$5</td><td>$6</td><td>".&General::color_devices("$7")."</td><td>".&General::color_devices("$8")."</td><td>$9</td><td>$10</td><td>$11</td></tr>\n"
    }
    else {
        print "<tr><td>&nbsp;</td><td colspan='11'>$line</td></tr>\n";
    }
}
print "</table>\n";

&Header::closebox();

&Header::closebigbox();
&Header::closepage();


sub formattarget
{
  my $target = shift;

    if ($target eq 'ACCEPT') {
        return "<font class='ipcop_iface_green'>$target</font>";
    }
    elsif ($target =~ m/^(DROP|REJECT)$/) {
        return "<font class='ipcop_iface_red'>$target</font>";
    }
    elsif ($target =~ m/^(DNAT|SNAT|MASQUERADE|LOG|MARK|RETURN)$/) {
        return $target;
    }
    else {
        if ($cgiparams{'CHAIN'} eq '') {
            return "<a href='#$target'>$target</a>";
        }
        else {
            return "$target";
        }
    }
}
