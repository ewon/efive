#!/usr/bin/perl
#
# SmoothWall CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) The SmoothWall Team
# Copyright (c) 2002/04/13 Steve Bootes - Add source IP support
#
# $Id: fwrulesadm.cgi 4659 2010-06-08 07:24:08Z owes $
#
#
# Darren Critchley February 2003 - I added the multiple external access rules for each port forward
# A couple of things to remember when reading the code
#   There are two kinds of records in the config file, those with a number in the first field, and then 0,
#       these are port forward rules, these records will have a 0 or 0.0.0.0 in position 9 (ORIG_ADR)
#       If there is a 0, it means that there are external access rules, otherwise the port is open to ALL.
#   The second type of record is a number followed by a number which indicates that it is an external access
#   rule. The first number indicates which Portfw rule it belongs to, and the second is just a unique key.
#
# Darren Critchley - March 5, 2003 - if you come along after me and work on this page, please comment your
#       work. Put your name, and date and then your comment - it helps the person that comes along after you
#       to figure out why and how things have changed, and it is considered good coding practice
# Thanks . . .
#
# Achim Weber November - December 2003
#       I modified this file to work with BlockOutTraffic addon.
#       This is the configuration-page
#
# Achim Weber January 2004
#       Added more settings options,
#       some cosmetical changes on GUI,
#       settings are checked for validation everytime now
#
# Achim Weber Autumn 2004
#       Settings are stored in "hash-format" (&writehash, &readhash) now.
#       Added option to select position of "native" rules:
#           Append: behind BOT rules
#           Insert: before BOT rules
#       Dropped OrangeAsGreen because you can use Blue in IPCop 1.4 now.
#
# Achim Weber Autumn 2005
#       Dropped "native" rules. BOT uses its own chains and people can use
#       the CUSTOM* chains now.
#
# 6 May 2006 Achim Weber:
#       Re-worked code to use it in IPCop 1.5, renamed all variables, keys, etc.
#       from "BOT" to "FW".

# Add entry in menu
# MENUENTRY firewall 010 "firewall settings" "firewall settings"

use strict;

# enable only the following on debugging purpose
use warnings;
no warnings 'once';
use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';
require '/usr/lib/ipcop/firewall-lib.pl';

my %cgiparams;
my $saveerror    = 0;
my $errormessage = '';
my $error        = '';
my @dummy        = ($FW::configCGI, $FW::settingsfile);
undef @dummy;

&Header::showhttpheaders();

$cgiparams{'ACTION'}          = '';
$cgiparams{'IFACE_NAME'}      = '';
$cgiparams{'CON_STATE'}       = 'off';
$cgiparams{'ADV_MODE_ENABLE'} = 'off';
$cgiparams{'USE_ADMIN_MAC'}   = 'off';
$cgiparams{'SHOW_COLORS'}     = 'off';

&General::getcgihash(\%cgiparams);

my %ifacePolicies = ();
&DATA::readReadPolicies(\%FW::interfaces, \%ifacePolicies);

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'EDIT_FORM'} eq 'policy') {
    &validSavePolicy();

    if ($errormessage) {
        $saveerror = 1;
        $cgiparams{'ACTION'} = $Lang::tr{'edit'};
    }
    else {

        # no error, all right, save policies

        $ifacePolicies{$cgiparams{'IFACE_NAME'}}{'POLICY'}         = $cgiparams{'POLICY'};
        $ifacePolicies{$cgiparams{'IFACE_NAME'}}{'DEFAULT_LOG'}    = $cgiparams{'DEFAULT_LOG'};
        $ifacePolicies{$cgiparams{'IFACE_NAME'}}{'DEFAULT_ACTION'} = $cgiparams{'DEFAULT_ACTION'};
        $ifacePolicies{$cgiparams{'IFACE_NAME'}}{'ADDRESSFILTER'}    = $cgiparams{'ADDRESSFILTER'};

        &DATA::savePolicies(\%ifacePolicies);
        `/usr/local/bin/setfwrules --all < /dev/null > /dev/null 2>&1 &`;
    }
}    # end if ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'EDIT_FORM'} eq 'policy')

