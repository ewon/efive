#!/bin/bash
#
# Build a list of PCI and USB identification codes for inclusion on the ipcop.org wiki
# This is a slighlty modified version from the IPCop 1.4 script to allow for multiple platforms
#
# Use this script at top level after full build with ./tools/prepareIDmap.sh
#
# $Id: make.sh 180 2007-04-15 03:26:52Z chepati $
# 


KVER=`grep --max-count=1 VER lfs/linux | awk '{ print $3 }'`
if [ -z $KVER ]; then
  echo "I'm confused (Kernel version not found), please run me from top level with ./tools/prepareIDmap.sh"
  exit 0
fi
MACHINE=''
for i in i486 alpha ppc sparc
do
  if [ -d "build_$i" ]; then
    MACHINE=$i
  fi
done

if [ -z $MACHINE ]; then
  echo "No build directory found, build IPCop first using: make.sh"
  exit 0
fi
echo "Preparing $MACHINE pci and usb maps for publication on the wiki"
if [ ! -s build_$MACHINE/ipcop/lib/modules ]; then
  echo "Module info not found, try rebuilding IPCop using: make.sh clean && make.sh build"
  exit 1
fi
if [ ! -s build_$MACHINE/ipcop/lib/modules/$KVER/modules.pcimap ]; then
  echo "PCI map not found for kernel $KVER, try rebuilding IPCop using: make.sh clean && make.sh build"
  exit 1
fi
if [ ! -s build_$MACHINE/ipcop/lib/modules/$KVER/modules.usbmap ]; then
  echo "USB map not found for kernel $KVER, try rebuilding IPCop using: make.sh clean && make.sh build"
  exit 1
fi


# suppress first line temporary and sort by module name
sed -e '/module/d' build_$MACHINE/ipcop/lib/modules/$KVER/modules.pcimap | sort > doc/tmpmap1.txt

# cells are seperated by ;
# CnxADSL is interpreted as link, fix that
sed -i  -e 's/  */ /g'    \
  -e 's/ /;/g'    \
  -e 's/^/;/'   \
  -e 's/|#|/;/'   \
  -e 's/BusLogic/!BusLogic/'    \
  -e 's/CnxADSL/!CnxADSL/'    \
  doc/tmpmap1.txt

# get rid of LF character
tr -d "\n" < doc/tmpmap1.txt > doc/tmpmap2.txt

# add comment
echo "PCI id from $KVER compilation `date +'%Y-%m-%d'`" > doc/PCIidmap.txt
echo " "  >>  doc/PCIidmap.txt

# add table header
echo -n "{{table columns=\"8\" cells=\"==pci module==;==vendor==;==device==;==subvendor==;==subdevice==;==class==;==class_mask==;==driver_data==" \
  >>  doc/PCIidmap.txt

cat doc/tmpmap2.txt >> doc/PCIidmap.txt

# and table terminator
echo -n "\"}}" >> doc/PCIidmap.txt
echo "PCI map stored as doc/PCIidmap.txt"


# suppress first line temporary and sort by module name
sed -e '/module/d' build_$MACHINE/ipcop/lib/modules/$KVER/modules.usbmap | sort > doc/tmpmap1.txt

# cells are seperated by ;
sed -i  -e 's/  */ /g'    \
  -e 's/ /;/g'    \
  -e 's/^/;/'   \
  -e 's/|#|/;/'   \
  doc/tmpmap1.txt

# get rid of LF character
tr -d "\n" < doc/tmpmap1.txt > doc/tmpmap2.txt

# add comment
echo "USB id from $KVER compilation `date +'%Y-%m-%d'`" > doc/USBidmap.txt
echo " "  >>  doc/USBidmap.txt

# add table header
echo -n "{{table columns=\"13\" cells=\"==usb module==;==match_flags==;==idVendor==;==idProduct==;==bcdDevice_lo==;==bcdDevice_hi==;==b!DeviceClass==;==b!DeviceSubClass==;==b!DeviceProtocol==;==b!InterfaceClass==;==b!InterfaceSubClass==;==b!InterfaceProtocol==;==driver_info==" \
  >>  doc/USBidmap.txt

cat doc/tmpmap2.txt >> doc/USBidmap.txt

# and table terminator
echo -n "\"}}" >> doc/USBidmap.txt
echo "USB map stored as doc/USBidmap.txt"

# clean up
rm doc/tmpmap1.txt
rm doc/tmpmap2.txt

