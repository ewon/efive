#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: changepw.cgi 4549 2010-05-04 09:24:12Z owes $
#

# Add entry in menu
# MENUENTRY system 040 "sspasswords" "sspasswords"
#
# Make sure translation exists $Lang::tr{'sspasswords'}

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

my %cgiparams    = ();
my $errormessage = '';
my $error_admin  = '';
my $error_dial   = '';

&Header::showhttpheaders();

$cgiparams{'ACTION_ADMIN'} = '';
$cgiparams{'ACTION_DIAL'}  = '';

&General::getcgihash(\%cgiparams);

if ($cgiparams{'ACTION_ADMIN'} eq $Lang::tr{'save'}) {
    my $password1 = $cgiparams{'ADMIN_PASSWORD1'};
    my $password2 = $cgiparams{'ADMIN_PASSWORD2'};
    if ($password1 eq $password2) {
        if ($password1 =~ m/[\s\"']/) {
            $errormessage = $Lang::tr{'password contains illegal characters'} . ": [ &#92;s&#92; &#34; &#39; ]";
            $error_admin  = 'error';
        }
        elsif (length($password1) >= 6) {
            if (system('/usr/sbin/htpasswd', '-m', '-b', '/var/ipcop/auth/users', 'admin', "${password1}")) {
                $errormessage = $Lang::tr{'errmsg change fail'};
                $error_admin  = 'error';
            }
            else {
                &General::log($Lang::tr{'admin user password has been changed'});
            }
        }
        else {
            $errormessage = $Lang::tr{'passwords must be at least 6 characters in length'};
            $error_admin  = 'error';
        }
    }
    else {
        $errormessage = $Lang::tr{'passwords do not match'};
        $error_admin  = 'error';
    }
}

if ($cgiparams{'ACTION_DIAL'} eq $Lang::tr{'save'}) {
    my $password1 = $cgiparams{'DIAL_PASSWORD1'};
    my $password2 = $cgiparams{'DIAL_PASSWORD2'};
    if ($password1 eq $password2) {
        if ($password1 =~ m/[\s\"']/) {
            $errormessage = $Lang::tr{'password contains illegal characters'} . ": [ &#92;s&#92; &#34; &#39; ]";
            $error_dial   = 'error';
        }
        elsif (length($password1) >= 6) {
            if (system('/usr/sbin/htpasswd', '-m', '-b', '/var/ipcop/auth/users', 'dial', "${password1}")) {
                $errormessage = $Lang::tr{'errmsg change fail'};
                $error_dial  = 'error';
            }
            else {
                &General::log($Lang::tr{'dial user password has been changed'});
            }
        }
        else {
            $errormessage = $Lang::tr{'passwords must be at least 6 characters in length'};
            $error_dial   = 'error';
        }
    }
    else {
        $errormessage = $Lang::tr{'passwords do not match'};
        $error_dial   = 'error';
    }
}

&Header::openpage($Lang::tr{'change passwords'}, 1, '');

&Header::openbigbox('100%', 'left', '');

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:", 'error');
    print "<class name='base'>$errormessage\n";
    print "&nbsp;</class>\n";
    &Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'administrator user password'}:", $error_admin);
print <<END
<table width='100%'>
<tr>
    <td width='20%' class='base'>$Lang::tr{'username'}:&nbsp;'admin'</td>
    <td width='15%' class='base' align='right'>$Lang::tr{'password'}:&nbsp;</td>
    <td><input type='password' name='ADMIN_PASSWORD1' size='20' maxlength='40'/></td>
</tr><tr>
    <td width='20%' class='base'>&nbsp;</td>
    <td width='15%' class='base' align='right'>$Lang::tr{'again'}:&nbsp;</td>
    <td><input type='password' name='ADMIN_PASSWORD2' size='20' maxlength='40'/></td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='comment1button'> &nbsp; </td>
    <td class='button1button'><input type='submit' name='ACTION_ADMIN' value='$Lang::tr{'save'}' /></td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/system-passwords.html' target='_blank'><img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>
    </td>
</tr>
</table>
END
    ;
&Header::closebox();

&Header::openbox('100%', 'left', "$Lang::tr{'dial user password'}:", $error_dial);
print <<END
<table width='100%'>
<tr>
    <td width='20%' class='base'>$Lang::tr{'username'}:&nbsp;'dial'</td>
    <td width='15%' class='base' align='right'>$Lang::tr{'password'}:&nbsp;</td>
    <td><input type='password' name='DIAL_PASSWORD1' size='20' maxlength='40'/></td>
</tr><tr>
    <td width='20%' class='base'>&nbsp;</td>
    <td width='15%' class='base' align='right'>$Lang::tr{'again'}:&nbsp;</td>
    <td><input type='password' name='DIAL_PASSWORD2' size='20' maxlength='40'/></td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='comment1button'> &nbsp; </td>
    <td class='button1button'><input type='submit' name='ACTION_DIAL' value='$Lang::tr{'save'}' /></td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/system-passwords.html' target='_blank'><img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>
    </td>
</tr>
</table>
END
    ;
&Header::closebox();

print "</form>\n";

&Header::closebigbox();

&Header::closepage();
