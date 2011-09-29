#!/usr/bin/perl
#
# IPCop CGI's - base.cgi
#
# This code is distributed under the terms of the GPL
#
# (c) place a name here
#
# $Id: base.cgi 3759 2009-10-29 11:46:13Z owes $
#
#
# This file is a starting base for writting a new GUI screen using the three box model
#   Box 1 : global settings with no repetition
#   Box 2 : line editor for multiple data line
#   Box 3 : the list of data line, with edit/remove buttons
#
#   This example do the following
#   Read global settings:
#       a NAME and an interface (ITF)
#   Lines of data composed of:
#       an ipaddress (IP), an enabled/disabled options (CB), a comment (CO)
#
#   It uses the multiline module for ALL config-data reading and writing
#   Every GUI module must be converted to this behavior
#   Addons should also use this model
#
# All you need to do is
#   replace 'XY' with your app name
#   define your global $settings{'var name'}
#   define your strings translations
#   write validation code for Settings1 and Settings2
#   complete box Settings1 and Settings2 with your fields
#   adapt the sort function (numeric, IP, ....)
#   write the configuration file for your app if needed
#
#
use strict;

# to troubleshot your code, uncomment warnings and CGI::Carp 'fatalsToBrowser'
use warnings;
no warnings 'once';    # 'redefine', 'uninitialized';
use CGI::Carp 'fatalsToBrowser';

# this may help to uncomment diagnostics, Carp and cluck lines but need some files added
# use diagnostics; # need to add the file /usr/lib/perl5/5.8.x/pods/perldiag.pod before to work
# next look at /var/log/httpd/error_log , http://www.perl.com/pub/a/2002/05/07/mod_perl.html may help
#use Carp ();
#local $SIG{__WARN__} = \&Carp::cluck;

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';
require '/usr/lib/ipcop/multilines.pl';

# Files used
our $settingsfile = '/var/ipcop/XY/settings';    # global settings with no repetition
my $datafile = '/var/ipcop/XY/data';             # repeted settings (multilines)
our $configfile = '/var/ipcop/XY/XY.conf';       # Config file for application XY

# for testing purpose of base code only, autoconfiguration the file
if (-w '/var/ipcop/XY') {
    mkdir('/var/ipcop/XY');
    open(FILE, ">$settingsfile") or die "Unable to create $settingsfile\n";
    close(FILE);
    open(FILE, ">$datafile") or die "Unable to create $datafile\n";
    close(FILE);
    open(FILE, ">$configfile") or die "Unable to create $configfile\n";
    close(FILE);
}

# strings to add to languages databases or in addon language file
# this is not efficient to require different text with same translation like 'add data', 'edit data'
$Lang::tr{'XY title'}     = 'XY service';
$Lang::tr{'XY settings'}  = 'XY setup';
$Lang::tr{'XY add data'}  = 'add data';
$Lang::tr{'XY edit data'} = 'edit data';
$Lang::tr{'XY data'}      = 'XY data';

# information & log strings, no translation required
my $msg_added         = 'XY added';
my $msg_modified      = 'XY modified';
my $msg_deleted       = 'XY removed';
my $msg_datafileerror = 'XY data file error';
our $msg_configfileerror = 'XY configuration file error';

my %settings = ();

# Global settings
$settings{'NAME'}  = '';       # a text field whose content will be checked to be 'foo' or 'bar' later
$settings{'ITF'}   = '';       # an option field to select color interface
$settings{'TURBO'} = 'off';    # a checkbox field to enable something

# Repeted settings for editing the multi-line list
# Must not be saved by writehash !
$settings{'IP'}      = '';       # datalines are: IPaddress,enable,comment
$settings{'CB'}      = 'off';    # Every check box must be set to off
$settings{'COMMENT'} = '';
my @nosaved = ('IP', 'CB', 'COMMENT');    # List here ALL repeted fields. Mandatory

$settings{'ACTION'} = '';                 # add/edit/remove....
$settings{'KEY1'}   = '';                 # point record for ACTION

# Define each field that can be used to sort columns
# as well as a visual indicators variable for each.
my $sortstring = '^IP|^COMMENT';
our $sort_IP      = '';
our $sort_COMMENT = '';

# Error handling
my $errormessage = '';
my $warnmessage  = '';

&Header::showhttpheaders();

# Read needed Ipcop settings (exemple)
my %mainsettings = ();
&General::readhash('/var/ipcop/main/settings', \%mainsettings);

