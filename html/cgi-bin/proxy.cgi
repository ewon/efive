#!/usr/bin/perl
#
# IPCop CGIs - proxy.cgi: web proxy service configuration
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
# along with IPCop.  If not, see <http://www.gnu.org/licenses/>.
#
# (c) 2004-2009 marco.s - http://www.advproxy.net
# (c) 2009-2011 The IPCop Team
#
# $Id: proxy.cgi 5831 2011-08-24 15:04:16Z owes $
#

# Add entry in menu
# MENUENTRY services 010 "proxy" "web proxy configuration"
#
# Make sure translation exists $Lang::tr{'proxy'}

use strict;
use NetAddr::IP;

# enable only the following on debugging purpose
#use warnings;
use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

my @squidversion = `/usr/sbin/squid -v`;
my $http_port='81';
my $https_port='8443';      # default value, pull actual value from main/settings later

my %proxysettings=();
my %netsettings=();
my %ovpnsettings=();
my %filtersettings=();
my %updaccelsettings=();
my %stdproxysettings=();
my %mainsettings=();
my $urlfilter_addon=0;
my $updaccel_addon=0;

my %checked=();
my %selected=();

my @throttle_limits=(64,128,256,384,512,1024,2048,3072,5120,8192,10240);
my $throttle_binary="7z|bz2|bin|cab|dmg|exe|gz|rar|sea|tar|tgz|zip";
my $throttle_dskimg="b5t|bin|bwt|ccd|cdi|cue|flp|gho|img|iso|mds|nrg|pqi|raw|tib";
my $throttle_mmedia="aiff?|asf|avi|divx|flv|mov|mp(3|4)|mpe?g|qt|ra?m";

my $def_ports_safe="80 # http\n21 # ftp\n443 # https\n1025-65535 # unprivileged ports\n8080 # Squids port (for icons)\n";
my $def_ports_ssl="443 # https\n8443 # alternative https\n";

my %language = (
"af","Afrikaans",
"ar","Arabic",
"az","Azerbaijani",
"bg","Bulgarian",
"ca","Catalan",
"cs","Czech",
"da","Danish",
"de","German",
"el","Greek",
"en","English",
"es","Spanish",
"et","Estonian",
"fa","Persian",
"fi","Finnish",
"fr","French",
"he","Hebrew",
"hu","Hungarian",
"hy","Armenian",
"id","Indonesian",
"it","Italian",
"ja","Japanese",
"ko","Korean",
"lt","Lithuanian",
"lv","Latvian",
"ms","Malay",
"nl","Dutch",
"oc","Occitan",
"pl","Polish",
"pt","Portuguese",
"pt-br","Portuguese - Brazil",
"ro","Romanian",
"ru","Russian",
"sk","Slovak",
"sr-cyrl","Serbian - Cyrillic",
"sr-latn","Serbian - Latin",
"sv","Swedish",
"th","Thai",
"tr","Turkish",
"uk","Ukrainian",
"uz","Uzbek",
"vi","Vietnamese",
"zh-cn","Chinese - China",
"zh-tw","Chinese - Taiwan",
);

my @useragent=();
my @useragentlist=();

my $hintcolour='#FFFFCC';
my $ncsa_buttontext='';
my $countrycode='';
my $language='';
my $i=0;
my $n=0;
my $id=0;
my $line='';
my $user='';
my @userlist=();
my @grouplist=();
my @temp=();
my @templist=();

my $cachemem=0;
my $proxy1='';
my $proxy2='';
my $replybodymaxsize=0;
my $browser_regexp='';
my $needhup = 0;
my $errormessage='';
my $error_settings='';
my $error_options='';

my $acldir   = "/var/ipcop/proxy/acls";
my $ncsadir  = "/var/ipcop/proxy/ncsa";
my $ntlmdir  = "/var/ipcop/proxy/ntlm";
my $raddir   = "/var/ipcop/proxy/radius";
my $identdir = "/var/ipcop/proxy/ident";
my $credir   = "/var/ipcop/proxy/cre";

my $userdb = "$ncsadir/passwd";
my $stdgrp = "$ncsadir/standard.grp";
my $extgrp = "$ncsadir/extended.grp";
my $disgrp = "$ncsadir/disabled.grp";

my $browserdb = "/var/ipcop/proxy/useragents";
my $mimetypes = "/var/ipcop/proxy/mimetypes";
my $throttled_urls = "/var/ipcop/proxy/throttle";

my $cre_enabled = "/var/ipcop/proxy/cre/enable";
my $cre_groups  = "/var/ipcop/proxy/cre/classrooms";
my $cre_svhosts = "/var/ipcop/proxy/cre/supervisors";

my $identhosts = "$identdir/hosts";

my $authdir  = "/usr/lib/squid";
my $errordir = "/usr/lib/squid/errors";

my $acl_src_subnets  = "$acldir/src_subnets.acl";
my $acl_src_networks = "$acldir/src_networks.acl";
my $acl_src_banned_ip  = "$acldir/src_banned_ip.acl";
my $acl_src_banned_mac = "$acldir/src_banned_mac.acl";
my $acl_src_unrestricted_ip  = "$acldir/src_unrestricted_ip.acl";
my $acl_src_unrestricted_mac = "$acldir/src_unrestricted_mac.acl";
my $acl_src_noaccess_ip  = "$acldir/src_noaccess_ip.acl";
my $acl_src_noaccess_mac = "$acldir/src_noaccess_mac.acl";
my $acl_dst_noauth = "$acldir/dst_noauth.acl";
my $acl_dst_noauth_dom = "$acldir/dst_noauth_dom.acl";
my $acl_dst_noauth_net = "$acldir/dst_noauth_net.acl";
my $acl_dst_noauth_url = "$acldir/dst_noauth_url.acl";
my $acl_dst_nocache = "$acldir/dst_nocache.acl";
my $acl_dst_nocache_dom = "$acldir/dst_nocache_dom.acl";
my $acl_dst_nocache_net = "$acldir/dst_nocache_net.acl";
my $acl_dst_nocache_url = "$acldir/dst_nocache_url.acl";
my $acl_dst_mime_exceptions = "$acldir/dst_mime_exceptions.acl";
my $acl_dst_mime_exceptions_dom = "$acldir/dst_mime_exceptions_dom.acl";
my $acl_dst_mime_exceptions_net = "$acldir/dst_mime_exceptions_net.acl";
my $acl_dst_mime_exceptions_url = "$acldir/dst_mime_exceptions_url.acl";
my $acl_dst_throttle = "$acldir/dst_throttle.acl";
my $acl_ports_safe = "$acldir/ports_safe.acl";
my $acl_ports_ssl  = "$acldir/ports_ssl.acl";
my $acl_include = "$acldir/include.acl";

my $updaccelversion  = 'n/a';
my $urlfilterversion = 'n/a';

unless (-d "$acldir")   { mkdir("$acldir"); }
unless (-d "$ncsadir")  { mkdir("$ncsadir"); }
unless (-d "$ntlmdir")  { mkdir("$ntlmdir"); }
unless (-d "$raddir")   { mkdir("$raddir"); }
unless (-d "$identdir") { mkdir("$identdir"); }
unless (-d "$credir")   { mkdir("$credir"); }

unless (-e $cre_groups)  { system("touch $cre_groups"); }
unless (-e $cre_svhosts) { system("touch $cre_svhosts"); }

unless (-e $userdb) { system("touch $userdb"); }
unless (-e $stdgrp) { system("touch $stdgrp"); }
unless (-e $extgrp) { system("touch $extgrp"); }
unless (-e $disgrp) { system("touch $disgrp"); }

unless (-e $acl_src_subnets)    { system("touch $acl_src_subnets"); }
unless (-e $acl_src_networks)   { system("touch $acl_src_networks"); }
unless (-e $acl_src_banned_ip)  { system("touch $acl_src_banned_ip"); }
unless (-e $acl_src_banned_mac) { system("touch $acl_src_banned_mac"); }
unless (-e $acl_src_unrestricted_ip)  { system("touch $acl_src_unrestricted_ip"); }
unless (-e $acl_src_unrestricted_mac) { system("touch $acl_src_unrestricted_mac"); }
unless (-e $acl_src_noaccess_ip)  { system("touch $acl_src_noaccess_ip"); }
unless (-e $acl_src_noaccess_mac) { system("touch $acl_src_noaccess_mac"); }
unless (-e $acl_dst_noauth)     { system("touch $acl_dst_noauth"); }
unless (-e $acl_dst_noauth_dom) { system("touch $acl_dst_noauth_dom"); }
unless (-e $acl_dst_noauth_net) { system("touch $acl_dst_noauth_net"); }
unless (-e $acl_dst_noauth_url) { system("touch $acl_dst_noauth_url"); }
unless (-e $acl_dst_nocache)     { system("touch $acl_dst_nocache"); }
unless (-e $acl_dst_nocache_dom) { system("touch $acl_dst_nocache_dom"); }
unless (-e $acl_dst_nocache_net) { system("touch $acl_dst_nocache_net"); }
unless (-e $acl_dst_nocache_url) { system("touch $acl_dst_nocache_url"); }
unless (-e $acl_dst_mime_exceptions)     { system("touch $acl_dst_mime_exceptions"); }
unless (-e $acl_dst_mime_exceptions_dom) { system("touch $acl_dst_mime_exceptions_dom"); }
unless (-e $acl_dst_mime_exceptions_net) { system("touch $acl_dst_mime_exceptions_net"); }
unless (-e $acl_dst_mime_exceptions_url) { system("touch $acl_dst_mime_exceptions_url"); }
unless (-e $acl_dst_throttle) { system("touch $acl_dst_throttle"); }
unless (-e $acl_ports_safe) { system("touch $acl_ports_safe"); }
unless (-e $acl_ports_ssl)  { system("touch $acl_ports_ssl"); }
unless (-e $acl_include) { system("touch $acl_include"); }

unless (-e $browserdb) { system("touch $browserdb"); }
unless (-e $mimetypes) { system("touch $mimetypes"); }

open FILE, $browserdb;
@useragentlist = sort { reverse(substr(reverse(substr($a,index($a,',')+1)),index(reverse(substr($a,index($a,','))),',')+1)) cmp reverse(substr(reverse(substr($b,index($b,',')+1)),index(reverse(substr($b,index($b,','))),',')+1))} grep !/(^$)|(^\s*#)/,<FILE>;
close(FILE);

&General::readhash("/var/ipcop/ethernet/settings", \%netsettings);
&General::readhash("/var/ipcop/main/settings", \%mainsettings);
if (-e "/var/ipcop/openvpn/settings") {
    &General::readhash("/var/ipcop/openvpn/settings", \%ovpnsettings);
}

$https_port = $mainsettings{'GUIPORT'} if (defined($mainsettings{'GUIPORT'}));

if (-e "/usr/bin/squidGuard") { $urlfilter_addon = 1; }
if (-e "/var/ipcop/addons/updatexlrator/version") { $updaccel_addon = 1; }

if ($urlfilter_addon) {
    $filtersettings{'CHILDREN'} = '5';
    if (-e "/var/ipcop/proxy/filtersettings") {
        &General::readhash("/var/ipcop/proxy/filtersettings", \%filtersettings);
    }
    $urlfilterversion = `/usr/bin/squidGuard -v 2>&1`;
    $urlfilterversion =~ s/^SquidGuard://i;
    $urlfilterversion =~ s/^\s+//g;
    $urlfilterversion =~ s/([^\s]+).*/$1/;
}

if ($updaccel_addon) {
    $updaccelsettings{'CHILDREN'} = '10';
    if (-e "/var/ipcop/addons/updatexlrator/settings") {
        &General::readhash("/var/ipcop/addons/updatexlrator/settings", \%updaccelsettings);
    }
    $updaccelversion = `cat /var/ipcop/addons/updatexlrator/version`;
    $updaccelversion =~ s/([^\s]+).*/$1/;
}

&Header::showhttpheaders();

$proxysettings{'ACTION'} = '';
$proxysettings{'VALID'} = '';

$proxysettings{'ENABLED_GREEN_1'} = 'off';
$proxysettings{'ENABLED_BLUE_1'} = 'off';
$proxysettings{'ENABLED_OVPN'} = 'off';
$proxysettings{'TRANSPARENT_GREEN_1'} = 'off';
$proxysettings{'TRANSPARENT_BLUE_1'} = 'off';
$proxysettings{'TRANSPARENT_OVPN'} = 'off';
$proxysettings{'PROXY_PORT'} = '8080';
$proxysettings{'VISIBLE_HOSTNAME'} = '';
$proxysettings{'ADMIN_MAIL_ADDRESS'} = '';
$proxysettings{'ERR_LANGUAGE'} = 'en';
$proxysettings{'ERR_DESIGN'} = 'IPCop';
$proxysettings{'SUPPRESS_VERSION'} = 'off';
$proxysettings{'FORWARD_VIA'} = 'off';
$proxysettings{'FORWARD_IPADDRESS'} = 'off';
$proxysettings{'FORWARD_USERNAME'} = 'off';
$proxysettings{'NO_CONNECTION_AUTH'} = 'off';
$proxysettings{'UPSTREAM_PROXY'} = '';
$proxysettings{'UPSTREAM_USER'} = '';
$proxysettings{'UPSTREAM_PASSWORD'} = '';
$proxysettings{'LOGGING'} = 'off';
$proxysettings{'LOGQUERY'} = 'off';
$proxysettings{'LOGUSERAGENT'} = 'off';
$proxysettings{'CACHE_MEM'} = '4';
$proxysettings{'CACHE_SIZE'} = '50';
$proxysettings{'MAX_SIZE'} = '4096';
$proxysettings{'MIN_SIZE'} = '0';
$proxysettings{'MEM_POLICY'} = 'LRU';
$proxysettings{'CACHE_POLICY'} = 'LRU';
$proxysettings{'L1_DIRS'} = '16';
$proxysettings{'OFFLINE_MODE'} = 'off';
$proxysettings{'CLASSROOM_EXT'} = 'off';
$proxysettings{'SUPERVISOR_PASSWORD'} = '';
$proxysettings{'NO_PROXY_LOCAL'} = 'off';
$proxysettings{'NO_PROXY_LOCAL_GREEN'} = 'off';
$proxysettings{'NO_PROXY_LOCAL_BLUE'} = 'off';
$proxysettings{'TIME_ACCESS_MODE'} = 'allow';
$proxysettings{'TIME_FROM_HOUR'} = '00';
$proxysettings{'TIME_FROM_MINUTE'} = '00';
$proxysettings{'TIME_TO_HOUR'} = '24';
$proxysettings{'TIME_TO_MINUTE'} = '00';
$proxysettings{'MAX_OUTGOING_SIZE'} = '0';
$proxysettings{'MAX_INCOMING_SIZE'} = '0';
$proxysettings{'THROTTLING_GREEN_TOTAL'} = 'unlimited';
$proxysettings{'THROTTLING_GREEN_HOST'} = 'unlimited';
$proxysettings{'THROTTLING_BLUE_TOTAL'} = 'unlimited';
$proxysettings{'THROTTLING_BLUE_HOST'} = 'unlimited';
$proxysettings{'THROTTLE_BINARY'} = 'off';
$proxysettings{'THROTTLE_DSKIMG'} = 'off';
$proxysettings{'THROTTLE_MMEDIA'} = 'off';
$proxysettings{'ENABLE_MIME_FILTER'} = 'off';
$proxysettings{'ENABLE_BROWSER_CHECK'} = 'off';
$proxysettings{'FAKE_USERAGENT'} = '';
$proxysettings{'FAKE_REFERER'} = '';
$proxysettings{'AUTH_METHOD'} = 'none';
$proxysettings{'AUTH_REALM'} = '';
$proxysettings{'AUTH_MAX_USERIP'} = '';
$proxysettings{'AUTH_CACHE_TTL'} = '60';
$proxysettings{'AUTH_IPCACHE_TTL'} = '0';
$proxysettings{'AUTH_CHILDREN'} = '5';
$proxysettings{'NCSA_MIN_PASS_LEN'} = '6';
$proxysettings{'NCSA_BYPASS_REDIR'} = 'off';
$proxysettings{'NCSA_USERNAME'} = '';
$proxysettings{'NCSA_GROUP'} = '';
$proxysettings{'NCSA_PASS'} = '';
$proxysettings{'NCSA_PASS_CONFIRM'} = '';
$proxysettings{'LDAP_BASEDN'} = '';
$proxysettings{'LDAP_TYPE'} = 'ADS';
$proxysettings{'LDAP_SERVER'} = '';
$proxysettings{'LDAP_PORT'} = '389';
$proxysettings{'LDAP_BINDDN_USER'} = '';
$proxysettings{'LDAP_BINDDN_PASS'} = '';
$proxysettings{'LDAP_GROUP'} = '';
$proxysettings{'NTLM_DOMAIN'} = '';
$proxysettings{'NTLM_PDC'} = '';
$proxysettings{'NTLM_BDC'} = '';
$proxysettings{'NTLM_ENABLE_ACL'} = 'off';
$proxysettings{'NTLM_USER_ACL'} = 'positive';
$proxysettings{'RADIUS_SERVER'} = '';
$proxysettings{'RADIUS_PORT'} = '1812';
$proxysettings{'RADIUS_IDENTIFIER'} = '';
$proxysettings{'RADIUS_SECRET'} = '';
$proxysettings{'RADIUS_ENABLE_ACL'} = 'off';
$proxysettings{'RADIUS_USER_ACL'} = 'positive';
$proxysettings{'IDENT_REQUIRED'} = 'off';
$proxysettings{'IDENT_TIMEOUT'} = '10';
$proxysettings{'IDENT_ENABLE_ACL'} = 'off';
$proxysettings{'IDENT_USER_ACL'} = 'positive';

if ($urlfilter_addon) {
    $proxysettings{'ENABLE_FILTER'} = 'off';
}

if ($updaccel_addon) {
    $proxysettings{'ENABLE_UPDXLRATOR'} = 'off';
}

$ncsa_buttontext = $Lang::tr{'NCSA create user'};

&General::getcgihash(\%proxysettings);

if ($proxysettings{'THROTTLING_GREEN_TOTAL'} eq 0) {$proxysettings{'THROTTLING_GREEN_TOTAL'} = 'unlimited';}
if ($proxysettings{'THROTTLING_GREEN_HOST'}  eq 0) {$proxysettings{'THROTTLING_GREEN_HOST'}  = 'unlimited';}
if ($proxysettings{'THROTTLING_BLUE_TOTAL'}  eq 0) {$proxysettings{'THROTTLING_BLUE_TOTAL'}  = 'unlimited';}
if ($proxysettings{'THROTTLING_BLUE_HOST'}   eq 0) {$proxysettings{'THROTTLING_BLUE_HOST'}   = 'unlimited';}

if ($proxysettings{'ACTION'}) {

if ($proxysettings{'ACTION'} eq $Lang::tr{'NCSA user management'})
{
    $proxysettings{'NCSA_EDIT_MODE'} = 'yes';
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'add'})
{
    $proxysettings{'NCSA_EDIT_MODE'} = 'yes';
    if (length($proxysettings{'NCSA_PASS'}) < $proxysettings{'NCSA_MIN_PASS_LEN'}) {
        $errormessage = $Lang::tr{'errmsg password length 1'}.$proxysettings{'NCSA_MIN_PASS_LEN'}.$Lang::tr{'errmsg password length 2'};
    }
    if (!($proxysettings{'NCSA_PASS'} eq $proxysettings{'NCSA_PASS_CONFIRM'})) {
        $errormessage = $Lang::tr{'errmsg passwords different'};
    }
    if ($proxysettings{'NCSA_USERNAME'} eq '') {
        $errormessage = $Lang::tr{'errmsg no username'};
    }
    if (!$errormessage) {
        $proxysettings{'NCSA_USERNAME'} =~ tr/A-Z/a-z/;
        &adduser($proxysettings{'NCSA_USERNAME'}, $proxysettings{'NCSA_PASS'}, $proxysettings{'NCSA_GROUP'});
    }
    $proxysettings{'NCSA_USERNAME'} = '';
    $proxysettings{'NCSA_GROUP'} = '';
    $proxysettings{'NCSA_PASS'} = '';
    $proxysettings{'NCSA_PASS_CONFIRM'} = '';
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'remove'})
{
    $proxysettings{'NCSA_EDIT_MODE'} = 'yes';
    &deluser($proxysettings{'ID'});
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'edit'})
{
    $proxysettings{'NCSA_EDIT_MODE'} = 'yes';
    $ncsa_buttontext = $Lang::tr{'NCSA update user'};
    @temp = split(/:/,$proxysettings{'ID'});
    $proxysettings{'NCSA_USERNAME'} = $temp[0];
    $proxysettings{'NCSA_GROUP'} = $temp[1];
    $proxysettings{'NCSA_PASS'} = "lEaVeAlOnE";
    $proxysettings{'NCSA_PASS_CONFIRM'} = $proxysettings{'NCSA_PASS'};
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'save'})
{
    if ($proxysettings{'ENABLED_GREEN_1'} !~ /^(on|off)$/ ||
        $proxysettings{'TRANSPARENT_GREEN_1'} !~ /^(on|off)$/ ||
        $proxysettings{'ENABLED_BLUE_1'} !~ /^(on|off)$/ ||
        $proxysettings{'TRANSPARENT_BLUE_1'} !~ /^(on|off)$/ ) {
        $errormessage = $Lang::tr{'invalid input'};
        goto ERROR;
    }
    if (!(&General::validport($proxysettings{'PROXY_PORT'})))
    {
        $errormessage = $Lang::tr{'errmsg invalid proxy port'};
        $error_settings = 'error';
        goto ERROR;
    }
    my @free = `/bin/df -B M /var/log/cache | /bin/grep -v Filesystem | /usr/bin/cut -d M -f1`;
    if (!($proxysettings{'CACHE_SIZE'} =~ /^\d+/) || ($proxysettings{'CACHE_SIZE'} < 10)) {
        if (!($proxysettings{'CACHE_SIZE'} eq '0')) {
            $errormessage = $Lang::tr{'errmsg hdd cache size'};
            $error_options = 'error';
            goto ERROR;
        }
    }
    else {
        my @cachedisk = split(' ', $free[0]);
        # Make sure we have enough space for logs etc.
        $cachedisk[1] = $cachedisk[1] - 128;
        $cachedisk[1] = 0 if ($cachedisk[1] < 10);
        $proxysettings{'CACHE_SIZE'} = $cachedisk[1] if ($proxysettings{'CACHE_SIZE'} > $cachedisk[1]);
    }
    if (!($proxysettings{'CACHE_MEM'} =~ /^\d+/) ||
        ($proxysettings{'CACHE_MEM'} < 1))
    {
        $errormessage = $Lang::tr{'errmsg mem cache size'};
        $error_options = 'error';
        goto ERROR;
    }
    @free = `/usr/bin/free`;
    $free[1] =~ m/(\d+)/;
    $cachemem = int $1 / 2048;
    if ($proxysettings{'CACHE_MEM'} > $cachemem) {
        $proxysettings{'CACHE_MEM'} = $cachemem;
    }
    if (!($proxysettings{'MAX_SIZE'} =~ /^\d+/))
    {
        $errormessage = $Lang::tr{'invalid maximum object size'};
        $error_options = 'error';
        goto ERROR;
    }
    if (!($proxysettings{'MIN_SIZE'} =~ /^\d+/))
    {
        $errormessage = $Lang::tr{'invalid minimum object size'};
        $error_options = 'error';
        goto ERROR;
    }
    if (!($proxysettings{'MAX_OUTGOING_SIZE'} =~ /^\d+/))
    {
        $errormessage = $Lang::tr{'invalid maximum outgoing size'};
        $error_options = 'error';
        goto ERROR;
    }
    if (!($proxysettings{'TIME_TO_HOUR'}.$proxysettings{'TIME_TO_MINUTE'} gt $proxysettings{'TIME_FROM_HOUR'}.$proxysettings{'TIME_FROM_MINUTE'}))
    {
        $errormessage = $Lang::tr{'errmsg time restriction'};
        $error_options = 'error';
        goto ERROR;
    }
    if (!($proxysettings{'MAX_INCOMING_SIZE'} =~ /^\d+/))
    {
        $errormessage = $Lang::tr{'invalid maximum incoming size'};
        $error_options = 'error';
        goto ERROR;
    }
    if ($proxysettings{'ENABLE_BROWSER_CHECK'} eq 'on')
    {
        $browser_regexp = '';
        foreach (@useragentlist)
        {
            chomp;
            @useragent = split(/,/);
            if ($proxysettings{'UA_'.@useragent[0]} eq 'on') { $browser_regexp .= "@useragent[2]|"; }
        }
        chop($browser_regexp);
        if (!$browser_regexp)
        {
            $errormessage = $Lang::tr{'errmsg no browser'};
            goto ERROR;
        }
    }
    if (!($proxysettings{'AUTH_METHOD'} eq 'none'))
    {
        unless (($proxysettings{'AUTH_METHOD'} eq 'ident') &&
            ($proxysettings{'IDENT_REQUIRED'} eq 'off') &&
            ($proxysettings{'IDENT_ENABLE_ACL'} eq 'off'))
        {
            if ($netsettings{'BLUE_COUNT'} >= 1)
            {
                if ((($proxysettings{'ENABLED_GREEN_1'} eq 'off') || ($proxysettings{'TRANSPARENT_GREEN_1'} eq 'on')) &&
                    (($proxysettings{'ENABLED_BLUE_1'} eq 'off') || ($proxysettings{'TRANSPARENT_BLUE_1'} eq 'on')))
                {
                    $errormessage = $Lang::tr{'errmsg non-transparent proxy required'};
                    goto ERROR;
                }
            }
            else {
                if (($proxysettings{'ENABLED_GREEN_1'} eq 'off') || ($proxysettings{'TRANSPARENT_GREEN_1'} eq 'on'))
                {
                    $errormessage = $Lang::tr{'errmsg non-transparent proxy required'};
                    goto ERROR;
                }
            }
        }
        if ((!($proxysettings{'AUTH_MAX_USERIP'} eq '')) &&
            ((!($proxysettings{'AUTH_MAX_USERIP'} =~ /^\d+/)) || ($proxysettings{'AUTH_MAX_USERIP'} < 1) || ($proxysettings{'AUTH_MAX_USERIP'} > 255)))
        {
            $errormessage = $Lang::tr{'errmsg max userip'};
            goto ERROR;
        }
        if (!($proxysettings{'AUTH_CACHE_TTL'} =~ /^\d+/))
        {
            $errormessage = $Lang::tr{'errmsg auth cache ttl'};
            goto ERROR;
        }
        if (!($proxysettings{'AUTH_IPCACHE_TTL'} =~ /^\d+/))
        {
            $errormessage = $Lang::tr{'errmsg auth ipcache ttl'};
            goto ERROR;
        }
        if ((!($proxysettings{'AUTH_MAX_USERIP'} eq '')) && ($proxysettings{'AUTH_IPCACHE_TTL'} eq '0'))
        {
            $errormessage = $Lang::tr{'errmsg auth ipcache may not be null'};
            goto ERROR;
        }
        if ((!($proxysettings{'AUTH_CHILDREN'} =~ /^\d+/)) || ($proxysettings{'AUTH_CHILDREN'} < 1) || ($proxysettings{'AUTH_CHILDREN'} > 255))
        {
            $errormessage = $Lang::tr{'errmsg auth children'};
            goto ERROR;
        }
    }
    if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
    {
        if ((!($proxysettings{'NCSA_MIN_PASS_LEN'} =~ /^\d+/)) || ($proxysettings{'NCSA_MIN_PASS_LEN'} < 1) || ($proxysettings{'NCSA_MIN_PASS_LEN'} > 255))
        {
            $errormessage = $Lang::tr{'errmsg password length'};
            goto ERROR;
        }
    }
    if ($proxysettings{'AUTH_METHOD'} eq 'ident')
    {
        if ((!($proxysettings{'IDENT_TIMEOUT'} =~ /^\d+/)) || ($proxysettings{'IDENT_TIMEOUT'} < 1))
        {
            $errormessage = $Lang::tr{'errmsg ident timeout'};
            goto ERROR;
        }
    }
    if ($proxysettings{'AUTH_METHOD'} eq 'ldap')
    {
        if ($proxysettings{'LDAP_BASEDN'} eq '')
        {
            $errormessage = $Lang::tr{'errmsg ldap base dn'};
            goto ERROR;
        }
        if (!&General::validip($proxysettings{'LDAP_SERVER'}))
        {
            $errormessage = $Lang::tr{'errmsg ldap server'};
            goto ERROR;
        }
        if (!&General::validport($proxysettings{'LDAP_PORT'}))
        {
            $errormessage = $Lang::tr{'errmsg ldap port'};
            goto ERROR;
        }
        if (($proxysettings{'LDAP_TYPE'} eq 'ADS') || ($proxysettings{'LDAP_TYPE'} eq 'NDS'))
        {
            if (($proxysettings{'LDAP_BINDDN_USER'} eq '') || ($proxysettings{'LDAP_BINDDN_PASS'} eq ''))
            {
                $errormessage = $Lang::tr{'errmsg ldap bind dn'};
                goto ERROR;
            }
        }
    }
    if ($proxysettings{'AUTH_METHOD'} eq 'ntlm')
    {
        if ($proxysettings{'NTLM_DOMAIN'} eq '')
        {
            $errormessage = $Lang::tr{'errmsg ntlm domain'};
            goto ERROR;
        }
        if ($proxysettings{'NTLM_PDC'} eq '')
        {
            $errormessage = $Lang::tr{'errmsg ntlm pdc'};
            goto ERROR;
        }
        if (!&General::validhostname($proxysettings{'NTLM_PDC'}))
        {
            $errormessage = $Lang::tr{'errmsg invalid pdc'};
            goto ERROR;
        }
        if ((!($proxysettings{'NTLM_BDC'} eq '')) && (!&General::validhostname($proxysettings{'NTLM_BDC'})))
        {
            $errormessage = $Lang::tr{'errmsg invalid bdc'};
            goto ERROR;
        }

        $proxysettings{'NTLM_DOMAIN'} = lc($proxysettings{'NTLM_DOMAIN'});
        $proxysettings{'NTLM_PDC'}    = lc($proxysettings{'NTLM_PDC'});
        $proxysettings{'NTLM_BDC'}    = lc($proxysettings{'NTLM_BDC'});
    }
    if ($proxysettings{'AUTH_METHOD'} eq 'radius')
    {
        if (!&General::validip($proxysettings{'RADIUS_SERVER'}))
        {
            $errormessage = $Lang::tr{'errmsg radius server'};
            goto ERROR;
        }
        if (!&General::validport($proxysettings{'RADIUS_PORT'}))
        {
            $errormessage = $Lang::tr{'errmsg radius port'};
            goto ERROR;
        }
        if ($proxysettings{'RADIUS_SECRET'} eq '')
        {
            $errormessage = $Lang::tr{'errmsg radius secret'};
            goto ERROR;
        }
    }

    # Quick parent proxy error checking of username and password info. If username password don't both exist give an error.
    $proxy1 = 'YES';
    $proxy2 = 'YES';
    if (($proxysettings{'UPSTREAM_USER'} eq '')) {$proxy1 = '';}
    if (($proxysettings{'UPSTREAM_PASSWORD'} eq '')) {$proxy2 = '';}
    if ($proxysettings{'UPSTREAM_USER'} eq 'PASS')  {$proxy1=$proxy2='PASS'; $proxysettings{'UPSTREAM_PASSWORD'} = '';}
    if (($proxy1 ne $proxy2))
    {
        $errormessage = $Lang::tr{'errmsg invalid upstream proxy username or password setting'};
        $error_settings = 'error';
        goto ERROR;
    }

ERROR:
    &check_acls;

    if ($errormessage) {
        $proxysettings{'VALID'} = 'no'; }
    else {
        $proxysettings{'VALID'} = 'yes'; }

    if ($proxysettings{'VALID'} eq 'yes')
    {
        &write_acls;

        delete $proxysettings{'SRC_SUBNETS'};
        delete $proxysettings{'SRC_BANNED_IP'};
        delete $proxysettings{'SRC_BANNED_MAC'};
        delete $proxysettings{'SRC_UNRESTRICTED_IP'};
        delete $proxysettings{'SRC_UNRESTRICTED_MAC'};
        delete $proxysettings{'DST_NOCACHE'};
        delete $proxysettings{'DST_NOAUTH'};
        delete $proxysettings{'PORTS_SAFE'};
        delete $proxysettings{'PORTS_SSL'};
        delete $proxysettings{'MIME_TYPES'};
        delete $proxysettings{'MIME_EXCEPTIONS'};
        delete $proxysettings{'NTLM_ALLOW_USERS'};
        delete $proxysettings{'NTLM_DENY_USERS'};
        delete $proxysettings{'RADIUS_ALLOW_USERS'};
        delete $proxysettings{'RADIUS_DENY_USERS'};
        delete $proxysettings{'IDENT_HOSTS'};
        delete $proxysettings{'IDENT_ALLOW_USERS'};
        delete $proxysettings{'IDENT_DENY_USERS'};

        delete $proxysettings{'CRE_GROUPS'};
        delete $proxysettings{'CRE_SVHOSTS'};

        delete $proxysettings{'NCSA_USERNAME'};
        delete $proxysettings{'NCSA_GROUP'};
        delete $proxysettings{'NCSA_PASS'};
        delete $proxysettings{'NCSA_PASS_CONFIRM'};

        $proxysettings{'TIME_MON'} = 'off' unless exists $proxysettings{'TIME_MON'};
        $proxysettings{'TIME_TUE'} = 'off' unless exists $proxysettings{'TIME_TUE'};
        $proxysettings{'TIME_WED'} = 'off' unless exists $proxysettings{'TIME_WED'};
        $proxysettings{'TIME_THU'} = 'off' unless exists $proxysettings{'TIME_THU'};
        $proxysettings{'TIME_FRI'} = 'off' unless exists $proxysettings{'TIME_FRI'};
        $proxysettings{'TIME_SAT'} = 'off' unless exists $proxysettings{'TIME_SAT'};
        $proxysettings{'TIME_SUN'} = 'off' unless exists $proxysettings{'TIME_SUN'};

        $proxysettings{'AUTH_ALWAYS_REQUIRED'} = 'off' unless exists $proxysettings{'AUTH_ALWAYS_REQUIRED'};
        $proxysettings{'NTLM_ENABLE_INT_AUTH'} = 'off' unless exists $proxysettings{'NTLM_ENABLE_INT_AUTH'};

        &General::writehash("/var/ipcop/proxy/settings", \%proxysettings);

        &writeconfig;
        &writepacfile;

        system('/usr/local/bin/restartsquid');
        if (($proxysettings{'ENABLED_GREEN_1'} eq 'on') || ($proxysettings{'ENABLED_BLUE_1'} eq 'on')) {
            # wait a bit so proxy can start and we can display proper running state
            sleep(5);
        }
    }
}

