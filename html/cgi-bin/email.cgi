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
# $Id: email.cgi 5834 2011-08-28 19:30:53Z dotzball $
#

# Add entry in menu
# MENUENTRY system 070 "email settings" "email settings"

use strict;

# enable only the following on debugging purpose
use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require "/usr/lib/ipcop/lang.pl";
require "/usr/lib/ipcop/header.pl";

my %cgiparams;
my %settings;
my $errormessage = '';
my $infomessage  = '';
my $saveerror    = '';

my $debugFormparams = 0;

#~ my @dummy = ($settingsfile);
#~ undef(@dummy);

&Header::showhttpheaders();

# Init parameters
$cgiparams{'EMAIL_TO'}          = '';
$cgiparams{'EMAIL_FROM'}        = '';
$cgiparams{'EMAIL_USR'}         = '';
$cgiparams{'EMAIL_PW'}          = '';
$cgiparams{'EMAIL_SERVER'}      = '';
$cgiparams{'EMAIL_SERVER_PORT'} = '';

&General::getcgihash(\%cgiparams);

&General::readhash('/var/ipcop/email/settings', \%settings);

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'}) {
    &validSave();

    if ($errormessage) {
        $saveerror = 'error';
    }
    else {    # no error, all right, save new settings

        $settings{'EMAIL_TO'}          = $cgiparams{'EMAIL_TO'};
        $settings{'EMAIL_FROM'}        = $cgiparams{'EMAIL_FROM'};
        $settings{'EMAIL_USR'}         = $cgiparams{'EMAIL_USR'};
        $settings{'EMAIL_PW'}          = $cgiparams{'EMAIL_PW'};
        $settings{'EMAIL_SERVER'}      = $cgiparams{'EMAIL_SERVER'};
        $settings{'EMAIL_SERVER_PORT'} = $cgiparams{'EMAIL_SERVER_PORT'};

        &General::writehash('/var/ipcop/email/settings', \%settings);

    }
}    # end if ($cgiparams{'ACTION'} eq $Lang::tr{'save'})

# If user wants to save settings, but gets an errormessage, we don't
# overwrite users input
unless ($saveerror) {

    # Set default EMAIL_FROM if not configured
    if (!exists($settings{'EMAIL_FROM'})) {
        my %mainsettings = ();
        &General::readhash('/var/ipcop/main/settings', \%mainsettings);
        $settings{'EMAIL_FROM'} = $mainsettings{'HOSTNAME'} . "@" . $mainsettings{'DOMAINNAME'};
    }

    $cgiparams{'EMAIL_TO'}          = $settings{'EMAIL_TO'};
    $cgiparams{'EMAIL_FROM'}        = $settings{'EMAIL_FROM'};
    $cgiparams{'EMAIL_USR'}         = $settings{'EMAIL_USR'};
    $cgiparams{'EMAIL_PW'}          = $settings{'EMAIL_PW'};
    $cgiparams{'EMAIL_SERVER'}      = $settings{'EMAIL_SERVER'};
    $cgiparams{'EMAIL_SERVER_PORT'} = $settings{'EMAIL_SERVER_PORT'};

}    # end unless ($saveerror)

if ($cgiparams{'ACTION'} eq $Lang::tr{'send test mail'}) {

    my $template = "/var/ipcop/email/templates/test";

    if (-e "$template.${Lang::language}.tpl") {
        $template .= ".${Lang::language}.tpl";
    }
    else {
        $template .= ".en.tpl";
    }

    my $subject = $Lang::tr{'subject test'};

    unless($subject =~ /^[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_:\.\+,\ ]+$/) {
        # found some problematic characters, use english subject text
        &Lang::reload(2);

        $subject = $Lang::tr{'subject test'};

        # switch back to selected language
        &Lang::reload(0);
    }

    # send test email
    my $cmd = "/usr/local/bin/emailhelper ";
    $cmd .= " -s \"$subject\" ";
    $cmd .= " -m \"$template\" ";

    my $return = `$cmd`;

    if ($return =~ /Email was sent successfully!/) {
        $infomessage = "$Lang::tr{'test email was sent'}";
    }
    else {
        $errormessage = "$Lang::tr{'test email could not be sent'}:<br/>";
        $errormessage .= "$return <br />";
    }
}    # end if ($cgiparams{'ACTION'} eq $Lang::tr{'send test mail'})

&Header::openpage($Lang::tr{'email settings'}, 1, '');
&Header::openbigbox('100%', 'left');

###############
# DEBUG DEBUG
if ($debugFormparams == 1) {
    &Header::openbox('100%', 'left', 'DEBUG');
    my $debugCount = 0;
    foreach my $line (sort keys %cgiparams) {
        print "$line = $cgiparams{$line}<br />\n";
        $debugCount++;
    }
    print "&nbsp;Count: $debugCount\n";
    &Header::closebox();
}

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}", 'error');
    print "<font class='base'>$errormessage&nbsp;</font>";
    &Header::closebox();
}

if ($infomessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'information messages'}:", 'warning');
    print "<class name='base'>$infomessage\n";
    print "&nbsp;</class>\n";
    &Header::closebox();
}

