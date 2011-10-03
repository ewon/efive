#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: upload.cgi 4008 2009-12-14 10:42:12Z owes $
#

# Add entry in menu
# Crooks disabled
# MENU..ENTRY network 020 "upload" "firmware upload"
#
# Make sure translation exists $Lang::tr{'firmware upload'}

use File::Copy;
use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

my %uploadsettings   = ();
my $errormessage     = '';
my $error_speedtouch = '';
my $error_eci        = '';
my $error_fritz      = '';

&Header::showhttpheaders();
$uploadsettings{'ACTION'} = '';

&General::getcgihash(\%uploadsettings, {'wantfile' => 1, 'filevar' => 'FH'});
# When using ' or " in button text (ACTION value) it cannot be compared directly because language text will have &#039; or &quot;
# Use cleanhtml to 'translate' ', " etc. so comparison is possible
$uploadsettings{'ACTION'} = &Header::cleanhtml ($uploadsettings{'ACTION'});

my $extraspeedtouchmessage = '';
my $extrafritzdslmessage   = '';
my $extraeciadslmessage    = '';
my $modem                  = '';
my $firmwarename           = '';
my $kernel                 = '';

my $speedtouch = &General::speedtouchversion;
if ($speedtouch == 4) {
    $modem        = 'v4_b';
    $firmwarename = "$Lang::tr{'upload'} ZZZL_3.012";
}
else {
    $modem        = 'v0123';
    $firmwarename = "$Lang::tr{'upload'} KQD6_3.012";
}

$kernel = `/bin/uname -r | /usr/bin/tr -d '\012'`;

if ($uploadsettings{'ACTION'} eq $firmwarename) {
    if ($modem eq 'v0123' || $modem eq 'v4_b') {
        if (copy($uploadsettings{'FH'}, "/var/ipcop/alcatelusb/firmware.$modem.bin") != 1) {
            $errormessage     = $!;
            $error_speedtouch = 'error';
        }
        else {
            $extraspeedtouchmessage = $Lang::tr{'upload successful'};
        }
    }
}
elsif ($uploadsettings{'ACTION'} eq "$Lang::tr{'upload'} ipcop-avmdrv.tgz") {
    if (copy($uploadsettings{'FH'}, "/var/patches/fcdsl-x.tgz") != 1) {
        $errormessage = $!;
        $error_fritz  = 'error';
    }
    else {
        $extrafritzdslmessage = $Lang::tr{'upload successful'};
    }
}
elsif ($uploadsettings{'ACTION'} eq $Lang::tr{'upload synch.bin'}) {
    if (copy($uploadsettings{'FH'}, "/var/ipcop/eciadsl/synch.bin") != 1) {
        $errormessage = $!;
        $error_eci    = 'error';
    }
    else {
        $extraeciadslmessage = $Lang::tr{'upload successful'};
    }
}

&Header::openpage($Lang::tr{'firmware upload'}, 1, '');

&Header::openbigbox('100%', 'left', '');

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:", 'error');
    print "<font class='base'>$errormessage&nbsp;</font>\n";
    &Header::closebox();
}
print "<form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>\n";

&Header::openbox('100%', 'left', $Lang::tr{'alcatelusb upload'}, $error_speedtouch);
print <<END
<table width='100%'>
<tr>
    <td colspan='4'>$Lang::tr{'alcatelusb help'}<br />
    URL: <a href='http://www.speedtouch.com/support.htm'>http://www.speedtouch.com/support.htm</a>
    </td>
</tr>
<tr><td colspan='4'>$Lang::tr{'modem'}: Rev <b>$speedtouch</b></td></tr>
<tr>
    <td width='5%' class='base' nowrap='nowrap'>$Lang::tr{'upload file'}:&nbsp;</td>
    <td width='45%'><input type="file" size='30' name="FH" /></td>
    <td width='35%' align='center'><input type='submit' name='ACTION' value='$firmwarename' /></td>
    <td width='15%'>
END
    ;
if (-e "/var/ipcop/alcatelusb/firmware.$modem.bin") {
    if ($extraspeedtouchmessage ne '') {
        print("$extraspeedtouchmessage</td>");
    }
    else {
        print("$Lang::tr{'present'}</td>");
    }
}
else {
    print("$Lang::tr{'not present'}</td>");
}
print <<END
</tr>
</table>
END
    ;

&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'eciadsl upload'}, $error_eci);
print <<END
<table width='100%'>
<tr>
    <td colspan='4'>$Lang::tr{'eciadsl help'}<br />
    URL: <a href='http://eciadsl.flashtux.org/'>http://eciadsl.flashtux.org/</a>
    </td>
</tr>
<tr>
    <td width='5%' class='base' nowrap='nowrap'>$Lang::tr{'upload file'}:&nbsp;</td>
    <td width='45%'><input type="file" size='30' name="FH" /></td>
    <td width='35%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'upload synch.bin'}' /></td>
    <td width='15%'>
END
    ;
if (-e "/var/ipcop/eciadsl/synch.bin") {
    if ($extraeciadslmessage ne '') {
        print("$extraeciadslmessage</td>");
    }
    else {
        print("$Lang::tr{'present'}</td>");
    }
}
else {
    print("$Lang::tr{'not present'}</td>");
}
print <<END
</tr>
</table>
END
    ;
&Header::closebox();

&Header::openbox('100%', 'left', $Lang::tr{'fritzdsl upload'}, $error_fritz);
print <<END
<table width='100%'>
<tr>
    <td colspan='4'>$Lang::tr{'fritzdsl help'}<br />
    URL: <a href='http://www.ipcop.org/'>http://www.ipcop.org/</a>
    </td>
</tr>
<tr>
    <td width='5%' class='base' nowrap='nowrap'>$Lang::tr{'upload file'}:&nbsp;</td>
    <td width='45%'><input type="file" size='30' name="FH" /></td>
    <td width='35%' align='center'><input type='submit' name='ACTION' value="$Lang::tr{'upload'} ipcop-avmdrv.tgz"/></td>
    <td width='15%'>
END
    ;
if ($extrafritzdslmessage ne '') {
    print("$extrafritzdslmessage</td></tr><tr><td>&nbsp;</td><td><pre>");
    print `/usr/local/bin/installfcdsl`;
    print("</pre></td>");
}
else {
    if (-e "/lib/modules/$kernel/extra/fcdsl.ko.gz") {
        print("$Lang::tr{'present'}</td>");
    }
    else {
        print("$Lang::tr{'not present'}</td>");
    }
}
print <<END
</tr>
</table>
END
    ;
&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();