if ($proxysettings{'ACTION'} eq $Lang::tr{'clear cache'})
{
    system('/usr/local/bin/restartsquid','-f');
}

} # end of ACTION

if (!$errormessage)
{
    if (-e "/var/ipcop/proxy/settings") {
        &General::readhash("/var/ipcop/proxy/settings", \%proxysettings);
    }
    &read_acls;
}

$checked{'ENABLED_GREEN_1'}{'off'} = '';
$checked{'ENABLED_GREEN_1'}{'on'} = '';
$checked{'ENABLED_GREEN_1'}{$proxysettings{'ENABLED_GREEN_1'}} = "checked='checked'";

$checked{'TRANSPARENT_GREEN_1'}{'off'} = '';
$checked{'TRANSPARENT_GREEN_1'}{'on'} = '';
$checked{'TRANSPARENT_GREEN_1'}{$proxysettings{'TRANSPARENT_GREEN_1'}} = "checked='checked'";

$checked{'ENABLED_BLUE_1'}{'off'} = '';
$checked{'ENABLED_BLUE_1'}{'on'} = '';
$checked{'ENABLED_BLUE_1'}{$proxysettings{'ENABLED_BLUE_1'}} = "checked='checked'";

$checked{'TRANSPARENT_BLUE_1'}{'off'} = '';
$checked{'TRANSPARENT_BLUE_1'}{'on'} = '';
$checked{'TRANSPARENT_BLUE_1'}{$proxysettings{'TRANSPARENT_BLUE_1'}} = "checked='checked'";

$checked{'ENABLED_OVPN'}{'off'} = '';
$checked{'ENABLED_OVPN'}{'on'} = '';
$checked{'ENABLED_OVPN'}{$proxysettings{'ENABLED_OVPN'}} = "checked='checked'";

$checked{'TRANSPARENT_OVPN'}{'off'} = '';
$checked{'TRANSPARENT_OVPN'}{'on'} = '';
$checked{'TRANSPARENT_OVPN'}{$proxysettings{'TRANSPARENT_OVPN'}} = "checked='checked'";

$checked{'SUPPRESS_VERSION'}{'off'} = '';
$checked{'SUPPRESS_VERSION'}{'on'} = '';
$checked{'SUPPRESS_VERSION'}{$proxysettings{'SUPPRESS_VERSION'}} = "checked='checked'";

$checked{'FORWARD_IPADDRESS'}{'off'} = '';
$checked{'FORWARD_IPADDRESS'}{'on'} = '';
$checked{'FORWARD_IPADDRESS'}{$proxysettings{'FORWARD_IPADDRESS'}} = "checked='checked'";
$checked{'FORWARD_USERNAME'}{'off'} = '';
$checked{'FORWARD_USERNAME'}{'on'} = '';
$checked{'FORWARD_USERNAME'}{$proxysettings{'FORWARD_USERNAME'}} = "checked='checked'";
$checked{'FORWARD_VIA'}{'off'} = '';
$checked{'FORWARD_VIA'}{'on'} = '';
$checked{'FORWARD_VIA'}{$proxysettings{'FORWARD_VIA'}} = "checked='checked'";
$checked{'NO_CONNECTION_AUTH'}{'off'} = '';
$checked{'NO_CONNECTION_AUTH'}{'on'} = '';
$checked{'NO_CONNECTION_AUTH'}{$proxysettings{'NO_CONNECTION_AUTH'}} = "checked='checked'";

$selected{'MEM_POLICY'}{$proxysettings{'MEM_POLICY'}} = "selected='selected'";
$selected{'CACHE_POLICY'}{$proxysettings{'CACHE_POLICY'}} = "selected='selected'";
$selected{'L1_DIRS'}{$proxysettings{'L1_DIRS'}} = "selected='selected'";
$checked{'OFFLINE_MODE'}{'off'} = '';
$checked{'OFFLINE_MODE'}{'on'} = '';
$checked{'OFFLINE_MODE'}{$proxysettings{'OFFLINE_MODE'}} = "checked='checked'";

$checked{'LOGGING'}{'off'} = '';
$checked{'LOGGING'}{'on'} = '';
$checked{'LOGGING'}{$proxysettings{'LOGGING'}} = "checked='checked'";
$checked{'LOGQUERY'}{'off'} = '';
$checked{'LOGQUERY'}{'on'} = '';
$checked{'LOGQUERY'}{$proxysettings{'LOGQUERY'}} = "checked='checked'";
$checked{'LOGUSERAGENT'}{'off'} = '';
$checked{'LOGUSERAGENT'}{'on'} = '';
$checked{'LOGUSERAGENT'}{$proxysettings{'LOGUSERAGENT'}} = "checked='checked'";

$selected{'ERR_LANGUAGE'}{$proxysettings{'ERR_LANGUAGE'}} = "selected='selected'";
$selected{'ERR_DESIGN'}{$proxysettings{'ERR_DESIGN'}} = "selected='selected'";

$checked{'NO_PROXY_LOCAL'}{'off'} = '';
$checked{'NO_PROXY_LOCAL'}{'on'} = '';
$checked{'NO_PROXY_LOCAL'}{$proxysettings{'NO_PROXY_LOCAL'}} = "checked='checked'";
$checked{'NO_PROXY_LOCAL_GREEN'}{'off'} = '';
$checked{'NO_PROXY_LOCAL_GREEN'}{'on'} = '';
$checked{'NO_PROXY_LOCAL_GREEN'}{$proxysettings{'NO_PROXY_LOCAL_GREEN'}} = "checked='checked'";
$checked{'NO_PROXY_LOCAL_BLUE'}{'off'} = '';
$checked{'NO_PROXY_LOCAL_BLUE'}{'on'} = '';
$checked{'NO_PROXY_LOCAL_BLUE'}{$proxysettings{'NO_PROXY_LOCAL_BLUE'}} = "checked='checked'";

$checked{'CLASSROOM_EXT'}{'off'} = '';
$checked{'CLASSROOM_EXT'}{'on'} = '';
$checked{'CLASSROOM_EXT'}{$proxysettings{'CLASSROOM_EXT'}} = "checked='checked'";

$selected{'TIME_ACCESS_MODE'}{$proxysettings{'TIME_ACCESS_MODE'}} = "selected='selected'";
$selected{'TIME_FROM_HOUR'}{$proxysettings{'TIME_FROM_HOUR'}} = "selected='selected'";
$selected{'TIME_FROM_MINUTE'}{$proxysettings{'TIME_FROM_MINUTE'}} = "selected='selected'";
$selected{'TIME_TO_HOUR'}{$proxysettings{'TIME_TO_HOUR'}} = "selected='selected'";
$selected{'TIME_TO_MINUTE'}{$proxysettings{'TIME_TO_MINUTE'}} = "selected='selected'";

$proxysettings{'TIME_MON'} = 'on' unless exists $proxysettings{'TIME_MON'};
$proxysettings{'TIME_TUE'} = 'on' unless exists $proxysettings{'TIME_TUE'};
$proxysettings{'TIME_WED'} = 'on' unless exists $proxysettings{'TIME_WED'};
$proxysettings{'TIME_THU'} = 'on' unless exists $proxysettings{'TIME_THU'};
$proxysettings{'TIME_FRI'} = 'on' unless exists $proxysettings{'TIME_FRI'};
$proxysettings{'TIME_SAT'} = 'on' unless exists $proxysettings{'TIME_SAT'};
$proxysettings{'TIME_SUN'} = 'on' unless exists $proxysettings{'TIME_SUN'};

$checked{'TIME_MON'}{'off'} = '';
$checked{'TIME_MON'}{'on'} = '';
$checked{'TIME_MON'}{$proxysettings{'TIME_MON'}} = "checked='checked'";
$checked{'TIME_TUE'}{'off'} = '';
$checked{'TIME_TUE'}{'on'} = '';
$checked{'TIME_TUE'}{$proxysettings{'TIME_TUE'}} = "checked='checked'";
$checked{'TIME_WED'}{'off'} = '';
$checked{'TIME_WED'}{'on'} = '';
$checked{'TIME_WED'}{$proxysettings{'TIME_WED'}} = "checked='checked'";
$checked{'TIME_THU'}{'off'} = '';
$checked{'TIME_THU'}{'on'} = '';
$checked{'TIME_THU'}{$proxysettings{'TIME_THU'}} = "checked='checked'";
$checked{'TIME_FRI'}{'off'} = '';
$checked{'TIME_FRI'}{'on'} = '';
$checked{'TIME_FRI'}{$proxysettings{'TIME_FRI'}} = "checked='checked'";
$checked{'TIME_SAT'}{'off'} = '';
$checked{'TIME_SAT'}{'on'} = '';
$checked{'TIME_SAT'}{$proxysettings{'TIME_SAT'}} = "checked='checked'";
$checked{'TIME_SUN'}{'off'} = '';
$checked{'TIME_SUN'}{'on'} = '';
$checked{'TIME_SUN'}{$proxysettings{'TIME_SUN'}} = "checked='checked'";

$selected{'THROTTLING_GREEN_TOTAL'}{$proxysettings{'THROTTLING_GREEN_TOTAL'}} = "selected='selected'";
$selected{'THROTTLING_GREEN_HOST'}{$proxysettings{'THROTTLING_GREEN_HOST'}} = "selected='selected'";
$selected{'THROTTLING_BLUE_TOTAL'}{$proxysettings{'THROTTLING_BLUE_TOTAL'}} = "selected='selected'";
$selected{'THROTTLING_BLUE_HOST'}{$proxysettings{'THROTTLING_BLUE_HOST'}} = "selected='selected'";

$checked{'THROTTLE_BINARY'}{'off'} = '';
$checked{'THROTTLE_BINARY'}{'on'} = '';
$checked{'THROTTLE_BINARY'}{$proxysettings{'THROTTLE_BINARY'}} = "checked='checked'";
$checked{'THROTTLE_DSKIMG'}{'off'} = '';
$checked{'THROTTLE_DSKIMG'}{'on'} = '';
$checked{'THROTTLE_DSKIMG'}{$proxysettings{'THROTTLE_DSKIMG'}} = "checked='checked'";
$checked{'THROTTLE_MMEDIA'}{'off'} = '';
$checked{'THROTTLE_MMEDIA'}{'on'} = '';
$checked{'THROTTLE_MMEDIA'}{$proxysettings{'THROTTLE_MMEDIA'}} = "checked='checked'";

$checked{'ENABLE_MIME_FILTER'}{'off'} = '';
$checked{'ENABLE_MIME_FILTER'}{'on'} = '';
$checked{'ENABLE_MIME_FILTER'}{$proxysettings{'ENABLE_MIME_FILTER'}} = "checked='checked'";

$checked{'ENABLE_BROWSER_CHECK'}{'off'} = '';
$checked{'ENABLE_BROWSER_CHECK'}{'on'} = '';
$checked{'ENABLE_BROWSER_CHECK'}{$proxysettings{'ENABLE_BROWSER_CHECK'}} = "checked='checked'";

foreach (@useragentlist) {
    @useragent = split(/,/);
    $checked{'UA_'.@useragent[0]}{'off'} = '';
    $checked{'UA_'.@useragent[0]}{'on'} = '';
    $checked{'UA_'.@useragent[0]}{$proxysettings{'UA_'.@useragent[0]}} = "checked='checked'";
}

$checked{'AUTH_METHOD'}{'none'} = '';
$checked{'AUTH_METHOD'}{'ncsa'} = '';
$checked{'AUTH_METHOD'}{'ident'} = '';
$checked{'AUTH_METHOD'}{'ldap'} = '';
$checked{'AUTH_METHOD'}{'ntlm'} = '';
$checked{'AUTH_METHOD'}{'radius'} = '';
$checked{'AUTH_METHOD'}{$proxysettings{'AUTH_METHOD'}} = "checked='checked'";