# Get GUI values
&Header::getcgihash(\%settings);

# Load multiline data. Do it before use in save action
our $f = new Multilines(
    filename => $datafile,
    fields   => [ 'IP', 'CB', 'COMMENT' ],
    comment  => 1,
    debug    => 1,
    debugtag => 'App XY',
);

##
## SAVE global settings
##
# Remove if no global settings are needed
if ($settings{'ACTION'} eq $Lang::tr{'save'}) {

    #Validate each fields
    if (($settings{"NAME"} ne "foo") && ($settings{"NAME"} ne "bar")) {
        $errormessage = 'Enter foo or bar in Name field';
    }

    #if (validip

    unless ($errormessage) {    # Everything is ok, save settings
        map (delete($settings{$_}), (@nosaved, 'ACTION', 'KEY1'));    # Must never be saved
        &General::writehash($settingsfile, \%settings);               # Save settings
        $settings{'ACTION'} = $Lang::tr{'save'};                      # Recreate  'ACTION'
        map ($settings{$_} = '', (@nosaved, 'KEY1'));                 # and reinit var to empty

        # Rebuild configuration file if needed
        &BuildConfiguration;
    }

ERROR:                                                                # Leave the faulty field untouched
}
else {
    &General::readhash($settingsfile, \%settings);    # Get saved settings in case we not just write them
}

## Now manipulate the multiline list with Settings2
# Basic actions are:
#   toggle the check box
#   add/update a new line
#   begin editing a line
#   remove a line
# $KEY1 contains the index of the line manipulated

## Toggle CB field.
if ($settings{'ACTION'} eq $Lang::tr{'toggle enable disable'}) {
    $f->togglebyfields($settings{'KEY1'}, 'CB');    # toggle checkbox
    $settings{'KEY1'} = '';                         # End edit mode
    &General::log($msg_modified);

    # save changes
    $f->savedata || die "$msg_datafileerror";

    # Rebuild configuration file
    &BuildConfiguration;
}

##
## ADD/UPDATE a line of configuration from Settings2
if ($settings{'ACTION'} eq $Lang::tr{'add'}) {

    # Validate inputs
    if (!&General::validip($settings{'IP'})) { $errormessage = "Specify an IP value !" }
    if (!$settings{'COMMENT'}) { $warnmessage = "no comment specified" }

    unless ($errormessage) {
        if ($settings{'KEY1'} eq '') {    #add or edit ?
                                          # insert new data line
            $f->writeline(-1, $settings{'IP'}, $settings{'CB'}, $settings{'COMMENT'});
            &General::log($msg_added);
        }
        else {

            # modify data line
            $f->writedata($settings{'KEY1'}, $settings{'IP'}, $settings{'CB'}, $settings{'COMMENT'});
            $settings{'KEY1'} = '';       # End edit mode
            &General::log($msg_modified);
        }

        # save changes
        $f->savedata || die "$msg_datafileerror";

        # Rebuild configuration file
        &BuildConfiguration;

        # if entering data line is a repetitive task, choose here to not erase fields between each addition
        map ($settings{$_} = '', @nosaved);
    }
}

## begin EDIT: move data fields to Settings2 controls
if ($settings{'ACTION'} eq $Lang::tr{'edit'}) {
    $f->readline($settings{'KEY1'}, $settings{'IP'}, $settings{'CB'}, $settings{'COMMENT'});
}
## REMOVE: remove selected line
if ($settings{'ACTION'} eq $Lang::tr{'remove'}) {
    $f->deleteline($settings{'KEY1'});
    $settings{'KEY1'} = '';    # End remove mode
    &General::log($msg_deleted);

    # save changes
    $f->savedata || die "$msg_datafileerror";

    # Rebuild configuration file
    &BuildConfiguration;
}

## Check if sorting is asked
if ($ENV{'QUERY_STRING'} =~ /$sortstring/) {
    my $newsort = $ENV{'QUERY_STRING'};
    my $actual  = $settings{'SORT_XY'};

    # Reverse actual sort or choose new column ?
    if ($actual =~ $newsort) {
        $f->setsortorder($newsort, rindex($actual, '_Rev'));
        $newsort .= rindex($actual, '_Rev') == -1 ? '_Rev' : '';
    }
    else {
        $f->setsortorder($newsort, 1);
    }
    $f->savedata;    # Synchronise file & display
    $settings{'SORT_XY'} = $newsort;
    map (delete($settings{$_}), (@nosaved, 'ACTION', 'KEY1'));    # Must never be saved
    &General::writehash($settingsfile, \%settings);
    $settings{'ACTION'} = 'SORT';                                 # Recreate an 'ACTION'
    map ($settings{$_} = '', (@nosaved,, 'KEY1'));                # and reinit var to empty
}

