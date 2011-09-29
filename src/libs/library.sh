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
# Copyright (c) 2009 The IPCop Team
#
# $Id: library.sh 3688 2009-10-14 12:10:10Z owes $
#


# Some helper functions useable by IPCop addons
# Return values are 0 if ok, otherwise error

export LIBVERSION=1
export IPCOPVERSION=`/usr/bin/perl -e "require '/usr/lib/ipcop/general-functions.pl';print \\$General::version;"`
export IPCOPMACHINE=`/usr/bin/perl -e "require '/usr/lib/ipcop/general-functions.pl';print \\$General::machine;"`


# Test for IPCop version
#   Parameter 1 is IPCop version to test for
#   Parameter 2 optional, if set a min-max version test is done
#
#   isversion 2.0.0             tests for version equal v2.0.0 
#   isversion 2.0.0 2.0.5       tests for version between v2.0.0 and v2.0.5
isversion()
{
    local i

    # Test for exact match
    if [ "x${1}" = "x${IPCOPVERSION}" -o "x${2}" = "x${IPCOPVERSION}" ]; then
        return 0
    fi
    if [ -z ${2} ]; then
        return 1
    fi

    # Now test if version is within wanted range
    for i in `seq 1 3`; do
        if [ 0`echo ${IPCOPVERSION} | cut -d"." -f ${i}` -lt 0`echo ${1} | cut -d"." -f ${i}` ]; then
            return 1
        elif [ 0`echo ${IPCOPVERSION} | cut -d"." -f ${i}` -gt 0`echo ${2} | cut -d"." -f ${i}` ]; then
            return 1
        fi
    done

    return 0
}


# Test for IPCop architecture
#   Parameter 1 is architecture: alpha, i486, ppc, sparc
ismachine()
{
    if [ "x${1}" = "x${IPCOPMACHINE}" ]; then
        return 0
    fi

    return 1
}


# Add language files
#   Parameter 1 is Addon name
#   Parameter 2 is list of languages (en,de,es,fr,it)
#   Parameter 3 is path to language files
#
#   Language textfiles must be named en.pl, de.pl, es.pl, fr.pl, it.pl etc.
#   For format of these .pl files look at /usr/lib/ipcop/lang.pl
#
#   addtolanguage addon en,es,fr,it /my/install/path
#           will take en.pl,es.pl,fr.pl and it.pl from /my/install/path
#           copy that as addon.en.pl, addon.es.pl, addon.fr.pl, addon.it.pl into /var/ipcop/addons/lang
#           and then rebuild languages DB
addtolanguage()
{
    local lang
    local langfile

    for lang in `echo "${2}" | tr "," " "`; do
        if [ -e "${3}/${lang}.pl" ]; then
            langfile="/var/ipcop/addons/lang/${1}.${lang}.pl"
            cp -f "${3}/${lang}.pl" "${langfile}"
            chown root.root ${langfile}
            chmod 444 ${langfile}
        else
            echo "File for language ${lang}, not found in ${3}"
        fi
    done

    /usr/local/bin/rebuildlangtexts
}


# Remove language files
#   Parameter 1 is Addon name
#
removefromlanguage()
{
    rm -f /var/ipcop/addons/lang/${1}.*.pl
    /usr/local/bin/rebuildlangtexts
}


# Add CGI file and rebuild menu
#   Parameter 1 is CGI file including path
#
addcgi()
{
    local filename

    filename="/home/httpd/cgi-bin/`basename ${1}`"
    cp -f ${1} ${filename}
    chown root.root ${filename}
    chmod 755 ${filename}
    /usr/local/bin/updatemenu.pl
}


# Remove CGI file and rebuild menu
#   Parameter 1 is CGI file without path
#
removecgi()
{
    rm -f /home/httpd/cgi-bin/${1}
    /usr/local/bin/updatemenu.pl
}


# Add to a file at a specific position
#   Parameter 1 is Addon name
#   Parameter 2 is file with section to add
#   Parameter 3 is target file
#   Parameter 4 is search pattern in target file
#
#   Identifying lines will automatically surround the section to add,
#   for easy removal later
addtofile()
{
    echo "### STARTaddto ${1}" > addtofile
    cat ${2} >> addtofile
    echo "### ENDaddto ${1}" >> addtofile

    # TODO: make a safety backup first
    sed -i -e "/${4}/ r addtofile" ${3}
    rm addtofile
}


# Add to end of a file
#   Parameter 1 is Addon name
#   Parameter 2 is file with section to add
#   Parameter 3 is target file 
#
#   Identifying lines will automatically surround the section to add,
#   for easy removal later
addtofiletail()
{
    echo "### STARTaddto ${1}" >> ${3}
    cat ${2} >> ${3}
    echo "### ENDaddto ${1}" >> ${3}
}


# Remove added section from file
#   Parameter 1 is Addon name
#   Parameter 2 is file with section to remove
#
removefromfile()
{
    local starts
    local ends

    starts=`grep -c "### STARTaddto ${1}" ${2}`
    ends=`grep -c "### ENDaddto ${1}" ${2}`

    if [ $starts = 0 -a $ends = 0 ]; then
        # Nothing to do, silently ignore
        return 0
    fi
    if [ $starts = 0 -o $ends = 0 -o $starts -ne $ends ]; then
        echo "Error in removefromfile, sectionmarkers do not match."
        return 1
    fi

    # TODO: make a safety backup first
    sed -i -e "/### STARTaddto ${1}/,/### ENDaddto ${1}/"d ${2}
}
