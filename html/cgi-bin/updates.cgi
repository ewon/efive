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
# updates.cgi is based on Smoothwall updates.cgi which is
# (c) The SmoothWall Team
#
# With many, many changes since 2001,
# (c) 2001-2010, the IPCop team
#
# $Id: updates.cgi 5296 2011-01-04 12:42:39Z owes $
#

# Add entry in menu
# MENUENTRY system 030 "updates" "updates"

use LWP::UserAgent;
use File::Copy;
use XML::Simple;
use strict;

# enable only the following on debugging purpose
#use warnings; no warnings 'once';# 'redefine', 'uninitialized';
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';


my $errormessage  = '';
my $available;
my $installed;
my $showfreespace = 0;
my %mainsettings  = ();
my %checked       = ();
$mainsettings{'CHECKUPDATES'} = 'off';
$mainsettings{'PRELOADUPDATES'} = 'off';

sub get_error() {
    my $exit_code = shift || return '';

    if ($exit_code == 0) {
        return '';
    }
    elsif ($exit_code == 2) {
        return "$Lang::tr{'could not create directory'}";
    }
    elsif ($exit_code == 3) {
        return "$Lang::tr{'this is not an authorised update'}";
    }
    elsif ($exit_code == 4) {
        return "$Lang::tr{'this is not a valid archive'}";
    }
    elsif ($exit_code == 5) {
        return "$Lang::tr{'could not open update information file'}";
    }
    elsif ($exit_code == 6) {
        return "$Lang::tr{'could not open installed updates file'}";
    }
    elsif ($exit_code == 7) {
        return "$Lang::tr{'this update is already installed'}";
    }
    elsif ($exit_code == 11) {
        return "$Lang::tr{'not enough disk space'}";
    }
    elsif ($exit_code == 32) {
        return "$Lang::tr{'connection is down'}";
    }
    else {
        return "$Lang::tr{'package failed to install'}";
    }
}

&Header::showhttpheaders();
&General::readhash('/var/ipcop/main/settings', \%mainsettings);

my %uploadsettings = ();
$uploadsettings{'ACTION'} = '';
$uploadsettings{'CHECKUPDATES'} = 'off';
$uploadsettings{'PRELOADUPDATES'} = 'off';
&General::getcgihash(\%uploadsettings, {'wantfile' => 1, 'filevar' => 'FH'});

if ($uploadsettings{'ACTION'} eq $Lang::tr{'upload'}) {

    # TODO: verify if we know about this .tgz.gpg file

    &General::log("installpackage", "Uploaded update file: $uploadsettings{'FH'}");

    if (copy($uploadsettings{'FH'}, "/var/patches/$uploadsettings{'FH'}") != 1) {
        $errormessage = $!;
    }
    else {
        $errormessage = &get_error(system("/usr/local/bin/installpackage --test=/var/patches/$uploadsettings{'FH'} >/dev/null") >> 8);
    }
}
elsif (index($uploadsettings{'ACTION'}, 'download-') != -1) {

    # We do not include URL in information because it does not support different arch

    my @tmp = split(/-/, $uploadsettings{'ACTION'});
    $errormessage = &get_error(&General::downloadpatch($tmp[1], 1));
}
elsif ($uploadsettings{'ACTION'} eq $Lang::tr{'apply'}) {
    my $filename = "ipcop-$uploadsettings{'APPLY_VERSION'}-update.${General::machine}.tgz.gpg";
    &General::log("installpackage", "Apply update: ${filename}");
    $errormessage = &get_error(system("/usr/local/bin/installpackage --install=/var/patches/${filename} >/dev/null") >> 8);
    if ($errormessage eq '') {

        #Hack to get correct version displayed after update
        open(XX, "/usr/bin/perl -e \"require'/usr/lib/ipcop/general-functions.pl';print \\\$General::version\"|");
        $General::version = <XX>;
        close(XX);
    }
}
elsif (index($uploadsettings{'ACTION'}, "delete-") != -1) {
    my @tmp = split(/-/, $uploadsettings{'ACTION'});
    my $filename = "ipcop-$tmp[1]-update.${General::machine}.tgz.gpg";
    &General::log("installpackage", "Delete update: ${filename}");
    unlink("/var/patches/${filename}");
    $filename = "ipcop-$tmp[1]-update.${General::machine}.sig";
    unlink("/var/patches/${filename}");
}
elsif ($uploadsettings{'ACTION'} eq $Lang::tr{'refresh update list'}) {
    my $return = 1;
    if (-e '/var/ipcop/red/active') {
        # Start gathering the information from scratch, do not zap the list if offline
        system('/bin/echo -e "<ipcop>\n</ipcop>" > /var/ipcop/patches/available.xml');
        $return = &General::downloadpatchlist();
    }
    if ($return == 0) {
        &General::log("installpackage", $Lang::tr{'successfully refreshed updates list'});
    }
    elsif ($return == 1) {
        $errormessage = $Lang::tr{'connection is down'};
    }
    elsif ($return == 2) {
        $errormessage = $Lang::tr{'could not open available updates file'};
    }
    else {
        $errormessage = $Lang::tr{'could not download the available updates list'};
    }
}
elsif ($uploadsettings{'ACTION'} eq "$Lang::tr{'clear cache'} (squid)") {
    system('/usr/local/bin/restartsquid', '-f');
}
elsif ($uploadsettings{'ACTION'} eq "$Lang::tr{'save'}") {
    $mainsettings{'CHECKUPDATES'}   = $uploadsettings{'CHECKUPDATES'};
    $mainsettings{'PRELOADUPDATES'} = $uploadsettings{'PRELOADUPDATES'};
    &General::writehash('/var/ipcop/main/settings', \%mainsettings);
}

