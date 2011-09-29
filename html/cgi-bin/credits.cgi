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
# along with IPCop.  If not, see <http://www.gnu.org/licenses/>.
#
# (c) The SmoothWall Team
# Copyright (c) 2001-2011 The IPCop Team
#
# $Id: credits.cgi 5859 2011-09-21 05:05:40Z owes $
#

# Add entry in menu
# MENUENTRY system 100 "credits" "credits"

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/usr/lib/ipcop/general-functions.pl';
require '/usr/lib/ipcop/lang.pl';
require '/usr/lib/ipcop/header.pl';

&Header::showhttpheaders();

&Header::openpage($Lang::tr{'credits'}, 1, '');

&Header::openbigbox('100%', 'left');

&Header::openbox('100%', 'left', $Lang::tr{'credits'});

print <<END

<table width='100%'>
<tr>
    <td align='left' width='20%'><img src='/ipcop_small.gif' alt=''/></td>
    <td align='center' width='60%'><b><span style='font-size:14px'>IPCop - The Bad Packets Stop Here</span><br />
    <br />Visit us at <a href='http://www.ipcop.org/' target='_blank'>www.ipcop.org</a></b></td>
    <td align='left' width='20%'>&nbsp;</td>
</tr>
</table>
<hr />
<p><b>Main credits</b><br />
Release coordinator - Olaf Westrik
(<a href='mailto:'>&nbsp;</a>)<br />
Developer - Achim Weber
(<a href='mailto:'>&nbsp;</a>)<br />
Developer - Alan Hourihane
(<a href='mailto:alanh\@fairlite.demon.co.uk'>alanh\@fairlite.demon.co.uk</a>)<br />
Developer - Eric Oberlander
(<a href='mailto:eric\@oberlander.co.uk'>eric\@oberlander.co.uk</a>)<br />
Developer - Gilles Espinasse
(<a href='mailto:g.esp.ipcop\@free.fr'>g.esp.ipcop\@free.fr</a>)<br />
Developer - Ivan Kabaivanov
(<a href='mailto:'>&nbsp;</a>)<br />
Developer - Marco Sondermann
(<a href='mailto:'>&nbsp;</a>)<br />
Developer - Mark Wormgoor
(<a href='mailto:mark\@wormgoor.com'>mark\@wormgoor.com</a>)<br />
Developer - Robert Kerr
(<a href='mailto:LittleThor\@xsw.terminator.net'>LittleThor\@xsw.terminator.net</a>)<br />
Developer - Ufuk Altinkaynak
(<a href='mailto:'>&nbsp;</a>)<br />
Graphics - Seth Bareiss
(<a href='mailto:seth\@fureai-ch.ne.jp'>seth\@fureai-ch.ne.jp</a>)<br />
Graphics - Tom Eichstaedt
(<a href='mailto:info\@ipadd.de'>info\@ipadd.de</a>)<br />
</p>

