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
# Copyright (C) 2005-10-25 Franck Bourdonnec
#
# $Id: multilines.pl 2993 2009-06-07 12:41:51Z owes $
#
#
package Multilines;
use strict;

#
# PURPOSE: manipulation of repetitive config lines
#
# +----start of text file--
# | x,y,z
# | a,b,c
# +----end of text file --
#
# This example file contains two lines, three fields in each line, comma separated.
#

#
# log ("tag","message")
#
sub log ($,$)
{
    my $tag = shift;
    $_ = shift;
    $_ =~ /([\w\W]*)/;
    system('logger', '-t', $tag, $1);
}

#
# create the object
#
# parameters are passed in a hash form, eg  'var'=>'value';
# my $L = new multines(
#		filename=>'the data file'	needed!
#		fields=>\@list,			by ref, contains a list a fields name, optional
#		debug=>0,			set to 1 to print some debug message
#		debugtag=>'config',		use a tag for debug message
#		separator=>','			default to ',' but can be tab or a any string
#		autosave=>'0'			issue a savedata() after each edition of a line.
#		sort=>''			specify a field name to sort on when reading
#		sortrev='1'			set to  >0 up, <0 down
#		comment='0'			set to 1 add description of the file
#		commenttext=''			optional text added
#		commentchar='#'			line beginning with this are ignored
#
#
sub new($)
{
    my $type = shift;    # (object programming)
    my $this = {};       # create the object in a hash (classic)
    bless $this, $type;  # 'tag' the object

    my %p = @_;          # store remaining params in a hash;
    $this->{_filename} = $p{filename} || '';
    $this->{_fields}   = $p{fields};
    $this->{_debug}    = $p{debug} || 0;
    $this->{_debugtag} = $p{debugtag} || 'config';

    if ($this->{_debug}) {
        &log($this->{_debugtag}, "Data file: $this->{_filename}");
        $this->listfields;
    }

    # init other values
    $this->{_sep}      = $p{separator} || ',';
    $this->{_autosave} = $p{autosave}  || '0';
    $this->{_modified}    = 0;                                                 # true when modified
    $this->{_toggle}      = $p{toggle} || 'off,on';                            # default value for boolean fields
    $this->{_sort}        = $p{sort} || '';                                    # a sort field when reading lines
    $this->{_sortrev}     = $p{sortrev} || '1';                                # a sort field when reading lines
    $this->{_sorted}      = 0;                                                 # not sorted
    $this->{_comment}     = $p{comment} || '0';
    $this->{_commenttext} = $p{commenttext} || '';
    $this->{_commentchar} = defined $p{commentchar} ? $p{commentchar} : '#';
    my @lines = ();                                                            # the line are here
    $this->{_lines} = \@lines;                                                 # ref to @lines
                                                                               #load the file
    $this->readfile;
    $this->readreset;
    return $this;                                                              # return the object
}

#
# Add lines from a file. This can be used to collect lines from multiple source. Remenber
# that it results only in a one file when saving
#
# Optional param: filemane to load
#
sub readfile($)
{
    my $this = shift;
    my $fn = shift || $this->{_filename};
    return if (!$fn);

    #read in the file if present
    if (!open(FILE, $fn)) {
        &log($this->{_debugtag}, "File not found:$fn ") if ($this->{_debug});
    }
    else {
        my @lines = <FILE>;    # read in data
        close(FILE);

        # remove end of line character
        chomp(@lines);

        # remove commented lines
        if ($this->{_commentchar} ne '') {
            for (my $y = @lines - 1; $y >= 0; $y--) {
                splice(@lines, $y, 1) if ($lines[$y] =~ /^[ \t]*$this->{_commentchar}/);
            }
        }
        @{$this->{_lines}} = (@{$this->{_lines}}, @lines);    # add new lines to existing list
        if ($this->{_debug}) {
            &log($this->{_debugtag}, "Read " . @lines . " more lines");
            $this->listlines;                                 # I know this lists all lines, not only added lines!
        }
        $this->{_sorted} = 0;
    }
}