# Read-in the XML list files installed/ready to install
$installed = eval { XMLin('/var/ipcop/patches/installed.xml') };
if ($@) {
    $errormessage = $Lang::tr{'could not open installed updates file'};
}

$available = eval { XMLin('/var/ipcop/patches/available.xml') };
if ($@) {
    $errormessage = $Lang::tr{'could not open available updates file'};
    $available->{"latest"} = ${General::version};
}

&Header::openpage($Lang::tr{'updates'}, 1, '');
&Header::openbigbox('100%', 'left', '');

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:", 'error');
    print $errormessage;
    print "&nbsp;";
    &Header::closebox();
}

my $age = &General::age("/var/ipcop/patches/available.xml");
if ($age =~ m/(\d{1,3})d/) {
    if ($1 >= 7) {
        &Header::openbox('100%', 'left', $Lang::tr{'warning messages'}, 'warning');
        print "$Lang::tr{'updates is old1'} $1 $Lang::tr{'updates is old3'}";
        &Header::closebox();
    }
}

$checked{'CHECKUPDATES'}{'off'} = '';
$checked{'CHECKUPDATES'}{'on'}  = '';
$checked{'CHECKUPDATES'}{$mainsettings{'CHECKUPDATES'}} = "checked='checked'";
$checked{'PRELOADUPDATES'}{'off'} = '';
$checked{'PRELOADUPDATES'}{'on'}  = '';
$checked{'PRELOADUPDATES'}{$mainsettings{'PRELOADUPDATES'}} = "checked='checked'";

&Header::openbox('100%', 'left', "$Lang::tr{'settings'}:");
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'><table width='100%'>
<tr>
    <td><input type='checkbox' name='CHECKUPDATES' $checked{'CHECKUPDATES'}{'on'} /></td>
    <td width='100%'>$Lang::tr{'check for updates after connect'}</td>
</tr><tr>
    <td><input type='checkbox' name='PRELOADUPDATES' $checked{'PRELOADUPDATES'}{'on'} /></td>
    <td>$Lang::tr{'preload available updates'}</td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='comment1button'>&nbsp;</td>
    <td class='button1button'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
    <td class='onlinehelp'>
    <a href='${General::adminmanualurl}/system-updates.html' target='_blank'>
    <img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a></td>
</tr>
</table></form>
END
;
&Header::closebox();