if ($cgiparams{'ACTION'} eq $Lang::tr{'save'} && $cgiparams{'EDIT_FORM'} eq 'settings') {

    # change '-' in mac to ':'
    $cgiparams{'ADMIN_MAC'} =~ s/-/:/g;

    &validSaveSettings();

    if ($errormessage) {
        $saveerror = 1;
        $cgiparams{'ACTION'} = $Lang::tr{'edit'};
    }
    else {    # no error, all right, save new settings
        &General::writehash($FW::settingsfile, \%cgiparams);
        `/usr/local/bin/setfwrules --all < /dev/null > /dev/null 2>&1 &`;
    }
}    # end if ($cgiparams{'ACTION'} eq $Lang::tr{'save'})

if ($cgiparams{'ACTION'} eq "logging-$Lang::tr{'toggle enable disable'}" && $cgiparams{'EDIT_FORM'} eq 'setting') {

    if ($ifacePolicies{$cgiparams{'IFACE_NAME'}}{'DEFAULT_LOG'} eq 'on') {
        $ifacePolicies{$cgiparams{'IFACE_NAME'}}{'DEFAULT_LOG'} = 'off';
    }
    else {
        $ifacePolicies{$cgiparams{'IFACE_NAME'}}{'DEFAULT_LOG'} = 'on';
    }
    &DATA::savePolicies(\%ifacePolicies);
    `/usr/local/bin/setfwrules --all < /dev/null > /dev/null 2>&1 &`;
}

if ($cgiparams{'ACTION'} eq "addressfilter-$Lang::tr{'toggle enable disable'}" && $cgiparams{'EDIT_FORM'} eq 'setting') {

    if ($ifacePolicies{$cgiparams{'IFACE_NAME'}}{'ADDRESSFILTER'} eq 'on') {
        $ifacePolicies{$cgiparams{'IFACE_NAME'}}{'ADDRESSFILTER'} = 'off';
    }
    else {
        $ifacePolicies{$cgiparams{'IFACE_NAME'}}{'ADDRESSFILTER'} = 'on';
    }
    &DATA::savePolicies(\%ifacePolicies);
    `/usr/local/bin/setfwrules --all < /dev/null > /dev/null 2>&1 &`;
}

# user input was invalid before reset,
# re-read settings from file,
# we are still in edit
if ($cgiparams{'ACTION'} eq $Lang::tr{'reset'}) {
    $cgiparams{'ACTION'} = "$Lang::tr{'edit'}";
}

# if user want to save settings and get a errormessage, we don't
# overwrite users input
unless ($saveerror) {
    &FW::readValidSettings();

    foreach my $iface (sort keys %FW::interfaces) {
        next if ($FW::interfaces{$iface}{'COLOR'} eq 'RED_COLOR');
        if (defined($FW::fwSettings{'ADMIN_' . $FW::interfaces{$iface}{'ID'}})) {
            $cgiparams{'ADMIN_' . $FW::interfaces{$iface}{'ID'}} =
                $FW::fwSettings{'ADMIN_' . $FW::interfaces{$iface}{'ID'}};
        }
        else {
            $cgiparams{'ADMIN_' . $FW::interfaces{$iface}{'ID'}} = 'off';
        }
    }

    $cgiparams{'USE_ADMIN_MAC'}   = $FW::fwSettings{'USE_ADMIN_MAC'};
    $cgiparams{'ADMIN_MAC'}       = $FW::fwSettings{'ADMIN_MAC'};
    $cgiparams{'ADV_MODE_ENABLE'} = $FW::fwSettings{'ADV_MODE_ENABLE'};
    $cgiparams{'SHOW_COLORS'}     = $FW::fwSettings{'SHOW_COLORS'};
}    # end unless ($saveerror)

my %checked;
$checked{'USE_ADMIN_MAC'}{'off'}                       = '';
$checked{'USE_ADMIN_MAC'}{'on'}                        = '';
$checked{'USE_ADMIN_MAC'}{$cgiparams{'USE_ADMIN_MAC'}} = "checked='checked'";

$checked{'ADV_MODE_ENABLE'}{'off'}                         = '';
$checked{'ADV_MODE_ENABLE'}{'on'}                          = '';
$checked{'ADV_MODE_ENABLE'}{$cgiparams{'ADV_MODE_ENABLE'}} = "checked='checked'";

$checked{'SHOW_COLORS'}{'off'}                     = '';
$checked{'SHOW_COLORS'}{'on'}                      = '';
$checked{'SHOW_COLORS'}{$cgiparams{'SHOW_COLORS'}} = "checked='checked'";