# Evaluate the visual sort indicator. Only one variable can contain an 'arrow'! All others are blank.
{
    my $arrow     = $Header::sortup;
    my $sortfield = 'sort_' . $settings{'SORT_XY'};
    if (rindex($sortfield, '_Rev') != -1) {
        $arrow = $Header::sortdn;
        $sortfield =~ s/_Rev//;                                   # cleanup the variable name
    }
    no strict;                                                    # next line evaluate as the variable name
    ${$sortfield} = $arrow;                                       # then assign it the sortup or sortdn symbol
}

&Header::openpage($Lang::tr{'XY title'}, 1, '');
### Remove if no Settings1 needed
&Header::openbigbox('100%', 'left', '', $errormessage);
if ($settings{'ACTION'} eq '') {                                  # First launch from GUI
                                                                  # Place here default value when nothing is initialized

}
my %checked = ();                                                 # Checkbox manipulations

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:");
    print "<font class='base'>$errormessage&nbsp;</font>";
    &Header::closebox();
}

## Change with 1.4: it is bad method to code interface names/properties inside the cgis. Another layer
## must be inserted! I have no idea on what it could be, so I use multilines to build a list of
## interfaces with properties. You can also use a simple thing like
## @ITFS =('RED','ORANGE','BLUE','GREEN') with a foreach loop;
##
my $ITFS = &buildipcopinterface;

## First box Settings1. Remove if not needed
$warnmessage = "<font color=${Header::colourred}><b>$Lang::tr{'capswarning'}</b></font>: $warnmessage"
    if ($warnmessage);

&Header::openbox('100%', 'left', $Lang::tr{'XY settings'});
print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>";

$checked{'TURBO'} = ($settings{'TURBO'} eq 'on') ? "checked='checked'" : '';

print <<END
<table width='100%'>
<tr>
    <td class='base'>Name:</td>
    <td><input type='text' name='NAME' value='$settings{'NAME'}' /></td>
    <td align='right'>Turbo:<input type='checkbox' name='TURBO' $checked{'TURBO'} /></td>
    <td align='right'>INTERFACE</td>
    <td>empty</td>
</tr>
END
    ;

#   The bad method to remove:
#   $checked{'ITF'}{'RED'} = '';
#   $checked{'ITF'}{'GREEN'} = '';
#   $checked{'ITF'}{'ORANGE'} = '';
#   $checked{'ITF'}{'BLUE'} = '';

# Create a radiobutton for each interface
$ITFS->readreset;
while (my ($DEV) = $ITFS->readbyfieldsseq('DEVICE')) {
    $checked{'ITF'}{$DEV} = $settings{'ITF'} eq $DEV ? "checked='checked'" : '';
    print
"<tr><td colspan='5'></td><td><input type='radio' name='ITF' value='$DEV' $checked{'ITF'}{$DEV} />$DEV</td></tr>";
}
print "</table><br />";

print <<END
<table width='100%'>
<hr />
<tr>
    <td class='base' width='25%'><img src='/blob.gif' align='top' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td>
    <td class='base' width='25%'>$warnmessage</td>
    <td width='50%' align='center'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
</tr>
</table>
</form>
END
    ;
&Header::closebox();    # end of Settings1
###
### End Of Remove if no Settings1 needed

## Second box is for editing an item of the list
$checked{'CB'} = ($settings{'CB'} eq 'on') ? "checked='checked'" : '';

my $buttontext = $Lang::tr{'add'};
if ($settings{'KEY1'} ne '') {
    $buttontext = $Lang::tr{'update'};
    &Header::openbox('100%', 'left', $Lang::tr{'XY edit data'});
}
else {
    &Header::openbox('100%', 'left', $Lang::tr{'XY add data'});
}