$proxysettings{'AUTH_ALWAYS_REQUIRED'} = 'on' unless exists $proxysettings{'AUTH_ALWAYS_REQUIRED'};

$checked{'AUTH_ALWAYS_REQUIRED'}{'off'} = '';
$checked{'AUTH_ALWAYS_REQUIRED'}{'on'} = '';
$checked{'AUTH_ALWAYS_REQUIRED'}{$proxysettings{'AUTH_ALWAYS_REQUIRED'}} = "checked='checked'";

$checked{'NCSA_BYPASS_REDIR'}{'off'} = '';
$checked{'NCSA_BYPASS_REDIR'}{'on'} = '';
$checked{'NCSA_BYPASS_REDIR'}{$proxysettings{'NCSA_BYPASS_REDIR'}} = "checked='checked'";

$selected{'NCSA_GROUP'}{$proxysettings{'NCSA_GROUP'}} = "selected='selected'";

$selected{'LDAP_TYPE'}{$proxysettings{'LDAP_TYPE'}} = "selected='selected'";

$proxysettings{'NTLM_ENABLE_INT_AUTH'} = 'on' unless exists $proxysettings{'NTLM_ENABLE_INT_AUTH'};

$checked{'NTLM_ENABLE_INT_AUTH'}{'off'} = '';
$checked{'NTLM_ENABLE_INT_AUTH'}{'on'} = '';
$checked{'NTLM_ENABLE_INT_AUTH'}{$proxysettings{'NTLM_ENABLE_INT_AUTH'}} = "checked='checked'";

$checked{'NTLM_ENABLE_ACL'}{'off'} = '';
$checked{'NTLM_ENABLE_ACL'}{'on'} = '';
$checked{'NTLM_ENABLE_ACL'}{$proxysettings{'NTLM_ENABLE_ACL'}} = "checked='checked'";

$checked{'NTLM_USER_ACL'}{'positive'} = '';
$checked{'NTLM_USER_ACL'}{'negative'} = '';
$checked{'NTLM_USER_ACL'}{$proxysettings{'NTLM_USER_ACL'}} = "checked='checked'";

$checked{'RADIUS_ENABLE_ACL'}{'off'} = '';
$checked{'RADIUS_ENABLE_ACL'}{'on'} = '';
$checked{'RADIUS_ENABLE_ACL'}{$proxysettings{'RADIUS_ENABLE_ACL'}} = "checked='checked'";

$checked{'RADIUS_USER_ACL'}{'positive'} = '';
$checked{'RADIUS_USER_ACL'}{'negative'} = '';
$checked{'RADIUS_USER_ACL'}{$proxysettings{'RADIUS_USER_ACL'}} = "checked='checked'";

$checked{'IDENT_REQUIRED'}{'off'} = '';
$checked{'IDENT_REQUIRED'}{'on'} = '';
$checked{'IDENT_REQUIRED'}{$proxysettings{'IDENT_REQUIRED'}} = "checked='checked'";

$checked{'IDENT_ENABLE_ACL'}{'off'} = '';
$checked{'IDENT_ENABLE_ACL'}{'on'} = '';
$checked{'IDENT_ENABLE_ACL'}{$proxysettings{'IDENT_ENABLE_ACL'}} = "checked='checked'";

$checked{'IDENT_USER_ACL'}{'positive'} = '';
$checked{'IDENT_USER_ACL'}{'negative'} = '';
$checked{'IDENT_USER_ACL'}{$proxysettings{'IDENT_USER_ACL'}} = "checked='checked'";

if ($urlfilter_addon) {
    $checked{'ENABLE_FILTER'}{'off'} = '';
    $checked{'ENABLE_FILTER'}{'on'} = '';
    $checked{'ENABLE_FILTER'}{$proxysettings{'ENABLE_FILTER'}} = "checked='checked'";
}

if ($updaccel_addon) {
    $checked{'ENABLE_UPDXLRATOR'}{'off'} = '';
    $checked{'ENABLE_UPDXLRATOR'}{'on'} = '';
    $checked{'ENABLE_UPDXLRATOR'}{$proxysettings{'ENABLE_UPDXLRATOR'}} = "checked='checked'";
}

&Header::openpage($Lang::tr{'web proxy configuration'}, 1, '');

&Header::openbigbox('100%', 'left', '', $errormessage);

if ($errormessage) {
    &Header::openbox('100%', 'left', "$Lang::tr{'error messages'}:", 'error');
    print "<font class='base'>$errormessage&nbsp;</font>\n";
    &Header::closebox();
}

if ($squidversion[0] =~ /^Squid\sCache:\sVersion\s/i)
{
    $squidversion[0] =~ s/^Squid\sCache:\sVersion//i;
    $squidversion[0] =~ s/^\s+//g;
    $squidversion[0] =~ s/\s+$//g;
} else {
    $squidversion[0] = $Lang::tr{'unknown'};
}

# ===================================================================
#  Main settings
# ===================================================================