<p><b>IPCop 1.x developers</b><br />
Project Member - Mark Wormgoor
(<a href='mailto:mark\@wormgoor.com'>mark\@wormgoor.com</a>)<br />
Project Member &amp; Configuration backup/restore - Eric S. Johansson
(<a href='mailto:esj\@harvee.billerica.ma.us'>esj\@harvee.billerica.ma.us</a>)<br />
Project Member - Jack Beglinger
(<a href='mailto:jackb_guppy\@yahoo.com'>jackb_guppy\@yahoo.com</a>)<br />
Developer - Darren Critchley
(<a href='mailto:darrenc\@telus.net'>darrenc\@telus.net</a>)<br />
Developer - Robert Kerr
(<a href='mailto:LittleThor\@xsw.terminator.net'>LittleThor\@xsw.terminator.net</a>)<br />
Developer - Alan Hourihane
(<a href='mailto:alanh\@fairlite.demon.co.uk'>alanh\@fairlite.demon.co.uk</a>)<br />
Release coordinator - Gilles Espinasse
(<a href='mailto:g.esp.ipcop\@free.fr'>g.esp.ipcop\@free.fr</a>)<br />
Perl Developer - Franck Bourdonnec
(<a href='mailto:fbourdonnec\@chez.com'>fbourdonnec\@chez.com</a>)<br />
Testing - Dave Roberts
(<a href='mailto:dave\@daver.demon.co.uk'>dave\@daver.demon.co.uk</a>)<br />
Website Design + Graphics - Seth Bareiss
(<a href='mailto:seth\@fureai-ch.ne.jp'>seth\@fureai-ch.ne.jp</a>)<br />
Documentation - Harry Goldschmitt
(<a href='mailto:harry\@hgac.com'>harry\@hgac.com</a>)<br />
Red IP Aliasing - Steve Bootes
(<a href='mailto:Steve\@computingdynamics.co.uk'>Steve\@computingdynamics.co.uk</a>)<br />
Static DHCP Addresses - Graham Smith
(<a href='mailto:grhm\@grhm.co.uk'>grhm\@grhm.co.uk</a>)<br />
Squid graphs - Robert Wood
(<a href='rob\@empathymp3.co.uk'>rob\@empathymp3.co.uk</a>)<br />
Time Synchronization - Eric Oberlander
(<a href='mailto:eric\@oberlander.co.uk'>eric\@oberlander.co.uk</a>)<br />
Backup - Tim Butterfield
(<a href='mailto:timbutterfield\@mindspring.com'>timbutterfield\@mindspring.com</a>)<br />
DOV Support and Improved Dual ISDN Support - Traverse Technologies
(<a href='http://www.traverse.com.au/'>http://www.traverse.com.au/</a>)<br />
Traffic Shaping - David Kilpatrick
(<a href='mailto:dave\@thunder.com.au'>dave\@thunder.com.au</a>)<br />
Improved VPN Documentation - Christiaan Theron
(<a href='mailto:christiaan.theron\@virgin.net'>christiaan.theron\@virgin.net</a>)<br />
</p>

<p><b>Translations</b><br />
Eric Oberlander - Translation Coordinator
(<a href='mailto:eric\@oberlander.co.uk'>eric\@oberlander.co.uk</a>)<br />
Marco van Beek - Website Translation Database Developer
(<a href='mailto:mvanbeek\@supporting-role.co.uk'>mvanbeek\@supporting-role.co.uk</a>)<br />
Afrikaans:<br />
&nbsp; Johann du Preez<br />
Arabic:<br />
&nbsp; Ghalia Saleh Shariha
(<a href='mailto:ghalia2050\@yahoo.com'>ghalia2050\@yahoo.com</a>)<br />
&nbsp; Salma Mahmod Ashour
(<a href='mailto:salma1100\@yahoo.com'>salma1100\@yahoo.com</a>)<br />
Bulgarian<br />
&nbsp; Alexander Dimitrov
(<a href='mailto:alexander\@avdesigngroup.org'>alexander\@avdesigngroup.org</a>)<br />
Brazilian Portuguese:<br />
&nbsp; Edson-Empresa
(<a href='mailto:soma2\@somainformatica.com.br'>soma2\@somainformatica.com.br</a>)<br />
&nbsp; Claudio Corr&ecirc;a Porto
(<a href='mailto:claudio\@tsasp.com.br'>claudio\@tsasp.com.br</a>)<br />
&nbsp; Adilson Oliveira
(<a href='mailto:adilson\@linuxembarcado.com.br'>adilson\@linuxembarcado.com.br</a>)<br />
&nbsp; Mauricio Andrade
(<a href='mailto:mandrade\@mma.com.br'>mandrade\@mma.com.br</a>)<br />
&nbsp; Wladimir Nunes
(<a href='mailto:wnunes\@treesystems.com.br'>wnunes\@treesystems.com.br</a>)<br />
Catalan:<br />
&nbsp; Albert Ferran Casas<br />
&nbsp; Sergi Valls<br />
&nbsp; Josep Sanchez<br />
&nbsp; Toni
(<a href='mailto:devegades\@gmail.com'>devegades\@gmail.com</a>)<br />
Chinese (Simplified):<br />
&nbsp; Vince Chu
(<a href='mailto:chuhei\@beunion.net'>chuhei\@beunion.net</a>)<br />
&nbsp; Yuan-Chen Cheng
(<a href='mailto:ycheng\@wiscore.com'>ycheng\@wiscore.com</a>)<br />
&nbsp; Sohoguard
(<a href='mailto:sohoguard\@hotmail.com'>sohoguard\@hotmail.com</a>)<br />
Chinese (Traditional):<br />
&nbsp; Ronald Ng
(<a href='mailto:mwpmo\@hotmail.com'>mwpmo\@hotmail.com</a>)<br />
Czech:<br />
&nbsp; Petr Dvoracek
(<a href='mailto:mandrake\@tiscali.cz'>mandrake\@tiscali.cz</a>)<br />
&nbsp; Jakub Moc
(<a href='mailto:Jakub.Moc\@seznam.cz'>Jakub.Moc\@seznam.cz</a>)<br />
Danish:<br />
&nbsp; Michael Rasmussen
(<a href='mailto:mir\@datanom.net'>mir\@datanom.net</a>)<br />
&nbsp; Daniel Hammer
<br />
&nbsp; Morten Christensen
(m(dot)c(at)c(dot)dk)<br />
Dutch:<br />
&nbsp; Gerard Zwart
(<a href='mailto:zwartg\@home.nl'>zwartg\@home.nl</a>)<br />
&nbsp; Berdt van der Lingen
(<a href='mailto:berdt\@xs4all.nl'>berdt\@xs4all.nl</a>)<br />
&nbsp; Tony Vroon
(<a href='mailto:mrchainsaw\@users.sourceforge.net'>mrchainsaw\@users.sourceforge.net</a>)<br />
&nbsp; Mark Wormgoor<br />
&nbsp; Maikel Punie
(<a href='mailto:maikel.punie\@gmail.com'>maikel.punie\@gmail.com</a>)<br />
&nbsp; Bjorn Kaag<br />
English:<br />
&nbsp; Jack Beglinger
(<a href='mailto:jackb_guppy\@yahoo.com'>jackb_guppy\@yahoo.com</a>)<br />
&nbsp; James Brice
(<a href='mailto:jbrice\@jamesbrice.com'>jbrice\@jamesbrice.com</a><br />
&nbsp; Tim Butterfield
(<a href='mailto:timbutterfield\@mindspring.com'>timbutterfield\@mindspring.com</a>)<br />
&nbsp; Chris Clancey
(<a href='mailto:chrisjc\@amoose.com'>chrisjc\@amoose.com</a>)<br />
&nbsp; Harry Goldschmitt
(<a href='mailto:harry\@hgac.com'>harry\@hgac.com</a>)<br />
&nbsp; John Kastner
(<a href='mailto:john\@kastner.us'>john\@kastner.us</a>)<br />
&nbsp; Eric Oberlander
(<a href='mailto:eric\@oberlander.co.uk'>eric\@oberlander.co.uk</a>)<br />
&nbsp; Stephen Pielschmidt
(<a href='mailto:stephen.pielschmidt\@sfp.com.au'>stephen.pielschmidt\@sfp.com.au</a>)<br />
&nbsp; Peter Walker
(<a href='mailto:peter.walker\@stockfast.co.uk'>peter.walker\@stockfast.co.uk</a>)<br />
Finnish:<br />
&nbsp; Kai Käpölä
(<a href='mailto:kai\@kapola.fi'>kai\@kapola.fi</a>)<br />
&nbsp; Tapani Tarvainen
<br />
French:<br />
&nbsp; Bertrand Sarthre
(<a href='mailto:zetrebu\@softhome.net'>zetrebu\@softhome.net</a>)<br />
&nbsp; Michel Janssens
(<a href='mailto:micj\@ixus.net'>micj\@ixus.net</a>)<br />
&nbsp; Erwann Simon
(<a href='mailto:esn\@infobi.com'>esn\@infobi.com</a>) (<a href='mailto:wann\@ixus.net'>wann\@ixus.net</a>)<br />
&nbsp; Patrick Bernaud
(<a href='mailto:patrickbernaud\@users.sourceforge.net'>patrickbernaud\@users.sourceforge.net</a>)<br />
&nbsp; Marc Faid\'herbe
(<a href='mailto:marc\@decad.fr'>marc\@decad.fr</a>)<br />
&nbsp; Eric Legigan
(<a href='mailto:eric.legigan\@wanadoo.fr'>eric.legigan\@wanadoo.fr</a>)<br />
&nbsp; Eric Berthomier
(<a href='mailto:ebr\@infobi.com'>ebr\@infobi.com</a>)<br />
&nbsp; Stéphane Le Bourdon
(<a href='mailto:stephane.lebourdon\@free.fr'>stephane.lebourdon\@free.fr</a>)<br />
&nbsp; Stéphane Thirion
(<a href='mailto:sthirion\@activlan.com'>sthirion\@activlan.com</a>)<br />
&nbsp; Jan M. Dziewulski
(<a href='mailto:jan\@dziewulski.com'>jan\@dziewulski.com</a>)<br />
&nbsp;
(<a href='mailto:spoutnik\@inbox.lv'>spoutnik\@inbox.lv</a>)<br />
&nbsp; Eric
(<a href='mailto:darriak\@users.sourceforge.net'>darriak\@users.sourceforge.net</a>)<br />
&nbsp; Eric Boniface
(<a href='mailto:ericboniface\@chez.com'>ericboniface\@chez.com</a>)<br />
&nbsp; Franck Bourdonnec
(<a href='mailto:fbourdonnec\@chez.com'>fbourdonnec\@chez.com</a>)<br />
&nbsp; Jean Pierre Bargheon
<br />
&nbsp; Guy Godin
<br />
&nbsp; Rodeus AKA Neosys
<br />
German:<br />
&nbsp; Dirk Loss
(<a href='mailto:dloss\@uni-muenster.de'>dloss\@uni-muenster.de</a>)<br />
&nbsp; Ludwig Steininger
(<a href='mailto:antispam1eastcomp\@gmx.de'>antispam1eastcomp\@gmx.de</a>)<br />
&nbsp; Helmet
(<a href='mailto:list\@metatalk.de'>list\@metatalk.de</a>)<br />
&nbsp; Markus
(<a href='mailto:mstl\@gmx.de'>mstl\@gmx.de</a>)<br />
&nbsp; Michael Knappe
(<a href='mailto:michael.knappe\@chello.at'>michael.knappe\@chello.at</a>)<br />
&nbsp; Michael Linke
(<a href='mailto:linke\@netmedia.de'>linke\@netmedia.de</a>)<br />
&nbsp; Richard Hartmann
(<a href='mailto:linux\@smhsoftware.de'>linux\@smhsoftware.de</a>)<br />
&nbsp; Gerhard Abrahams
(<a href='mailto:g.abrahams\@gmx.de'>g.abrahams\@gmx.de</a>)<br />
&nbsp; Benjamin Kohberg
(<a href='mailto:b.kohberg\@pci-software.de'>b.kohberg\@pci-software.de</a>)<br />
&nbsp; Samuel Wiktor
(<a href='mailto:samuel.wiktor\@stud.tu-ilmenau.de'>samuel.wiktor\@stud.tu-ilmenau.de</a>)<br />
&nbsp; Tom Eichstaedt
(<a href='mailto:info\@ipadd.de'>info\@ipadd.de</a>)<br />
Greek:<br />
&nbsp; Spyros Tsiolis
(<a href='mailto:info\@abaxb2b.com'>info\@abaxb2b.com</a>)<br />
&nbsp; A. Papageorgiou
(<a href='mailto:apap\@freemail.gr'>apap\@freemail.gr</a>)<br />
&nbsp; G. Xrysostomou
(<a href='mailto:gxry\@freemail.gr'>gxry\@freemail.gr</a>)<br />
Gujarati:<br />
&nbsp; Kartik Mistry
(<a href='mailto:kartik.mistry\@gmail.com'>kartik.mistry\@gmail.com</a>)<br />
Hungarian:<br />
&nbsp; Ádám Makovecz
(<a href='mailto:adam\@makovecz.hu'>adam\@makovecz.hu</a>)<br />
&nbsp; Ferenc Mányi-Szabó
(<a href='mailto:asd1234\@freemail.hu'>asd1234\@freemail.hu</a>)<br />
Italian:<br />
&nbsp; Fabio Gava
(<a href='mailto:fabio.gava\@bloomtech.it'>fabio.gava\@bloomtech.it</a>)<br />
&nbsp; Antonio Stano
(<a href='mailto:admin\@securityinfos.com'>admin\@securityinfos.com</a>)<br />
&nbsp; Marco Spreafico
(<a href='mailto:marco\@yetopen.it'>marco\@yetopen.it</a>)<br />
&nbsp; Alessio Cecchi
<br />
&nbsp; Gabrielle Bellini
<br />
&nbsp; Massimiliano Neri
(<a href='mailto:xantas\@hotmail.it'>xantas\@hotmail.it</a>)<br />
Japanese:<br />
&nbsp; Adam Barbary
<br />
&nbsp; Raina Otoni
<br />
Lithuanian:<br />
&nbsp; Aurimas Fišeras
(<a href='mailto:aurimas\@gmail.com'>aurimas\@gmail.com</a>)<br />
&nbsp; Rodion Kotelnikov
(<a href='mailto:r0dik\@takas.lt'>r0dik\@takas.lt</a>)<br />
Norwegian:<br />
&nbsp; Morten Grendal
(<a href='mailto:morten\@grendal.no'>morten\@grendal.no</a>)<br />
&nbsp; Alexander Dawson
(<a href='mailto:daftkid\@users.sourceforge.net'>daftkid\@users.sourceforge.net</a>)<br />
&nbsp; Mounir S. Chermiti
(<a href='mailto:mounir\@solidonline.org'>mounir\@solidonline.org</a>)<br />
&nbsp; Runar Skraastad
(<a href='mailto:rus-\@home.no'>rus-\@home.no</a>)<br />
&nbsp; Alf-Ivar Holm
(<a href='mailto:alfh\@ifi.uio.no'>alfh\@ifi.uio.no</a>)<br />
Persian (Farsi):<br />
&nbsp; Ali Tajik
(<a href='mailto:trosec113\@gmail.com'>trosec113\@gmail.com</a>)<br />
&nbsp; A T Khalilian<br />
Polish:<br />
&nbsp; Jack Korzeniowski
(<a href='mailto:jk2002\@mail.com'>jk2002\@mail.com</a>)<br />
&nbsp; Piotr
(<a href='mailto:piotr\@esse.pl'>piotr\@esse.pl</a>)<br />
&nbsp; Andrzej Zolnierowicz
(<a href='mailto:zolnierowicz\@users.sourceforge.net'>zolnierowicz\@users.sourceforge.net</a>)<br />
&nbsp; Remi Schleicher
(remi(dot)schleicher(at)phreaker(dot)net)<br />
Portuguese:<br />
&nbsp; Luis Santos
(<a href='mailto:luis\@ciclo2000.com'>luis\@ciclo2000.com</a>)<br />
&nbsp; Renato Kenji Kano
(<a href='mailto:renato_kenji\@users.sourceforge.net'>renato_kenji\@users.sourceforge.net</a>)<br />
&nbsp; Mark Peter
(<a href='mailto:mark\@markpeter.com'>mark\@markpeter.com</a>)<br />
&nbsp; Wladimir Nunes
(<a href='mailto:wnunes\@users.sourceforge.net'>wnunes\@users.sourceforge.net</a>)<br />
&nbsp; Daniela Cattarossi
(<a href='mailto:daniela\@netpandora.com'>daniela\@netpandora.com</a>)<br />
Romanian:<br />
&nbsp; Viorel Melinte
(<a href='mailto:viorel.melinte\@hidro.ro'>viorel.melinte\@hidro.ro</a>)<br />
Russian/Ukranian:<br />
&nbsp; Vladimir Grichina
(<a href='mailto:vgua\@users.sourceforge.net'>vgua\@users.sourceforge.net</a>)<br />
&nbsp; Vitaly Tarasov
(<a href='mailto:vtarasov\@knoa.com'>vtarasov\@knoa.com</a>)<br />
&nbsp; Rodion Kotelnikov
(<a href='mailto:r0dik\@takas.lt'>r0dik\@takas.lt</a>)<br />
&nbsp; Nikolay Parukhin
<br />
Slovak:<br />
&nbsp; Miloš Mráz
(<a href='mailto:Milos.Mraz\@svum.sk'>Milos.Mraz\@svum.sk</a>)<br />
&nbsp; Drlik Zbynek
(<a href='mailto:denix\@host.sk'>denix\@host.sk</a>)<br />
Slovenian:<br />
&nbsp; Miha Martinec
(<a href='mailto:miha\@martinec.si'>miha\@martinec.si</a>)<br />
&nbsp; Grega Varl
(<a href='mailto:gregav\@finea-holding.si'>gregav\@finea-holding.si</a>)<br />
Somali:<br />
&nbsp; Arnt Karlsen
(<a href='mailto:arnt\@c2i.net'>arnt\@c2i.net</a>)<br />
&nbsp; Mohamed Musa Ali
(<a href='mailto:alimuse\@hotmail.com'>alimuse\@hotmail.com</a>)<br />
&nbsp; Michael Spann
(<a href='mailto:dr-ms\@lycos.de'>dr-ms\@lycos.de</a>)<br />
Spanish:<br />
&nbsp; Curtis Anderson
(<a href='mailto:curtis_anderson\@curtisanderson.com'>curtis_anderson\@curtisanderson.com</a>)<br />
&nbsp; Diego Lombardia
(<a href='mailto:Diego.Lombardia\@IT-Plus.com.ar'>Diego.Lombardia\@IT-Plus.com.ar</a>)<br />
&nbsp; Mark Peter
(<a href='mailto:mark\@markpeter.com'>mark\@markpeter.com</a>)<br />
&nbsp; QuiQue Soriano
(<a href='mailto:jqsoriano\@hotmail.com'>jqsoriano\@hotmail.com</a>)<br />
&nbsp; David Cabrera Lozano
(<a href='mailto:silews\@users.sourceforge.net'>silews\@users.sourceforge.net</a>)<br />
&nbsp; Jose Sanchez
(<a href='mailto:jsanchez\@cyberdude.com'>jsanchez\@cyberdude.com</a>)<br />
&nbsp; Santiago Cassina
(<a href='mailto:scap2000\@yahoo.com'>scap2000\@yahoo.com</a>)<br />
&nbsp; Marcelo Zunino
(<a href='mailto:cezuni\@adinet.com.uy'>cezuni\@adinet.com.uy</a>)<br />
&nbsp; Alfredo Matignon
(<a href='mailto:amatignon\@softhome.net'>amatignon\@softhome.net</a>)<br />
&nbsp; Juan Janczuk
(<a href='mailto:jjanzcuk\@msn.com'>jjanzcuk\@msn.com</a>)<br />
&nbsp; Vicente Javier Garcia Mayen
(neofito(at)gmail(dot)com)<br />
&nbsp; Ricardo Lopez
<br />
&nbsp; Enrique Porta
<br />
&nbsp; Delfin
<br />
Spanish Latino:<br />
&nbsp; Fernando Díaz
(<a href='mailto:fernando.diaz\@adinet.com.uy'>fernando.diaz\@adinet.com.uy</a>)<br />
Swedish:<br />
&nbsp; Anders Sahlman
(<a href='mailto:anders.sahlman\@dataunit.se'>anders.sahlman\@dataunit.se</a>)<br />
&nbsp; Christer Jonson
(<a href='mailto:christer.jonson\@swipnet.se'>christer.jonson\@swipnet.se</a>)<br />
Thai:<br />
&nbsp; Touchie
(<a href='mailto:pongsathorns\@se-ed.net'>pongsathorns\@se-ed.net</a>)<br />
Turkish:<br />
&nbsp; Ismail Murat Dilek
(<a href='mailto:olive\@zoom.co.uk'>olive\@zoom.co.uk</a>)<br />
&nbsp; Emre Sumengen
<br />
&nbsp; Caglar Ulkuderner
(<a href='mailto:caglar\@profelis.com.tr'>caglar\@profelis.com.tr</a>)<br />
Urdu:<br />
&nbsp; Mudassar Iqbal
(<a href='mailto:mudassar\@arl.com.pk'>mudassar\@arl.com.pk</a>)<br />
Vietnamese:<br />
&nbsp; Le Dinh Long
(<a href='mailto:longld\@yahoo.com'>longld\@yahoo.com</a>)<br />
</p>

<p><b>Linux From Scratch</b><br />
For building IPCop information from the Linux From Scratch (LFS) books is used.
The <a href='http://www.linuxfromscratch.org/index.html'>LFS books</a> are highly
recommended to anyone who wants to get some insight into what makes Linux systems tick.
</p>

<p><b>Smoothwall</b><br />
IPCop is partially based on the <a href='http://www.smoothwall.org'>Smoothwall</a> GPL
version, v0.9.9.  We are grateful to them for both inspiring this product and
giving us the codebase to work with.
</p>
<br />
END
    ;

&Header::closebox();

&Header::closebigbox();

&Header::closepage();
