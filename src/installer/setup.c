/* 
 * setup.c: setup main loop
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
 * (c) 2007-2009, the IPCop team
 *
 * Commandline options:
 *
 * $Id: setup.c 3360 2009-07-30 10:16:12Z owes $
 *
 */


#include <errno.h>
#include <libintl.h>
#include <newt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "common.h"
#include "common_newt.h"
#include "arch_defs.h"


NODEKV *kv = NULL;              // contains a list key=value pairs
installer_setup_t flag_is_state = setup;
supported_media_t medium_console = console;
char selected_locale[STRING_SIZE];
struct utsname utsbuf;


char *ipcop_gettext(char *txt)
{
    return gettext(txt);
}


int main(int argc, char **argv)
{
    int i;
    int rc;
    int choice;
    char *menuchoices[10];

    /* check cmd line */
    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--install")) {
            flag_is_state = setupchroot;
        }
        if (!strcmp(argv[i], "--serial")) {
            medium_console = serial;
        }
    }

    if (medium_console == serial) {
        flog = fopen("/tmp/flog", "w");
        fstderr = freopen("/tmp/fstderr", "w", stderr);
    }
    else if (flag_is_state == setupchroot) {
        if (!(flog = fopen("/dev/tty2", "w+"))) {
            printf("Failed to open /dev/tty2 for logging\n");
            exit(0);
        }

        fstderr = freopen("/dev/tty3", "w+", stderr);
    }
    else {
        // owes: flog is helpful for hw detection, may need to change to something other than tty5 one day
        if (!(flog = fopen("/dev/tty5", "w+"))) {
            printf("Failed to open /dev/tty5 for logging\n");
            exit(0);
        }

        fstderr = freopen("/dev/tty6", "w+", stderr);
    }

    memset(&utsbuf, 0, sizeof(struct utsname));
    uname(&utsbuf);

    newtInit();
    newtCls();

    /* Have to get proper locale here */
    read_kv_from_file(&kv, "/var/ipcop/main/settings");
    strcpy(selected_locale, "en_GB");
    find_kv_default(kv, "LOCALE", selected_locale);
    /* We store locale as en_GB not as en_GB.utf8 in settings 
       append .utf8 to make setlocale happy.
     */
    strcat(selected_locale, ".utf8");

    bindtextdomain("install", "/usr/share/locale");
    textdomain("install");
    setlocale(LC_ALL, selected_locale);

    menuchoices[0] = gettext("TR_KEYBOARD_MAPPING");
    menuchoices[1] = gettext("TR_TIMEZONE");
    menuchoices[2] = gettext("TR_HOSTNAME");
    menuchoices[3] = gettext("TR_DOMAINNAME");
    menuchoices[4] = gettext("TR_NETWORKING");
    menuchoices[5] = gettext("TR_PASSWORDS");
    menuchoices[6] = NULL;

    newtDrawRootText(18, 0, get_title());
    newtPushHelpLine(gettext("TR_HELPLINE"));

    if (flag_is_state == setupchroot) {
        /* all settings in a row, no main menu */
        handlekeymap();
        handlehostname();
        handledomainname();
        handlenetworking();
        password("root");
        password("admin");
        password("backup");
        /* The dial user is fully optional and will created after the password is set through the GUI or setup */
    }
    else {
        choice = 0;
        for (;;) {
            rc = newtWinMenu(gettext("TR_SECTION_MENU"),
                             gettext("TR_SELECT_THE_ITEM"), 50, 5, 5, 11,
                             menuchoices, &choice, gettext("TR_SELECT"), gettext("TR_EXIT"), NULL);

            if (rc == 2)
                break;

            switch (choice) {
            case 0:
                handlekeymap();
                break;
            case 1:
                handletimezone();
                break;
            case 2:
                handlehostname();
                break;
            case 3:
                handledomainname();
                break;
            case 4:
                handlenetworking();
                break;
            case 5:
                handlepasswords();
                break;

            default:
                break;
            }
        }
    }
    newtFinished();

    fclose(flog);
    fclose(fstderr);
    exit(0);
}