&Header::openbox('100%', 'left', "$Lang::tr{'email settings'}:", $saveerror);

print <<END;
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
    <tr>
        <td width='25%' align='left' class='base' nowrap='nowrap'>
            $Lang::tr{'email server'}: &nbsp;
        </td>
        <td width='75%' align='left' class='base' >
            <input type='text' name='EMAIL_SERVER' value='$cgiparams{'EMAIL_SERVER'}' size='25' />&nbsp;
        </td>
    </tr>
    <tr>
        <td align='left' class='base' nowrap='nowrap'>
            $Lang::tr{'email server port'}:&nbsp;<img src='/blob.gif' alt='*' />
        </td>
        <td align='left' class='base' >
            <input type='text' name='EMAIL_SERVER_PORT' value='$cgiparams{'EMAIL_SERVER_PORT'}' size='25' />
        </td>
    </tr>
    <tr>
        <td align='left' class='base' nowrap='nowrap'>
            $Lang::tr{'username'}:&nbsp;<img src='/blob.gif' alt='*' />
        </td>
        <td align='left' class='base' >
            <input type='text' name='EMAIL_USR' value='$cgiparams{'EMAIL_USR'}' size='25' />
        </td>
    </tr>
    <tr>
        <td align='left' class='base' nowrap='nowrap'>
            $Lang::tr{'password'}:&nbsp;<img src='/blob.gif' alt='*' />
        </td>
        <td align='left' class='base' >
            <input type='password' name='EMAIL_PW' value='$cgiparams{'EMAIL_PW'}' size='25' />
        </td>
    </tr>
    <tr>
        <td align='left' class='base' nowrap='nowrap'>
            $Lang::tr{'from email adr'}: &nbsp;
        </td>
        <td align='left' class='base' >
            <input type='text' name='EMAIL_FROM' value='$cgiparams{'EMAIL_FROM'}' size='25' />&nbsp;
        </td>
    </tr>
    <tr>
        <td align='left' class='base' nowrap='nowrap'>
            $Lang::tr{'to email adr'}:&nbsp;<img src='/blob.gif' alt='*' /><img src='/blob.gif' alt='*' />
        </td>
        <td align='left' class='base' >
            <input type='text' name='EMAIL_TO' value='$cgiparams{'EMAIL_TO'}' size='25' />&nbsp;
        </td>
    </tr>
    <tr>
        <td align='left' class='base' colspan="2">
            <input type='submit' name='ACTION' value='$Lang::tr{'send test mail'}' />
        </td>
    </tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='comment2buttons'>
        <img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}
    </td>
    <td colspan='2'>&nbsp;</td>
</tr><tr>
    <td class='comment2buttons'>
        <img src='/blob.gif' alt='*' /><img src='/blob.gif' alt='*' />&nbsp;$Lang::tr{'email to help'}
    </td>
    <td class='button2buttons'>
        <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
    </td>
    <td class='button2buttons'>
END

# If user input caused an error
# and user wants a reset, we re-read settings from settingsfile
if ($errormessage ne '') {
    print "<input type='submit' name='ACTION' value='$Lang::tr{'reset'}' />";
}
else {
    print "<input type='reset' name='ACTION' value='$Lang::tr{'reset'}' />";
}

print <<END;
    </td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/system-email-settings.html' target='_blank'><img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>
    </td>
</tr>
</table>
</form>
END

&Header::closebox();
&Header::closebigbox();
&Header::closepage();

sub validSave
{
    chomp($cgiparams{'EMAIL_TO'});
    my @emails_to = split(/\s+/, $cgiparams{'EMAIL_TO'});

    my $email_ok = 1;
    if ($cgiparams{'EMAIL_TO'} eq '' ) {
        $email_ok = 0;
    }
    foreach my $email (@emails_to) {
        if (!&General::validemail($email)) {
            $email_ok = 0;
        }
    }

    if ($email_ok == 0) {
        $errormessage .= "$Lang::tr{'to email bad'}<br/>";
    }

    if ($cgiparams{'EMAIL_FROM'} eq '' || (!&General::validemail($cgiparams{'EMAIL_FROM'}))) {
        $errormessage .= "$Lang::tr{'from email bad'}<br/>";
    }

    if ($cgiparams{'EMAIL_SERVER'} eq '') {
        $errormessage .= "$Lang::tr{'email server can not be empty'}<br/>";
    }
    elsif (!&General::validhostname($cgiparams{'EMAIL_SERVER'})
        && !&General::validfqdn($cgiparams{'EMAIL_SERVER'}))
    {
        $errormessage .= "$Lang::tr{'email server'}: $Lang::tr{'invalid hostname'}<br/>";
    }

    if ($cgiparams{'EMAIL_SERVER_PORT'} ne '' && (!&General::validport($cgiparams{'EMAIL_SERVER_PORT'}))) {
        $errormessage .= "$Lang::tr{'email server port bad'}<br/>";
    }

    # Remove trailing break
    $errormessage =~ s/<br\/>$//;
}