&Header::openpage($Lang::tr{'firewall settings'}, 1, '');
&Header::openbigbox('100%', 'left');

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:", 'error');
    print "<class name='base'>$errormessage\n";
    print "&nbsp;</class>\n";
    &Header::closebox();

    $error = 'error';
}

if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'EDIT_FORM'} eq 'policy') {

    &Header::openbox('100%', 'left', "$Lang::tr{'edit policy'}:", $error);

    my $tr_iface = &General::translateinterface($cgiparams{'IFACE_NAME'});
    my $blueblob = '&nbsp;';

    my %selected;
    $selected{'DEFAULT_ACTION'}{'reject'}                                                   = '';
    $selected{'DEFAULT_ACTION'}{'drop'}                                                     = '';
    $selected{'DEFAULT_ACTION'}{$ifacePolicies{$cgiparams{'IFACE_NAME'}}{'DEFAULT_ACTION'}} = "selected='selected'";

    $selected{'POLICY'}{'open'}                                             = '';
    $selected{'POLICY'}{'half-open'}                                        = '';
    $selected{'POLICY'}{'addressfilter'}                                      = '';
    $selected{'POLICY'}{'closed'}                                           = '';
    $selected{'POLICY'}{$ifacePolicies{$cgiparams{'IFACE_NAME'}}{'POLICY'}} = "selected='selected'";

    $checked{'DEFAULT_LOG'}{'off'}                                                   = '';
    $checked{'DEFAULT_LOG'}{'on'}                                                    = '';
    $checked{'DEFAULT_LOG'}{$ifacePolicies{$cgiparams{'IFACE_NAME'}}{'DEFAULT_LOG'}} = "checked='checked'";

    $checked{'ADDRESSFILTER'}{'off'}                                                   = '';
    $checked{'ADDRESSFILTER'}{'on'}                                                    = '';
    $checked{'ADDRESSFILTER'}{$ifacePolicies{$cgiparams{'IFACE_NAME'}}{'ADDRESSFILTER'}} = "checked='checked'";

    print <<END;
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%' cellpadding='0' cellspacing='5' border='0'>
<tr>
    <td align='left' class='base' width='15%' nowrap='nowrap'>
        $Lang::tr{'interface'}:
    </td>
    <td align='left' class='base'>
        <b>$tr_iface</b>
        <input type='hidden' name='IFACE_NAME' value='$cgiparams{'IFACE_NAME'}' />
    </td>
</tr>
</table>

<table width='100%' cellpadding='0' cellspacing='5' border='0'>
<tr>
    <td width='15%'>$Lang::tr{'policy'}:</td>
    <td align='left' width='85%'>
END

    # RED and Custom Interfaces (do not have COLOR defined) always have 'Closed' policy
    if (!defined($FW::interfaces{$cgiparams{'IFACE_NAME'}}{'COLOR'}) ||
        ($FW::interfaces{$cgiparams{'IFACE_NAME'}}{'COLOR'} eq 'RED_COLOR')) {
        print <<END;
        <input type="hidden" name="POLICY" value='closed' />
        <b>$Lang::tr{'policy closed'}</b>
END
    }
    else {

        print <<END;
        <select name='POLICY'>
            <option value='open' $selected{'POLICY'}{'open'}>$Lang::tr{'policy open'}</option>
END
        if ($FW::interfaces{$cgiparams{'IFACE_NAME'}}{'COLOR'} ne 'ORANGE_COLOR') {
            print "<option value='half-open' $selected{'POLICY'}{'half-open'}>$Lang::tr{'policy half-open'}</option>\n";
        }
        print <<END;
            <option value='closed' $selected{'POLICY'}{'closed'}>$Lang::tr{'policy closed'}</option>
        </select>
END
    }
    print <<END;
    </td>
</tr>
<tr>
    <td class='base'><br/>$Lang::tr{'logging'}:</td>
    <td align='left'>
        <input type="checkbox" name="DEFAULT_LOG" $checked{'DEFAULT_LOG'}{'on'} />&nbsp;
        $Lang::tr{'enable logging not matched packets'}
    </td>
</tr>
<tr>
    <td class='base'><br/>$Lang::tr{'default action'}:</td>
    <td align='left'>
        <select name='DEFAULT_ACTION'>
            <option value='drop' $selected{'DEFAULT_ACTION'}{'drop'}>DROP</option>
            <option value='reject' $selected{'DEFAULT_ACTION'}{'reject'}>REJECT</option>
        </select>
        &nbsp;$Lang::tr{'default action not matched packets'}
    </td>
</tr>
<tr>
END

    if (defined($FW::interfaces{$cgiparams{'IFACE_NAME'}}{'COLOR'}) &&
        ($FW::interfaces{$cgiparams{'IFACE_NAME'}}{'COLOR'} eq 'BLUE_COLOR')) {
        $blueblob = "<img src='/blob.gif' align='top' alt='*' />&nbsp;$Lang::tr{'use addressfilter for this interface'}";
        print <<END;
    <td class='base'><br/>$Lang::tr{'addressfilter'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td align='left'>
        <input type="checkbox" name="ADDRESSFILTER" $checked{'ADDRESSFILTER'}{'on'} />
    </td>
END
    }
    else {
        print <<END;
    <td class='base' colspan='2'>
        <input type='hidden' name='ADDRESSFILTER' value='-' />
    </td>
END
    }
    print <<END;
    </tr>
</table>
<hr />
<table width='100%' cellpadding='0' cellspacing='5' border='0'>
<tr>
    <td class='comment2buttons'>
        $blueblob
    </td>
    <td class='button2buttons'>
        <input type='hidden' name='EDIT_FORM' value='policy' />
        <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
    </td>
    <td class='button2buttons'>
END
    # if user input cause an error
    # and user want a reset, we re-read settings from settingsfile
    if ($errormessage ne '') {
        print "<input type='submit' name='ACTION' value='$Lang::tr{'reset'}' />";
    }
    else {
        print "<input type='reset' name='ACTION' value='$Lang::tr{'reset'}' />";
    }

    print <<END;
    </td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/firewall-settings.html' target='_blank'><img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>
    </td>
</tr>
</table>
</form>
END
}    # end if ($cgiparams{'ACTION'} eq $Lang::tr{'edit'} && $cgiparams{'EDIT_FORM'} eq 'policy')
else {

    # "normal" page
    &Header::openbox('100%', 'left', "$Lang::tr{'settings'}:", $error);

    print <<END;
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%' cellpadding='0' cellspacing='5' border='0'>
<tr>
    <td class='base' nowrap='nowrap'>
        $Lang::tr{'admin network'}:&nbsp;
    </td>
</tr>
END
    foreach my $iface (sort keys %FW::interfaces) {
        next if (($FW::interfaces{$iface}{'COLOR'} eq 'RED_COLOR') || ($FW::interfaces{$iface}{'COLOR'} eq 'ORANGE_COLOR'));
        my $isAdminNetwork = '';
        if ($cgiparams{'ADMIN_' . $FW::interfaces{$iface}{'ID'}} eq 'on') {
            $isAdminNetwork = "checked='checked'";
        }

        my $tr_iface = &General::translateinterface($iface);
        print <<END;
<tr>
    <td class='base' nowrap='nowrap'>
        &nbsp;
        <input type="checkbox" name="ADMIN_$FW::interfaces{$iface}{'ID'}" $isAdminNetwork />&nbsp;
        $tr_iface
    </td>
</tr>
END
    }
    print <<END;

<tr>
    <td class='base' nowrap='nowrap'>
        &nbsp;
        <input type="checkbox" name="USE_ADMIN_MAC" $checked{'USE_ADMIN_MAC'}{'on'} />&nbsp;
        $Lang::tr{'admin mac'}:&nbsp;<img src='/blob.gif' alt='*' />&nbsp;
        <input type='text' name='ADMIN_MAC' value='$cgiparams{'ADMIN_MAC'}' size='20' maxlength='17' />

    </td>
</tr>
</table>

<table width='100%' cellpadding='0' cellspacing='5' border='0'>
<tr>
    <td class='base' width='25%'>
        <br/>$Lang::tr{'adv mode'}:
    </td>
    <td align='left'>
        &nbsp;
        <input type="checkbox" name="ADV_MODE_ENABLE" $checked{'ADV_MODE_ENABLE'}{'on'} />
        &nbsp;$Lang::tr{'enabledtitle'}
    </td>
</tr><tr>
    <td class='base' width='25%'>
        <br/>$Lang::tr{'gui settings'}:
    </td>
    <td align='left' class='base' nowrap='nowrap'>
        &nbsp;
        <input type="checkbox" name="SHOW_COLORS" $checked{'SHOW_COLORS'}{'on'} />
        &nbsp;$Lang::tr{'show interface colors'} <br />
    </td>
</tr>
</table>
<hr />
<table width='100%' cellpadding='0' cellspacing='5' border='0'>
<tr>
    <td class='comment2buttons'>
        <img src='/blob.gif' align='top' alt='*' />
        &nbsp;<font class='base'>$Lang::tr{'if this is not your mac'}</font>
    </td>
    <td class='button2buttons'>
        <input type='hidden' name='EDIT_FORM' value='settings' />
        <input type='submit' name='ACTION' value='$Lang::tr{'save'}' />
    </td>
    <td class='button2buttons'>
END

    # if user input cause an error
    # and user want a reset, we re-read settings from settingsfile
    if ($errormessage ne '') {
        print "<input type='submit' name='ACTION' value='$Lang::tr{'reset'}' />";
    }
    else {
        print "<input type='reset' name='ACTION' value='$Lang::tr{'reset'}' />";
    }

    print <<END;
    </td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/firewall-settings.html' target='_blank'><img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>
    </td>
</tr>
</table>
</form>
END
}    # end "normal" page

&Header::closebox();

&Header::openbox('100%', 'left', "$Lang::tr{'interface policies'}:");
print <<END;
<div align='center'>
<table width='100%' align='center'>
<tr align="center">
    <td><strong>$Lang::tr{'name'}</strong></td>
    <td width='4%'><strong>$Lang::tr{'color'}</strong></td>
    <td><strong>$Lang::tr{'policy'}</strong></td>
    <td><strong>$Lang::tr{'logging'}</strong></td>
    <td><strong>$Lang::tr{'default action'}</strong></td>
    <td><strong>$Lang::tr{'addressfilter'}</strong></td>
    <td width='6%' class='boldbase' align='center'><strong>$Lang::tr{'action'}</strong></td>

</tr>
END

my $id = 0;
foreach my $iface (sort keys %ifacePolicies) {
    my $rowColor;
    if (   $iface eq $cgiparams{'IFACE_NAME'}
        && $cgiparams{'ACTION'}    eq $Lang::tr{'edit'}
        && $cgiparams{'EDIT_FORM'} eq 'policy')
    {
        $rowColor = "selectcolour";
    }
    else {
        $rowColor = "table".int(($id % 2) + 1)."colour";
    }

    my $tr_iface = &General::translateinterface($iface);
    my $ifaceColor = '';
    my $txtAddressfilter = '';
    if (!defined($FW::interfaces{$iface}{'COLOR'})) {
        # Either a customInterface or interface is M.I.A.
        $ifaceColor = '';
    }
    elsif ($FW::interfaces{$iface}{'COLOR'} eq 'GREEN_COLOR') {
        $ifaceColor = 'ipcop_iface_bg_green';
    }
    elsif ($FW::interfaces{$iface}{'COLOR'} eq 'BLUE_COLOR') {
        $ifaceColor = 'ipcop_iface_bg_blue';

        my $imgAddressfilter = 'off.gif';
        my $descLogging = $Lang::tr{'click to enable'};

        if ($ifacePolicies{$iface}{'ADDRESSFILTER'} eq 'on') {
            $imgAddressfilter = 'on.gif';
            $descLogging = $Lang::tr{'click to disable'};
        }

        $txtAddressfilter =  "<form method='post' name='addressfilter' action='$ENV{'SCRIPT_NAME'}'>";
        $txtAddressfilter .= "<input type='hidden' name='ACTION' value='addressfilter-$Lang::tr{'toggle enable disable'}' />";
        $txtAddressfilter .= "<input type='hidden' name='IFACE_NAME' value='$iface' />";
        $txtAddressfilter .= "<input type='hidden' name='EDIT_FORM' value='setting' />";
        $txtAddressfilter .= "<input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$imgAddressfilter' alt='$descLogging' title='$descLogging' />";
        $txtAddressfilter .= "</form>";
    }
    elsif ($FW::interfaces{$iface}{'COLOR'} eq 'ORANGE_COLOR') {
        $ifaceColor = 'ipcop_iface_bg_orange';
    }
    elsif ($FW::interfaces{$iface}{'COLOR'} eq 'RED_COLOR') {
        $ifaceColor = 'ipcop_iface_bg_red';
    }
    elsif ($FW::interfaces{$iface}{'COLOR'} eq 'IPSEC_COLOR') {
        $ifaceColor = 'ipcop_iface_bg_ipsec';
    }
    elsif ($FW::interfaces{$iface}{'COLOR'} eq 'OVPN_COLOR') {
        $ifaceColor = 'ipcop_iface_bg_ovpn';
    }

    my $imgLogging = 'off.gif';
    my $descLogging = $Lang::tr{'click to enable'};
    if ($ifacePolicies{$iface}{'DEFAULT_LOG'} eq 'on') {
        $imgLogging = 'on.gif';
        $descLogging = $Lang::tr{'click to disable'};
    }

    print <<END;
<tr class='$rowColor'>
    <td>$tr_iface</td>
    <td align='center' class='$ifaceColor'></td>
    <td align='center'>$Lang::tr{"policy $ifacePolicies{$iface}{'POLICY'}"}</td>
    <td align='center'>
        <form method='post' name='frmlog$id' action='$ENV{'SCRIPT_NAME'}'>
            <input type='hidden' name='ACTION' value='logging-$Lang::tr{'toggle enable disable'}' />
            <input type='hidden' name='IFACE_NAME' value='$iface' />
            <input type='hidden' name='EDIT_FORM' value='setting' />
            <input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$imgLogging' alt='$descLogging' title='$descLogging' />
        </form>
    </td>
    <td align='center'>\U$ifacePolicies{$iface}{'DEFAULT_ACTION'}\E</td>
    <td align='center'>$txtAddressfilter</td>
    <td align='center'>
        <form method='post' name='frm$id' action='$ENV{'SCRIPT_NAME'}'>
            <input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
            <input type='hidden' name='EDIT_FORM' value='policy' />
            <input type='hidden' name='IFACE_NAME' value='$iface' />
            <input type='image' name='$Lang::tr{'edit'}' value='$id' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}'  />
        </form>
    </td>
</tr>
END
    $id++;
}

