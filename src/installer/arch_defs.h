/*
 * arch_defs.h: Global defines, function definitions etc. concerning portabilty
 *              Probably only necessary for installer. 
 *
 * This file is part of the IPCop Firewall.
 *
 * IPCop is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * IPCop is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with IPCop; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
 *
 * (c) 2007-2010, the IPCop team
 *
 * $Id: arch_defs.h 4520 2010-04-26 14:25:03Z owes $
 * 
 */


/*  
    Test which arch is used for building.
    We currently support i386, alpha, powerpc and sparc.

    If you want to compile on a different architecture look in this file for modifications.
*/
#if defined (__i386__)
#elif defined (__alpha__)
#elif defined (__powerpc__) || defined (__powerpc64__)
#elif defined (__sparc__) || defined (__sparc64__)
#else
#error "We currently do not support your hardware architecture"
#endif


/* To fetch running kernel release (i.e. 2.6.27) */
#include <sys/utsname.h>


/*
    Number of partitions
*/
#define IPCOP_PARTITIONS    2
#if defined (__i386__)
#define NR_PARTITIONS       2
#elif defined (__alpha__)
#define NR_PARTITIONS       2
#elif defined (__powerpc__) || defined (__powerpc64__)
#define NR_PARTITIONS       4
#elif defined (__sparc__) || defined (__sparc64__)
#define NR_PARTITIONS       3
#endif

/*
    Partioning settings (all in MByte)
*/
#define DISK_MINIMUM    480     /* 512 MB minus several MB 'marketing-margin' */
#define ROOT_MINIMUM    256
#define ROOT_MAXIMUM    512
#define SWAP_MINIMUM     32
#define SWAP_MAXIMUM    256
#define LOGCOMPRESSED    64


#define TARBALL_IPCOP    "ipcop-" VERSION ".tar.gz"


typedef enum
{
    none = 0,
    floppy,                     /* bootable, restore */
    cdrom,                      /* bootable and sources available */
    usb,                        /* bootable, sources available and restore */
    harddisk,                   /* possible installation target */
    flash,                      /* target */
    network,                    /* bootable (PXE), sources available (http/ftp server) and restore (http/ftp server) */
    console,                    /* console: standard */
    serial,                     /* console: serial */
    specialmodule = 100,        /* for module list only */
    unknown,
} supported_media_t;


extern supported_media_t medium_boot;
extern supported_media_t medium_sources;
extern supported_media_t medium_target;
extern supported_media_t medium_console;

struct hardware_s
{
    char *module;               /* kernel module */
    char *device;               /* hda, sda, eth0 etc. */
    char *description;
    supported_media_t type;     /* network */
    char *vendorid;             /* vendor and device ID for better NIC matching */
    char *modelid;
};

extern unsigned int numhardwares;
extern unsigned int numharddisk;
extern unsigned int numcdrom;
extern unsigned int numnetwork;
extern struct hardware_s *hardwares;

extern char network_source[STRING_SIZE];        /* something like http://ip/path */
extern unsigned int memtotal;   /* Total memory in MB */

extern unsigned int serial_console;             /* 0 = ttyS0, 1 = ttyS1, etc. */
extern unsigned int serial_bitrate;             /* 9600, 38400, etc. */
extern char *serial_commandline;                /* ttyS0,38400n81 */

/*
    Functions implemented in hardware.c and partition.c    
*/
void scan_hardware(int installer_setup, int nopcmcia, int nousb, int noscsi, int manualmodule);
int make_ipcop_disk(char *device, char *device2, long int disk_size, long int swapfilesize, int part_options);

#define PART_OPTIONS_PARTED     0x01
#define PART_OPTIONS_NO_MBR     0x02

/*
    Some global variables used when installing
*/
extern struct utsname utsbuf;