#
# Used in conjunction with readdataseq/readbyfieldsseq. Position read pointer to first line.
sub readreset($)
{
    my $this = shift;
    $this->{_index} = 0;                                      # for sequential read/loop
    $this->sortdata;
}

#
# Get/Set index line used by readdataseq
sub index()
{
    my ($this, $v) = @_;
    $this->{_index} = $v if ((@_ > 1) && ($v < @{$this->{_lines}}) && ($v >= 0));
    return $this->{_index};                                   # for sequential read/loop
}

#
# Return the number of lines in the list
sub getlinecount($)
{
    my $this = shift;
    return scalar(@{$this->{_lines}});
}

#
# setsortorder
#
# Params: fieldname, [rev]
sub setsortorder
{
    my $this = shift;
    $this->{_sort}    = shift || '';
    $this->{_sortrev} = shift || 1;
    $this->{_sorted}  = 0;
    $this->{_modified} = 1;    #not really but keep in sync memory represention and real file
    $this->readreset;
}

#
# deletefields (fieldname,...);
# Use this to delete an entire column of data
#
sub deletefields($)
{
    my $this = shift;
    if (scalar(@_) > 1) {      # a least one field!
        foreach my $col (@_) {
            my $f_index = 0;    # locate fields index first
            foreach my $f (@{$this->{_fields}}) {
                last if ($col eq $f);
                $f_index++;
            }
            if ($f_index == @{$this->{_fields}}) {
                &log($this->{_debugtag}, "Unknown field $col in deletefields.") if ($this->{_debug});
            }
            else {

                #delete
                splice(@{$this->{_fields}}, $f_index, 1);    # kill field name
                if ($col eq $this->{_sort}) {                # no more a sort field
                    $this->{_sort}    = '';
                    $this->{_sortrev} = 1;
                    $this->{_sorted}  = 0;
                }

                # delete field data in each lines
                for (my $line = 0; $line < @{$this->{_lines}}; $line++) {
                    my @fields = split($this->{_sep}, $this->{_lines}->[$line]);
                    splice(@fields, $f_index, 1);            # kill field
                    $this->{_lines}->[$line] = join($this->{_sep}, @fields);
                }
                $this->{_modified} = 1;                      # modified
            }
            $this->savedata() if ($this->{_autosave});
        }
        return 1;    #why 1 what does it mean, we should standardize to 0=success everything else is error or special
    }
    return 0;
}

#
# get a line of data. Each field of the line fills the passed parameters in sequence.
# return the index of the line read
# return undef when last line is read
# 	$L->readreset;
#	while ( defined( $z=$L->readlineseq($x,$y) ) ) {
#    		print "ligne $z contains $x, $y\n";
#    	};
#
#  Calling 'new' or 'readreset' moves read pointer to first line.
#  This sub is for sequential access
#
sub readlineseq($)
{
    my $this = shift;
    if ($this->{_index} < @{$this->{_lines}}) {    # end of table reached ?
            #split line in separate field, then copy each field into passed parameters
        my @fields = split($this->{_sep}, $this->{_lines}->[ $this->{_index} ]);
        for my $index (0 .. scalar(@_)) {    #how many variable passed to readdata?
            @_[$index] = ($index < scalar(@fields)) ? $fields[$index] : undef;
        }
        return $this->{_index}++;            # return index of the line
    }
    else {

        # $this->readreset; 			# prepare next loop
        return undef;                        # nothing more to read
    }
}

#
# Read a line
# readline(index,arglist...);
#  fields values are returned in passed args
# Returns 1 when success
# we should standardize to 0=success 1 or greater=failure
#
sub readline($)
{
    my $this = shift;
    if (scalar(@_) > 0) {
        my $line = shift;
        if (($line < @{$this->{_lines}}) && ($line >= 0)) {

            # valid line requested ?
            #split line in separate field, then copy each field into passed parameters
            my @fields = split($this->{_sep}, $this->{_lines}->[$line]);
            for my $index (0 .. scalar(@_)) {

                #how many variable passed to readdata?
                @_[$index] = ($index < scalar(@fields)) ? $fields[$index] : undef;
            }
            return 1;    # we should standardize to 0=success everything else is error or special
        }
    }
    return 0;
}

