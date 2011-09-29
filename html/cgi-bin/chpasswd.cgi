#!/usr/bin/perl
#
# IPCop CGIs
#
# This code is distributed under the terms of the GPL
#
# (c) 2010 The IPCop Team
#
# $Id: chpasswd.cgi 4219 2010-02-07 11:07:04Z eoberlander $
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

my %cgiparams;
my %proxysettings;

$proxysettings{'NCSA_MIN_PASS_LEN'} = 6;

### Initialize environment
&General::readhash("/var/ipcop/proxy/settings", \%proxysettings);

my $userdb = "/var/ipcop/proxy/ncsa/passwd";

my @users = ();
my @temp = ();

my $success = 0;
my $errormessage = '';
my $username = '';
my $cryptpwd = '';
my $returncode = '';

&General::getcgihash(\%cgiparams);

if ($cgiparams{'SUBMIT'} eq $Lang::tr{'change password'})
{
    if ($cgiparams{'USERNAME'} eq '') {
        $errormessage = $Lang::tr{'errmsg no username'};
        goto ERROR;
    }
    if (($cgiparams{'OLD_PASSWORD'} eq '') || ($cgiparams{'NEW_PASSWORD_1'} eq '') || ($cgiparams{'NEW_PASSWORD_2'} eq '')) {
        $errormessage = $Lang::tr{'errmsg no password'};
        goto ERROR;
    }
    if (!($cgiparams{'NEW_PASSWORD_1'} eq $cgiparams{'NEW_PASSWORD_2'})) {
        $errormessage = $Lang::tr{'errmsg passwords different'};
        goto ERROR;
    }
    if (length($cgiparams{'NEW_PASSWORD_1'}) < $proxysettings{'NCSA_MIN_PASS_LEN'}) {
        $errormessage = $Lang::tr{'errmsg password length 1'}.' '.$proxysettings{'NCSA_MIN_PASS_LEN'}.' '.$Lang::tr{'errmsg password length 2'};
        goto ERROR;
    }
    if (! -z $userdb) {
        open FILE, $userdb;
        @users = <FILE>;
        close FILE;

        $username = '';
        $cryptpwd = '';

        foreach (@users) {
             chomp;
            @temp = split(/:/,$_);
            if ($temp[0] =~ /^$cgiparams{'USERNAME'}$/i) {
                $username = $temp[0];
                $cryptpwd = $temp[1];
            }
        }
    }
    if ($username eq '') {
        $errormessage = $Lang::tr{'errmsg invalid user'};
        goto ERROR;
    }
    if (!(crypt($cgiparams{'OLD_PASSWORD'}, $cryptpwd) eq $cryptpwd)) {
        $errormessage = $Lang::tr{'incorrect password'};
        goto ERROR;
    }
    $returncode = system("/usr/sbin/htpasswd -b $userdb $username $cgiparams{'NEW_PASSWORD_1'}");
    if ($returncode == 0) {
        $success = 1;
        undef %cgiparams;
    } 
    else {
        $errormessage = $Lang::tr{'errmsg change fail'};
        goto ERROR;
    }
}

ERROR:

&Header::showhttpheaders();

print <<END
<!DOCTYPE html
     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>IPCop - $Lang::tr{'change web access password'}</title>
    
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <link rel="shortcut icon" href="/favicon.ico" />
    <style type="text/css">\@import url(/include/ipcop.css);</style>
</head>
 
<body>

