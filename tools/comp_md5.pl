#!/usr/bin/perl
#
############################################################################
#                                                                          #
# This file is part of the IPCop Firewall.                                 #
#                                                                          #
# IPCop is free software; you can redistribute it and/or modify            #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPCop is distributed in the hope that it will be useful,                 #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPCop; if not, write to the Free Software                     #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
#                                                                          #
# $Id: comp_md5.pl 5591 2011-04-04 16:14:31Z owes $
#                                                                          #
############################################################################

use Fcntl ':mode';

my ( $file_version, $file_previousversion, $file_update, $file_known );
my ( %md5_version, %md5_previousversion, %update, %known );
my $kernel_update = 'ABCnevermatches';
my $squid_langpack_update = 'ABCnevermatches';

# We want a total of 6 parameters
# BaseDirectory, version, previous version, machine, KVER, PERLVER
if (defined($ARGV[0]) && defined($ARGV[1]) && defined($ARGV[2]) &&
        defined($ARGV[3]) && defined($ARGV[4]) && defined($ARGV[5])) {
    $BASEDIR    = "$ARGV[0]";
    $MACHINE    = "$ARGV[3]";
    $KVER       = "$ARGV[4]";
    $PERLVER    = "$ARGV[5]";
    $file_version = "$BASEDIR/doc/IPCop-$ARGV[1]-all-files-list.$MACHINE.txt.md5";
    $file_previousversion = "$BASEDIR/doc/IPCop-$ARGV[2]-all-files-list.$MACHINE.txt.md5";
    $file_update = "$BASEDIR/updates/$ARGV[1]/ROOTFILES.$MACHINE-$ARGV[1]";
    $file_known = "$BASEDIR/doc/files-with-different-md5";
}
else {
    die "Parameters missing";
}

# Check whether files exist
die "$file_version not found" unless (-e $file_version);
die "$file_previousversion not found" unless (-e $file_previousversion);
die "$file_update not found" unless (-e $file_update);
die "$file_known not found" unless (-e $file_known);

open (LIST, "$file_update") or die "Unable to open $file_update";
while (<LIST>) {
    next if $_ =~ m/^#/;
    chomp($_);
    $update{$_} = 1;
    # Special hack to filter all kernel modules in case of kernel update
    $kernel_update = $_ if ($_ =~ /^\/lib\/modules\/.*\/kernel$/);
    # Special hack to filter squid langpack found in /usr/lib/squid/errors and /usr/lib/squid/errors.ipcop
    $squid_langpack_update = $_ if ($_ =~ /^\/usr\/lib\/squid\/errors$/);
}
close (LIST);

# Parameter 7 is optional, when used we have update split into 2 packages
if (defined($ARGV[6])) {
    $file_update = "$BASEDIR/updates/$ARGV[6]/ROOTFILES.$MACHINE-$ARGV[6]";
    open (LIST, "$file_update") or die "Unable to open $file_update";
    while (<LIST>) {
        next if $_ =~ m/^#/;
        chomp($_);
        $update{$_} = 1;
        # Special hack to filter all kernel modules in case of kernel update
        $kernel_update = $_ if ($_ =~ /^\/lib\/modules\/.*\/kernel$/);
        # Special hack to filter squid langpack found in /usr/lib/squid/errors and /usr/lib/squid/errors.ipcop
        $squid_langpack_update = $_ if ($_ =~ /^\/usr\/lib\/squid\/errors$/);
    }
    close (LIST);
}

open (LIST, "$file_version") or die "Unable to open $file_version";
while (<LIST>) {
    next if $_ =~ m/^#/;
    chomp($_);
    my @temp = split(/ /,$_);
    next if ($temp[2] =~ /^${kernel_update}/);
    next if ($temp[2] =~ /^${squid_langpack_update}/);
    $md5_version{$temp[2]} = $temp[0];
}
close (LIST);

open (LIST, "$file_previousversion") or die "Unable to open $file_previousversion";
while (<LIST>) {
    next if $_ =~ m/^#/;
    chomp($_);
    my @temp = split(/ /,$_);
    $md5_previousversion{$temp[2]} = $temp[0];
}
close (LIST);

open (LIST, "$file_known") or die "Unable to open $file_known";
while (<LIST>) {
    next if $_ =~ m/^#/;
    chomp($_);
    s/KVER/$KVER/g;
    s/MACHINE/$MACHINE/g;
    s/PERLVER/$PERLVER/g;
    my @temp = split(/\s+/,$_);
    $known{$temp[0]} = 1;
}
close (LIST);

# To debug, replace 0 => 1
if (0) {
    print "size of known hash:  " . keys( %known ) . ".\n";
    for my $key ( keys %known ) {
        my $value = $known{$key};
        print "$key => $value\n";
    }
}

open (OUTLIST, ">diff.tmp") or die "Unable to create diff list";
print OUTLIST "# Comparing md5 for each file in $ARGV[1] to $ARGV[2]\n";
print OUTLIST "UPDATEK $kernel_update\n" if ($kernel_update ne 'ABCnevermatches');
print OUTLIST "UPDATESLP $squid_langpack_update\n" if ($squid_langpack_update ne 'ABCnevermatches');

for my $file (sort keys %md5_version) {
    if (!defined($md5_previousversion{$file})) {
        if (defined($update{$file})) {
            print OUTLIST "NEWUPD  $file\n";
        }
        else {
            print OUTLIST "NEW     $file\n";
        }
        next;
    }

    next if ($md5_version{$file} eq $md5_previousversion{$file});

    if (defined($update{$file})) {
        # This one is different but we already have it in update
        print OUTLIST "UPDATE  $file\n";
        next;
    }

    if (defined($known{$file})) {
        # This one is different and we know about
        print OUTLIST "KNOWN   $file\n";
        next;
    }

    if (($file =~ /^\/lib\/.*/) || ($file =~ /^\/usr\/lib\/.*/)) {
        my $mode = (lstat("${BASEDIR}/build_${MACHINE}/ipcop/$file"))[2];
        if (S_ISLNK($mode)) {
            print OUTLIST "SYMLINK $file\n";
            next;
        }
    }

    # Hello, major hack. Find the package that causes the difference.
    my $file_in_rootfile = substr($file, 1);
    if ($file_in_rootfile eq 'usr/bin/[') { $file_in_rootfile = 'usr/bin/\['; } # simple escape
    my $rootfile = `grep -l "^${file_in_rootfile}\$" $BASEDIR/config/rootfiles/common/* $BASEDIR/config/rootfiles/arch_$MACHINE/*`;
    chomp($rootfile);
    if (-e "$rootfile") {
        $rootfile = `basename $rootfile`;
        chomp($rootfile);
    }
    else {
        # Try again with MACHINE and PERLVER replaced to find CPAN packages
        $file_in_rootfile =~ s/$MACHINE/MACHINE/;
        $file_in_rootfile =~ s/$PERLVER/PERLVER/;
        $rootfile = `grep -l "^${file_in_rootfile}\$" $BASEDIR/config/rootfiles/common/* $BASEDIR/config/rootfiles/arch_$MACHINE/*`;
        chomp($rootfile);
        if (-e "$rootfile") {
            $rootfile = `basename $rootfile`;
            chomp($rootfile);
        }
    }
    printf OUTLIST "DIFF    %-60s %s\n", $file, $rootfile;
}
close (OUTLIST);

system("sort diff.tmp > $BASEDIR/doc/IPCop-$ARGV[1]-diff-list.$MACHINE.txt");
system("rm diff.tmp");