#
# Write a full line a data.
# writeline (index, argslist...);
# index: select the line to be modified. index 0 points first line.
# 	 if index is -1, then insert a new line a data a end of list.
#	  return 1 if successfull.
# arglists:
#	 pass any data here. They fill fields sequentially.
#
# return 0 if index is outbound.
# we should standardize to 0=success everything else is error or special
sub writeline
{
    my $this = shift;
    if (scalar(@_) > 1) {    # a least a field and the line index needed!
        my $line = shift;
        if (($line < @{$this->{_lines}}) && ($line >= -1)) {

            # valid line requested ?
            $line = @{$this->{_lines}} if ($line == -1);    # if -1 then insert a new line
            my @fields = split($this->{_sep}, $this->{_lines}->[$line]);

            #copy each field from passed parameters
            for my $index (0 .. scalar(@_) - 1) {

                # how many variable passed to writeline?
                $fields[$index] = @_[$index];
            }
            $this->{_modified} = 1;                         # modified (optimize:if values doestn't change=>0)
            $this->{_sorted}   = 0;                         # not sorted
            $this->{_lines}->[$line] = join($this->{_sep}, @fields);
            $this->savedata() if ($this->{_autosave});
            return 1;
        }
    }
    return 0;
}

#
# Insert a full line a data.
# insertline (index, argslist...);
# index: position of the line to be inserted. Use getlinecount to insert a last position.
# arglists:
#	 pass any data here. They fill fields sequentially.
#
# return 0 if index is outbound.
#
sub insertline
{
    my $this = shift;
    if (scalar(@_) > 1) {

        # a least a value to change and the line index needed!
        my $line = shift;
        if (($line <= @{$this->{_lines}}) && ($line >= 0)) {    # valid line requested ?
            my @fields = ();

            #copy each field from passed parameters
            for my $index (0 .. scalar(@_) - 1) {               # how many variable passed to insertline?
                $fields[$index] = @_[$index];
            }
            $this->{_modified} = 1;                             # modified
            $this->{_sorted}   = 0;                             # not sorted
            splice(@{$this->{_lines}}, $line, 0, join($this->{_sep}, @fields));
            $this->savedata() if ($this->{_autosave});
            return 1;
        }
    }
    return 0;
}

#
# Swap two lines.
# swaplines (index, index);
# index: position of the line to be inserted. Use getlinecount to insert a last position.
# arglists:
#	 pass any data here. They fill fields sequentially.
#
# return 0 if line not found.
#
sub swaplines
{
    my $this = shift;
    if (scalar(@_) > 1) {

        # a least a value to change and the line index needed!
        my $line1 = shift;
        my $line2 = shift;
        if (   ($line1 <= @{$this->{_lines}})
            && ($line1 >= 0)
            && ($line2 <= @{$this->{_lines}})
            && ($line2 >= 0)
            && ($line1 != $line2))
        {

            # valid line requested ?
            ($this->{_lines}->[$line2], $this->{_lines}->[$line1]) =
                ($this->{_lines}->[$line1], $this->{_lines}->[$line2]);
            $this->{_modified} = 1;    # modified
            $this->{_sorted}   = 0;    # not sorted
            $this->savedata() if ($this->{_autosave});
            return 1;
        }
    }
    return 0;
}

#
# deleteline (index)
sub deleteline
{
    my $this = shift;
    if (scalar(@_) == 1) {    # only line index needed
        my $line = shift;
        if (($line < @{$this->{_lines}}) && ($line >= 0)) {

            # valid line requested
            splice(@{$this->{'_lines'}}, $line, 1);
            $this->{_modified} = 1;    # modified
            $this->savedata() if ($this->{_autosave});
            return @{$this->{'_lines'}};    # number of remaining lines
        }
    }
    return 0;
}

#
# Call a callback for each lines with fields passed as parameters
#   sub callback { my ($a,$b,$c)=@_; print "field1=$a, field2=$b, field3=$c\n";}
#   $L->foreachline (\&callback);
sub foreachline($ $)
{
    my $this = shift;
    my $proc = shift;
    return if (ref($proc) ne 'CODE');
    foreach my $line (@{$this->{_lines}}) {
        &$proc(split($this->{_sep}, $line));
    }
}