<!-- IPCOP CONTENT -->

  <table width='100%' border='0'>
    <tr>
      <td valign='top' align='center'>
        <table width='100%' cellspacing='0' cellpadding='10' border='0'>
          <tr>
            <td align='left' valign='top'>
              <form method='post' action='/cgi-bin/chpasswd.cgi'>
                 <table cellspacing='0' cellpadding='0' width='100%' border='0'>
                  <col width='18' />
                  <col width='12' />
                  <col width='100%' />
                  <col width='145' />
                  <col width='18' />

                  <tr>
                    <td width='18'><img src='/images/null.gif' width='18' height='1' alt='' /></td>

                    <td width='12'><img src='/images/null.gif' width='12' height='1' alt='' /></td>

                    <td width='100%'><img src='/images/null.gif' width='257' height='1' alt='' /></td>

                    <td width='145'><img src='/images/null.gif' width='145' height='1' alt='' /></td>

                    <td width='18'><img src='/images/null.gif' width='18' height='1' alt='' /></td>
                  </tr>

                  <tr>
                    <td colspan='2'><img src='/images/boxtop1.png' width='30' height='53' alt='' /></td>

                    <td style='background: url(/images/boxtop2.png);'><b>$Lang::tr{'change web access password'}:</b></td>

                    <td colspan='2'><img src='/images/boxtop3.png' width='163' height='53' alt='' /></td>
                  </tr>
                </table>

                <table cellspacing='0' cellpadding='0' width='100%' border='0'>
                  <tr>
                    <td style='background: url(/images/boxleft.png);'><img src='/images/null.gif' width='18' height='1' alt='' /></td>

                    <td colspan='3' style='background-color: #E0E0E0;' width='100%'>
                      <table width='100%' cellpadding='5'>
                        <tr>
                          <td align='left' valign='top'>
                            <table width='100%'>
                              <tr><td>&nbsp;</td></tr>
                              <tr>
                                <td width='15%' class='base'>&nbsp;</td>
                                <td width='25%' class='base' align='right'>$Lang::tr{'username'}:</td>
                                <td width='5%'>&nbsp;</td>
                                <td><input type='text' name='USERNAME' size='19' maxlength='40' /></td>
                              </tr>
                              <tr><td>&nbsp;</td></tr>
                              <tr>
                                <td width='15%' class='base'>&nbsp;</td>
                                <td width='25%' class='base' align='right'>$Lang::tr{'current password'}:</td>
                                <td width='5%'>&nbsp;</td>
                                <td><input type='password' name='OLD_PASSWORD' size='20' maxlength='128' /></td>
                              </tr>
                              <tr><td>&nbsp;</td></tr>
                              <tr>
                                <td width='15%' class='base'>&nbsp;</td>
                                <td width='25%' class='base' align='right'>$Lang::tr{'new password'}:</td>
                                <td width='5%'>&nbsp;</td>
                                <td><input type='password' name='NEW_PASSWORD_1' size='20' maxlength='128' /></td>
                              </tr>
                              <tr><td>&nbsp;</td></tr>
                              <tr>
                                <td width='15%' class='base'>&nbsp;</td>
                                <td width='25%' class='base' align='right'>$Lang::tr{'confirm new password'}:</td>
                                <td width='5%'>&nbsp;</td>
                                <td><input type='password' name='NEW_PASSWORD_2' size='20' maxlength='128' /></td>
                              </tr>
                              <tr><td>&nbsp;</td></tr>
                        </table>
                            <hr />
                            <table width='100%'>
END
;

if ($errormessage) {
    print "<tr><td width='5%'></td><td bgcolor=#CC0000><center><b><font color=white>$Lang::tr{'capserror'}: $errormessage</font></b></center></td><td width='5%'></td></tr>\n";
}
else {
    if ($success) {
        print "<tr><td width='5%'></td><td bgcolor=#339933><center><b><font color=white>$Lang::tr{'$errmsg change success'}</font></b></center></td><td width='5%'></td></tr>\n";
    }
    else {
        print "<tr><td><center>$Lang::tr{'web access password hint'}</center></td></tr>\n";
    }
}

print <<END
                            </table>
                            <hr />
                            <table width='100%'>
                              <tr>
                                <td class='comment1button'>&nbsp;</td>

                                <td class='button1button'><input type='submit' name='SUBMIT' value='$Lang::tr{'change password'}' /></td>

                                <td class='onlinehelp'>
                                <!--<a href='http://www.ipcop.org/2.0.0/en/admin/html/webaccess-passwords.html'
                                target='_blank'><img src='/images/web-support.png' alt='Online Help (in English)'
                                title='Online Help (in English)' /></a>-->
                                </td>
                              </tr>
                            </table>
                          </td>
                        </tr>
                      </table>
                    </td>

                    <td style='background: url(/images/boxright.png);'><img src='/images/null.gif' width='12' alt='' /></td>
                  </tr>

                  <tr>
                    <td style='background: url(/images/boxbottom1.png);background-repeat:no-repeat;'><img src=
                    '/images/null.gif' width='18' height='18' alt='' /></td>

                    <td style='background: url(/images/boxbottom2.png);background-repeat:repeat-x;' colspan='3'><img src=
                    '/images/null.gif' width='1' height='18' alt='' /></td>

                    <td style='background: url(/images/boxbottom3.png);background-repeat:no-repeat;'><img src=
                    '/images/null.gif' width='18' height='18' alt='' /></td>
                  </tr>

                  <tr>
                    <td colspan='5'><img src='/images/null.gif' width='1' height='5' alt='' /></td>
                  </tr>
                </table>
              </form>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
  
<!-- IPCOP FOOTER -->

  <table width='100%' border='0'>
    <tr>
      <td width='175' align='left'><img src='/images/null.gif' width='15' height='12' alt='' /><a href=
      'http://sourceforge.net/projects/ipcop' target='_blank'><img src='/images/sflogo.gif' width='120' height='30' alt=
      'Get IPCop Firewall at SourceForge.net. Fast, secure and Free Open Source software downloads' /></a></td>

      <td align='center' valign='middle'><small>IPCop v${General::version} &copy; 2001-2010 The IPCop Team</small></td>

      <td width='175' align='right' valign='bottom'><a href='http://www.ipcop.org/' target='_blank'><img src=
      '/images/shieldedtux.png' width='113' height='82' alt='IPCop Tux' /></a><img src='/images/null.gif' width='15' height=
      '12' alt='' /></td>
    </tr>
  </table>
</body>
</html>

END
;