unless ($proxysettings{'NCSA_EDIT_MODE'} eq 'yes') {

print "<form method='post' action='$ENV{'SCRIPT_NAME'}'>\n";

&Header::openbox('100%', 'left', "$Lang::tr{'settings'}", $error_settings);
my $sactive = &General::isrunning('squid', 'nosize');

print <<END
<table width='100%'>
<tr>
    <td>$Lang::tr{'web proxy'}:</td>
    $sactive
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
<tr>
    <td colspan='4' class='base'><hr /></td>
</tr>
<tr>
    <td colspan='4' class='base'><b>$Lang::tr{'common settings'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'enabled on'} <span class='ipcop_iface_green' style='font-weight: bold;'>$Lang::tr{'green'}</span>:</td>
    <td width='20%'><input type='checkbox' name='ENABLED_GREEN_1' $checked{'ENABLED_GREEN_1'}{'on'} /></td>
    <td width='30%' class='base'>$Lang::tr{'transparent on'} <span class='ipcop_iface_green' style='font-weight: bold;'>$Lang::tr{'green'}</span>:</td>
    <td width='25%'><input type='checkbox' name='TRANSPARENT_GREEN_1' $checked{'TRANSPARENT_GREEN_1'}{'on'} /></td>
</tr>
END
;
if ($netsettings{'BLUE_COUNT'} >= 1) {
    print "<tr><td class='base'>$Lang::tr{'enabled on'} <span class='ipcop_iface_blue' style='font-weight: bold;'>$Lang::tr{'blue'}</span>:</td>";
    print "<td><input type='checkbox' name='ENABLED_BLUE_1' $checked{'ENABLED_BLUE_1'}{'on'} /></td>";
    print "<td class='base'>$Lang::tr{'transparent on'} <span class='ipcop_iface_blue' style='font-weight: bold;'>$Lang::tr{'blue'}</span>:</td>";
    print "<td><input type='checkbox' name='TRANSPARENT_BLUE_1' $checked{'TRANSPARENT_BLUE_1'}{'on'} /></td></tr>";
}
if ((defined($ovpnsettings{'ENABLED_RED_1'}) && $ovpnsettings{'ENABLED_RED_1'} eq 'on')
    || (defined($ovpnsettings{'ENABLED_BLUE_1'}) && $ovpnsettings{'ENABLED_BLUE_1'} eq 'on')) {
    print "<tr><td class='base'>$Lang::tr{'enabled on'} <span class='ipcop_iface_ovpn' style='font-weight: bold;'>OpenVPN</span>:</td>";
    print "<td><input type='checkbox' name='ENABLED_OVPN' $checked{'ENABLED_OVPN'}{'on'} /></td>";
    print "<td class='base'>$Lang::tr{'transparent on'} <span class='ipcop_iface_ovpn' style='font-weight: bold;'>OpenVPN</span>:</td>";
    print "<td><input type='checkbox' name='TRANSPARENT_OVPN' $checked{'TRANSPARENT_OVPN'}{'on'} /></td></tr>";
}
print <<END

<tr>
    <td class='base'>$Lang::tr{'proxy port'}:</td>
    <td><input type='text' name='PROXY_PORT' value='$proxysettings{'PROXY_PORT'}' size='5' /></td>
    <td class='base'>$Lang::tr{'visible hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='VISIBLE_HOSTNAME' value='$proxysettings{'VISIBLE_HOSTNAME'}' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'error language'}:</td>
    <td class='base'>
    <select name='ERR_LANGUAGE'>
END
;
    foreach (<$errordir/*>) {
        if (-d) {
            $countrycode = substr($_,rindex($_,"/")+1);
            print "<option value='$countrycode' $selected{'ERR_LANGUAGE'}{$countrycode}>$language{$countrycode}</option>\n";
        }
    }
print <<END
    </select>
    </td>
    <td class='base'>$Lang::tr{'admin mail'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='ADMIN_MAIL_ADDRESS' value='$proxysettings{'ADMIN_MAIL_ADDRESS'}' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'error design'}:</td>
    <td class='base'><select name='ERR_DESIGN'>
        <option value='ipcop' $selected{'ERR_DESIGN'}{'ipcop'}>IPCop</option>
        <option value='squid' $selected{'ERR_DESIGN'}{'squid'}>$Lang::tr{'standard'}</option>
    </select></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'suppress version'}:</td>
    <td><input type='checkbox' name='SUPPRESS_VERSION' $checked{'SUPPRESS_VERSION'}{'on'} /></td>
    <td class='base'>$Lang::tr{'squid version'}:</td>
    <td class='base'>&nbsp;[ $squidversion[0] ]</td>
</tr>
<tr>
    <td colspan='4'><hr size='1'/></td>
</tr>
<tr>
    <td colspan='4' class='base'><b>$Lang::tr{'upstream proxy'}</b></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'via forwarding'}:</td>
    <td><input type='checkbox' name='FORWARD_VIA' $checked{'FORWARD_VIA'}{'on'} /></td>
    <td class='base'>$Lang::tr{'upstream proxy host:port'}&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='UPSTREAM_PROXY' value='$proxysettings{'UPSTREAM_PROXY'}' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'client IP forwarding'}:</td>
    <td><input type='checkbox' name='FORWARD_IPADDRESS' $checked{'FORWARD_IPADDRESS'}{'on'} /></td>
    <td class='base'>$Lang::tr{'upstream username'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='UPSTREAM_USER' value='$proxysettings{'UPSTREAM_USER'}' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'username forwarding'}:</td>
    <td><input type='checkbox' name='FORWARD_USERNAME' $checked{'FORWARD_USERNAME'}{'on'} /></td>
    <td class='base'>$Lang::tr{'upstream password'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='password' name='UPSTREAM_PASSWORD' value='$proxysettings{'UPSTREAM_PASSWORD'}' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'no connection auth'}:</td>
    <td><input type='checkbox' name='NO_CONNECTION_AUTH' $checked{'NO_CONNECTION_AUTH'}{'on'} /></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
<tr>
    <td colspan='4'><hr size='1'/></td>
</tr>
<tr>
    <td colspan='4' class='base'><b>$Lang::tr{'log settings'}</b></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'log enabled'}:</td>
    <td><input type='checkbox' name='LOGGING' $checked{'LOGGING'}{'on'} /></td>
    <td class='base'>$Lang::tr{'log query'}:</td>
    <td><input type='checkbox' name='LOGQUERY' $checked{'LOGQUERY'}{'on'} /></td>
</tr>
<tr>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td class='base'>$Lang::tr{'log useragent'}:</td>
    <td><input type='checkbox' name='LOGUSERAGENT' $checked{'LOGUSERAGENT'}{'on'} /></td>
</tr>
</table>

<hr />
<table width='100%'>
<tr>
    <td class='comment1button'><img src='/blob.gif' align='top' alt='*' />&nbsp;
    <font class='base'>$Lang::tr{'this field may be blank'}</font>
    </td>
    <td class='button2buttons'><input type='submit' name='ACTION' value='$Lang::tr{'clear cache'}' /></td>
    <td class='button2buttons'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/services-webproxy.html' target='_blank'>
        <img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>

    </td>
</tr>
</table>

END
;

&Header::closebox();

&Header::openbox('100%', 'left', "$Lang::tr{'adv options'}", $error_options);

print <<END
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'cache management'}</b></td>
</tr>
<tr>
    <td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'ram cache size'}:</td>
    <td><input type='text' name='CACHE_MEM' value='$proxysettings{'CACHE_MEM'}' size='5' /></td>
    <td class='base'>$Lang::tr{'hdd cache size'}:</td>
    <td><input type='text' name='CACHE_SIZE' value='$proxysettings{'CACHE_SIZE'}' size='5' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'min size'}:</td>
    <td><input type='text' name='MIN_SIZE' value='$proxysettings{'MIN_SIZE'}' size='5' /></td>
    <td class='base'>$Lang::tr{'max size'}:</td>
    <td><input type='text' name='MAX_SIZE' value='$proxysettings{'MAX_SIZE'}' size='5' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'number of L1 dirs'}:</td>
    <td class='base'><select name='L1_DIRS'>
        <option value='16'  $selected{'L1_DIRS'}{'16'}>16</option>
        <option value='32'  $selected{'L1_DIRS'}{'32'}>32</option>
        <option value='64'  $selected{'L1_DIRS'}{'64'}>64</option>
        <option value='128' $selected{'L1_DIRS'}{'128'}>128</option>
        <option value='256' $selected{'L1_DIRS'}{'256'}>256</option>
    </select></td>
    <td colspan='2' rowspan= '5' valign='top' class='base'>
        <table cellspacing='0' cellpadding='0'>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
            <td>$Lang::tr{'no cache sites'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
            </tr>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
            <td><textarea name='DST_NOCACHE' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'DST_NOCACHE'};

print <<END
</textarea></td>
        </tr>
        </table>
    </td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'memory replacement policy'}:</td>
    <td class='base'><select name='MEM_POLICY'>
        <option value='LRU' $selected{'MEM_POLICY'}{'LRU'}>LRU</option>
        <option value='heap LFUDA' $selected{'MEM_POLICY'}{'heap LFUDA'}>heap LFUDA</option>
        <option value='heap GDSF' $selected{'MEM_POLICY'}{'heap GDSF'}>heap GDSF</option>
        <option value='heap LRU' $selected{'MEM_POLICY'}{'heap LRU'}>heap LRU</option>
    </select></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'cache replacement policy'}:</td>
    <td class='base'><select name='CACHE_POLICY'>
        <option value='LRU' $selected{'CACHE_POLICY'}{'LRU'}>LRU</option>
        <option value='heap LFUDA' $selected{'CACHE_POLICY'}{'heap LFUDA'}>heap LFUDA</option>
        <option value='heap GDSF' $selected{'CACHE_POLICY'}{'heap GDSF'}>heap GDSF</option>
        <option value='heap LRU' $selected{'CACHE_POLICY'}{'heap LRU'}>heap LRU</option>
    </select></td>
</tr>
<tr>
    <td colspan='2'>&nbsp;</td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'offline mode'}:</td>
    <td><input type='checkbox' name='OFFLINE_MODE' $checked{'OFFLINE_MODE'}{'on'} /></td>
</tr>
</table>
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'destination ports'}</b></td>
</tr>
<tr>
    <td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
    <td colspan='2' class='base'>$Lang::tr{'standard ports'}:</td>
    <td colspan='2' class='base'>$Lang::tr{'ssl ports'}:</td>
</tr>
<tr>
    <td colspan='2'><textarea name='PORTS_SAFE' cols='32' rows='6' wrap='off'>
END
;
    if (!$proxysettings{'PORTS_SAFE'}) { print $def_ports_safe; } else { print $proxysettings{'PORTS_SAFE'}; }

print <<END
</textarea></td>
    <td colspan='2'><textarea name='PORTS_SSL' cols='32' rows='6' wrap='off'>
END
;
    if (!$proxysettings{'PORTS_SSL'}) { print $def_ports_ssl; } else { print $proxysettings{'PORTS_SSL'}; }

print <<END
</textarea></td>
</tr>
</table>
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'network based access'}</b></td>
</tr>
<tr>
    <td width='25%'></td> <td width='20%'> </td><td width='30%'> </td><td width='25%'></td>
</tr>
<tr>
    <td colspan='2' class='base'>$Lang::tr{'allowed subnets'}:</td>
    <td colspan='2'>&nbsp;</td>
</tr>
<tr>
    <td colspan='2' rowspan='4' valign='top'><textarea name='SRC_SUBNETS' cols='32' rows='6' wrap='off'>
END
;

if (!$proxysettings{'SRC_SUBNETS'})
{
    print "$netsettings{'GREEN_1_NETADDRESS'}\/$netsettings{'GREEN_1_NETMASK'}\n";
    if ($netsettings{'BLUE_COUNT'} >= 1)
    {
        print "$netsettings{'BLUE_1_NETADDRESS'}\/$netsettings{'BLUE_1_NETMASK'}\n";
    }
}
else {
    print $proxysettings{'SRC_SUBNETS'};
}

print <<END
</textarea></td>
END
;

$line = $Lang::tr{'no internal proxy'};
print "<td class='base'>$line:</td>\n";
print <<END
    <td><input type='checkbox' name='NO_PROXY_LOCAL' $checked{'NO_PROXY_LOCAL'}{'on'} /></td>
</tr>
END
;

$line = $Lang::tr{'no internal proxy on green'};
$line =~ s/Green/<span class='ipcop_iface_green' style='font-weight: bold;'>$Lang::tr{'green'}<\/span>/i;
print "<tr><td class='base'>$line:</td>\n";
print <<END
    <td><input type='checkbox' name='NO_PROXY_LOCAL_GREEN' $checked{'NO_PROXY_LOCAL_GREEN'}{'on'} /></td>
</tr>
END
;
if ($netsettings{'BLUE_COUNT'} >= 1) {
    $line = $Lang::tr{'no internal proxy on blue'};
    $line =~ s/Blue/<span class='ipcop_iface_blue' style='font-weight: bold;'>$Lang::tr{'blue'}<\/span>/i;
    print "<tr>\n";
    print "<td class='base'>$line:</td>\n";
    print <<END
    <td><input type='checkbox' name='NO_PROXY_LOCAL_BLUE' $checked{'NO_PROXY_LOCAL_BLUE'}{'on'} /></td>
</tr>
END
;
}
print <<END
<tr>
    <td colspan='2'>&nbsp;</td>
</tr>
</table>
<table width='100%'>
<tr>
    <td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
    <td colspan='2' class='base'>$Lang::tr{'unrestricted ip clients'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td colspan='2' class='base'>$Lang::tr{'unrestricted mac clients'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
    <td colspan='2'><textarea name='SRC_UNRESTRICTED_IP' cols='32' rows='6' wrap='off'>
END
;

    print $proxysettings{'SRC_UNRESTRICTED_IP'};

print <<END
</textarea></td>
    <td colspan='2'><textarea name='SRC_UNRESTRICTED_MAC' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'SRC_UNRESTRICTED_MAC'};

print <<END
</textarea></td>
</tr>
</table>
<table width='100%'>
<tr>
    <td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
    <td colspan='2' class='base'>$Lang::tr{'banned ip clients'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td colspan='2' class='base'>$Lang::tr{'banned mac clients'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
    <td colspan='2'><textarea name='SRC_BANNED_IP' cols='32' rows='6' wrap='off'>
END
;

    print $proxysettings{'SRC_BANNED_IP'};

print <<END
</textarea></td>
    <td colspan='2'><textarea name='SRC_BANNED_MAC' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'SRC_BANNED_MAC'};

print <<END
</textarea></td>
</tr>
</table>

<hr size='1'/>

END
;
# -------------------------------------------------------------------
#  CRE GUI - optional
# -------------------------------------------------------------------

if (-e $cre_enabled) { print <<END
<table width='100%'>

<tr>
    <td colspan='4'><b>$Lang::tr{'classroom extensions'}</b></td>
</tr>
<tr>
    <td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'enabled'}:</td>
    <td><input type='checkbox' name='CLASSROOM_EXT' $checked{'CLASSROOM_EXT'}{'on'} /></td>
    <td class='base'>$Lang::tr{'supervisor password'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='password' name='SUPERVISOR_PASSWORD' value='$proxysettings{'SUPERVISOR_PASSWORD'}' size='12' /></td>
</tr>
<tr>
    <td colspan='2' class='base'>$Lang::tr{'cre group definitions'}:</td>
    <td colspan='2' class='base'>$Lang::tr{'cre supervisors'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
    <td colspan='2'><textarea name='CRE_GROUPS' cols='32' rows='6' wrap='off'>
END
;

    print $proxysettings{'CRE_GROUPS'};

print <<END
</textarea></td>
    <td colspan='2'><textarea name='CRE_SVHOSTS' cols='32' rows='6' wrap='off'>
END
;
    print $proxysettings{'CRE_SVHOSTS'};

print <<END
</textarea></td>
</tr>

</table>

<hr size='1'/>
END
;
} else {
    print <<END
    <input type='hidden' name='SUPERVISOR_PASSWORD' value='$proxysettings{'SUPERVISOR_PASSWORD'}' />
    <input type='hidden' name='CRE_GROUPS'          value='$proxysettings{'CRE_GROUPS'}' />
    <input type='hidden' name='CRE_SVHOSTS'         value='$proxysettings{'CRE_SVHOSTS'}' />
END
;
}

# -------------------------------------------------------------------

print <<END

<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'time restrictions'}</b></td>
</tr>
<tr>
    <td width='2%'>$Lang::tr{'access'}</td>
    <td width='1%'>&nbsp;</td>
    <td width='2%' align='center'>$Lang::tr{'monday short'}</td>
    <td width='2%' align='center'>$Lang::tr{'tuesday short'}</td>
    <td width='2%' align='center'>$Lang::tr{'wednesday short'}</td>
    <td width='2%' align='center'>$Lang::tr{'thursday short'}</td>
    <td width='2%' align='center'>$Lang::tr{'friday short'}</td>
    <td width='2%' align='center'>$Lang::tr{'saturday short'}</td>
    <td width='2%' align='center'>$Lang::tr{'sunday short'}</td>
    <td width='1%'>&nbsp;&nbsp;</td>
    <td width='7%' colspan=3>$Lang::tr{'from'}</td>
    <td width='1%'>&nbsp;</td>
    <td width='7%' colspan=3>$Lang::tr{'to'}</td>
    <td>&nbsp;</td>
</tr>
<tr>
    <td class='base'>
    <select name='TIME_ACCESS_MODE'>
    <option value='allow' $selected{'TIME_ACCESS_MODE'}{'allow'}>$Lang::tr{'mode allow'}</option>
    <option value='deny'  $selected{'TIME_ACCESS_MODE'}{'deny'}>$Lang::tr{'mode deny'}</option>
    </select>
    </td>
    <td>&nbsp;</td>
    <td class='base'><input type='checkbox' name='TIME_MON' $checked{'TIME_MON'}{'on'} /></td>
    <td class='base'><input type='checkbox' name='TIME_TUE' $checked{'TIME_TUE'}{'on'} /></td>
    <td class='base'><input type='checkbox' name='TIME_WED' $checked{'TIME_WED'}{'on'} /></td>
    <td class='base'><input type='checkbox' name='TIME_THU' $checked{'TIME_THU'}{'on'} /></td>
    <td class='base'><input type='checkbox' name='TIME_FRI' $checked{'TIME_FRI'}{'on'} /></td>
    <td class='base'><input type='checkbox' name='TIME_SAT' $checked{'TIME_SAT'}{'on'} /></td>
    <td class='base'><input type='checkbox' name='TIME_SUN' $checked{'TIME_SUN'}{'on'} /></td>
    <td>&nbsp;</td>
    <td class='base'>
    <select name='TIME_FROM_HOUR'>
END
;
for ($i=0;$i<=24;$i++) {
    $_ = sprintf("%02s",$i);
    print "<option $selected{'TIME_FROM_HOUR'}{$_}>$_</option>\n";
}
print <<END
    </select>
    </td>
    <td>:</td>
    <td class='base'>
    <select name='TIME_FROM_MINUTE'>
END
;
for ($i=0;$i<=45;$i+=15) {
    $_ = sprintf("%02s",$i);
    print "<option $selected{'TIME_FROM_MINUTE'}{$_}>$_</option>\n";
}
print <<END
    </select>
    </td>
    <td> - </td>
    <td class='base'>
    <select name='TIME_TO_HOUR'>
END
;
for ($i=0;$i<=24;$i++) {
    $_ = sprintf("%02s",$i);
    print "<option $selected{'TIME_TO_HOUR'}{$_}>$_</option>\n";
}
print <<END
    </select>
    </td>
    <td>:</td>
    <td class='base'>
    <select name='TIME_TO_MINUTE'>
END
;
for ($i=0;$i<=45;$i+=15) {
    $_ = sprintf("%02s",$i);
    print "<option $selected{'TIME_TO_MINUTE'}{$_}>$_</option>\n";
}
print <<END
    </select>
    </td>
</tr>
</table>
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'transfer limits'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'max download size'}:</td>
    <td width='20%'><input type='text' name='MAX_INCOMING_SIZE' value='$proxysettings{'MAX_INCOMING_SIZE'}' size='5' /></td>
    <td width='25%' class='base'>$Lang::tr{'max upload size'}:</td>
    <td width='30%'><input type='text' name='MAX_OUTGOING_SIZE' value='$proxysettings{'MAX_OUTGOING_SIZE'}' size='5' /></td>
</tr>
</table>
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'download throttling'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'throttling total on'} <span class='ipcop_iface_green' style='font-weight: bold;'>$Lang::tr{'green'}</span>:</td>
    <td width='20%' class='base'>
    <select name='THROTTLING_GREEN_TOTAL'>
END
;

foreach (@throttle_limits) {
    print "\t<option value='$_' $selected{'THROTTLING_GREEN_TOTAL'}{$_}>$_ kBit/s</option>\n";
}

print <<END
    <option value='0' $selected{'THROTTLING_GREEN_TOTAL'}{'unlimited'}>$Lang::tr{'throttling unlimited'}</option>
    </select>
    </td>
    <td width='25%' class='base'>$Lang::tr{'throttling per host on'} <span class='ipcop_iface_green' style='font-weight: bold;'>$Lang::tr{'green'}</span>:</td>
    <td width='30%' class='base'>
    <select name='THROTTLING_GREEN_HOST'>
END
;

foreach (@throttle_limits) {
    print "\t<option value='$_' $selected{'THROTTLING_GREEN_HOST'}{$_}>$_ kBit/s</option>\n";
}

print <<END
    <option value='0' $selected{'THROTTLING_GREEN_HOST'}{'unlimited'}>$Lang::tr{'throttling unlimited'}</option>
    </select>
    </td>
</tr>
END
;

if ($netsettings{'BLUE_COUNT'} >= 1) {
    print <<END
<tr>
    <td class='base'>$Lang::tr{'throttling total on'} <span class='ipcop_iface_blue' style='font-weight: bold;'>$Lang::tr{'blue'}</span>:</td>
    <td class='base'>
    <select name='THROTTLING_BLUE_TOTAL'>
END
;

foreach (@throttle_limits) {
    print "\t<option value='$_' $selected{'THROTTLING_BLUE_TOTAL'}{$_}>$_ kBit/s</option>\n";
}

print <<END
    <option value='0' $selected{'THROTTLING_BLUE_TOTAL'}{'unlimited'}>$Lang::tr{'throttling unlimited'}</option>\n";
    </select>
    </td>
    <td class='base'>$Lang::tr{'throttling per host on'} <span class='ipcop_iface_blue' style='font-weight: bold;'>$Lang::tr{'blue'}</span>:</td>
    <td class='base'>
    <select name='THROTTLING_BLUE_HOST'>
END
;

foreach (@throttle_limits) {
    print "\t<option value='$_' $selected{'THROTTLING_BLUE_HOST'}{$_}>$_ kBit/s</option>\n";
}

print <<END
    <option value='0' $selected{'THROTTLING_BLUE_HOST'}{'unlimited'}>$Lang::tr{'throttling unlimited'}</option>\n";
    </select>
    </td>
</tr>
END
;
}

print <<END
</table>
<table width='100%'>
<tr>
    <td colspan='4'><i>$Lang::tr{'content based throttling'}:</i></td>
</tr>
<tr>
    <td width='15%' class='base'>$Lang::tr{'throttle binary'}:</td>
    <td width='10%'><input type='checkbox' name='THROTTLE_BINARY' $checked{'THROTTLE_BINARY'}{'on'} /></td>
    <td width='15%' class='base'>$Lang::tr{'throttle dskimg'}:</td>
    <td width='10%'><input type='checkbox' name='THROTTLE_DSKIMG' $checked{'THROTTLE_DSKIMG'}{'on'} /></td>
    <td width='15%' class='base'>$Lang::tr{'throttle mmedia'}:</td>
    <td width='10%'><input type='checkbox' name='THROTTLE_MMEDIA' $checked{'THROTTLE_MMEDIA'}{'on'} /></td>
    <td width='15%'>&nbsp;</td>
    <td width='10%'>&nbsp;</td>
</tr>
</table>
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'MIME filter'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'enabled'}:</td>
    <td width='20%'><input type='checkbox' name='ENABLE_MIME_FILTER' $checked{'ENABLE_MIME_FILTER'}{'on'} /></td>
</tr>
<tr>
    <td  colspan='2' class='base'>$Lang::tr{'MIME block types'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td  colspan='2' class='base'>$Lang::tr{'MIME filter exceptions'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
    <td colspan='2'><textarea name='MIME_TYPES' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'MIME_TYPES'};

print <<END
</textarea></td>
    <td colspan='2'><textarea name='MIME_EXCEPTIONS' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'MIME_EXCEPTIONS'};

print <<END
</textarea></td>
</tr>
</table>
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'web browser'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'UA enable filter'}:</td>
    <td width='20%'><input type='checkbox' name='ENABLE_BROWSER_CHECK' $checked{'ENABLE_BROWSER_CHECK'}{'on'} /></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
<tr>
    <td colspan='4'><i>
END
;
if (@useragentlist) { print "$Lang::tr{'allowed web browsers'}:"; } else { print "$Lang::tr{'no clients defined'}"; }
print <<END
</i></td>
</tr>
</table>
<table width='100%'>
END
;

for ($n=0; $n<=@useragentlist; $n = $n + $i) {
    for ($i=0; $i<=3; $i++) {
        if ($i eq 0) { print "<tr>\n"; }
        if (($n+$i) < @useragentlist) {
            @useragent = split(/,/,@useragentlist[$n+$i]);
            print "<td width='15%'>@useragent[1]:<\/td>\n";
            print "<td width='10%'><input type='checkbox' name='UA_@useragent[0]' $checked{'UA_'.@useragent[0]}{'on'} /></td>\n";
        }
        if ($i eq 3) { print "<\/tr>\n"; }
    }
}

print <<END
</table>
<hr size='1'/>
<table width='100%'>
<tr>
    <td><b>$Lang::tr{'privacy'}</b></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'fake useragent'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
    <td><input type='text' name='FAKE_USERAGENT' value='$proxysettings{'FAKE_USERAGENT'}' size='56' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'fake referer'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
    <td><input type='text' name='FAKE_REFERER' value='$proxysettings{'FAKE_REFERER'}' size='56' /></td>
</tr>
</table>
<hr size='1'/>
END
;

if ($urlfilter_addon) {
    print <<END
<table width='100%'>
<tr>
    <td class='base' colspan='4'><b>$Lang::tr{'url filter'}</b>&nbsp; [ SquidGuard: $urlfilterversion ]</td>
</tr>
<tr>
    <td class='base' width='25%'>$Lang::tr{'enabled'}:</td>
    <td class='base' width='20%'><input type='checkbox' name='ENABLE_FILTER' $checked{'ENABLE_FILTER'}{'on'} /></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
</table>
<hr size='1'/>
END
; }

if ($updaccel_addon) {
    print <<END
<table width='100%'>
<tr>
    <td class='base' colspan='4'><b>$Lang::tr{'update accelerator'}</b>&nbsp; [ $updaccelversion ]</td>
</tr>
<tr>
    <td class='base' width='25%'>$Lang::tr{'enabled'}:</td>
    <td class='base' width='20%'><input type='checkbox' name='ENABLE_UPDXLRATOR' $checked{'ENABLE_UPDXLRATOR'}{'on'} /></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
</table>
<hr size='1'/>
END
; }

print <<END
<table width='100%'>
<tr>
    <td colspan='5'><b>$Lang::tr{'AUTH method'}</b></td>
</tr>
<tr>
    <td width='16%' class='base'><input type='radio' name='AUTH_METHOD' value='none' $checked{'AUTH_METHOD'}{'none'} />$Lang::tr{'AUTH method none'}</td>
    <td width='16%' class='base'><input type='radio' name='AUTH_METHOD' value='ncsa' $checked{'AUTH_METHOD'}{'ncsa'} />$Lang::tr{'AUTH method ncsa'}</td>
    <td width='16%' class='base'><input type='radio' name='AUTH_METHOD' value='ident' $checked{'AUTH_METHOD'}{'ident'} />$Lang::tr{'AUTH method ident'}</td>
    <td width='16%' class='base'><input type='radio' name='AUTH_METHOD' value='ldap' $checked{'AUTH_METHOD'}{'ldap'} />$Lang::tr{'AUTH method ldap'}</td>
    <td width='16%' class='base'><input type='radio' name='AUTH_METHOD' value='ntlm' $checked{'AUTH_METHOD'}{'ntlm'} />$Lang::tr{'AUTH method ntlm'}</td>
    <td width='16%' class='base'><input type='radio' name='AUTH_METHOD' value='radius' $checked{'AUTH_METHOD'}{'radius'} />$Lang::tr{'AUTH method radius'}</td>
</tr>
</table>
END
;

if (!($proxysettings{'AUTH_METHOD'} eq 'none')) { if (!($proxysettings{'AUTH_METHOD'} eq 'ident')) { print <<END
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'AUTH global settings'}</b></td>
</tr>
<tr>
    <td width='25%'></td> <td width='20%'> </td><td width='25%'> </td><td width='30%'></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'AUTH number of auth processes'}:</td>
    <td><input type='text' name='AUTH_CHILDREN' value='$proxysettings{'AUTH_CHILDREN'}' size='5' /></td>
    <td colspan='2' rowspan= '6' valign='top' class='base'>
        <table cellpadding='0' cellspacing='0'>
            <tr>
            <td class='base'>$Lang::tr{'AUTH realm'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
            </tr>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
            <td><input type='text' name='AUTH_REALM' value='$proxysettings{'AUTH_REALM'}' size='40' /></td>
            </tr>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
            <td>$Lang::tr{'AUTH no auth'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
            </tr>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
                <!-- intentionally left empty -->
            </tr>
            <tr>
            <td><textarea name='DST_NOAUTH' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'DST_NOAUTH'};

print <<END
</textarea></td>
        </tr>
        </table>
    </td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'AUTH auth cache TTL'}:</td>
    <td><input type='text' name='AUTH_CACHE_TTL' value='$proxysettings{'AUTH_CACHE_TTL'}' size='5' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'AUTH limit of IP addresses'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='AUTH_MAX_USERIP' value='$proxysettings{'AUTH_MAX_USERIP'}' size='5' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'AUTH user IP cache TTL'}:</td>
    <td><input type='text' name='AUTH_IPCACHE_TTL' value='$proxysettings{'AUTH_IPCACHE_TTL'}' size='5' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'AUTH always required'}:</td>
    <td><input type='checkbox' name='AUTH_ALWAYS_REQUIRED' $checked{'AUTH_ALWAYS_REQUIRED'}{'on'} /></td>
</tr>
<tr>
    <td colspan='2'>&nbsp;</td>
</tr>
</table>
END
;
}

# ===================================================================
#  NCSA auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'ncsa') {
print <<END
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'NCSA auth'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'NCSA min password length'}:</td>
    <td width='20%'><input type='text' name='NCSA_MIN_PASS_LEN' value='$proxysettings{'NCSA_MIN_PASS_LEN'}' size='5' /></td>
    <td width='25%' class='base'>$Lang::tr{'NCSA redirector bypass'} \'$Lang::tr{'NCSA grp extended'}\':</td>
    <td width='20%'><input type='checkbox' name='NCSA_BYPASS_REDIR' $checked{'NCSA_BYPASS_REDIR'}{'on'} /></td>
</tr>
<tr>
    <td colspan='2'><br>&nbsp;<input type='submit' name='ACTION' value='$Lang::tr{'NCSA user management'}'></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
</table>
END
; }

# ===================================================================
#  IDENTD auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'ident') {
print <<END
<hr size ='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'IDENT identd settings'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'IDENT required'}:</td>
    <td width='20%'><input type='checkbox' name='IDENT_REQUIRED' $checked{'IDENT_REQUIRED'}{'on'} /></td>
    <td width='25%' class='base'>$Lang::tr{'AUTH always required'}:</td>
    <td width='30%'><input type='checkbox' name='AUTH_ALWAYS_REQUIRED' $checked{'AUTH_ALWAYS_REQUIRED'}{'on'} /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'IDENT timeout'}:</td>
    <td><input type='text' name='IDENT_TIMEOUT' value='$proxysettings{'IDENT_TIMEOUT'}' size='5' /></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
<tr>
    <td colspan='2' class='base'>$Lang::tr{'IDENT aware hosts'}:</td>
    <td colspan='2' class='base'>$Lang::tr{'AUTH no auth'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
</tr>
<tr>
    <td colspan='2'><textarea name='IDENT_HOSTS' cols='32' rows='6' wrap='off'>
END
;
if (!$proxysettings{'IDENT_HOSTS'}) {
    print "$netsettings{'GREEN_1_NETADDRESS'}\/$netsettings{'GREEN_1_NETMASK'}\n";
    if ($netsettings{'BLUE_COUNT'} >= 1) {
        print "$netsettings{'BLUE_1_NETADDRESS'}\/$netsettings{'BLUE_1_NETMASK'}\n";
    }
} else {
    print $proxysettings{'IDENT_HOSTS'};
}

print <<END
</textarea></td>
            <td colspan='2'><textarea name='DST_NOAUTH' cols='32' rows='6' wrap='off'>
END
;

print $proxysettings{'DST_NOAUTH'};

print <<END
</textarea></td>
</tr>
</table>
<hr size ='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'IDENT user based access restrictions'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'enabled'}:</td>
    <td width='20%'><input type='checkbox' name='IDENT_ENABLE_ACL' $checked{'IDENT_ENABLE_ACL'}{'on'} /></td>
    <td width='25%'>&nbsp;</td>
    <td width='30%'>&nbsp;</td>
</tr>
<tr>
    <td colspan='2'><input type='radio' name='IDENT_USER_ACL' value='positive' $checked{'IDENT_USER_ACL'}{'positive'} />
    $Lang::tr{'IDENT use positive access list'}:</td>
    <td colspan='2'><input type='radio' name='IDENT_USER_ACL' value='negative' $checked{'IDENT_USER_ACL'}{'negative'} />
    $Lang::tr{'IDENT use negative access list'}:</td>
</tr>
<tr>
    <td colspan='2'>$Lang::tr{'IDENT authorized users'}</td>
    <td colspan='2'>$Lang::tr{'IDENT unauthorized users'}</td>
</tr>
<tr>
    <td colspan='2'><textarea name='IDENT_ALLOW_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') { print $proxysettings{'IDENT_ALLOW_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') { print <<END
</textarea></td>
    <td colspan='2'><textarea name='IDENT_DENY_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') { print $proxysettings{'IDENT_DENY_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') { print <<END
</textarea></td>
</tr>
</table>
END
; }

# ===================================================================
#  NTLM auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'ntlm') {
print <<END
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='6'><b>$Lang::tr{'NTLM domain settings'}</b></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'NTLM domain'}:</td>
    <td><input type='text' name='NTLM_DOMAIN' value='$proxysettings{'NTLM_DOMAIN'}' size='15' /></td>
    <td class='base'>$Lang::tr{'NTLM PDC hostname'}:</td>
    <td><input type='text' name='NTLM_PDC' value='$proxysettings{'NTLM_PDC'}' size='14' /></td>
    <td class='base'>$Lang::tr{'NTLM BDC hostname'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='NTLM_BDC' value='$proxysettings{'NTLM_BDC'}' size='14' /></td>
</tr>
</table>
<hr size ='1'/>
<table width='100%'>
<tr>
    <td colspan='3'><b>$Lang::tr{'NTLM auth mode'}</b></td>
</tr>
<tr>
    <td width='25%' class='base' width='25%'>$Lang::tr{'NTLM use integrated auth'}:</td>
    <td width='20%'><input type='checkbox' name='NTLM_ENABLE_INT_AUTH' $checked{'NTLM_ENABLE_INT_AUTH'}{'on'} /></td>
    <td>&nbsp;</td>
</tr>
</table>
<hr size ='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'NTLM user based access restrictions'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'enabled'}:</td>
    <td width='20%'><input type='checkbox' name='NTLM_ENABLE_ACL' $checked{'NTLM_ENABLE_ACL'}{'on'} /></td>
    <td width='25%'>&nbsp;</td>
    <td width='30%'>&nbsp;</td>
</tr>
<tr>
    <td colspan='2'><input type='radio' name='NTLM_USER_ACL' value='positive' $checked{'NTLM_USER_ACL'}{'positive'} />
    $Lang::tr{'NTLM use positive access list'}:</td>
    <td colspan='2'><input type='radio' name='NTLM_USER_ACL' value='negative' $checked{'NTLM_USER_ACL'}{'negative'} />
    $Lang::tr{'NTLM use negative access list'}:</td>
</tr>
<tr>
    <td colspan='2'>$Lang::tr{'NTLM authorized users'}</td>
    <td colspan='2'>$Lang::tr{'NTLM unauthorized users'}</td>
</tr>
<tr>
    <td colspan='2'><textarea name='NTLM_ALLOW_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'ntlm') { print $proxysettings{'NTLM_ALLOW_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'ntlm') { print <<END
</textarea></td>
    <td colspan='2'><textarea name='NTLM_DENY_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'ntlm') { print $proxysettings{'NTLM_DENY_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'ntlm') { print <<END
</textarea></td>
</tr>
</table>
END
; }

# ===================================================================
#  LDAP auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'ldap') {
print <<END
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'LDAP common settings'}</b></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'LDAP basedn'}:</td>
    <td><input type='text' name='LDAP_BASEDN' value='$proxysettings{'LDAP_BASEDN'}' size='37' /></td>
    <td class='base'>$Lang::tr{'LDAP type'}:</td>
    <td class='base'><select name='LDAP_TYPE'>
        <option value='ADS' $selected{'LDAP_TYPE'}{'ADS'}>$Lang::tr{'LDAP ADS'}</option>
        <option value='NDS' $selected{'LDAP_TYPE'}{'NDS'}>$Lang::tr{'LDAP NDS'}</option>
        <option value='V2' $selected{'LDAP_TYPE'}{'V2'}>$Lang::tr{'LDAP V2'}</option>
        <option value='V3' $selected{'LDAP_TYPE'}{'V3'}>$Lang::tr{'LDAP V3'}</option>
    </select></td>
</tr>
<tr>
    <td width='20%' class='base'>$Lang::tr{'LDAP server'}:</td>
    <td width='40%'><input type='text' name='LDAP_SERVER' value='$proxysettings{'LDAP_SERVER'}' size='14' /></td>
    <td width='20%' class='base'>$Lang::tr{'LDAP port'}:</td>
    <td><input type='text' name='LDAP_PORT' value='$proxysettings{'LDAP_PORT'}' size='3' /></td>
</tr>
</table>
<hr size ='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'LDAP binddn settings'}</b></td>
</tr>
<tr>
    <td width='20%' class='base'>$Lang::tr{'LDAP binddn username'}:</td>
    <td width='40%'><input type='text' name='LDAP_BINDDN_USER' value='$proxysettings{'LDAP_BINDDN_USER'}' size='37' /></td>
    <td width='20%' class='base'>$Lang::tr{'LDAP binddn password'}:</td>
    <td><input type='password' name='LDAP_BINDDN_PASS' value='$proxysettings{'LDAP_BINDDN_PASS'}' size='14' /></td>
</tr>
</table>
<hr size ='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'LDAP group access control'}</b></td>
</tr>
<tr>
    <td width='20%' class='base'>$Lang::tr{'LDAP group required'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td width='40%'><input type='text' name='LDAP_GROUP' value='$proxysettings{'LDAP_GROUP'}' size='37' /></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
</tr>
</table>
END
; }

# ===================================================================
#  RADIUS auth settings
# ===================================================================

if ($proxysettings{'AUTH_METHOD'} eq 'radius') {
print <<END
<hr size='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'RADIUS radius settings'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'RADIUS server'}:</td>
    <td width='20%'><input type='text' name='RADIUS_SERVER' value='$proxysettings{'RADIUS_SERVER'}' size='14' /></td>
    <td width='25%' class='base'>$Lang::tr{'RADIUS port'}:</td>
    <td width='30%'><input type='text' name='RADIUS_PORT' value='$proxysettings{'RADIUS_PORT'}' size='3' /></td>
</tr>
<tr>
    <td class='base'>$Lang::tr{'RADIUS identifier'}:&nbsp;<img src='/blob.gif' alt='*' /></td>
    <td><input type='text' name='RADIUS_IDENTIFIER' value='$proxysettings{'RADIUS_IDENTIFIER'}' size='14' /></td>
    <td class='base'>$Lang::tr{'RADIUS secret'}:</td>
    <td><input type='password' name='RADIUS_SECRET' value='$proxysettings{'RADIUS_SECRET'}' size='14' /></td>
</tr>
</table>
<hr size ='1'/>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'RADIUS user based access restrictions'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'enabled'}:</td>
    <td width='20%'><input type='checkbox' name='RADIUS_ENABLE_ACL' $checked{'RADIUS_ENABLE_ACL'}{'on'} /></td>
    <td width='25%'>&nbsp;</td>
    <td width='30%'>&nbsp;</td>
</tr>
<tr>
    <td colspan='2'><input type='radio' name='RADIUS_USER_ACL' value='positive' $checked{'RADIUS_USER_ACL'}{'positive'} />
    $Lang::tr{'RADIUS use positive access list'}:</td>
    <td colspan='2'><input type='radio' name='RADIUS_USER_ACL' value='negative' $checked{'RADIUS_USER_ACL'}{'negative'} />
    $Lang::tr{'RADIUS use negative access list'}:</td>
</tr>
<tr>
    <td colspan='2'>$Lang::tr{'RADIUS authorized users'}</td>
    <td colspan='2'>$Lang::tr{'RADIUS unauthorized users'}</td>
</tr>
<tr>
    <td colspan='2'><textarea name='RADIUS_ALLOW_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'radius') { print $proxysettings{'RADIUS_ALLOW_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'radius') { print <<END
</textarea></td>
    <td colspan='2'><textarea name='RADIUS_DENY_USERS' cols='32' rows='6' wrap='off'>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'radius') { print $proxysettings{'RADIUS_DENY_USERS'}; }

if ($proxysettings{'AUTH_METHOD'} eq 'radius') { print <<END
</textarea></td>
</tr>
</table>
END
; }

# ===================================================================

}

print "<table>\n<tr>\n";

if ($proxysettings{'AUTH_METHOD'} eq 'none') {
print <<END
<td><input type='hidden' name='AUTH_CHILDREN'        value='$proxysettings{'AUTH_CHILDREN'}'/></td>
<td><input type='hidden' name='AUTH_CACHE_TTL'       value='$proxysettings{'AUTH_CACHE_TTL'}' size='5' /></td>
<td><input type='hidden' name='AUTH_MAX_USERIP'      value='$proxysettings{'AUTH_MAX_USERIP'}' size='5' /></td>
<td><input type='hidden' name='AUTH_IPCACHE_TTL'     value='$proxysettings{'AUTH_IPCACHE_TTL'}' size='5' /></td>
<td><input type='hidden' name='AUTH_ALWAYS_REQUIRED' value='$proxysettings{'AUTH_ALWAYS_REQUIRED'}'/></td>
<td><input type='hidden' name='AUTH_REALM'           value='$proxysettings{'AUTH_REALM'}'/></td>
<td><input type='hidden' name='DST_NOAUTH'           value='$proxysettings{'DST_NOAUTH'}'/></td>
END
; }

if ($proxysettings{'AUTH_METHOD'} eq 'ident') {
print <<END
<td><input type='hidden' name='AUTH_CHILDREN'        value='$proxysettings{'AUTH_CHILDREN'}'/></td>
<td><input type='hidden' name='AUTH_CACHE_TTL'       value='$proxysettings{'AUTH_CACHE_TTL'}' size='5' /></td>
<td><input type='hidden' name='AUTH_MAX_USERIP'      value='$proxysettings{'AUTH_MAX_USERIP'}' size='5' /></td>
<td><input type='hidden' name='AUTH_IPCACHE_TTL'     value='$proxysettings{'AUTH_IPCACHE_TTL'}' size='5' /></td>
<td><input type='hidden' name='AUTH_REALM'           value='$proxysettings{'AUTH_REALM'}'/></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'ncsa')) {
print <<END
<td><input type='hidden' name='NCSA_MIN_PASS_LEN' value='$proxysettings{'NCSA_MIN_PASS_LEN'}'/></td>
<td><input type='hidden' name='NCSA_BYPASS_REDIR' value='$proxysettings{'NCSA_BYPASS_REDIR'}'/></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'ident')) {
print <<END
<td><input type='hidden' name='IDENT_REQUIRED'    value='$proxysettings{'IDENT_REQUIRED'}'/></td>
<td><input type='hidden' name='IDENT_TIMEOUT'     value='$proxysettings{'IDENT_TIMEOUT'}'/></td>
<td><input type='hidden' name='IDENT_HOSTS'       value='$proxysettings{'IDENT_HOSTS'}'/></td>
<td><input type='hidden' name='IDENT_ENABLE_ACL'  value='$proxysettings{'IDENT_ENABLE_ACL'}'/></td>
<td><input type='hidden' name='IDENT_USER_ACL'    value='$proxysettings{'IDENT_USER_ACL'}'/></td>
<td><input type='hidden' name='IDENT_ALLOW_USERS' value='$proxysettings{'IDENT_ALLOW_USERS'}'/></td>
<td><input type='hidden' name='IDENT_DENY_USERS'  value='$proxysettings{'IDENT_DENY_USERS'}'/></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'ldap')) {
print <<END
<td><input type='hidden' name='LDAP_BASEDN'      value='$proxysettings{'LDAP_BASEDN'}'/></td>
<td><input type='hidden' name='LDAP_TYPE'        value='$proxysettings{'LDAP_TYPE'}'/></td>
<td><input type='hidden' name='LDAP_SERVER'      value='$proxysettings{'LDAP_SERVER'}'/></td>
<td><input type='hidden' name='LDAP_PORT'        value='$proxysettings{'LDAP_PORT'}'/></td>
<td><input type='hidden' name='LDAP_BINDDN_USER' value='$proxysettings{'LDAP_BINDDN_USER'}'/></td>
<td><input type='hidden' name='LDAP_BINDDN_PASS' value='$proxysettings{'LDAP_BINDDN_PASS'}'/></td>
<td><input type='hidden' name='LDAP_GROUP'       value='$proxysettings{'LDAP_GROUP'}'/></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'ntlm')) {
print <<END
<td><input type='hidden' name='NTLM_DOMAIN'          value='$proxysettings{'NTLM_DOMAIN'}'/></td>
<td><input type='hidden' name='NTLM_PDC'             value='$proxysettings{'NTLM_PDC'}'/></td>
<td><input type='hidden' name='NTLM_BDC'             value='$proxysettings{'NTLM_BDC'}'/></td>
<td><input type='hidden' name='NTLM_ENABLE_INT_AUTH' value='$proxysettings{'NTLM_ENABLE_INT_AUTH'}'/></td>
<td><input type='hidden' name='NTLM_ENABLE_ACL'      value='$proxysettings{'NTLM_ENABLE_ACL'}'/></td>
<td><input type='hidden' name='NTLM_USER_ACL'        value='$proxysettings{'NTLM_USER_ACL'}'/></td>
<td><input type='hidden' name='NTLM_ALLOW_USERS'     value='$proxysettings{'NTLM_ALLOW_USERS'}'/></td>
<td><input type='hidden' name='NTLM_DENY_USERS'      value='$proxysettings{'NTLM_DENY_USERS'}'/></td>
END
; }

if (!($proxysettings{'AUTH_METHOD'} eq 'radius')) {
print <<END
<td><input type='hidden' name='RADIUS_SERVER'      value='$proxysettings{'RADIUS_SERVER'}'/></td>
<td><input type='hidden' name='RADIUS_PORT'        value='$proxysettings{'RADIUS_PORT'}'/></td>
<td><input type='hidden' name='RADIUS_IDENTIFIER'  value='$proxysettings{'RADIUS_IDENTIFIER'}'/></td>
<td><input type='hidden' name='RADIUS_SECRET'      value='$proxysettings{'RADIUS_SECRET'}'/></td>
<td><input type='hidden' name='RADIUS_ENABLE_ACL'  value='$proxysettings{'RADIUS_ENABLE_ACL'}'/></td>
<td><input type='hidden' name='RADIUS_USER_ACL'    value='$proxysettings{'RADIUS_USER_ACL'}'/></td>
<td><input type='hidden' name='RADIUS_ALLOW_USERS' value='$proxysettings{'RADIUS_ALLOW_USERS'}'/></td>
<td><input type='hidden' name='RADIUS_DENY_USERS'  value='$proxysettings{'RADIUS_DENY_USERS'}'/></td>
END
; }

print "</tr></table>\n";

print <<END
<hr />
<table width='100%'>
<tr>
    <td class='comment1button'><img src='/blob.gif' align='top' alt='*' />&nbsp;
    <font class='base'>$Lang::tr{'this field may be blank'}</font>
    </td>
    <td class='button2buttons'><input type='submit' name='ACTION' value='$Lang::tr{'clear cache'}' /></td>
    <td class='button2buttons'><input type='submit' name='ACTION' value='$Lang::tr{'save'}' /></td>
    <td class='onlinehelp'>
        <a href='${General::adminmanualurl}/services-webproxy.html' target='_blank'>
        <img src='/images/web-support.png' alt='$Lang::tr{'online help en'}' title='$Lang::tr{'online help en'}' /></a>

    </td>
</tr>
</table>
END
;

&Header::closebox();

print "</form>\n";

} else {

# ===================================================================
#  NCSA user management
# ===================================================================

&Header::openbox('100%', 'left', "$Lang::tr{'NCSA auth'}");
print <<END
<form method='post' action='$ENV{'SCRIPT_NAME'}'>
<table width='100%'>
<tr>
    <td colspan='4'><b>$Lang::tr{'NCSA user management'}</b></td>
</tr>
<tr>
    <td width='25%' class='base'>$Lang::tr{'NCSA username'}:</td>
    <td width='25%'><input type='text' name='NCSA_USERNAME' value='$proxysettings{'NCSA_USERNAME'}' size='12'
END
;
    if ($proxysettings{'ACTION'} eq $Lang::tr{'edit'}) { print " readonly "; }
    print <<END
     /></td>
    <td width='25%' class='base'>$Lang::tr{'NCSA group'}:</td>
    <td class='base'>
        <select name='NCSA_GROUP'>
        <option value='standard' $selected{'NCSA_GROUP'}{'standard'}>$Lang::tr{'NCSA grp standard'}</option>
        <option value='extended' $selected{'NCSA_GROUP'}{'extended'}>$Lang::tr{'NCSA grp extended'}</option>
        <option value='disabled' $selected{'NCSA_GROUP'}{'disabled'}>$Lang::tr{'NCSA grp disabled'}</option>
        </select>
    </td>

</tr>
<tr>
    <td class='base'>$Lang::tr{'NCSA password'}:</td>
    <td><input type='password' name='NCSA_PASS' value='$proxysettings{'NCSA_PASS'}' size='14' /></td>
    <td class='base'>$Lang::tr{'NCSA password confirm'}:</td>
    <td><input type='password' name='NCSA_PASS_CONFIRM' value='$proxysettings{'NCSA_PASS_CONFIRM'}' size='14' /></td>
</tr>
</table>
<br>
<table>
<tr>
    <td>&nbsp;</td>
    <td><input type='submit' name='SUBMIT' value='$ncsa_buttontext' /></td>
    <td><input type='hidden' name='ACTION' value='$Lang::tr{'add'}' /></td>
    <td><input type='hidden' name='NCSA_MIN_PASS_LEN' value='$proxysettings{'NCSA_MIN_PASS_LEN'}'/></td>
END
;
    if ($proxysettings{'ACTION'} eq $Lang::tr{'edit'}) {
        print "<td><input type='reset' name='ACTION' value='$Lang::tr{'reset'}' /></td>\n";
    }

print <<END
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td><input type='button' name='return2main' value='$Lang::tr{'back to main page'}' onClick='self.location.href="$ENV{'SCRIPT_NAME'}"'/></td>
</tr>
</table>
</form>
<hr size='1'/>
<table width='100%'>
<tr>
    <td><b>$Lang::tr{'NCSA user accounts'}:</b></td>
</tr>
</table>
<table width='100%' align='center'>
END
;

if (-e $extgrp)
{
    open(FILE, $extgrp); @grouplist = <FILE>; close(FILE);
    foreach $user (@grouplist) { chomp($user); push(@userlist,$user.":extended"); }
}
if (-e $stdgrp)
{
    open(FILE, $stdgrp); @grouplist = <FILE>; close(FILE);
    foreach $user (@grouplist) { chomp($user); push(@userlist,$user.":standard"); }
}
if (-e $disgrp)
{
    open(FILE, $disgrp); @grouplist = <FILE>; close(FILE);
    foreach $user (@grouplist) { chomp($user); push(@userlist,$user.":disabled"); }
}

@userlist = sort(@userlist);

# If the password file contains entries, print entries and action icons

if (! -z "$userdb") {
    print <<END
    <tr>
        <td width='30%' class='boldbase' align='center'><b><i>$Lang::tr{'NCSA username'}</i></b></td>
        <td width='30%' class='boldbase' align='center'><b><i>$Lang::tr{'NCSA group membership'}</i></b></td>
        <td class='boldbase' colspan='2' align='center'>&nbsp;</td>
    </tr>
END
;
    $id = 0;
    foreach $line (@userlist)
    {
        $id++;
        chomp($line);
        @temp = split(/:/,$line);
        if($proxysettings{'ACTION'} eq $Lang::tr{'edit'} && $proxysettings{'ID'} eq $line) {
            print "<tr class='selectcolour'>";
        }
        else {
            print "<tr class='table".int($id % 2)."colour'>";
        }
        print <<END
        <td align='center'>$temp[0]</td>
        <td align='center'>
END
;
        if ($temp[1] eq 'standard') {
            print $Lang::tr{'NCSA grp standard'};
        } elsif ($temp[1] eq 'extended') {
            print $Lang::tr{'NCSA grp extended'};
        } elsif ($temp[1] eq 'disabled') {
            print $Lang::tr{'NCSA grp disabled'}; }
        print <<END
        </td>
        <td width='8%' align='center'>
        <form method='post' name='frma$id' action='$ENV{'SCRIPT_NAME'}'>
        <input type='image' name='$Lang::tr{'edit'}' src='/images/edit.gif' title='$Lang::tr{'edit'}' alt='$Lang::tr{'edit'}' />
        <input type='hidden' name='ID' value='$line' />
        <input type='hidden' name='ACTION' value='$Lang::tr{'edit'}' />
        </form>
        </td>

        <td width='8%' align='center'>
        <form method='post' name='frmb$id' action='$ENV{'SCRIPT_NAME'}'>
        <input type='image' name='$Lang::tr{'remove'}' src='/images/delete.gif' title='$Lang::tr{'remove'}' alt='$Lang::tr{'remove'}' />
        <input type='hidden' name='ID' value='$temp[0]' />
        <input type='hidden' name='ACTION' value='$Lang::tr{'remove'}' />
        </form>
        </td>
    </tr>
END
;
    }

print <<END
</table>
<br>
<table>
<tr>
    <td class='boldbase'>&nbsp; <b>$Lang::tr{'legend'}:</b></td>
    <td>&nbsp; &nbsp; <img src='/images/edit.gif' alt='$Lang::tr{'edit'}' /></td>
    <td class='base'>$Lang::tr{'edit'}</td>
    <td>&nbsp; &nbsp; <img src='/images/delete.gif' alt='$Lang::tr{'remove'}' /></td>
    <td class='base'>$Lang::tr{'remove'}</td>
</tr>
END
;
} else {
    print <<END
    <tr>
        <td><i>$Lang::tr{'NCSA no accounts'}</i></td>
    </tr>
END
;
}

print <<END
</table>
END
;

&Header::closebox();

}

# ===================================================================

&Header::closebigbox();

&Header::closepage();

# -------------------------------------------------------------------

sub sysversion
{
    my $vshort=shift;
    my $vextended='';

    foreach ($vshort) { $vextended .= join('.', map { sprintf("%02d", $_) } split(/\./, $_)); }

    if ($vshort =~ /\s\[\w+\]$/) { $vextended .= lc($&); } else { $vextended .= ' [stable]'; }

    return ($vextended);
}

# -------------------------------------------------------------------

sub read_acls
{
    if (-e "$acl_src_subnets") {
        open(FILE,"$acl_src_subnets");
        delete $proxysettings{'SRC_SUBNETS'};
        while (<FILE>) { $proxysettings{'SRC_SUBNETS'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_src_banned_ip") {
        open(FILE,"$acl_src_banned_ip");
        delete $proxysettings{'SRC_BANNED_IP'};
        while (<FILE>) { $proxysettings{'SRC_BANNED_IP'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_src_banned_mac") {
        open(FILE,"$acl_src_banned_mac");
        delete $proxysettings{'SRC_BANNED_MAC'};
        while (<FILE>) { $proxysettings{'SRC_BANNED_MAC'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_src_unrestricted_ip") {
        open(FILE,"$acl_src_unrestricted_ip");
        delete $proxysettings{'SRC_UNRESTRICTED_IP'};
        while (<FILE>) { $proxysettings{'SRC_UNRESTRICTED_IP'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_src_unrestricted_mac") {
        open(FILE,"$acl_src_unrestricted_mac");
        delete $proxysettings{'SRC_UNRESTRICTED_MAC'};
        while (<FILE>) { $proxysettings{'SRC_UNRESTRICTED_MAC'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_dst_nocache") {
        open(FILE,"$acl_dst_nocache");
        delete $proxysettings{'DST_NOCACHE'};
        while (<FILE>) { $proxysettings{'DST_NOCACHE'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_dst_noauth") {
        open(FILE,"$acl_dst_noauth");
        delete $proxysettings{'DST_NOAUTH'};
        while (<FILE>) { $proxysettings{'DST_NOAUTH'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_ports_safe") {
        open(FILE,"$acl_ports_safe");
        delete $proxysettings{'PORTS_SAFE'};
        while (<FILE>) { $proxysettings{'PORTS_SAFE'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_ports_ssl") {
        open(FILE,"$acl_ports_ssl");
        delete $proxysettings{'PORTS_SSL'};
        while (<FILE>) { $proxysettings{'PORTS_SSL'} .= $_ };
        close(FILE);
    }
    if (-e "$mimetypes") {
        open(FILE,"$mimetypes");
        delete $proxysettings{'MIME_TYPES'};
        while (<FILE>) { $proxysettings{'MIME_TYPES'} .= $_ };
        close(FILE);
    }
    if (-e "$acl_dst_mime_exceptions") {
        open(FILE,"$acl_dst_mime_exceptions");
        delete $proxysettings{'MIME_EXCEPTIONS'};
        while (<FILE>) { $proxysettings{'MIME_EXCEPTIONS'} .= $_ };
        close(FILE);
    }
    if (-e "$ntlmdir/msntauth.allowusers") {
        open(FILE,"$ntlmdir/msntauth.allowusers");
        delete $proxysettings{'NTLM_ALLOW_USERS'};
        while (<FILE>) { $proxysettings{'NTLM_ALLOW_USERS'} .= $_ };
        close(FILE);
    }
    if (-e "$ntlmdir/msntauth.denyusers") {
        open(FILE,"$ntlmdir/msntauth.denyusers");
        delete $proxysettings{'NTLM_DENY_USERS'};
        while (<FILE>) { $proxysettings{'NTLM_DENY_USERS'} .= $_ };
        close(FILE);
    }
    if (-e "$raddir/radauth.allowusers") {
        open(FILE,"$raddir/radauth.allowusers");
        delete $proxysettings{'RADIUS_ALLOW_USERS'};
        while (<FILE>) { $proxysettings{'RADIUS_ALLOW_USERS'} .= $_ };
        close(FILE);
    }
    if (-e "$raddir/radauth.denyusers") {
        open(FILE,"$raddir/radauth.denyusers");
        delete $proxysettings{'RADIUS_DENY_USERS'};
        while (<FILE>) { $proxysettings{'RADIUS_DENY_USERS'} .= $_ };
        close(FILE);
    }
    if (-e "$identdir/identauth.allowusers") {
        open(FILE,"$identdir/identauth.allowusers");
        delete $proxysettings{'IDENT_ALLOW_USERS'};
        while (<FILE>) { $proxysettings{'IDENT_ALLOW_USERS'} .= $_ };
        close(FILE);
    }
    if (-e "$identdir/identauth.denyusers") {
        open(FILE,"$identdir/identauth.denyusers");
        delete $proxysettings{'IDENT_DENY_USERS'};
        while (<FILE>) { $proxysettings{'IDENT_DENY_USERS'} .= $_ };
        close(FILE);
    }
    if (-e "$identhosts") {
        open(FILE,"$identhosts");
        delete $proxysettings{'IDENT_HOSTS'};
        while (<FILE>) { $proxysettings{'IDENT_HOSTS'} .= $_ };
        close(FILE);
    }
    if (-e "$cre_groups") {
        open(FILE,"$cre_groups");
        delete $proxysettings{'CRE_GROUPS'};
        while (<FILE>) { $proxysettings{'CRE_GROUPS'} .= $_ };
        close(FILE);
    }
    if (-e "$cre_svhosts") {
        open(FILE,"$cre_svhosts");
        delete $proxysettings{'CRE_SVHOSTS'};
        while (<FILE>) { $proxysettings{'CRE_SVHOSTS'} .= $_ };
        close(FILE);
    }
}

# -------------------------------------------------------------------

sub check_acls
{
    @temp = split(/\n/,$proxysettings{'PORTS_SAFE'});
    undef $proxysettings{'PORTS_SAFE'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g;
        if ($_)
        {
            $line = $_;
            if (/^[^#]+\s+#\sSquids\sport/) { s/(^[^#]+)(\s+#\sSquids\sport)/$proxysettings{'PROXY_PORT'}\2/; $line=$_; }
            s/#.*//g; s/\s+//g;
            if (/.*-.*-.*/) { $errormessage = $Lang::tr{'errmsg invalid destination port'}; }
            @templist = split(/-/);
            foreach (@templist) { unless (&General::validport($_)) { $errormessage = $Lang::tr{'errmsg invalid destination port'}; } }
            $proxysettings{'PORTS_SAFE'} .= $line."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'PORTS_SSL'});
    undef $proxysettings{'PORTS_SSL'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g;
        if ($_)
        {
            $line = $_;
            s/#.*//g; s/\s+//g;
            if (/.*-.*-.*/) { $errormessage = $Lang::tr{'errmsg invalid destination port'}; }
            @templist = split(/-/);
            foreach (@templist) { unless (&General::validport($_)) { $errormessage = $Lang::tr{'errmsg invalid destination port'}; } }
            $proxysettings{'PORTS_SSL'} .= $line."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'DST_NOCACHE'});
    undef $proxysettings{'DST_NOCACHE'};
    foreach (@temp)
    {
        s/^\s+//g;
        unless (/^#/) { s/\s+//g; }
        if ($_)
        {
            if (/^\./) { $_ = '*'.$_; }
            $proxysettings{'DST_NOCACHE'} .= $_."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'SRC_SUBNETS'});
    undef $proxysettings{'SRC_SUBNETS'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g;
        if ($_)
        {
            $_ = NetAddr::IP->new ($_);
            unless (&General::validipandmask($_)) { $errormessage = $Lang::tr{'errmsg invalid ip or mask'}; }
            $proxysettings{'SRC_SUBNETS'} .= $_."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'SRC_BANNED_IP'});
    undef $proxysettings{'SRC_BANNED_IP'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g;
        if ($_)
        {
            $_ = NetAddr::IP->new ($_);
            s/\/32$//;
            unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'errmsg invalid ip or mask'}; }
            $proxysettings{'SRC_BANNED_IP'} .= $_."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'SRC_BANNED_MAC'});
    undef $proxysettings{'SRC_BANNED_MAC'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g; s/-/:/g;
        if ($_)
        {
            unless (&General::validmac($_)) { $errormessage = $Lang::tr{'errmsg invalid mac'}; }
            $proxysettings{'SRC_BANNED_MAC'} .= $_."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'SRC_UNRESTRICTED_IP'});
    undef $proxysettings{'SRC_UNRESTRICTED_IP'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g;
        if ($_)
        {
            $_ = NetAddr::IP->new ($_);
            s/\/32$//;
            unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'errmsg invalid ip or mask'}; }
            $proxysettings{'SRC_UNRESTRICTED_IP'} .= $_."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'SRC_UNRESTRICTED_MAC'});
    undef $proxysettings{'SRC_UNRESTRICTED_MAC'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g; s/-/:/g;
        if ($_)
        {
            unless (&General::validmac($_)) { $errormessage = $Lang::tr{'errmsg invalid mac'}; }
            $proxysettings{'SRC_UNRESTRICTED_MAC'} .= $_."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'MIME_EXCEPTIONS'});
    undef $proxysettings{'MIME_EXCEPTIONS'};
    foreach (@temp)
    {
        s/^\s+//g;
        unless (/^#/) { s/\s+//g; }
        if ($_)
        {
            if (/^\./) { $_ = '*'.$_; }
            $proxysettings{'MIME_EXCEPTIONS'} .= $_."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'DST_NOAUTH'});
    undef $proxysettings{'DST_NOAUTH'};
    foreach (@temp)
    {
        s/^\s+//g;
        unless (/^#/) { s/\s+//g; }
        if ($_)
        {
            if (/^\./) { $_ = '*'.$_; }
            $proxysettings{'DST_NOAUTH'} .= $_."\n";
        }
    }

    if (($proxysettings{'NTLM_ENABLE_ACL'} eq 'on') && ($proxysettings{'NTLM_USER_ACL'} eq 'positive'))
    {
        @temp = split(/\n/,$proxysettings{'NTLM_ALLOW_USERS'});
        undef $proxysettings{'NTLM_ALLOW_USERS'};
        foreach (@temp)
        {
            s/^\s+//g; s/\s+$//g;
            if ($_) { $proxysettings{'NTLM_ALLOW_USERS'} .= $_."\n"; }
        }
        if ($proxysettings{'NTLM_ALLOW_USERS'} eq '') { $errormessage = $Lang::tr{'errmsg acl cannot be empty'}; }
    }

    if (($proxysettings{'NTLM_ENABLE_ACL'} eq 'on') && ($proxysettings{'NTLM_USER_ACL'} eq 'negative'))
    {
        @temp = split(/\n/,$proxysettings{'NTLM_DENY_USERS'});
        undef $proxysettings{'NTLM_DENY_USERS'};
        foreach (@temp)
        {
            s/^\s+//g; s/\s+$//g;
            if ($_) { $proxysettings{'NTLM_DENY_USERS'} .= $_."\n"; }
        }
        if ($proxysettings{'NTLM_DENY_USERS'} eq '') { $errormessage = $Lang::tr{'errmsg acl cannot be empty'}; }
    }

    if (($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') && ($proxysettings{'IDENT_USER_ACL'} eq 'positive'))
    {
        @temp = split(/\n/,$proxysettings{'IDENT_ALLOW_USERS'});
        undef $proxysettings{'IDENT_ALLOW_USERS'};
        foreach (@temp)
        {
            s/^\s+//g; s/\s+$//g;
            if ($_) { $proxysettings{'IDENT_ALLOW_USERS'} .= $_."\n"; }
        }
        if ($proxysettings{'IDENT_ALLOW_USERS'} eq '') { $errormessage = $Lang::tr{'errmsg acl cannot be empty'}; }
    }

    if (($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') && ($proxysettings{'IDENT_USER_ACL'} eq 'negative'))
    {
        @temp = split(/\n/,$proxysettings{'IDENT_DENY_USERS'});
        undef $proxysettings{'IDENT_DENY_USERS'};
        foreach (@temp)
        {
            s/^\s+//g; s/\s+$//g;
            if ($_) { $proxysettings{'IDENT_DENY_USERS'} .= $_."\n"; }
        }
        if ($proxysettings{'IDENT_DENY_USERS'} eq '') { $errormessage = $Lang::tr{'errmsg acl cannot be empty'}; }
    }

    if (($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on') && ($proxysettings{'RADIUS_USER_ACL'} eq 'positive'))
    {
        @temp = split(/\n/,$proxysettings{'RADIUS_ALLOW_USERS'});
        undef $proxysettings{'RADIUS_ALLOW_USERS'};
        foreach (@temp)
        {
            s/^\s+//g; s/\s+$//g;
            if ($_) { $proxysettings{'RADIUS_ALLOW_USERS'} .= $_."\n"; }
        }
        if ($proxysettings{'RADIUS_ALLOW_USERS'} eq '') { $errormessage = $Lang::tr{'errmsg acl cannot be empty'}; }
    }

    if (($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on') && ($proxysettings{'RADIUS_USER_ACL'} eq 'negative'))
    {
        @temp = split(/\n/,$proxysettings{'RADIUS_DENY_USERS'});
        undef $proxysettings{'RADIUS_DENY_USERS'};
        foreach (@temp)
        {
            s/^\s+//g; s/\s+$//g;
            if ($_) { $proxysettings{'RADIUS_DENY_USERS'} .= $_."\n"; }
        }
        if ($proxysettings{'RADIUS_DENY_USERS'} eq '') { $errormessage = $Lang::tr{'errmsg acl cannot be empty'}; }
    }

    @temp = split(/\n/,$proxysettings{'IDENT_HOSTS'});
    undef $proxysettings{'IDENT_HOSTS'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g;
        if ($_)
        {
            $_ = NetAddr::IP->new ($_);
            s/\/32$//;
            unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'errmsg invalid ip or mask'}; }
            $proxysettings{'IDENT_HOSTS'} .= $_."\n";
        }
    }

    @temp = split(/\n/,$proxysettings{'CRE_SVHOSTS'});
    undef $proxysettings{'CRE_SVHOSTS'};
    foreach (@temp)
    {
        s/^\s+//g; s/\s+$//g;
        if ($_)
        {
            $_ = NetAddr::IP->new ($_);
            s/\/32$//;
            unless (&General::validipormask($_)) { $errormessage = $Lang::tr{'errmsg invalid ip or mask'}; }
            $proxysettings{'CRE_SVHOSTS'} .= $_."\n";
        }
    }
}

# -------------------------------------------------------------------

sub write_acls
{
    open(FILE, ">$acl_src_subnets");
    flock(FILE, 2);
    if (!$proxysettings{'SRC_SUBNETS'})
    {
        print FILE NetAddr::IP->new("$netsettings{'GREEN_1_NETADDRESS'}\/$netsettings{'GREEN_1_NETMASK'}")."\n";
        if ($netsettings{'BLUE_COUNT'} >= 1)
        {
            print FILE NetAddr::IP->new("$netsettings{'BLUE_1_NETADDRESS'}\/$netsettings{'BLUE_1_NETMASK'}")."\n";
        }
    }
    else {
        print FILE $proxysettings{'SRC_SUBNETS'};
    }
    close(FILE);

    open(FILE, ">$acl_src_networks");
    flock(FILE, 2);
    if (!$proxysettings{'SRC_SUBNETS'})
    {
        print FILE NetAddr::IP->new("$netsettings{'GREEN_1_NETADDRESS'}\/$netsettings{'GREEN_1_NETMASK'}")."\n";
        if ($netsettings{'BLUE_COUNT'} >= 1)
        {
            print FILE NetAddr::IP->new("$netsettings{'BLUE_1_NETADDRESS'}\/$netsettings{'BLUE_1_NETMASK'}")."\n";
        }
    }
    else {
        print FILE $proxysettings{'SRC_SUBNETS'};
    }

    if (($proxysettings{'ENABLED_OVPN'} eq 'on') &&
        ((defined($ovpnsettings{'ENABLED_RED_1'}) && $ovpnsettings{'ENABLED_RED_1'} eq 'on')
            || (defined($ovpnsettings{'ENABLED_BLUE_1'}) && $ovpnsettings{'ENABLED_BLUE_1'} eq 'on'))) {
        print FILE NetAddr::IP->new("$ovpnsettings{'DOVPN_SUBNET'}")."\n";
    }
    close(FILE);

    open(FILE, ">$acl_src_banned_ip");
    flock(FILE, 2);
    print FILE $proxysettings{'SRC_BANNED_IP'};
    close(FILE);

    open(FILE, ">$acl_src_banned_mac");
    flock(FILE, 2);
    print FILE $proxysettings{'SRC_BANNED_MAC'};
    close(FILE);

    open(FILE, ">$acl_src_unrestricted_ip");
    flock(FILE, 2);
    print FILE $proxysettings{'SRC_UNRESTRICTED_IP'};
    close(FILE);

    open(FILE, ">$acl_src_unrestricted_mac");
    flock(FILE, 2);
    print FILE $proxysettings{'SRC_UNRESTRICTED_MAC'};
    close(FILE);

    open(FILE, ">$acl_dst_noauth");
    flock(FILE, 2);
    print FILE $proxysettings{'DST_NOAUTH'};
    close(FILE);

    open(FILE, ">$acl_dst_noauth_net");
    close(FILE);
    open(FILE, ">$acl_dst_noauth_dom");
    close(FILE);
    open(FILE, ">$acl_dst_noauth_url");
    close(FILE);

    @temp = split(/\n/,$proxysettings{'DST_NOAUTH'});
    foreach(@temp)
    {
        unless (/^#/)
        {
            if (/^\*\.\w/)
            {
                s/^\*//;
                open(FILE, ">>$acl_dst_noauth_dom");
                flock(FILE, 2);
                print FILE "$_\n";
                close(FILE);
            }
            elsif (&General::validipormask($_))
            {
                open(FILE, ">>$acl_dst_noauth_net");
                flock(FILE, 2);
                $_ = NetAddr::IP->new ($_);
                s/\/32$//;
                print FILE "$_\n";
                close(FILE);
            }
            elsif (/\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?-\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?/)
            {
                open(FILE, ">>$acl_dst_noauth_net");
                flock(FILE, 2);
                print FILE "$_\n";
                close(FILE);
            }
            else
            {
                open(FILE, ">>$acl_dst_noauth_url");
                flock(FILE, 2);
                if (/^[fh]tt?ps?:\/\//) { print FILE "$_\n"; } else { print FILE "^[fh]tt?ps?://$_\n"; }
                close(FILE);
            }
        }
    }

    open(FILE, ">$acl_dst_nocache");
    flock(FILE, 2);
    print FILE $proxysettings{'DST_NOCACHE'};
    close(FILE);

    open(FILE, ">$acl_dst_nocache_net");
    close(FILE);
    open(FILE, ">$acl_dst_nocache_dom");
    close(FILE);
    open(FILE, ">$acl_dst_nocache_url");
    close(FILE);

    @temp = split(/\n/,$proxysettings{'DST_NOCACHE'});
    foreach(@temp)
    {
        unless (/^#/)
        {
            if (/^\*\.\w/)
            {
                s/^\*//;
                open(FILE, ">>$acl_dst_nocache_dom");
                flock(FILE, 2);
                print FILE "$_\n";
                close(FILE);
            }
            elsif (&General::validipormask($_))
            {
                open(FILE, ">>$acl_dst_nocache_net");
                flock(FILE, 2);
                $_ = NetAddr::IP->new ($_);
                s/\/32$//;
                print FILE "$_\n";
                close(FILE);
            }
            elsif (/\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?-\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?/)
            {
                open(FILE, ">>$acl_dst_nocache_net");
                flock(FILE, 2);
                print FILE "$_\n";
                close(FILE);
            }
            else
            {
                open(FILE, ">>$acl_dst_nocache_url");
                flock(FILE, 2);
                if (/^[fh]tt?ps?:\/\//) { print FILE "$_\n"; } else { print FILE "^[fh]tt?ps?://$_\n"; }
                close(FILE);
            }
        }
    }

    open(FILE, ">$acl_dst_mime_exceptions");
    flock(FILE, 2);
    print FILE $proxysettings{'MIME_EXCEPTIONS'};
    close(FILE);

    open(FILE, ">$acl_dst_mime_exceptions_net");
    close(FILE);
    open(FILE, ">$acl_dst_mime_exceptions_dom");
    close(FILE);
    open(FILE, ">$acl_dst_mime_exceptions_url");
    close(FILE);

    @temp = split(/\n/,$proxysettings{'MIME_EXCEPTIONS'});
    foreach(@temp)
    {
        unless (/^#/)
        {
            if (/^\*\.\w/)
            {
                s/^\*//;
                open(FILE, ">>$acl_dst_mime_exceptions_dom");
                flock(FILE, 2);
                print FILE "$_\n";
                close(FILE);
            }
            elsif (&General::validipormask($_))
            {
                open(FILE, ">>$acl_dst_mime_exceptions_net");
                flock(FILE, 2);
                $_ = NetAddr::IP->new ($_);
                s/\/32$//;
                print FILE "$_\n";
                close(FILE);
            }
            elsif (/\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?-\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?/)
            {
                open(FILE, ">>$acl_dst_mime_exceptions_net");
                flock(FILE, 2);
                print FILE "$_\n";
                close(FILE);
            }
            else
            {
                open(FILE, ">>$acl_dst_mime_exceptions_url");
                flock(FILE, 2);
                if (/^[fh]tt?ps?:\/\//) { print FILE "$_\n"; } else { print FILE "^[fh]tt?ps?://$_\n"; }
                close(FILE);
            }
        }
    }

    open(FILE, ">$acl_ports_safe");
    flock(FILE, 2);
    if (!$proxysettings{'PORTS_SAFE'}) { print FILE $def_ports_safe; } else { print FILE $proxysettings{'PORTS_SAFE'}; }
    close(FILE);

    open(FILE, ">$acl_ports_ssl");
    flock(FILE, 2);
    if (!$proxysettings{'PORTS_SSL'}) { print FILE $def_ports_ssl; } else { print FILE $proxysettings{'PORTS_SSL'}; }
    close(FILE);

    open(FILE, ">$acl_dst_throttle");
    flock(FILE, 2);
    if ($proxysettings{'THROTTLE_BINARY'} eq 'on')
    {
        @temp = split(/\|/,$throttle_binary);
        foreach (@temp) { print FILE "\\.$_\$\n"; }
    }
    if ($proxysettings{'THROTTLE_DSKIMG'} eq 'on')
    {
        @temp = split(/\|/,$throttle_dskimg);
        foreach (@temp) { print FILE "\\.$_\$\n"; }
    }
    if ($proxysettings{'THROTTLE_MMEDIA'} eq 'on')
    {
        @temp = split(/\|/,$throttle_mmedia);
        foreach (@temp) { print FILE "\\.$_\$\n"; }
    }
    if (-s $throttled_urls)
    {
        open(URLFILE, $throttled_urls);
        @temp = <URLFILE>;
        close(URLFILE);
        foreach (@temp) { print FILE; }
    }
    close(FILE);

    open(FILE, ">$mimetypes");
    flock(FILE, 2);
    print FILE $proxysettings{'MIME_TYPES'};
    close(FILE);

    open(FILE, ">$ntlmdir/msntauth.allowusers");
    flock(FILE, 2);
    print FILE $proxysettings{'NTLM_ALLOW_USERS'};
    close(FILE);

    open(FILE, ">$ntlmdir/msntauth.denyusers");
    flock(FILE, 2);
    print FILE $proxysettings{'NTLM_DENY_USERS'};
    close(FILE);

    open(FILE, ">$raddir/radauth.allowusers");
    flock(FILE, 2);
    print FILE $proxysettings{'RADIUS_ALLOW_USERS'};
    close(FILE);

    open(FILE, ">$raddir/radauth.denyusers");
    flock(FILE, 2);
    print FILE $proxysettings{'RADIUS_DENY_USERS'};
    close(FILE);

    open(FILE, ">$identdir/identauth.allowusers");
    flock(FILE, 2);
    print FILE $proxysettings{'IDENT_ALLOW_USERS'};
    close(FILE);

    open(FILE, ">$identdir/identauth.denyusers");
    flock(FILE, 2);
    print FILE $proxysettings{'IDENT_DENY_USERS'};
    close(FILE);

    open(FILE, ">$identhosts");
    flock(FILE, 2);
    print FILE $proxysettings{'IDENT_HOSTS'};
    close(FILE);

    open(FILE, ">$cre_groups");
    flock(FILE, 2);
    print FILE $proxysettings{'CRE_GROUPS'};
    close(FILE);

    open(FILE, ">$cre_svhosts");
    flock(FILE, 2);
    print FILE $proxysettings{'CRE_SVHOSTS'};
    close(FILE);
}

# -------------------------------------------------------------------

sub writepacfile
{
    open(FILE, ">/home/httpd/html/proxy.pac");
    flock(FILE, 2);
    print FILE "function FindProxyForURL(url, host)\n";
    print FILE "{\n";
    if (($proxysettings{'ENABLED_GREEN_1'} eq 'on') || ($proxysettings{'ENABLED_BLUE_1'} eq 'on'))
    {
        print FILE <<END
if (
     (isPlainHostName(host)) ||
     (dnsDomainIs(host, ".$mainsettings{'DOMAINNAME'}")) ||
     (isInNet(host, "10.0.0.0", "255.0.0.0")) ||
     (isInNet(host, "172.16.0.0", "255.240.0.0")) ||
     (isInNet(host, "192.168.0.0", "255.255.0.0")) ||
     (isInNet(host, "169.254.0.0", "255.255.0.0"))
   )
     return "DIRECT";

 else

END
;
        if ($proxysettings{'ENABLED_GREEN_1'} eq 'on')
        {
            print FILE "if (\n";
            print FILE "     (isInNet(myIpAddress(), \"$netsettings{'GREEN_1_NETADDRESS'}\", \"$netsettings{'GREEN_1_NETMASK'}\"))";

            undef @templist;
            if (-e "$acl_src_subnets") {
                open(SUBNETS,"$acl_src_subnets");
                @templist = <SUBNETS>;
                close(SUBNETS);
            }

            foreach (@templist)
            {
                @temp = split(/\//);
                if (
                    ($temp[0] ne $netsettings{'GREEN_1_NETADDRESS'}) && ($temp[1] ne $netsettings{'GREEN_1_NETMASK'}) &&
                    ($temp[0] ne $netsettings{'BLUE_1_NETADDRESS'}) && ($temp[1] ne $netsettings{'BLUE_1_NETMASK'})
                    )
                {
                    chomp $temp[1];
                    print FILE " ||\n     (isInNet(myIpAddress(), \"$temp[0]\", \"$temp[1]\"))";
                }
            }

            print FILE "\n";

            print FILE <<END
   )
     return "PROXY $netsettings{'GREEN_1_ADDRESS'}:$proxysettings{'PROXY_PORT'}";
END
;
        }
        if (($proxysettings{'ENABLED_GREEN_1'} eq 'on') && ($proxysettings{'ENABLED_BLUE_1'} eq 'on') && ($netsettings{'BLUE_COUNT'} >= 1))
        {
            print FILE "\n else\n\n";
        }
        if (($netsettings{'BLUE_COUNT'} >= 1) && ($proxysettings{'ENABLED_BLUE_1'} eq 'on'))
        {
            print FILE <<END
if (
     (isInNet(myIpAddress(), "$netsettings{'BLUE_1_NETADDRESS'}", "$netsettings{'BLUE_1_NETMASK'}"))
   )
     return "PROXY $netsettings{'BLUE_1_ADDRESS'}:$proxysettings{'PROXY_PORT'}";
END
;
        }
    }
    print FILE "}\n";
    close(FILE);
}

# -------------------------------------------------------------------

sub writeconfig
{
    my $authrealm;
    my $delaypools;

    if ($proxysettings{'THROTTLING_GREEN_TOTAL'} +
        $proxysettings{'THROTTLING_GREEN_HOST'}  +
        $proxysettings{'THROTTLING_BLUE_TOTAL'}  +
        $proxysettings{'THROTTLING_BLUE_HOST'} gt 0)
    {
        $delaypools = 1; } else { $delaypools = 0;
    }

    if ($proxysettings{'AUTH_REALM'} eq '')
    {
        $authrealm = "IPCop Advanced Proxy Server";
    } else {
        $authrealm = $proxysettings{'AUTH_REALM'};
    }

    $_ = $proxysettings{'UPSTREAM_PROXY'};
    my ($remotehost, $remoteport) = (/^(?:[a-zA-Z ]+\:\/\/)?(?:[A-Za-z0-9\_\.\-]*?(?:\:[A-Za-z0-9\_\.\-]*?)?\@)?([a-zA-Z0-9\.\_\-]*?)(?:\:([0-9]{1,5}))?(?:\/.*?)?$/);

    if ($remoteport eq '') { $remoteport = 80; }

    open(FILE, ">/var/ipcop/proxy/squid.conf");
    flock(FILE, 2);
    print FILE <<END
# Do not modify '/var/ipcop/proxy/squid.conf' directly since any changes
# you make will be overwritten whenever you resave proxy settings using the
# web interface!
#
# Instead, modify the file '$acl_include' and
# then restart the proxy service using the web interface. Changes made to the
# 'include.acl' file will propagate to the 'squid.conf' file at that time.

shutdown_lifetime 5 seconds
icp_port 0

END
    ;

    if ($proxysettings{'ENABLED_GREEN_1'} eq 'on') {
        print FILE "http_port $netsettings{'GREEN_1_ADDRESS'}:$proxysettings{'PROXY_PORT'}";
        if ($proxysettings{'TRANSPARENT_GREEN_1'} eq 'on') { print FILE " transparent" }
        if ($proxysettings{'NO_CONNECTION_AUTH'} eq 'on') { print FILE " no-connection-auth" }
        print FILE "\n";
    }
    if (($netsettings{'BLUE_COUNT'} >= 1) && ($proxysettings{'ENABLED_BLUE_1'} eq 'on')) {
        print FILE "http_port $netsettings{'BLUE_1_ADDRESS'}:$proxysettings{'PROXY_PORT'}";
        if ($proxysettings{'TRANSPARENT_BLUE_1'} eq 'on') { print FILE " transparent" }
        if ($proxysettings{'NO_CONNECTION_AUTH'} eq 'on') { print FILE " no-connection-auth" }
        print FILE "\n";
    }
    if ($proxysettings{'ENABLED_OVPN'} eq 'on') {
        my $serverip = NetAddr::IP->new($ovpnsettings{'DOVPN_SUBNET'})->first()->addr();
        print FILE "http_port $serverip:$proxysettings{'PROXY_PORT'}";
        if ($proxysettings{'TRANSPARENT_OVPN'} eq 'on') { print FILE " transparent" }
        if ($proxysettings{'NO_CONNECTION_AUTH'} eq 'on') { print FILE " no-connection-auth" }
        print FILE "\n";
    }

    if (($proxysettings{'CACHE_SIZE'} > 0) || ($proxysettings{'CACHE_MEM'} > 0)) {
        print FILE "\n";

        if (!-z $acl_dst_nocache_dom) {
            print FILE "acl no_cache_domains dstdomain \"$acl_dst_nocache_dom\"\n";
            print FILE "cache deny no_cache_domains\n";
        }
        if (!-z $acl_dst_nocache_net) {
            print FILE "acl no_cache_ipaddr dst \"$acl_dst_nocache_net\"\n";
            print FILE "cache deny no_cache_ipaddr\n";
        }
        if (!-z $acl_dst_nocache_url) {
            print FILE "acl no_cache_hosts url_regex -i \"$acl_dst_nocache_url\"\n";
            print FILE "cache deny no_cache_hosts\n";
        }
    }

    print FILE <<END

cache_effective_user squid
cache_effective_group squid
umask 022

pid_filename /var/run/squid.pid

cache_mem $proxysettings{'CACHE_MEM'} MB
END
    ;

    unless ($proxysettings{'CACHE_SIZE'} eq '0') {
        print FILE "cache_dir aufs /var/log/cache $proxysettings{'CACHE_SIZE'} $proxysettings{'L1_DIRS'} 256\n\n";
    }

    if (($proxysettings{'ERR_DESIGN'} eq 'ipcop') && ($proxysettings{'VISIBLE_HOSTNAME'} eq ''))
    {
        print FILE "error_directory $errordir.ipcop/$proxysettings{'ERR_LANGUAGE'}\n\n";
    } else {
        print FILE "error_directory $errordir/$proxysettings{'ERR_LANGUAGE'}\n\n";
    }

    if ($proxysettings{'OFFLINE_MODE'} eq 'on') {  print FILE "offline_mode on\n\n"; }

    if ((!($proxysettings{'MEM_POLICY'} eq 'LRU')) || (!($proxysettings{'CACHE_POLICY'} eq 'LRU')))
    {
        if (!($proxysettings{'MEM_POLICY'} eq 'LRU'))
        {
            print FILE "memory_replacement_policy $proxysettings{'MEM_POLICY'}\n";
        }
        if (!($proxysettings{'CACHE_POLICY'} eq 'LRU'))
        {
            print FILE "cache_replacement_policy $proxysettings{'CACHE_POLICY'}\n";
        }
        print FILE "\n";
    }

    if ($proxysettings{'LOGGING'} eq 'on')
    {
        print FILE <<END
access_log /var/log/squid/access.log
cache_log /var/log/squid/cache.log
cache_store_log none
END
    ;
        if ($proxysettings{'LOGUSERAGENT'} eq 'on') { print FILE "useragent_log \/var\/log\/squid\/user_agent.log\n"; }
        if ($proxysettings{'LOGQUERY'} eq 'on') { print FILE "\nstrip_query_terms off\n"; }
    } else {
        print FILE <<END
access_log /dev/null
cache_log /dev/null
cache_store_log none
END
    ;}
    print FILE <<END

log_mime_hdrs off
logfile_rotate 0
END
    ;

    if ($proxysettings{'FORWARD_IPADDRESS'} eq 'on')
    {
        print FILE "forwarded_for on\n";
    } else {
        print FILE "forwarded_for off\n";
    }
    if ($proxysettings{'FORWARD_VIA'} eq 'on')
    {
        print FILE "via on\n";
    } else {
        print FILE "via off\n";
    }
    print FILE "\n";

    if ((!($proxysettings{'AUTH_METHOD'} eq 'none')) && (!($proxysettings{'AUTH_METHOD'} eq 'ident')))
    {
        if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
        {
            print FILE "auth_param basic program $authdir/ncsa_auth $userdb\n";
            print FILE "auth_param basic children $proxysettings{'AUTH_CHILDREN'}\n";
            print FILE "auth_param basic realm $authrealm\n";
            print FILE "auth_param basic credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n";
            if (!($proxysettings{'AUTH_IPCACHE_TTL'} eq '0')) { print FILE "\nauthenticate_ip_ttl $proxysettings{'AUTH_IPCACHE_TTL'} minutes\n"; }
        }

        if ($proxysettings{'AUTH_METHOD'} eq 'ldap')
        {
            print FILE "auth_param basic program $authdir/squid_ldap_auth -b \"$proxysettings{'LDAP_BASEDN'}\"";
            if (!($proxysettings{'LDAP_BINDDN_USER'} eq '')) { print FILE " -D \"$proxysettings{'LDAP_BINDDN_USER'}\""; }
            if (!($proxysettings{'LDAP_BINDDN_PASS'} eq '')) { print FILE " -w $proxysettings{'LDAP_BINDDN_PASS'}"; }
            if ($proxysettings{'LDAP_TYPE'} eq 'ADS')
            {
                if ($proxysettings{'LDAP_GROUP'} eq '')
                {
                    print FILE " -f \"(\&(objectClass=person)(sAMAccountName=\%s))\"";
                } else {
                    print FILE " -f \"(\&(\&(objectClass=person)(sAMAccountName=\%s))(memberOf=$proxysettings{'LDAP_GROUP'}))\"";
                }
                print FILE " -u sAMAccountName -P";
            }
            if ($proxysettings{'LDAP_TYPE'} eq 'NDS')
            {
                if ($proxysettings{'LDAP_GROUP'} eq '')
                {
                    print FILE " -f \"(\&(objectClass=person)(cn=\%s))\"";
                } else {
                    print FILE " -f \"(\&(\&(objectClass=person)(cn=\%s))(groupMembership=$proxysettings{'LDAP_GROUP'}))\"";
                }
                print FILE " -u cn -P";
            }
            if (($proxysettings{'LDAP_TYPE'} eq 'V2') || ($proxysettings{'LDAP_TYPE'} eq 'V3'))
            {
                if ($proxysettings{'LDAP_GROUP'} eq '')
                {
                    print FILE " -f \"(\&(objectClass=person)(uid=\%s))\"";
                } else {
                    print FILE " -f \"(\&(\&(objectClass=person)(uid=\%s))(posixGroup=$proxysettings{'LDAP_GROUP'}))\"";
                }
                if ($proxysettings{'LDAP_TYPE'} eq 'V2') { print FILE " -v 2"; }
                if ($proxysettings{'LDAP_TYPE'} eq 'V3') { print FILE " -v 3"; }
                print FILE " -u uid -P";
            }
            print FILE " $proxysettings{'LDAP_SERVER'}:$proxysettings{'LDAP_PORT'}\n";
            print FILE "auth_param basic children $proxysettings{'AUTH_CHILDREN'}\n";
            print FILE "auth_param basic realm $authrealm\n";
            print FILE "auth_param basic credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n";
            if (!($proxysettings{'AUTH_IPCACHE_TTL'} eq '0')) { print FILE "\nauthenticate_ip_ttl $proxysettings{'AUTH_IPCACHE_TTL'} minutes\n"; }
        }

        if ($proxysettings{'AUTH_METHOD'} eq 'ntlm')
        {
            if ($proxysettings{'NTLM_ENABLE_INT_AUTH'} eq 'on')
            {
                print FILE "auth_param ntlm program $authdir/ntlm_smb_lm_auth $proxysettings{'NTLM_DOMAIN'}/$proxysettings{'NTLM_PDC'}";
                if ($proxysettings{'NTLM_BDC'} eq '') { print FILE "\n"; } else { print FILE " $proxysettings{'NTLM_DOMAIN'}/$proxysettings{'NTLM_BDC'}\n"; }
                print FILE "auth_param ntlm children $proxysettings{'AUTH_CHILDREN'}\n";
                if (!($proxysettings{'AUTH_IPCACHE_TTL'} eq '0')) { print FILE "\nauthenticate_ip_ttl $proxysettings{'AUTH_IPCACHE_TTL'} minutes\n"; }
            } else {
                print FILE "auth_param basic program $authdir/msnt_auth\n";
                print FILE "auth_param basic children $proxysettings{'AUTH_CHILDREN'}\n";
                print FILE "auth_param basic realm $authrealm\n";
                print FILE "auth_param basic credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n";
                if (!($proxysettings{'AUTH_IPCACHE_TTL'} eq '0')) { print FILE "\nauthenticate_ip_ttl $proxysettings{'AUTH_IPCACHE_TTL'} minutes\n"; }

                open(MSNTCONF, ">$ntlmdir/msntauth.conf");
                flock(MSNTCONF,2);
                print MSNTCONF "server $proxysettings{'NTLM_PDC'}";
                if ($proxysettings{'NTLM_BDC'} eq '') { print MSNTCONF " $proxysettings{'NTLM_PDC'}"; } else { print MSNTCONF " $proxysettings{'NTLM_BDC'}"; }
                print MSNTCONF " $proxysettings{'NTLM_DOMAIN'}\n";
                if ($proxysettings{'NTLM_ENABLE_ACL'} eq 'on')
                {
                    if ($proxysettings{'NTLM_USER_ACL'} eq 'positive')
                    {
                        print MSNTCONF "allowusers $ntlmdir/msntauth.allowusers\n";
                    } else {
                        print MSNTCONF "denyusers $ntlmdir/msntauth.denyusers\n";
                    }
                }
                close(MSNTCONF);
            }
        }

        if ($proxysettings{'AUTH_METHOD'} eq 'radius')
        {
            print FILE "auth_param basic program $authdir/squid_radius_auth -h $proxysettings{'RADIUS_SERVER'} -p $proxysettings{'RADIUS_PORT'} ";
            if (!($proxysettings{'RADIUS_IDENTIFIER'} eq '')) { print FILE "-i $proxysettings{'RADIUS_IDENTIFIER'} "; }
            print FILE "-w $proxysettings{'RADIUS_SECRET'}\n";
            print FILE "auth_param basic children $proxysettings{'AUTH_CHILDREN'}\n";
            print FILE "auth_param basic realm $authrealm\n";
            print FILE "auth_param basic credentialsttl $proxysettings{'AUTH_CACHE_TTL'} minutes\n";
            if (!($proxysettings{'AUTH_IPCACHE_TTL'} eq '0')) { print FILE "\nauthenticate_ip_ttl $proxysettings{'AUTH_IPCACHE_TTL'} minutes\n"; }
        }

        print FILE "\n";
        print FILE "acl for_inetusers proxy_auth REQUIRED\n";
        if (($proxysettings{'AUTH_METHOD'} eq 'ntlm') && ($proxysettings{'NTLM_ENABLE_INT_AUTH'} eq 'on') && ($proxysettings{'NTLM_ENABLE_ACL'} eq 'on'))
        {
            if ((!-z "$ntlmdir/msntauth.allowusers") && ($proxysettings{'NTLM_USER_ACL'} eq 'positive'))
            {
                print FILE "acl for_acl_users proxy_auth \"$ntlmdir/msntauth.allowusers\"\n";
            }
            if ((!-z "$ntlmdir/msntauth.denyusers") && ($proxysettings{'NTLM_USER_ACL'} eq 'negative'))
            {
                print FILE "acl for_acl_users proxy_auth \"$ntlmdir/msntauth.denyusers\"\n";
            }
        }
        if (($proxysettings{'AUTH_METHOD'} eq 'radius') && ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on'))
        {
            if ((!-z "$raddir/radauth.allowusers") && ($proxysettings{'RADIUS_USER_ACL'} eq 'positive'))
            {
                print FILE "acl for_acl_users proxy_auth \"$raddir/radauth.allowusers\"\n";
            }
            if ((!-z "$raddir/radauth.denyusers") && ($proxysettings{'RADIUS_USER_ACL'} eq 'negative'))
            {
                print FILE "acl for_acl_users proxy_auth \"$raddir/radauth.denyusers\"\n";
            }
        }
        if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
        {
            print FILE "\n";
            if (!-z $extgrp) { print FILE "acl for_extended_users proxy_auth \"$extgrp\"\n"; }
            if (!-z $disgrp) { print FILE "acl for_disabled_users proxy_auth \"$disgrp\"\n"; }
        }
        if (!($proxysettings{'AUTH_MAX_USERIP'} eq '')) { print FILE "\nacl concurrent max_user_ip -s $proxysettings{'AUTH_MAX_USERIP'}\n"; }
        print FILE "\n";

        if (!-z $acl_dst_noauth_net) { print FILE "acl to_ipaddr_without_auth dst \"$acl_dst_noauth_net\"\n"; }
        if (!-z $acl_dst_noauth_dom) { print FILE "acl to_domains_without_auth dstdomain \"$acl_dst_noauth_dom\"\n"; }
        if (!-z $acl_dst_noauth_url) { print FILE "acl to_hosts_without_auth url_regex -i \"$acl_dst_noauth_url\"\n"; }
        print FILE "\n";
    }

    if ($proxysettings{'AUTH_METHOD'} eq 'ident')
    {
        if ($proxysettings{'IDENT_REQUIRED'} eq 'on')
        {
            print FILE "acl for_inetusers ident REQUIRED\n";
        }
        if ($proxysettings{'IDENT_ENABLE_ACL'} eq 'on')
        {
            if ((!-z "$identdir/identauth.allowusers") && ($proxysettings{'IDENT_USER_ACL'} eq 'positive'))
            {
                print FILE "acl for_acl_users ident_regex -i \"$identdir/identauth.allowusers\"\n\n";
            }
            if ((!-z "$identdir/identauth.denyusers") && ($proxysettings{'IDENT_USER_ACL'} eq 'negative'))
            {
                print FILE "acl for_acl_users ident_regex -i \"$identdir/identauth.denyusers\"\n\n";
            }
        }
        if (!-z $acl_dst_noauth_net) { print FILE "acl to_ipaddr_without_auth dst \"$acl_dst_noauth_net\"\n"; }
        if (!-z $acl_dst_noauth_dom) { print FILE "acl to_domains_without_auth dstdomain \"$acl_dst_noauth_dom\"\n"; }
        if (!-z $acl_dst_noauth_url) { print FILE "acl to_hosts_without_auth url_regex -i \"$acl_dst_noauth_url\"\n"; }
        print FILE "\n";
    }

    if (($delaypools) && (!-z $acl_dst_throttle)) { print FILE "acl for_throttled_urls url_regex -i \"$acl_dst_throttle\"\n\n"; }

    if ($proxysettings{'ENABLE_BROWSER_CHECK'} eq 'on') { print FILE "acl with_allowed_useragents browser $browser_regexp\n\n"; }

    print FILE "acl within_timeframe time ";
    if ($proxysettings{'TIME_MON'} eq 'on') { print FILE "M"; }
    if ($proxysettings{'TIME_TUE'} eq 'on') { print FILE "T"; }
    if ($proxysettings{'TIME_WED'} eq 'on') { print FILE "W"; }
    if ($proxysettings{'TIME_THU'} eq 'on') { print FILE "H"; }
    if ($proxysettings{'TIME_FRI'} eq 'on') { print FILE "F"; }
    if ($proxysettings{'TIME_SAT'} eq 'on') { print FILE "A"; }
    if ($proxysettings{'TIME_SUN'} eq 'on') { print FILE "S"; }
    print FILE " $proxysettings{'TIME_FROM_HOUR'}:";
    print FILE "$proxysettings{'TIME_FROM_MINUTE'}-";
    print FILE "$proxysettings{'TIME_TO_HOUR'}:";
    print FILE "$proxysettings{'TIME_TO_MINUTE'}\n\n";

    if ((!-z $mimetypes) && ($proxysettings{'ENABLE_MIME_FILTER'} eq 'on')) {
        print FILE "acl blocked_mimetypes rep_mime_type \"$mimetypes\"\n";
        if (!-z $acl_dst_mime_exceptions_dom) { print FILE "acl mime_exception_domains dstdomain \"$acl_dst_mime_exceptions_dom\")\n"; }
        if (!-z $acl_dst_mime_exceptions_net) { print FILE "acl mime_exception_ipaddr dst \"$acl_dst_mime_exceptions_net\")\n"; }
        if (!-z $acl_dst_mime_exceptions_url) { print FILE "acl mime_exception_hosts url_regex -i \"$acl_dst_mime_exceptions_url\")\n"; }
        print FILE "\n";
    }

    print FILE <<END
#acl all src 0.0.0.0/0.0.0.0
acl localhost src 127.0.0.1/32
END
;
open (PORTS,"$acl_ports_ssl");
@temp = <PORTS>;
close PORTS;
if (@temp)
{
    foreach (@temp) { print FILE "acl SSL_ports port $_"; }
}
open (PORTS,"$acl_ports_safe");
@temp = <PORTS>;
close PORTS;
if (@temp)
{
    foreach (@temp) { print FILE "acl Safe_ports port $_"; }
}
    print FILE <<END

acl IPCop_http  port $http_port
acl IPCop_https port $https_port
acl IPCop_ips              dst $netsettings{'GREEN_1_ADDRESS'}
acl IPCop_networks         src "$acl_src_networks"
acl IPCop_servers          dst "$acl_src_subnets"
END
    ;
    print FILE "acl IPCop_green_network    src " . NetAddr::IP->new ("$netsettings{'GREEN_1_NETADDRESS'}/$netsettings{'GREEN_1_NETMASK'}") . "\n";
    print FILE "acl IPCop_green_servers    dst " . NetAddr::IP->new ("$netsettings{'GREEN_1_NETADDRESS'}/$netsettings{'GREEN_1_NETMASK'}") . "\n";
    if ($netsettings{'BLUE_COUNT'} >= 1) { print FILE "acl IPCop_blue_network     src " . NetAddr::IP->new ("$netsettings{'BLUE_1_NETADDRESS'}/$netsettings{'BLUE_1_NETMASK'}") . "\n"; }
    if ($netsettings{'BLUE_COUNT'} >= 1) { print FILE "acl IPCop_blue_servers     dst " . NetAddr::IP->new ("$netsettings{'BLUE_1_NETADDRESS'}/$netsettings{'BLUE_1_NETMASK'}") . "\n"; }
    if (!-z $acl_src_banned_ip) { print FILE "acl IPCop_banned_ips       src \"$acl_src_banned_ip\"\n"; }
    if (!-z $acl_src_banned_mac) { print FILE "acl IPCop_banned_mac       arp \"$acl_src_banned_mac\"\n"; }
    if (!-z $acl_src_unrestricted_ip) { print FILE "acl IPCop_unrestricted_ips src \"$acl_src_unrestricted_ip\"\n"; }
    if (!-z $acl_src_unrestricted_mac) { print FILE "acl IPCop_unrestricted_mac arp \"$acl_src_unrestricted_mac\"\n"; }
    print FILE <<END
acl CONNECT method CONNECT
END
    ;

    if ($proxysettings{'CLASSROOM_EXT'} eq 'on') {
        print FILE <<END

#Classroom extensions
acl IPCop_no_access_ips src "$acl_src_noaccess_ip"
acl IPCop_no_access_mac arp "$acl_src_noaccess_mac"
END
        ;
        print FILE "deny_info ";
        if ((($proxysettings{'ERR_DESIGN'} eq 'ipcop') && (-e "$errordir.ipcop/$proxysettings{'ERR_LANGUAGE'}/ERR_ACCESS_DISABLED")) ||
            (($proxysettings{'ERR_DESIGN'} eq 'squid') && (-e "$errordir/$proxysettings{'ERR_LANGUAGE'}/ERR_ACCESS_DISABLED")))
        {
            print FILE "ERR_ACCESS_DISABLED";
        } else {
            print FILE "ERR_ACCESS_DENIED";
        }
        print FILE " IPCop_no_access_ips\n";
        print FILE "deny_info ";
        if ((($proxysettings{'ERR_DESIGN'} eq 'ipcop') && (-e "$errordir.ipcop/$proxysettings{'ERR_LANGUAGE'}/ERR_ACCESS_DISABLED")) ||
            (($proxysettings{'ERR_DESIGN'} eq 'squid') && (-e "$errordir/$proxysettings{'ERR_LANGUAGE'}/ERR_ACCESS_DISABLED")))
        {
            print FILE "ERR_ACCESS_DISABLED";
        } else {
            print FILE "ERR_ACCESS_DENIED";
        }
        print FILE " IPCop_no_access_mac\n";

        print FILE <<END
http_access deny IPCop_no_access_ips
http_access deny IPCop_no_access_mac
END
    ;
    }

    #Insert acl file and replace __VAR__ with correct values
    my $blue_net = ''; #BLUE empty by default
    my $blue_ip = '';
    if (($netsettings{'BLUE_COUNT'} >= 1) && ($proxysettings{'ENABLED_BLUE_1'} eq 'on')) {
        $blue_net = "$netsettings{'BLUE_1_NETADDRESS'}/$netsettings{'BLUE_1_NETMASK'}";
        $blue_ip  = "$netsettings{'BLUE_1_ADDRESS'}";
    }
    if (!-z $acl_include)
    {
        open (ACL, "$acl_include");
        print FILE "\n#Start of custom includes\n\n";
        while (<ACL>) {
            $_ =~ s/__GREEN_IP__/$netsettings{'GREEN_1_ADDRESS'}/;
            $_ =~ s/__GREEN_NET__/$netsettings{'GREEN_1_NETADDRESS'}\/$netsettings{'GREEN_1_NETMASK'}/;
            $_ =~ s/__BLUE_IP__/$netsettings{'BLUE_1_ADDRESS'}/;
            $_ =~ s/__BLUE_NET__/$netsettings{'BLUE_1_NETADDRESS'}\/$netsettings{'BLUE_1_NETMASK'}/;
            $_ =~ s/__PROXY_PORT__/$proxysettings{'PROXY_PORT'}/;
            print FILE $_;
        }
        print FILE "\n#End of custom includes\n";
        close (ACL);
    }
    if ((!-z $extgrp) && ($proxysettings{'AUTH_METHOD'} eq 'ncsa') && ($proxysettings{'NCSA_BYPASS_REDIR'} eq 'on')) { print FILE "\nredirector_access deny for_extended_users\n"; }
    print FILE <<END

#Access to squid:
#local machine, no restriction
http_access allow         localhost

#GUI admin if local machine connects
http_access allow         IPCop_ips IPCop_networks IPCop_http
http_access allow CONNECT IPCop_ips IPCop_networks IPCop_https

#Deny not web services
http_access deny          !Safe_ports
http_access deny  CONNECT !SSL_ports

END
    ;

if ($proxysettings{'AUTH_METHOD'} eq 'ident')
{
print FILE "#Set ident ACLs\n";
if (!-z $identhosts)
    {
        print FILE "acl on_ident_aware_hosts src \"$identhosts\"\n";
        print FILE "ident_lookup_access allow on_ident_aware_hosts\n";
        print FILE "ident_lookup_access deny all\n";
    } else {
        print FILE "ident_lookup_access allow all\n";
    }
    print FILE "ident_timeout $proxysettings{'IDENT_TIMEOUT'} seconds\n\n";
}

if ($delaypools) {
    print FILE "#Set download throttling\n";

    if ($netsettings{'BLUE_COUNT'} >= 1)
    {
        print FILE "delay_pools 2\n";
    } else {
        print FILE "delay_pools 1\n";
    }

    print FILE "delay_class 1 3\n";
    if ($netsettings{'BLUE_COUNT'} >= 1) {	print FILE "delay_class 2 3\n"; }

    print FILE "delay_parameters 1 ";
    if ($proxysettings{'THROTTLING_GREEN_TOTAL'} eq 'unlimited')
    {
        print FILE "-1/-1";
    } else {
        print FILE $proxysettings{'THROTTLING_GREEN_TOTAL'} * 125;
        print FILE "/";
        print FILE $proxysettings{'THROTTLING_GREEN_TOTAL'} * 250;
    }

    print FILE " -1/-1 ";
    if ($proxysettings{'THROTTLING_GREEN_HOST'} eq 'unlimited')
    {
        print FILE "-1/-1";
    } else {
        print FILE $proxysettings{'THROTTLING_GREEN_HOST'} * 125;
        print FILE "/";
        print FILE $proxysettings{'THROTTLING_GREEN_HOST'} * 250;
    }
    print FILE "\n";

    if ($netsettings{'BLUE_COUNT'} >= 1)
    {
        print FILE "delay_parameters 2 ";
        if ($proxysettings{'THROTTLING_BLUE_TOTAL'} eq 'unlimited')
        {
            print FILE "-1/-1";
        } else {
            print FILE $proxysettings{'THROTTLING_BLUE_TOTAL'} * 125;
            print FILE "/";
            print FILE $proxysettings{'THROTTLING_BLUE_TOTAL'} * 250;
        }
        print FILE " -1/-1 ";
        if ($proxysettings{'THROTTLING_BLUE_HOST'} eq 'unlimited')
        {
            print FILE "-1/-1";
        } else {
            print FILE $proxysettings{'THROTTLING_BLUE_HOST'} * 125;
            print FILE "/";
            print FILE $proxysettings{'THROTTLING_BLUE_HOST'} * 250;
        }
        print FILE "\n";
    }

    print FILE "delay_access 1 deny  IPCop_ips\n";
    if (!-z $acl_src_unrestricted_ip)  { print FILE "delay_access 1 deny  IPCop_unrestricted_ips\n"; }
    if (!-z $acl_src_unrestricted_mac) { print FILE "delay_access 1 deny  IPCop_unrestricted_mac\n"; }
    if (($proxysettings{'AUTH_METHOD'} eq 'ncsa') && (!-z $extgrp)) { print FILE "delay_access 1 deny  for_extended_users\n"; }

    if ($netsettings{'BLUE_COUNT'} >= 1)
    {
        print FILE "delay_access 1 allow IPCop_green_network";
        if (!-z $acl_dst_throttle) { print FILE " for_throttled_urls"; }
        print FILE "\n";
        print FILE "delay_access 1 deny  all\n";
    } else {
        print FILE "delay_access 1 allow all";
        if (!-z $acl_dst_throttle) { print FILE " for_throttled_urls"; }
        print FILE "\n";
    }

    if ($netsettings{'BLUE_COUNT'} >= 1)
    {
        print FILE "delay_access 2 deny  IPCop_ips\n";
        if (!-z $acl_src_unrestricted_ip)  { print FILE "delay_access 2 deny  IPCop_unrestricted_ips\n"; }
        if (!-z $acl_src_unrestricted_mac) { print FILE "delay_access 2 deny  IPCop_unrestricted_mac\n"; }
        if (($proxysettings{'AUTH_METHOD'} eq 'ncsa') && (!-z $extgrp)) { print FILE "delay_access 2 deny  for_extended_users\n"; }
        print FILE "delay_access 2 allow IPCop_blue_network";
        if (!-z $acl_dst_throttle) { print FILE " for_throttled_urls"; }
        print FILE "\n";
        print FILE "delay_access 2 deny  all\n";
    }

    print FILE "delay_initial_bucket_level 100\n";
    print FILE "\n";
}

if ($proxysettings{'NO_PROXY_LOCAL'} eq 'on')
{
    print FILE "#Prevent internal proxy access\n";
    print FILE "http_access deny IPCop_servers\n\n";
}

if ($proxysettings{'NO_PROXY_LOCAL_GREEN'} eq 'on')
{
    print FILE "#Prevent internal proxy access to Green\n";
    print FILE "http_access deny IPCop_green_servers !IPCop_green_network\n\n";
}

if (($proxysettings{'NO_PROXY_LOCAL_BLUE'} eq 'on') && ($netsettings{'BLUE_COUNT'} >= 1))
{
    print FILE "#Prevent internal proxy access from Blue\n";
    print FILE "http_access allow IPCop_blue_network IPCop_blue_servers\n";
    print FILE "http_access deny  IPCop_blue_network IPCop_servers\n\n";
}

    print FILE <<END
#Set custom configured ACLs
END
    ;
    if (!-z $acl_src_banned_ip) { print FILE "http_access deny  IPCop_banned_ips\n"; }
    if (!-z $acl_src_banned_mac) { print FILE "http_access deny  IPCop_banned_mac\n"; }

    if ((!-z $acl_dst_noauth) && (!($proxysettings{'AUTH_METHOD'} eq 'none')))
    {
        if (!-z $acl_src_unrestricted_ip)
        {
            if (!-z $acl_dst_noauth_net) { print FILE "http_access allow IPCop_unrestricted_ips to_ipaddr_without_auth\n"; }
            if (!-z $acl_dst_noauth_dom) { print FILE "http_access allow IPCop_unrestricted_ips to_domains_without_auth\n"; }
            if (!-z $acl_dst_noauth_url) { print FILE "http_access allow IPCop_unrestricted_ips to_hosts_without_auth\n"; }
        }
        if (!-z $acl_src_unrestricted_mac)
        {
            if (!-z $acl_dst_noauth_net) { print FILE "http_access allow IPCop_unrestricted_mac to_ipaddr_without_auth\n"; }
            if (!-z $acl_dst_noauth_dom) { print FILE "http_access allow IPCop_unrestricted_mac to_domains_without_auth\n"; }
            if (!-z $acl_dst_noauth_url) { print FILE "http_access allow IPCop_unrestricted_mac to_hosts_without_auth\n"; }
        }
        if (!-z $acl_dst_noauth_net)
        {
            print FILE "http_access allow IPCop_networks";
            if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
                print FILE " !within_timeframe";
            } else {
                print FILE " within_timeframe"; }
            if ($proxysettings{'ENABLE_BROWSER_CHECK'} eq 'on') { print FILE " with_allowed_useragents"; }
            print FILE " to_ipaddr_without_auth\n";
        }
        if (!-z $acl_dst_noauth_dom)
        {
            print FILE "http_access allow IPCop_networks";
            if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
                print FILE " !within_timeframe";
            } else {
                print FILE " within_timeframe"; }
            if ($proxysettings{'ENABLE_BROWSER_CHECK'} eq 'on') { print FILE " with_allowed_useragents"; }
            print FILE " to_domains_without_auth\n";
        }
        if (!-z $acl_dst_noauth_url)
        {
            print FILE "http_access allow IPCop_networks";
            if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
                print FILE " !within_timeframe";
            } else {
                print FILE " within_timeframe"; }
            if ($proxysettings{'ENABLE_BROWSER_CHECK'} eq 'on') { print FILE " with_allowed_useragents"; }
            print FILE " to_hosts_without_auth\n";
        }
    }

    if (($proxysettings{'AUTH_METHOD'} eq 'ident') && ($proxysettings{'IDENT_REQUIRED'} eq 'on') && ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'on'))
    {
        print FILE "http_access deny  !for_inetusers";
        if (!-z $identhosts) { print FILE " on_ident_aware_hosts"; }
        print FILE "\n";
    }

    if (
         ($proxysettings{'AUTH_METHOD'} eq 'ident') &&
         ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'on') &&
         ($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') &&
         ($proxysettings{'IDENT_USER_ACL'} eq 'negative') &&
         (!-z "$identdir/identauth.denyusers")
       )
    {
        print FILE "http_access deny  for_acl_users";
        if (($proxysettings{'AUTH_METHOD'} eq 'ident') && (!-z "$identdir/hosts")) { print FILE " on_ident_aware_hosts"; }
        print FILE "\n";
    }

    if (!-z $acl_src_unrestricted_ip)
    {
        print FILE "http_access allow IPCop_unrestricted_ips";
        if ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'on')
        {
            if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
            {
                if (!-z $disgrp) { print FILE " !for_disabled_users"; } else { print FILE " for_inetusers"; }
            }
            if (($proxysettings{'AUTH_METHOD'} eq 'ldap') || (($proxysettings{'AUTH_METHOD'} eq 'ntlm') && ($proxysettings{'NTLM_ENABLE_INT_AUTH'} eq 'off')) || ($proxysettings{'AUTH_METHOD'} eq 'radius'))
            {
                print FILE " for_inetusers";
            }
            if (($proxysettings{'AUTH_METHOD'} eq 'ntlm') && ($proxysettings{'NTLM_ENABLE_INT_AUTH'} eq 'on'))
            {
                if ($proxysettings{'NTLM_ENABLE_ACL'} eq 'on')
                {
                    if (($proxysettings{'NTLM_USER_ACL'} eq 'positive') && (!-z "$ntlmdir/msntauth.allowusers"))
                    {
                        print FILE " for_acl_users";
                    }
                    if (($proxysettings{'NTLM_USER_ACL'} eq 'negative') && (!-z "$ntlmdir/msntauth.denyusers"))
                    {
                        print FILE " !for_acl_users";
                    }
                } else { print FILE " for_inetusers"; }
            }
            if (($proxysettings{'AUTH_METHOD'} eq 'radius') && ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on'))
            {
                if ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on')
                {
                    if (($proxysettings{'RADIUS_USER_ACL'} eq 'positive') && (!-z "$raddir/radauth.allowusers"))
                    {
                        print FILE " for_acl_users";
                    }
                    if (($proxysettings{'RADIUS_USER_ACL'} eq 'negative') && (!-z "$raddir/radauth.denyusers"))
                    {
                        print FILE " !for_acl_users";
                    }
                } else { print FILE " for_inetusers"; }
            }
        }
        print FILE "\n";
    }

    if (!-z $acl_src_unrestricted_mac)
    {
        print FILE "http_access allow IPCop_unrestricted_mac";
        if ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'on')
        {
            if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
            {
                if (!-z $disgrp) { print FILE " !for_disabled_users"; } else { print FILE " for_inetusers"; }
            }
            if (($proxysettings{'AUTH_METHOD'} eq 'ldap') || (($proxysettings{'AUTH_METHOD'} eq 'ntlm') && ($proxysettings{'NTLM_ENABLE_INT_AUTH'} eq 'off')) || ($proxysettings{'AUTH_METHOD'} eq 'radius'))
            {
                print FILE " for_inetusers";
            }
            if (($proxysettings{'AUTH_METHOD'} eq 'ntlm') && ($proxysettings{'NTLM_ENABLE_INT_AUTH'} eq 'on'))
            {
                if ($proxysettings{'NTLM_ENABLE_ACL'} eq 'on')
                {
                    if (($proxysettings{'NTLM_USER_ACL'} eq 'positive') && (!-z "$ntlmdir/msntauth.allowusers"))
                    {
                        print FILE " for_acl_users";
                    }
                    if (($proxysettings{'NTLM_USER_ACL'} eq 'negative') && (!-z "$ntlmdir/msntauth.denyusers"))
                    {
                        print FILE " !for_acl_users";
                    }
                } else { print FILE " for_inetusers"; }
            }
            if (($proxysettings{'AUTH_METHOD'} eq 'radius') && ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on'))
            {
                if ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on')
                {
                    if (($proxysettings{'RADIUS_USER_ACL'} eq 'positive') && (!-z "$raddir/radauth.allowusers"))
                    {
                        print FILE " for_acl_users";
                    }
                    if (($proxysettings{'RADIUS_USER_ACL'} eq 'negative') && (!-z "$raddir/radauth.denyusers"))
                    {
                        print FILE " !for_acl_users";
                    }
                } else { print FILE " for_inetusers"; }
            }
        }
        print FILE "\n";
    }

    if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
    {
        if (!-z $disgrp) { print FILE "http_access deny  for_disabled_users\n"; }
        if (!-z $extgrp) { print FILE "http_access allow IPCop_networks for_extended_users\n"; }
    }

    if (
        (
         ($proxysettings{'AUTH_METHOD'} eq 'ntlm') &&
         ($proxysettings{'NTLM_ENABLE_INT_AUTH'} eq 'on') &&
         ($proxysettings{'NTLM_ENABLE_ACL'} eq 'on') &&
         ($proxysettings{'NTLM_USER_ACL'} eq 'negative') &&
         (!-z "$ntlmdir/msntauth.denyusers")
        )
        ||
        (
         ($proxysettings{'AUTH_METHOD'} eq 'radius') &&
         ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on') &&
         ($proxysettings{'RADIUS_USER_ACL'} eq 'negative') &&
         (!-z "$raddir/radauth.denyusers")
        )
        ||
        (
         ($proxysettings{'AUTH_METHOD'} eq 'ident') &&
         ($proxysettings{'AUTH_ALWAYS_REQUIRED'} eq 'off') &&
         ($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') &&
         ($proxysettings{'IDENT_USER_ACL'} eq 'negative') &&
         (!-z "$identdir/identauth.denyusers")
        )
       )
    {
        print FILE "http_access deny  for_acl_users";
        if (($proxysettings{'AUTH_METHOD'} eq 'ident') && (!-z "$identdir/hosts")) { print FILE " on_ident_aware_hosts"; }
        print FILE "\n";
    }

    if (($proxysettings{'AUTH_METHOD'} eq 'ident') && ($proxysettings{'IDENT_REQUIRED'} eq 'on') && (!-z "$identhosts"))
    {
        print FILE "http_access allow";
        if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
            print FILE " !within_timeframe";
        } else {
            print FILE " within_timeframe"; }
        if ($proxysettings{'ENABLE_BROWSER_CHECK'} eq 'on') { print FILE " with_allowed_useragents"; }
        print FILE " !on_ident_aware_hosts\n";
    }

    print FILE "http_access allow IPCop_networks";
    if (
        (
         ($proxysettings{'AUTH_METHOD'} eq 'ntlm') &&
         ($proxysettings{'NTLM_ENABLE_INT_AUTH'} eq 'on') &&
         ($proxysettings{'NTLM_ENABLE_ACL'} eq 'on') &&
         ($proxysettings{'NTLM_USER_ACL'} eq 'positive') &&
         (!-z "$ntlmdir/msntauth.allowusers")
        )
        ||
        (
         ($proxysettings{'AUTH_METHOD'} eq 'radius') &&
         ($proxysettings{'RADIUS_ENABLE_ACL'} eq 'on') &&
         ($proxysettings{'RADIUS_USER_ACL'} eq 'positive') &&
         (!-z "$raddir/radauth.allowusers")
        )
        ||
        (
         ($proxysettings{'AUTH_METHOD'} eq 'ident') &&
         ($proxysettings{'IDENT_REQUIRED'} eq 'on') &&
         ($proxysettings{'IDENT_ENABLE_ACL'} eq 'on') &&
         ($proxysettings{'IDENT_USER_ACL'} eq 'positive') &&
         (!-z "$identdir/identauth.allowusers")
        )
       )
    {
        print FILE " for_acl_users";
    } elsif (((!($proxysettings{'AUTH_METHOD'} eq 'none')) && (!($proxysettings{'AUTH_METHOD'} eq 'ident'))) ||
        (($proxysettings{'AUTH_METHOD'} eq 'ident') && ($proxysettings{'IDENT_REQUIRED'} eq 'on'))) {
        print FILE " for_inetusers";
    }
    if ((!($proxysettings{'AUTH_MAX_USERIP'} eq '')) && (!($proxysettings{'AUTH_METHOD'} eq 'none')) && (!($proxysettings{'AUTH_METHOD'} eq 'ident')))
    {
        print FILE " !concurrent";
    }
    if ($proxysettings{'TIME_ACCESS_MODE'} eq 'deny') {
        print FILE " !within_timeframe";
    } else {
        print FILE " within_timeframe"; }
    if ($proxysettings{'ENABLE_BROWSER_CHECK'} eq 'on') { print FILE " with_allowed_useragents"; }
    print FILE "\n";

    print FILE "http_access deny  all\n\n";

    if (($proxysettings{'FORWARD_IPADDRESS'} eq 'off') || ($proxysettings{'FORWARD_VIA'} eq 'off') ||
        (!($proxysettings{'FAKE_USERAGENT'} eq '')) || (!($proxysettings{'FAKE_REFERER'} eq '')))
    {
        print FILE "#Strip HTTP Header\n";

        if ($proxysettings{'FORWARD_IPADDRESS'} eq 'off')
        {
            print FILE "request_header_access X-Forwarded-For deny all\n";
        }
        if ($proxysettings{'FORWARD_VIA'} eq 'off')
        {
            print FILE "request_header_access Via deny all\n";
        }
        if (!($proxysettings{'FAKE_USERAGENT'} eq ''))
        {
            print FILE "request_header_access User-Agent deny all\n";
        }
        if (!($proxysettings{'FAKE_REFERER'} eq ''))
        {
            print FILE "request_header_access Referer deny all\n";
        }

        print FILE "\n";

        if ((!($proxysettings{'FAKE_USERAGENT'} eq '')) || (!($proxysettings{'FAKE_REFERER'} eq '')))
        {
            if (!($proxysettings{'FAKE_USERAGENT'} eq ''))
            {
                print FILE "header_replace User-Agent $proxysettings{'FAKE_USERAGENT'}\n";
            }
            if (!($proxysettings{'FAKE_REFERER'} eq ''))
            {
                print FILE "header_replace Referer $proxysettings{'FAKE_REFERER'}\n";
            }
            print FILE "\n";
        }
    }

    if ($proxysettings{'SUPPRESS_VERSION'} eq 'on') { print FILE "httpd_suppress_version_string on\n\n" }

    if ((!-z $mimetypes) && ($proxysettings{'ENABLE_MIME_FILTER'} eq 'on')) {
        if (!-z $acl_src_unrestricted_ip)  { print FILE "http_reply_access allow IPCop_unrestricted_ips\n"; }
        if (!-z $acl_src_unrestricted_mac) { print FILE "http_reply_access allow IPCop_unrestricted_mac\n"; }
        if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
        {
            if (!-z $extgrp) { print FILE "http_reply_access allow for_extended_users\n"; }
        }
        if (!-z $acl_dst_mime_exceptions_dom) { print FILE "http_reply_access allow mime_exception_domains\n"; }
        if (!-z $acl_dst_mime_exceptions_net) { print FILE "http_reply_access allow mime_exception_ipaddr\n"; }
        if (!-z $acl_dst_mime_exceptions_url) { print FILE "http_reply_access allow mime_exception_hosts\n"; }
        print FILE "http_reply_access deny  blocked_mimetypes\n";
        print FILE "http_reply_access allow all\n\n";
    }

    if (($proxysettings{'CACHE_SIZE'} > 0) || ($proxysettings{'CACHE_MEM'} > 0)) {
        print FILE <<END
maximum_object_size $proxysettings{'MAX_SIZE'} KB
minimum_object_size $proxysettings{'MIN_SIZE'} KB

END
        ;
    } 
    else { 
        print FILE "cache deny all\n\n";
    }

    print FILE <<END
request_body_max_size $proxysettings{'MAX_OUTGOING_SIZE'} KB
END
    ;
    $replybodymaxsize = "$proxysettings{'MAX_INCOMING_SIZE'} KB";
    if ($proxysettings{'MAX_INCOMING_SIZE'} > 0) {
        if (!-z $acl_src_unrestricted_ip) { print FILE "reply_body_max_size none IPCop_unrestricted_ips\n"; }
        if (!-z $acl_src_unrestricted_mac) { print FILE "reply_body_max_size none IPCop_unrestricted_mac\n"; }
        if ($proxysettings{'AUTH_METHOD'} eq 'ncsa')
        {
            if (!-z $extgrp) { print FILE "reply_body_max_size none for_extended_users\n"; }
        }
    }
    if ($replybodymaxsize == 0) { $replybodymaxsize = 'none'; }
    print FILE "reply_body_max_size $replybodymaxsize all\n\n";

    print FILE "visible_hostname";
    if ($proxysettings{'VISIBLE_HOSTNAME'} eq '')
    {
        print FILE " $mainsettings{'HOSTNAME'}.$mainsettings{'DOMAINNAME'}\n\n";
    } else {
        print FILE " $proxysettings{'VISIBLE_HOSTNAME'}\n\n";
    }

    if (!($proxysettings{'ADMIN_MAIL_ADDRESS'} eq '')) { print FILE "cache_mgr $proxysettings{'ADMIN_MAIL_ADDRESS'}\n\n"; }

    # Write the parent proxy info, if needed.
    if ($remotehost ne '')
    {
        print FILE "cache_peer $remotehost parent $remoteport 3130 default no-query";

        # Enter authentication for the parent cache. Option format is
        # login=user:password   ($proxy1='YES')
        # login=PASS            ($proxy1='PASS')
        # login=*:password      ($proxysettings{'FORWARD_USERNAME'} eq 'on')
        if (($proxy1 eq 'YES') || ($proxy1 eq 'PASS'))
        {
            print FILE " login=$proxysettings{'UPSTREAM_USER'}";
            if ($proxy1 eq 'YES') { print FILE ":$proxysettings{'UPSTREAM_PASSWORD'}"; }
        }
        elsif ($proxysettings{'FORWARD_USERNAME'} eq 'on') { print FILE " login=*:password"; }

        print FILE "\nalways_direct allow IPCop_ips\n";
        print FILE "never_direct  allow all\n\n";
    }
    if (($urlfilter_addon) && ($updaccel_addon) && ($proxysettings{'ENABLE_FILTER'} eq 'on') && ($proxysettings{'ENABLE_UPDXLRATOR'} eq 'on'))
    {
        print FILE "url_rewrite_program /usr/sbin/redirect_wrapper\n";
        if ($filtersettings{'CHILDREN'} > $updaccelsettings{'CHILDREN'})
        {
            print FILE "url_rewrite_children $filtersettings{'CHILDREN'}\n\n";
        } else {
            print FILE "url_rewrite_children $updaccelsettings{'CHILDREN'}\n\n";
        }
    } else
    {
        if ($urlfilter_addon) {
            if ($proxysettings{'ENABLE_FILTER'} eq 'on')
            {
                print FILE <<END
url_rewrite_program /usr/bin/squidGuard
url_rewrite_children $filtersettings{'CHILDREN'}

END
                ;
            }
        }
        if ($updaccel_addon) {
            if ($proxysettings{'ENABLE_UPDXLRATOR'} eq 'on')
            {
                print FILE <<END
url_rewrite_program /usr/sbin/updxlrator
url_rewrite_children $updaccelsettings{'CHILDREN'}

END
                ;
            }
        }
    }
    close FILE;
}

# -------------------------------------------------------------------

sub adduser
{
    my ($str_user, $str_pass, $str_group) = @_;
    my @groupmembers=();

    if ($str_pass eq 'lEaVeAlOnE')
    {
        open(FILE, "$userdb");
        @groupmembers = <FILE>;
        close(FILE);
        foreach $line (@groupmembers) {	if ($line =~ /^$str_user:/i) { $str_pass = substr($line,index($line,":")); } }
        &deluser($str_user);
        open(FILE, ">>$userdb");
        flock FILE,2;
        print FILE "$str_user$str_pass";
        close(FILE);
    } else {
        &deluser($str_user);
        system("/usr/sbin/htpasswd -b $userdb $str_user $str_pass");
    }

    if ($str_group eq 'standard') { open(FILE, ">>$stdgrp");
    } elsif ($str_group eq 'extended') { open(FILE, ">>$extgrp");
    } elsif ($str_group eq 'disabled') { open(FILE, ">>$disgrp"); }
    flock FILE, 2;
    print FILE "$str_user\n";
    close(FILE);

    return;
}

# -------------------------------------------------------------------

sub deluser
{
    my ($str_user) = @_;
    my $groupfile='';
    my @groupmembers=();
    my @templist=();

    foreach $groupfile ($stdgrp, $extgrp, $disgrp)
    {
        undef @templist;
        open(FILE, "$groupfile");
        @groupmembers = <FILE>;
        close(FILE);
        foreach $line (@groupmembers) { if (!($line =~ /^$str_user$/i)) { push(@templist, $line); } }
        open(FILE, ">$groupfile");
        flock FILE, 2;
        print FILE @templist;
        close(FILE);
    }

    undef @templist;
    open(FILE, "$userdb");
    @groupmembers = <FILE>;
    close(FILE);
    foreach $line (@groupmembers) { if (!($line =~ /^$str_user:/i)) { push(@templist, $line); } }
    open(FILE, ">$userdb");
    flock FILE, 2;
    print FILE @templist;
    close(FILE);

    return;
}

# -------------------------------------------------------------------