#
#Get value by field names. Fields names must match those provided at object creation
# $L->readreset;
# while (   ($f1,$f2,$f3) = $L->readbyfields('field_name3','field_nameX')   ) {
#	print "field_name3=$f1 field_nameX=$f2 \n";
# }
# last variable ($f3), if specified, contain the line index.
sub readbyfieldsseq
{
    my $this = shift;
    if ($this->{_index} < @{$this->{_lines}}) {

        # end of table reached
        my @fields = split($this->{_sep}, $this->{_lines}->[ $this->{_index} ]);
        my @response = ();

        # lookup if a field asked exists
        foreach my $x (@_) {
            my $f_index = 0;
            my $xx      = $x;
            foreach my $f (@{$this->{_fields}}) {
                if ($x eq $f) {
                    push(@response, $fields[$f_index]);
                    $xx = '';    # for debugging
                    last;
                }
                $f_index++;
            }
            &log($this->{_debugtag}, "Unknown field $xx in readbyfieldsseq.") if ($xx && $this->{_debug});
        }
        return (@response, $this->{_index}++);
    }
    else {
        $this->readreset;        # prepare next loop
        return ();               # empty list, indicate to caller it's done.
    }
}

sub readbyfields
{
    my $this = shift;
    my $line = shift;
    if (($line < @{$this->{_lines}}) && ($line >= 0)) {

        # valid line requested ?
        my @fields = split($this->{_sep}, $this->{_lines}->[$line]);
        my @response = ();

        # lookup if a field asked exists
        foreach my $x (@_) {
            my $f_index = 0;
            my $xx      = $x;
            foreach my $f (@{$this->{_fields}}) {
                if ($x eq $f) {
                    push(@response, $fields[$f_index]);
                    $xx = '';    # for debugging
                    last;
                }
                $f_index++;
            }
            &log($this->{_debugtag}, "Unknown field $xx in readbyfields.") if ($xx && $this->{_debug});
        }
        return (@response);
    }
    else {
        return ();
    }
}

#
# Write a some fields in line a data.
# writebyfields (index, argslist)
# index: select the line to be modified. index 0 points first line.
# 	 if index is -1, then insert a new line a data a end of list.
#	  return 1 if successfull.
# arglists:
#		'field_name'=>'value',...
#
# return 0 if line not found.
sub writebyfields
{
    my $this = shift;
    if (scalar(@_) > 1) {

        # a least a value to change and the line index needed!
        my $line = shift;
        if (($line < @{$this->{_lines}}) && ($line >= -1)) {

            # valid line requested
            # if -1 then insert a new line
            $line = @{$this->{_lines}} if ($line == -1);
            my @fields = split($this->{_sep}, $this->{_lines}->[$line]);
            my %p = @_;
            foreach my $x (keys %p) {
                my $f_index = 0;
                my $xx      = $x;
                foreach my $f (@{$this->{_fields}}) {
                    if ($x eq $f) {
                        $fields[$f_index]  = $p{$x};
                        $this->{_modified} = 1;        # modified
                        $this->{_sorted}   = 0;        # not sorted
                        $xx                = '';       # for debugging
                        last;
                    }
                    $f_index++;
                }
                &log($this->{_debugtag}, "Unknown field $xx in writebyfields.") if ($xx && $this->{_debug});
            }
            $this->{_lines}->[$line] = join($this->{_sep}, @fields);
            $this->savedata() if ($this->{_autosave});
            return 1;
        }
    }
    return 0;
}