&Header::openbox('100%', 'left', "$Lang::tr{'available updates'}:");
if (defined($available->{"latest"}) && ($available->{"latest"} ne ${General::version})) {
    $showfreespace = 1;
    print <<END
<table width='100%' border='0'><tr>
    <td><b>$Lang::tr{'there are updates available'}</b></td>
    <td width='20%'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='submit' name='ACTION' value='$Lang::tr{'refresh update list'}' />
    </form></td>
</tr></table>
<table width='100%' cellpadding='2'>
<tr>
    <td colspan='6'>&nbsp;</td>
</tr>
<tr valign='bottom'>
    <td width='7%' class='boldbase'>$Lang::tr{'title'}</td>
    <td width='60%' class='boldbase'>$Lang::tr{'description'}</td>
    <td width='10%' class='boldbase'>$Lang::tr{'released'}</td>
    <td width='10%' class='boldbase'>$Lang::tr{'release notes'}</td>
    <td width='5%' class='boldbase'>$Lang::tr{'size'}</td>
    <td width='8%' class='boldbase' colspan='2'>$Lang::tr{'action'}</td>
</tr>
END
    ;
    my $number = 0;    # display download button only on first update
    my $done = 0;
    my $version = $available->{"update-${General::version}"}->{nextversion};

    while (($version ne "") && ($number < 10) && ! $done) {
        my $filename  = "ipcop-${version}-update.${General::machine}.tgz.gpg";
        my @signature = ('');

        if (open(SIGNATURE, "</var/patches/ipcop-${version}-update.${General::machine}.sig")) {
            @signature = <SIGNATURE>;
            close(SIGNATURE);

            $signature[0] = &Header::cleanhtml($signature[0]);
            $signature[1] = &Header::cleanhtml($signature[1]);
        }

        print "<tr valign='top' class='table".int(($number % 2) + 1)."colour'>";
        print <<END
    <td class='boldbase'>$version</td>
    <td>$available->{"update-${version}"}->{description}</td>
    <td>$available->{"update-${version}"}->{releasedate}</td>
    <td nowrap='nowrap'>
        <a href='http://prdownloads.sourceforge.net/ipcop/release-notes-${version}.txt?download' target='_blank'>
            notes-${version}
        </a>
    </td>
    <td nowrap='nowrap' align='right'>$available->{"update-${version}"}->{size} KiB</td>
    <td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='image' name='$Lang::tr{'download'}' value='download-${version}' src='/images/download.png' alt='download' title='$Lang::tr{'download'}' />
        <input type='hidden' name='ACTION' value='download-${version}' />
    </form></td>
END
        ;
        if (-e "/var/patches/${filename}" && ($signature[0] ne '')) {
            print <<END
    <td width='3%' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='image' name='$Lang::tr{'delete'}' src='/images/delete.gif' alt='delete' title='$Lang::tr{'delete'}' />
        <input type='hidden' name='ACTION' value='delete-${version}' />
    </form></td></tr>
END
            ;

            print "<tr valign='top' class='table".int(($number % 2) + 1)."colour'>";
            print "<td>&nbsp;</td>";
            print "<td colspan='2'>$signature[0]<br />$signature[1]</td>";

            if ($number == 0) {
                print <<END
    <td colspan='4' align='center'><form method='post' action='$ENV{'SCRIPT_NAME'}'>
        <input type='submit' name='ACTION' value='$Lang::tr{'apply'}' />
        <input type='hidden' name='APPLY_VERSION' value='${version}' />
    </form></td></tr>
END
                ;
            }
            else {
                print "<td colspan='4'>&nbsp;</td></tr>";
            }
        }
        else {
            print "<td width='4%' align='center'>&nbsp;</td></tr>";
        }

        if (defined($available->{"update-$version"}->{latest})) {
            $done = 1;
        }
        else {
            $version = $available->{"update-$version"}->{nextversion};
        }
        $number++;
    }
    print '</table>';
}
else {
    print <<END
<table width='100%' border='0'><tr>
    <td>$Lang::tr{'all updates installed'}</td>
    <td width='20%'><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='submit' name='ACTION' value='$Lang::tr{'refresh update list'}' /></form></td>
</tr></table>
END
        ;
}

print <<END
<hr />
<table>
<tr>
    <td colspan='2'>$Lang::tr{'manually upload an update'}:</td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'upload update file'}:&nbsp;</td>
    <td><form method='post' action='$ENV{'SCRIPT_NAME'}' enctype='multipart/form-data'>
        <input type="file" size='40' name="FH" /><input type='submit' name='ACTION' value='$Lang::tr{'upload'}' />
    </form></td>
    </tr>