print <<END;
</table>

</div>
END

&Header::closebox();

&Header::closebigbox();
&Header::closepage();

sub validSaveSettings
{

    my $haveAdminNetwork = 0;
    foreach my $iface (sort keys %FW::interfaces) {
        next if ($FW::interfaces{$iface}{'COLOR'} eq 'RED_COLOR');

        my $key = 'ADMIN_' . $FW::interfaces{$iface}{'ID'};
        if (defined($cgiparams{$key}) && $cgiparams{$key} eq 'on') {
            $haveAdminNetwork++;
        }
        else {
            $cgiparams{$key} = 'off';
        }
    }
    if ($haveAdminNetwork == 0) {
        $cgiparams{'ACTION'} = $Lang::tr{'edit'};
        $errormessage .= "$Lang::tr{'need admin network'}<br/>";
    }

    if ($cgiparams{'USE_ADMIN_MAC'} eq '') {
        $cgiparams{'USE_ADMIN_MAC'} = 'off';
    }
    if ($cgiparams{'USE_ADMIN_MAC'} eq 'on' && (!&General::validmac($cgiparams{'ADMIN_MAC'}))) {
        $cgiparams{'ACTION'} = $Lang::tr{'edit'};
        $errormessage .= "$Lang::tr{'mac bad'}<br/>";
    }

    if ($cgiparams{'ADV_MODE_ENABLE'} eq '') {
        $cgiparams{'ADV_MODE_ENABLE'} = 'off';
    }

    if ($cgiparams{'SHOW_COLORS'} ne 'on') {
        $cgiparams{'SHOW_COLORS'} = 'off';
    }
}

sub validSavePolicy
{
    if ($cgiparams{'DEFAULT_LOG'} ne 'on') {
        $cgiparams{'DEFAULT_LOG'} = 'off';
    }
    if ($cgiparams{'DEFAULT_ACTION'} ne 'drop' && $cgiparams{'DEFAULT_ACTION'} ne 'reject') {
        $cgiparams{'ACTION'} = $Lang::tr{'edit'};
        $errormessage .= "$Lang::tr{'invalid default action'}<br/>";
    }
    if ($cgiparams{'ADDRESSFILTER'} ne 'on' && $cgiparams{'ADDRESSFILTER'} ne '-') {
        $cgiparams{'ADDRESSFILTER'} = 'off';
    }

}