#
# toggle a 'boolean' field.
# togglebyfields (index, filedlist)
# index: select the line to be modified. index 0 points first line.
# arglists:
#		'field_name',...
#
# return 0 if line not found.
sub togglebyfields
{
    my $this = shift;
    if (scalar(@_) > 1) {

        # a least a value to change and the line index needed!
        my $line = shift;
        if (($line < @{$this->{_lines}}) && ($line >= 0)) {

            # valid line requested ?
            my @fields = split($this->{_sep}, $this->{_lines}->[$line]);
            my @states = split(',', $this->{_toggle});
            foreach my $x (@_) {
                my $f_index = 0;
                my $xx      = $x;
                foreach my $f (@{$this->{_fields}}) {
                    if ($x eq $f) {
                        $fields[$f_index] = ($fields[$f_index] eq $states[1]) ? $states[0] : $states[1];
                        $this->{_modified} = 1;     # modified
                                                    #$this->{_sorted} = 0; 			# notsorted
                        $xx                = '';    # for debugging
                        last;
                    }
                    $f_index++;
                }
                &log($this->{_debugtag}, "Unknown field $xx in togglebyfields.") if ($xx && $this->{_debug});
            }
            $this->{_lines}->[$line] = join($this->{_sep}, @fields);
            $this->savedata() if ($this->{_autosave});
            return 1;
        }
    }
    return 0;
}

#
# toggle some fields in line a data.
# togglebyfieldsx (index, argslist)
# index: select the line to be modified. index 0 points first line.
# arglists:
#		'field_name'=>'off,on',...
#	here the value contains the two possible states of the field.
#	When no state matches actual value of field, second state in list is used.
# return 0 if line not found.
sub togglebyfieldsx
{
    my $this = shift;
    if (scalar(@_) > 1) {    # a least a value to change and the line index needed!
        my $line = shift;
        if (($line < @{$this->{_lines}}) && ($line >= 0)) {

            # valid line requested
            my @fields = split($this->{_sep}, $this->{_lines}->[$line]);
            my %p = @_;
            foreach my $x (keys %p) {
                my $f_index = 0;
                my $xx      = $x;
                foreach my $f (@{$this->{_fields}}) {
                    if ($x eq $f) {
                        my @states = split(',', $p{$x});
                        if (@states == 2) {
                            $fields[$f_index] = ($fields[$f_index] eq $states[1]) ? $states[0] : $states[1];
                            $this->{_modified} = 1;    # modified
                                                       #$this->{_sorted} = 0; 		# not sorted
                        }
                        elsif ($this->{_debug}) {
                            &log($this->{_debugtag}, "Togglebyfieldx received bad states list <$p{$x}>!");
                        }
                        $xx = '';                      # for debugging
                        last;
                    }
                    $f_index++;
                }
                &log($this->{_debugtag}, "Unknown field $xx in togglebyfieldsx.") if ($xx && $this->{_debug});
            }
            $this->{_lines}->[$line] = join($this->{_sep}, @fields);
            $this->savedata() if ($this->{_autosave});
            return 1;
        }
    }
    return 0;
}

#
# All work is done in memory table. When finished editing data,
# you need to save them to the real file.
#
# Return 1 is success writing file
sub savedata
{
    my $this    = shift;
    my $newname = shift;

    # Write if a newname is specified or if data is modified
    return 1 if (!$this->{_modified} && !$newname);

    #change filename asked?
    $this->{_filename} = $newname  if ($newname);
    $this->{_filename} = "&STDOUT" if (!$this->{_filename});
    if (open(FILE, ">$this->{_filename}")) {
        if ($this->{_comment}) {
            print FILE "$this->{_commentchar}\n";
            print FILE "$this->{_commentchar} $this->{_commenttext}\n$this->{_commentchar}\n"
                if ($this->{_commenttext} ne '');
            print FILE "$this->{_commentchar} '$this->{_filename}'\n";
            print FILE "$this->{_commentchar}\n";
            print FILE "$this->{_commentchar} Field list is: ";
            foreach my $x (@{$this->{_fields}}) {
                print FILE "$x ";
            }
            print FILE "\n$this->{_commentchar} Field separator is:";
            print FILE ($this->{_sep} eq "\t") ? '<TAB>' : $this->{_sep};
            print FILE "\n";
            print FILE "$this->{_commentchar}\n";
        }
        foreach my $x (@{$this->{_lines}}) {
            print FILE "$x\n";
        }
        close(FILE);
        $this->{_modified} = 0;    # now not modified
        return 1;
    }
    else {
        &log($this->{_debugtag}, "File error write on $this->{_filename}") if ($this->{_debug});
        return 0;
    }
}

