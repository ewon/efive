#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
#
# $Id: remote.cgi 3122 2009-06-25 10:55:55Z owes $
#

# Add entry in menu
# MENUENTRY system 050 "ssh access" "ssh access"

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

my %remotesettings = ();
my %checked        = ();
my $errormessage   = '';

&Header::showhttpheaders();

$remotesettings{'ENABLE_SSH'}           = 'off';
$remotesettings{'ENABLE_SSH_PROTOCOL1'} = 'off';
$remotesettings{'ENABLE_SSH_PORTFW'}    = 'off';
$remotesettings{'ACTION'}               = '';
&General::getcgihash(\%remotesettings);

if ($remotesettings{'ACTION'} eq $Lang::tr{'save'}) {

    # not existing here indicates the box is unticked
    $remotesettings{'ENABLE_SSH_PASSWORDS'} = 'off' unless exists $remotesettings{'ENABLE_SSH_PASSWORDS'};
    $remotesettings{'ENABLE_SSH_KEYS'}      = 'off' unless exists $remotesettings{'ENABLE_SSH_KEYS'};

    &General::writehash('/var/ipcop/remote/settings', \%remotesettings);
    if ($remotesettings{'ENABLE_SSH'} eq 'on') {
        &General::log($Lang::tr{'ssh is enabled'});
        if (    $remotesettings{'ENABLE_SSH_PASSWORDS'} eq 'off'
            and $remotesettings{'ENABLE_SSH_KEYS'} eq 'off')
        {
            $errormessage = $Lang::tr{'ssh no auth'};
        }
    }
    else {
        &General::log($Lang::tr{'ssh is disabled'});
    }

    if ($remotesettings{'ENABLE_SSH_PROTOCOL1'} eq 'on') {
        &General::log($Lang::tr{'ssh1 enabled'});
    }
    else {
        &General::log($Lang::tr{'ssh1 disabled'});
    }

    system('/usr/local/bin/restartssh') == 0
        or $errormessage = "$Lang::tr{'bad return code'} $?";
}

&General::readhash('/var/ipcop/remote/settings', \%remotesettings);

# not existing here means they're undefined and the default value should be used
$remotesettings{'ENABLE_SSH_PASSWORDS'} = 'on' unless exists $remotesettings{'ENABLE_SSH_PASSWORDS'};
$remotesettings{'ENABLE_SSH_KEYS'}      = 'on' unless exists $remotesettings{'ENABLE_SSH_KEYS'};

$checked{'ENABLE_SSH'}{'off'}                                             = '';
$checked{'ENABLE_SSH'}{'on'}                                              = '';
$checked{'ENABLE_SSH'}{$remotesettings{'ENABLE_SSH'}}                     = "checked='checked'";
$checked{'ENABLE_SSH_PROTOCOL1'}{'off'}                                   = '';
$checked{'ENABLE_SSH_PROTOCOL1'}{'on'}                                    = '';
$checked{'ENABLE_SSH_PROTOCOL1'}{$remotesettings{'ENABLE_SSH_PROTOCOL1'}} = "checked='checked'";
$checked{'ENABLE_SSH_PORTFW'}{'off'}                                      = '';
$checked{'ENABLE_SSH_PORTFW'}{'on'}                                       = '';
$checked{'ENABLE_SSH_PORTFW'}{$remotesettings{'ENABLE_SSH_PORTFW'}}       = "checked='checked'";
$checked{'ENABLE_SSH_PASSWORDS'}{'off'}                                   = '';
$checked{'ENABLE_SSH_PASSWORDS'}{'on'}                                    = '';
$checked{'ENABLE_SSH_PASSWORDS'}{$remotesettings{'ENABLE_SSH_PASSWORDS'}} = "checked='checked'";
$checked{'ENABLE_SSH_KEYS'}{'off'}                                        = '';
$checked{'ENABLE_SSH_KEYS'}{'on'}                                         = '';
$checked{'ENABLE_SSH_KEYS'}{$remotesettings{'ENABLE_SSH_KEYS'}}           = "checked='checked'";

&Header::openpage($Lang::tr{'remote access'}, 1, '');

&Header::openbigbox('100%', 'left', '');

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:", 'error');
    print "<FONT CLASS='base'>$errormessage&nbsp;</FONT>\n";
    &Header::closebox();
}

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', 'SSH:');
print <<END
    <input type='checkbox' name='ENABLE_SSH' $checked{'ENABLE_SSH'}{'on'} />
    $Lang::tr{'ssh access'}
    <img src='/blob.gif' alt='*' />
<dl>
    <dd><input type='checkbox' name='ENABLE_SSH_PROTOCOL1' $checked{'ENABLE_SSH_PROTOCOL1'}{'on'} />
    $Lang::tr{'ssh1 support'}</dd>
    <dd><input type='checkbox' name='ENABLE_SSH_PORTFW' $checked{'ENABLE_SSH_PORTFW'}{'on'} />
    $Lang::tr{'ssh portfw'}</dd>
    <dd><input type='checkbox' name='ENABLE_SSH_PASSWORDS' $checked{'ENABLE_SSH_PASSWORDS'}{'on'} />
    $Lang::tr{'ssh passwords'}</dd>
    <dd><input type='checkbox' name='ENABLE_SSH_KEYS' $checked{'ENABLE_SSH_KEYS'}{'on'} />
    $Lang::tr{'ssh keys'}</dd>
</dl>
<hr />
<table width='100%'>
<tr>
    <td class='comment1button'><img src='/blob.gif' alt='*' /> $Lang::tr{'ssh access tip'}</td>
    <td class='button1button'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/system-ssh.html' target='_blank'>
        <img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>
    </td>
</tr>
</table>
END
    ;
&Header::closebox();

print "</form>\n";

&Header::openbox('100%', 'left', $Lang::tr{'ssh host keys'});

print "<table>\n";

print <<END
<tr><td class='boldbase'><b>$Lang::tr{'ssh key'}</b></td>
    <td class='boldbase'><b>$Lang::tr{'ssh fingerprint'}</b></td>
    <td class='boldbase'><b>$Lang::tr{'ssh key size'}</b></td></tr>
END
    ;

&viewkey("/etc/ssh/ssh_host_key.pub",     "RSA1");
&viewkey("/etc/ssh/ssh_host_rsa_key.pub", "RSA2");
&viewkey("/etc/ssh/ssh_host_dsa_key.pub", "DSA");
&viewkey("/etc/ssh/authorized_keys",      "x");
&viewkey("/root/.ssh/authorized_keys",    "x");

print "</table>\n";

&Header::closebox();

&Header::closebigbox();

&Header::closepage();

sub viewkey {
    my $key = $_[0];
    my $name = $_[1] || '?';

    if (-e $key) {
        my @temp        = split(/ /,                   `/usr/bin/ssh-keygen -l -f $key`);
        my $keysize     = &Header::cleanhtml($temp[0], "y");
        my $fingerprint = &Header::cleanhtml($temp[1], "y");
        print "<tr><td>$key ($name)</td><td><code>$fingerprint</code></td><td align='center'>$keysize</td></tr>\n";
    }
}