# Edited line number (KEY1) passed until cleared by 'save' or 'remove' or 'new sort order'
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<input type='hidden' name='KEY1' value='$settings{'KEY1'}' />
<table width='100%'>
<tr>
    <td class='base'>$Lang::tr{'ip address'}:</td>
    <td><input type='text' name='IP' value='$settings{'IP'}' /></td>
    <td class='base'>$Lang::tr{'enabled'}:</td>
    <td><input type='checkbox' name='CB' $checked{'CB'} /></td>
    <td class='base'>$Lang::tr{'remark'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type 'text' name='COMMENT' value='$settings{'COMMENT'}' /></td>
</tr>
</table>
<hr />
<table width='100%'>
<tr>
    <td class='base' width='50%'><img src='/blob.gif' align='top' alt='*' />&nbsp;$Lang::tr{'this field may be blank'}</td>
    <td width='50%' align='center'><input type='hidden' name='ACTION' value='$Lang::tr{'add'}' />
        <input type='submit' name='SUBMIT' value='$buttontext' />
    </td>
</tr>
</table>
</form>
END
    ;
&Header::closebox();

##
## Third box shows the list
##

# Columns headers may be a sort link. In this case it must be named in $sortstring (don't forget visual sort indicator)
&Header::openbox('100%', 'left', $Lang::tr{'XY data'});
print <<END
<table width='100%'>
<tr>
    <th width='20%' align='center'><a href='$ENV{'SCRIPT_NAME'}?IP'><b>$Lang::tr{'ip address'}</b></a>$sort_IP</th>
    <th width='70%' align='center'><a href='$ENV{'SCRIPT_NAME'}?COMMENT'><b>$Lang::tr{'remark'}</b></a>$sort_COMMENT</th>
    <th width='10%' colspan='3' class='boldbase' align='center'><b>$Lang::tr{'action'}</b></th>
</tr>
END
    ;

## Print each line of @current list
my $key = 0;
$f->readreset;    # beginning of data
for ($key = 0; $key < $f->getlinecount; $key++) {
    my ($cb, $comment, $ip) = $f->readbyfields($key, 'CB', 'COMMENT', 'IP');

    #Choose icon for checkbox
    my $gif   = '';
    my $gdesc = '';
    if ($cb eq "on") {
        $gif   = 'on.gif';
        $gdesc = $Lang::tr{'click to disable'};
    }
    else {
        $gif   = 'off.gif';
        $gdesc = $Lang::tr{'click to enable'};
    }

    #Colorize each line
    if ($settings{'KEY1'} eq $key) {
        print "<tr class='selectcolour'>";
    }
    else {
        print "<tr class='table".int(($key % 2) + 1)."colour'>";
    }
    print <<END
    <td align='center'>$ip</td>
    <td align='center'>$comment</td>
    <td align='center'>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
            <input type='hidden' name='ACTION' value='$Lang::tr{'toggle enable disable'}' />
            <input type='image' name='$Lang::tr{'toggle enable disable'}' src='/images/$gif' alt='$gdesc' title='$gdesc' />
            <input type='hidden' name='KEY1' value='$key' />
        </form>
    </td>
    <td align='center'>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
            <input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
            <input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
            <input type='hidden' name='KEY1' value='$key' />
        </form>
    </td>

    <td align='center'>
        <form method='post' action='$ENV{'SCRIPT_NAME'}'>
            <input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
            <input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' alt='$Lang::tr{'remove'}' title='$Lang::tr{'remove'}' />
            <input type='hidden' name='KEY1' value='$key' />
        </form>
    </td>
</tr>
END
        ;
}
print "</table>";

# If table contains entries, print 'Key to action icons'
if ($key) {
    print <<END
<table>
<tr>
    <td class='boldbase'>&nbsp;<b>$Lang::tr{'legend'}:&nbsp;</b></td>
    <td><img src='/images/on.gif' alt='$Lang::tr{'click to disable'}' /></td>
    <td class='base'>$Lang::tr{'click to disable'}</td>
    <td>&nbsp;&nbsp;</td>
    <td><img src='/images/off.gif' alt='$Lang::tr{'click to enable'}' /></td>
    <td class='base'>$Lang::tr{'click to enable'}</td>
    <td>&nbsp;&nbsp;</td>
    <td><img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
    <td class='base'>$Lang::tr{'edit'}</td>
    <td>&nbsp;&nbsp;</td>
    <td><img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
    <td class='base'>$Lang::tr{'remove'}</td>
</tr>
</table>
END
        ;
}

&Header::closebox();
&example();
&Header::closebigbox();
&Header::closepage();

## Build the configuration file for application XY
##
sub BuildConfiguration {
    open(FILE, ">/$configfile") or die "$msg_configfileerror\n";
    flock(FILE, 2);

    #Global settings
    print FILE "#\n#  Configuration file for application XY\n#\n\n";
    print FILE "#     do not edit manually\n";
    print FILE "#     build for Ipcop:$mainsettings{'HOSTNAME'}\n\n\n";
    print FILE "service=$settings{'NAME'}\n";
    print FILE "activate-turbo\n" if $settings{'TURBO'} eq 'on';
    print FILE "interface=$settings{'ITF'}\n\n\n";

    #write data line
    {
        my ($IP, $CB, $COMMENT);
        $f->readreset;
        while (defined($f->readlineseq($IP, $CB, $COMMENT))) {
            if ($CB eq "on") {
                print FILE "$IP\t\t\t\t\t#$COMMENT\n";
            }
            else {
                print FILE "#DISABLED $IP\t\t\t\t#$COMMENT\n";
            }
        }
    }
    close FILE;

    # Restart service
    #if (system '/usr/local/bin/restartyourhelper') {
    $errormessage = 'failure to...';
}

#
# Build a fake database representing some IPcop interfaces.
sub buildipcopinterface {
    my $itfs = new Multilines(
        filename => '',    # in memory only
        fields   => [ 'ACTIVE', 'NAME', 'DEVICE', 'CLASSCOLOR', 'IP', 'DHCPSERVER', 'TIMESERVER', 'COMMENT' ],
        comment  => 1,
        debug    => 1,
        debugtag => 'ITFS'
    );

    # Illustrate two ways for populating the data

    # Add a line at end (-1) with all fields specified
    $itfs->writeline(-1, 'on', 'Internet',  'eth0', 'RED', '134.0.0.1', 0, 0, 'Connect to internet');
    $itfs->writeline(-1, 'on', 'Internet2', 'eth1', 'RED', '0.0.0.0',   0, 0, 'Backup to internet');

    # Add by field names
    $itfs->writebyfields(
        -1,    #insert at end
        'ACTIVE'     => 'off',
        'DEVICE'     => 'eth0:0',
        'CLASSCOLOR' => 'ORANGE',
        'IP'         => '',
        'DHCPSERVER' => 0,
        'TIMESERVER' => 0,
        'NAME'       => 'DMZ-0',
        'COMMENT',   => 'share same device as Internet'
    );
    $itfs->writebyfields(
        -1,    #insert at end
        'ACTIVE'     => 'on',
        'DEVICE'     => 'eth2',
        'CLASSCOLOR' => 'GREEN',
        'IP'         => '10.0.0.100/16',
        'DHCPSERVER' => 1,
        'TIMESERVER' => 1,
        'NAME'       => 'Green1',
        'COMMENT',   => 'The secretary pool of green machine '
    );

    $itfs->writebyfields(
        -1,    #insert at end
        'ACTIVE'     => 'on',
        'DEVICE'     => 'eth3',
        'CLASSCOLOR' => 'GREEN',
        'IP'         => '10.1.0.100/16',
        'DHCPSERVER' => 1,
        'TIMESERVER' => 1,
        'NAME'       => 'Green2',
        'COMMENT',   => 'The factory pool of green machine '
    );
    $itfs->writebyfields(
        -1,    #insert at end
        'ACTIVE'     => 'on',
        'DEVICE'     => 'eth4',
        'CLASSCOLOR' => 'BLUE',
        'IP'         => '10.2.0.100/16;10.2.0.10',
        'DHCPSERVER' => 0,
        'TIMESERVER' => 1,
        'NAME'       => 'Wifi',
        'COMMENT',   => 'Roadwarriors'
    );
    return $itfs;
}

sub example() {
    &Header::openbox('100%', 'left', 'Interface summary');
    $ITFS->readreset;
    while (my ($DEV, $ACTIVE, $CLASSCOLOR, $IP, $DH, $TI, $NAME, $COMMENT) =
        $ITFS->readbyfieldsseq('DEVICE', 'ACTIVE', 'CLASSCOLOR', 'IP', 'DHCPSERVER', 'TIMESERVER', 'NAME', 'COMMENT'))
    {
        print "<p>";
        print "$NAME ($COMMENT) ";
        if ($ACTIVE eq 'on') {
            print "have ip:$IP and is class $CLASSCOLOR ";
            print "is dhcp server " if ($DH);
            print "is time server " if ($TI);
        }
        else {
            print " is disabled";
        }
        print "</p>";
    }
    &Header::closebox();
}

1