#
# The destructor object. Warn if not saved data
sub DESTROY
{
    my $this = shift;
    &log($this->{_debugtag}, "Warning, data not saved to file.") if ($this->{_modified} && $this->{_debug});
}

#
# some helper subs
#
sub listfields($)
{
    my $this = shift;
    &log($this->{_debugtag}, "Fields list is:");

    foreach my $y (0 .. @{$this->{_fields}} - 1) {
        &log($this->{_debugtag}, "field $y: $this->{'_fields'}->[$y]");
    }
}

sub listlines($)
{
    my $this = shift;
    foreach my $x (@{$this->{_lines}}) {
        &log($this->{_debugtag}, "$x");
    }
}

#
# internal use, sort the list
sub sortdata($)
{
    our $this = shift;
    return if ($this->{_sorted});        #sorted
    return if ($this->{_sort} eq '');    #no field specified

    if (!grep (/^$this->{_sort}$/, @{$this->{_fields}})) {
        &log($this->{_debugtag}, "Unknown sort field <$this->{_sort}> in sortdata") if ($this->{_debug});
        return;
    }
    our %entries = ();

    # Sort pair of record received in $a $b special vars.
    # Choose numeric, IP, then alpha comparison
    sub sortproc
    {
        my $va  = $entries{$a}->{$this->{_sort}};
        my $vb  = $entries{$b}->{$this->{_sort}};
        my $na  = $va =~ /^\d+$/;
        my $nb  = $vb =~ /^\d+$/;
        my $ipa = $va =~ /\d+.\d+.\d+.\d+.*/;       #ip [with mask]?
        my $ipb = $vb =~ /\d+.\d+.\d+.\d+.*/;       #ip [with mask]?
        &log($this->{_debugtag}, "Comparing $va $vb ($this->{_sort}) na=$na, nb=$nb, ipa=$ipa, ipb=$ipb.")
            if ($this->{_debug});
        if     ($this->{_sortrev} < 1) {

            if ($ipa && $ipb) {
                my @a = split(/\./, $va);
                my @b = split(/\./, $vb);
                       ($b[0] <=> $a[0])
                    || ($b[1] <=> $a[1])
                    || ($b[2] <=> $a[2])
                    || ($b[3] <=> $a[3]);
            }
            elsif ($na && $nb) {
                $vb <=> $va;
            }
            else {
                $vb cmp $va;
            }
        }
        else {

            #not reverse
            if ($ipa && $ipb) {
                my @a = split(/\./, $va);
                my @b = split(/\./, $vb);
                       ($a[0] <=> $b[0])
                    || ($a[1] <=> $b[1])
                    || ($a[2] <=> $b[2])
                    || ($a[3] <=> $b[3]);
            }
            elsif ($na && $nb) {
                $va <=> $vb;
            }
            else {
                $va cmp $vb;
            }
        }
    }

    #Use an associative array (%entries)
    my $key = 0;
    foreach my $line (@{$this->{_lines}}) {
        my @fields = split($this->{_sep}, $line);

        #build a hash with KEY=>$key, fieldsname=>fieldvalue
        my @record = ('KEY', $key++);
        foreach my $y (0 .. @{$this->{_fields}} - 1) {

            # push pairs 'field,value'
            push(@record, $this->{'_fields'}->[$y]);
            push(@record, $fields[$y]);
        }
        my $record = {};    # create a reference to empty hash
        %{$record} = @record;    # populate that hash with @record
        $entries{$record->{KEY}} = $record;    # add this to a hash of hashes
    }
    $this->{_lines} = [];                      # free list
                                               #rebuild the lists of lines
    foreach my $entry (sort sortproc keys %entries) {
        my @fields = ();
        foreach my $y (@{$this->{_fields}}) {
            push(@fields, $entries{$entry}->{$y});
        }
        push(@{$this->{_lines}}, join($this->{_sep}, @fields));
    }
    $this->{_sorted} = 1;                      #sorted
}

1;
__END__