</table>

END
    ;


if ($showfreespace) {

    # To show free space on hard disk
    open(XX, '/bin/df -B M -x rootfs -x tmpfs|');
    my @df = <XX>;
    close(XX);

    # skip first line:
    # Filesystem            Size  Used Avail Use% Mounted on
    shift(@df);
    chomp(@df);

    # discount possible patch.tgz.gpg size, (stat())[7] is size
    my $patchsize = 0;
    $patchsize = (stat('/var/patches/patch.tgz.gpg'))[7] / 1024 / 1024 if (-e '/var/patches/patch.tgz.gpg');

    # merge all lines to one single line separated by spaces
    my $all_inOneLine = join(' ', @df);

    # now get all entries in an array
    my @all_entries = split(' ', $all_inOneLine);

    # alert on rootfs available < 32MB, on /var/log 1MB
    my @alert = (32 - $patchsize, 1);
    print <<END
<hr />
<table>
<tr>
    <td colspan='7'><b>$Lang::tr{'disk usage'}:</b></td>
</tr><tr>
    <td align='left' class='boldbase'><b>$Lang::tr{'device'}</b></td>
    <td align='left' class='boldbase'><b>$Lang::tr{'mounted on'}</b></td>
    <td align='center' class='boldbase'><b>$Lang::tr{'size'}</b></td>
    <td align='center' class='boldbase'><b>$Lang::tr{'used'}</b></td>
    <td align='center' class='boldbase'><b>$Lang::tr{'free'}</b></td>
    <td align='left' class='boldbase'><b>$Lang::tr{'percentage'}</b></td>
</tr>
END
        ;

    my $count = 0;
    # loop over all entries. Six entries belong together.
    while (@all_entries > 0) {

        my $dev     = shift(@all_entries);
        if ($dev eq "/dev/disk/by-label/root") {
            $dev = `/bin/readlink -f /dev/disk/by-label/root`;
        }
        my $size    = shift(@all_entries);
        my $used    = shift(@all_entries);
        my $free    = shift(@all_entries);
        $free =~ m/^(\d+)M$/;
        my $freevalue = $1;
        my $percent = shift(@all_entries);
        my $mount   = shift(@all_entries);

        my $alertstyle = "";
        $alertstyle = "class='ipcop_error'" if ($freevalue <= $alert[$count]);
        print <<END
<tr $alertstyle>
    <td>$dev</td>
    <td>$mount</td>
    <td align='right'>$size</td>
    <td align='right'>$used</td>
    <td align='right'>$free</td>
    <td align='right'>$percent</td>
</tr>
END
            ;

        $count++;
    }
    print "</table>";
}

print <<END
<hr />
<table width='100%'>
<tr>
    <td class='comment1button'>&nbsp;</td>
    <td class='button1button'>&nbsp;</td>
    <td class='onlinehelp'>
    <a href='${General::adminmanualurl}/system-updates.html' target='_blank'>
    <img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a></td>
</tr>
</table>
END
    ;
&Header::closebox();

&Header::openbox('100%', 'left', "$Lang::tr{'installed updates'}:");
print <<END
<table width='100%'>
<tr>
    <td width='7%' class='boldbase'>$Lang::tr{'title'}</td>
    <td class='boldbase'>$Lang::tr{'description'}</td>
    <td width='10%' class='boldbase'>$Lang::tr{'released'}</td>
    <td width='10%' class='boldbase'>$Lang::tr{'installed'}</td>
</tr>
END
    ;

if (defined($installed->{"update-${General::version}"})) {
    my $number = 0;
    my $done = 0;
    my $version = ${General::version};

    while (! $done) {
        print "<tr valign='top' class='table".int(($number % 2) + 1)."colour'>";
        print <<END
    <td class='boldbase'>$version</td>
    <td>$installed->{"update-${version}"}->{description}</td>
    <td>$installed->{"update-${version}"}->{releasedate}</td>
    <td>$installed->{"update-${version}"}->{installdate}</td>
</tr>
END
        ;
        $version = $installed->{"update-$version"}->{previousversion};

        $done = 1 unless (defined($installed->{"update-$version"}->{description}));
        $number++;
    }
}
print "</table>";

&Header::closebox();

&Header::closebigbox();
&Header::closepage();
