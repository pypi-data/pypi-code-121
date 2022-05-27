# This file is placed in the Public Domain.


"xml tests"


import unittest


from bot.obj import Object
from bot.rss import Parser


items = "title,description,link,pubDate"


class Config(Object):

    pass

        
class Test_officielebekendmakingen(unittest.TestCase):

    def test_xml(self):
        p = Parser()
        res =  p.parse(txt, items)
        self.assertEqual(len(res), 151)


txt = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
<channel>
<title>Officiële bekendmakingen - RSS feed</title>
<link>https://zoek.officielebekendmakingen.nl/</link>
<description>De nieuwste publicaties van Officiële bekendmakingen.</description>
<language>nl-NL</language>
<copyright>Copyright www.overheid.nl</copyright>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027687.html</link>
<category>Kamerstuk</category>
<title>kst-1027687 : Tweede Kamer der Staten-Generaal</title>
<description>Maatregelen verkeersveiligheid; Brief regering; Stand van zaken verkeersveiligheid</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027738.html</link>
<category>Kamerstuk</category>
<title>kst-1027738 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van de begrotingsstaat van het Ministerie van Onderwijs, Cultuur en Wetenschap (VIII) voor het jaar 2022 (Zesde incidentele suppletoire begroting inzake suppletieregeling cultuur, ventilatie in scholen en Nationaal Programma Onderwijs); Voorstel van wet; Voorstel van wet</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027694.html</link>
<category>Kamerstuk</category>
<title>blg-1027694 : Tweede Kamer der Staten-Generaal</title>
<description>Handhavingsplan vrachtwagenparkeren</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027700.html</link>
<category>Kamerstuk</category>
<title>blg-1027700 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota verzamelbrief verkeersveiligheid</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027688.html</link>
<category>Kamerstuk</category>
<title>blg-1027688 : Tweede Kamer der Staten-Generaal</title>
<description>SWOV rapportage dodelijke verkeersongevallen op rijkswegen in 2020</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027732.html</link>
<category>Kamerstuk</category>
<title>blg-1027732 : Tweede Kamer der Staten-Generaal</title>
<description>Uitvoeringstoets tijdelijke verlaging brandstofaccijnzen CN</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027643.html</link>
<category>Kamerstuk</category>
<title>kst-1027643 : Tweede Kamer der Staten-Generaal</title>
<description>Langdurige zorg; Lijst van vragen en antwoorden; Lijst van vragen en antwoorden over de reactie op verzoek commissie om een juridische analyse openstelling Wlz voor jeugdigen met een psychische stoornis</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027669.html</link>
<category>Kamerstuk</category>
<title>kst-1027669 : Tweede Kamer der Staten-Generaal</title>
<description>Mensenrechten in het buitenlands beleid; Brief regering; Reactie op de moties van de leden Brekelmans, Kuzu, Piri en Jasper van Dijk over afhankelijkheden en mensenrechten</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027695.html</link>
<category>Kamerstuk</category>
<title>blg-1027695 : Tweede Kamer der Staten-Generaal</title>
<description>Verslag Ronde tafel verkeersveiligheid - halvering verkeersslachtoffers 2030</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027701.html</link>
<category>Kamerstuk</category>
<title>blg-1027701 : Tweede Kamer der Staten-Generaal</title>
<description>Afronding Landelijk Actieplan Verkeersveiligheid 2019-2021</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027689.html</link>
<category>Kamerstuk</category>
<title>blg-1027689 : Tweede Kamer der Staten-Generaal</title>
<description>Brief aan GS Overijssel</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027733.html</link>
<category>Kamerstuk</category>
<title>blg-1027733 : Tweede Kamer der Staten-Generaal</title>
<description>Uitvoeringstoets tijdelijke verlaging brandstofaccijnzen NL</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027638.html</link>
<category>Kamerstuk</category>
<title>kst-1027638 : Tweede Kamer der Staten-Generaal</title>
<description>Beroepsonderwijs en Volwassenen Educatie; Verslag van een schriftelijk overleg; Verslag van een schriftelijk overleg over de voorhang van het ontwerpbesluit tot wijziging van het uitvoeringsbesluit WEB , houdende maatstaven voor studiesucces in het mbo</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027670.html</link>
<category>Kamerstuk</category>
<title>blg-1027670 : Tweede Kamer der Staten-Generaal</title>
<description>Basisvragen voor het bepalen van mogelijke risico’s voor publieke belangen</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027708.html</link>
<category>Kamerstuk</category>
<title>kst-1027708 : Tweede Kamer der Staten-Generaal</title>
<description>Informatie- en communicatietechnologie (ICT); Brief regering; Hoofdlijnen beleid voor digitalisering (herdruk)</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027696.html</link>
<category>Kamerstuk</category>
<title>blg-1027696 : Tweede Kamer der Staten-Generaal</title>
<description>Landelijk Actieplan Verkeersveiligheid 2022-2025</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027632.html</link>
<category>Kamerstuk</category>
<title>kst-1027632 : Tweede Kamer der Staten-Generaal</title>
<description>Vaststelling van de begrotingsstaten van het Ministerie van Binnenlandse Zaken en Koninkrijksrelaties (VII) voor het jaar 2022; Brief regering; Eerste appreciatie van de belangrijke opgaven op het gebied van Binnenlandse Zaken en Koninkrijksrelaties (herdruk)</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027734.html</link>
<category>Kamerstuk</category>
<title>blg-1027734 : Tweede Kamer der Staten-Generaal</title>
<description>Uitvoeringstoets tijdelijke verlaging btw op energie</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027690.html</link>
<category>Kamerstuk</category>
<title>blg-1027690 : Tweede Kamer der Staten-Generaal</title>
<description>Notitie TU Delft Vermogen van LEVs</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027728.html</link>
<category>Kamerstuk</category>
<title>kst-1027728 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van enkele belastingwetten (Wet aanvullende fiscale koopkrachtmaatregelen 2022); Koninklijke boodschap; Koninklijke boodschap</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027697.html</link>
<category>Kamerstuk</category>
<title>blg-1027697 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota Integrale aanpak rijden onder invloed</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027633.html</link>
<category>Kamerstuk</category>
<title>kst-1027633 : Tweede Kamer der Staten-Generaal</title>
<description>Vaststelling van de begrotingsstaten van het Ministerie van Volksgezondheid, Welzijn en Sport (XVI) voor het jaar 2022; Brief regering; Planning uitwerking coalitieakkoord op het terrein van het ministerie van Volksgezondheid, Welzijn en Sport (herdruk)</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027646.html</link>
<category>Kamerstuk</category>
<title>kst-1027646 : Tweede Kamer der Staten-Generaal</title>
<description>Nieuwe Commissievoorstellen en initiatieven van de lidstaten van de Europese Unie; Verslag van een schriftelijk overleg; Verslag van een schriftelijk overleg over Fiches inzake voorstellen kapitaalmarktunie (o.a. Kamerstuk 22112-3265)</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027691.html</link>
<category>Kamerstuk</category>
<title>blg-1027691 : Tweede Kamer der Staten-Generaal</title>
<description>Notitie Impactanalyse nationaal toelatingskader Lichte Elektrische Voertuigen</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027729.html</link>
<category>Kamerstuk</category>
<title>kst-1027729 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van enkele belastingwetten (Wet aanvullende fiscale koopkrachtmaatregelen 2022); Voorstel van wet; Voorstel van wet</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027640.html</link>
<category>Kamerstuk</category>
<title>kst-1027640 : Tweede Kamer der Staten-Generaal</title>
<description>Nieuwe Commissievoorstellen en initiatieven van de lidstaten van de Europese Unie; Verslag van een schriftelijk overleg; Verslag van een schriftelijk overleg over het Fiche: Verordening anti-dwang instrument (Kamerstuk 22112-3300)</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027698.html</link>
<category>Kamerstuk</category>
<title>blg-1027698 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota aanpak veelplegers en zware overtreders</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027672.html</link>
<category>Kamerstuk</category>
<title>kst-1027672 : Tweede Kamer der Staten-Generaal</title>
<description>Landbouw- en Visserijraad; Brief regering; Verslag Landbouw- en Visserijraad 7 april 2022</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027634.html</link>
<category>Kamerstuk</category>
<title>kst-1027634 : Tweede Kamer der Staten-Generaal</title>
<description>Vaststelling van de begrotingsstaten van het Ministerie van Binnenlandse Zaken en Koninkrijksrelaties (VII) voor het jaar 2022; Brief regering; Uitstel reactie inzake de informatie- en werkafspraken tussen Tweede Kamer en kabinet</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027736.html</link>
<category>Kamerstuk</category>
<title>blg-1027736 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota's</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027647.html</link>
<category>Kamerstuk</category>
<title>kst-1027647 : Tweede Kamer der Staten-Generaal</title>
<description>Toezichtsverslagen AIVD en MIVD; Overig; Jaarverslag van de Toetsingscommissie Inzet Bevoegdheden (TIB) over de periode 1 januari tot en met 31 december 2021</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027692.html</link>
<category>Kamerstuk</category>
<title>blg-1027692 : Tweede Kamer der Staten-Generaal</title>
<description>Belangrijkste tussenresultaten per actielijn uit het plan Veilige mobiliteit ouderen – ‘Langer Veilig Onderweg’ 2021-2025</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027699.html</link>
<category>Kamerstuk</category>
<title>blg-1027699 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota LEV kader (Lichte Elektrische Voertuigen)</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027730.html</link>
<category>Kamerstuk</category>
<title>kst-1027730 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van enkele belastingwetten (Wet aanvullende fiscale koopkrachtmaatregelen 2022); Memorie van toelichting; Memorie van toelichting</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027737.html</link>
<category>Kamerstuk</category>
<title>kst-1027737 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van enkele belastingwetten (Wet aanvullende fiscale koopkrachtmaatregelen 2022); Advies Afdeling advisering Raad van State en Nader rapport; Advies Afdeling advisering Raad van State en Nader rapport</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027693.html</link>
<category>Kamerstuk</category>
<title>blg-1027693 : Tweede Kamer der Staten-Generaal</title>
<description>Rapportage Evaluatie Wijziging artikel 61a RVV 1990</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027649.html</link>
<category>Kamerstuk</category>
<title>blg-1027649 : Tweede Kamer der Staten-Generaal</title>
<description>Jaarverslag van de Toetsingscommissie Inzet Bevoegdheden (TIB) over de periode 1 januari tot en met 31 december 2021</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027731.html</link>
<category>Kamerstuk</category>
<title>blg-1027731 : Tweede Kamer der Staten-Generaal</title>
<description>Ramingstoelichting bij de Wet aanvullende fiscale koopkrachtmaatregelen 2022</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027636.html</link>
<category>Kamerstuk</category>
<title>kst-1027636 : Tweede Kamer der Staten-Generaal</title>
<description>Regels met betrekking tot de inlichtingen- en veiligheidsdiensten alsmede wijziging van enkele wetten (Wet op de inlichtingen- en veiligheidsdiensten 20..); Brief regering; Impact coalitieakkoord en stand van zaken wijziging Wiv 2017 (Tweede herdruk)</description>
<pubDate>Mon, 02 May 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-35825-15.html</link>
<category>Kamerstuk</category>
<title>kst-35825-15 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van Boek 1 van het Burgerlijk Wetboek in verband met het veranderen van de voorwaarden voor wijziging van de vermelding van het geslacht in de akte van geboorte; Amendement; Amendement van het lid Van der Staaij over het vervangen van het criterium van oprechtheid door duurzaamheid van de overtuiging bij het wijzigen van de vermelding van het geslacht door de rechter</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027586.html</link>
<category>Kamerstuk</category>
<title>blg-1027586 : Tweede Kamer der Staten-Generaal</title>
<description>Onderzoek afstandsnormen windturbines</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027599.html</link>
<category>Kamerstuk</category>
<title>kst-1027599 : Tweede Kamer der Staten-Generaal</title>
<description>Agenda Vitaal Platteland; Brief regering; Onderzoek buitenlandse aankoop landbouwgronden</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027587.html</link>
<category>Kamerstuk</category>
<title>kst-1027587 : Tweede Kamer der Staten-Generaal</title>
<description>Bouwbesluit; Brief regering; Bekendmaking besluit kwaliteitsborging voor het bouwen</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027625.html</link>
<category>Kamerstuk</category>
<title>kst-1027625 : Tweede Kamer der Staten-Generaal</title>
<description>Preventie en bestrijding van stille armoede en sociale uitsluiting; Brief regering; Nationaal Plan Kindergarantie</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027600.html</link>
<category>Kamerstuk</category>
<title>blg-1027600 : Tweede Kamer der Staten-Generaal</title>
<description>Buitenlands eigendom van agrarische grond in Nederland 2016-2021</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027626.html</link>
<category>Kamerstuk</category>
<title>blg-1027626 : Tweede Kamer der Staten-Generaal</title>
<description>Nationaal Plan Kindergarantie</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027601.html</link>
<category>Kamerstuk</category>
<title>kst-1027601 : Tweede Kamer der Staten-Generaal</title>
<description>Vogelpest (Aviaire influenza); Brief regering; Informatie over de vogelgriepsituatie</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027589.html</link>
<category>Kamerstuk</category>
<title>kst-1027589 : Tweede Kamer der Staten-Generaal</title>
<description>Raad voor Vervoer, Telecommunicatie en Energie; Brief regering; Verslag videoteleconferentie (VTC) van EU-transportministers d.d. 8 april 2022</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027596.html</link>
<category>Kamerstuk</category>
<title>kst-1027596 : Tweede Kamer der Staten-Generaal</title>
<description>Kabinetsaanpak Klimaatbeleid; Brief regering; Verkenning Afrekenbare Stoffenbalans</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027621.html</link>
<category>Kamerstuk</category>
<title>kst-1027621 : Tweede Kamer der Staten-Generaal</title>
<description>Zorg en maatschappelijke ondersteuning; Brief regering; Stand van zaken interbestuurlijk toezicht Wmo 2015</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027615.html</link>
<category>Kamerstuk</category>
<title>kst-1027615 : Tweede Kamer der Staten-Generaal</title>
<description>Grondstoffenvoorzieningszekerheid; Brief regering; Beleid uitgebreide producentenverantwoordelijkheid</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027622.html</link>
<category>Kamerstuk</category>
<title>blg-1027622 : Tweede Kamer der Staten-Generaal</title>
<description>Interbestuurlijk toezicht Wmo-verordening</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027603.html</link>
<category>Kamerstuk</category>
<title>kst-1027603 : Tweede Kamer der Staten-Generaal</title>
<description>Evaluatie Schipholbeleid; Brief regering; Voortgang Programma Omgeving Luchthaven Schiphol</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027616.html</link>
<category>Kamerstuk</category>
<title>kst-1027616 : Tweede Kamer der Staten-Generaal</title>
<description>Luchtkwaliteit; Brief regering; Stand van zaken en ontwikkelingen inzake het terugdringen van grootschalige grensoverschrijdende luchtverontreiniging</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-35825-14.html</link>
<category>Kamerstuk</category>
<title>kst-35825-14 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van Boek 1 van het Burgerlijk Wetboek in verband met het veranderen van de voorwaarden voor wijziging van de vermelding van het geslacht in de akte van geboorte; Amendement; Amendement van het lid Van der Staaij over het horen van minderjarigen vanaf 12 jaar door de rechter bij de wijziging van de vermelding van het geslacht van een ouder of voogd</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027623.html</link>
<category>Kamerstuk</category>
<title>blg-1027623 : Tweede Kamer der Staten-Generaal</title>
<description>Interbestuurlijk toezicht</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027585.html</link>
<category>Kamerstuk</category>
<title>kst-1027585 : Tweede Kamer der Staten-Generaal</title>
<description>Structuurvisie Windenergie op land; Brief regering; Onderzoeksrapport afstandsnormen voor windturbines</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027617.html</link>
<category>Kamerstuk</category>
<title>kst-1027617 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van de begrotingsstaat van het Ministerie van Volksgezondheid, Welzijn en Sport (XVI) voor het jaar 2022 (Zesde incidentele suppletoire begroting); Brief regering; 6e incidentele suppletoire begroting 2022 ministerie van VWS</description>
<pubDate>Fri, 29 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027548.html</link>
<category>Kamerstuk</category>
<title>blg-1027548 : Tweede Kamer der Staten-Generaal</title>
<description>Risk of carbon leakage in Dutch non-ETS sectors</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027485.html</link>
<category>Kamerstuk</category>
<title>blg-1027485 : Tweede Kamer der Staten-Generaal</title>
<description>Kwartaalrapportage CBR  corona-inhaalslag examenafname 6 april 2022</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027472.html</link>
<category>Kamerstuk</category>
<title>kst-1027472 : Tweede Kamer der Staten-Generaal</title>
<description>Geneesmiddelenbeleid; Brief regering; Tekort aan het geneesmiddel Visudyne (verteporfine)</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027542.html</link>
<category>Kamerstuk</category>
<title>kst-1027542 : Tweede Kamer der Staten-Generaal</title>
<description>Maatregelen verkeersveiligheid; Brief regering; Rapportage van het CBR over de Divisies Rijgeschiktheid Medisch en Klantenservice januari - maart 2022</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027549.html</link>
<category>Kamerstuk</category>
<title>kst-1027549 : Tweede Kamer der Staten-Generaal</title>
<description>Grondrechten in een pluriforme samenleving; Brief regering; Reactie op verzoek commissie over het oordeel van de Raad van State aangaande het gebiedsverbod van een Haagse imam</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027486.html</link>
<category>Kamerstuk</category>
<title>blg-1027486 : Tweede Kamer der Staten-Generaal</title>
<description>Aanbieding CBR aan IenW 6 april 2022</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027473.html</link>
<category>Kamerstuk</category>
<title>kst-1027473 : Tweede Kamer der Staten-Generaal</title>
<description>Integrale visie op de woningmarkt; Brief regering; Afschrift van de brief aan de commissarissen van de Koning, gedeputeerden, burgemeesters en wethouders over de taakstelling vergunninghouders in de tweede helft van 2022</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027543.html</link>
<category>Kamerstuk</category>
<title>blg-1027543 : Tweede Kamer der Staten-Generaal</title>
<description>Kwartaalrapportage eerste kwartaal 2022 Divisies Rijgeschiktheid Medisch en Klantenservice</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027454.html</link>
<category>Kamerstuk</category>
<title>kst-1027454 : Tweede Kamer der Staten-Generaal</title>
<description>Gaswinning; Brief regering; Voorbereiding besluitvorming gaswinning Groningenveld gasjaar 2022-2023</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027499.html</link>
<category>Kamerstuk</category>
<title>kst-1027499 : Tweede Kamer der Staten-Generaal</title>
<description>Vaststelling van de begrotingsstaat van het Mobiliteitsfonds voor het jaar 2022; Brief regering; Gevolgen verstoring materiaalketen op project Maaslijn</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027474.html</link>
<category>Kamerstuk</category>
<title>blg-1027474 : Tweede Kamer der Staten-Generaal</title>
<description>Afschrift van de brief aan de commissarissen van de Koning, gedeputeerden, burgemeesters en wethouders over de taakstelling vergunninghouders in de tweede helft van 2022</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027455.html</link>
<category>Kamerstuk</category>
<title>blg-1027455 : Tweede Kamer der Staten-Generaal</title>
<description>Validatie van GTS advies van 31 januari 2022</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027480.html</link>
<category>Kamerstuk</category>
<title>kst-1027480 : Tweede Kamer der Staten-Generaal</title>
<description>Verwerking en bescherming persoonsgegevens; Brief regering; Stand van zaken onderzoek naar autorisatiebeheer Handelsregister</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027493.html</link>
<category>Kamerstuk</category>
<title>kst-1027493 : Tweede Kamer der Staten-Generaal</title>
<description>Vaststelling van de begrotingsstaten van het Ministerie van Infrastructuur en Waterstaat (XII) voor het jaar 2022; Brief regering; Evaluatie subsidieregeling Dutch Cycling Embassy</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027506.html</link>
<category>Kamerstuk</category>
<title>kst-1027506 : Tweede Kamer der Staten-Generaal</title>
<description>Nederlandse Voedsel- en Warenautoriteit (NVWA); Brief regering; Rapportage van de Raad van Advies voor de onafhankelijke risicobeoordeling Voedsel en Waren Autoriteit over 2020</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027456.html</link>
<category>Kamerstuk</category>
<title>blg-1027456 : Tweede Kamer der Staten-Generaal</title>
<description>Advies leveringszekerheid voor benodigde Groningencapaciteiten en -volumes gasjaar 2022/2023 en verder</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027469.html</link>
<category>Kamerstuk</category>
<title>kst-1027469 : Tweede Kamer der Staten-Generaal</title>
<description>Bedrijfslevenbeleid; Brief regering; Uitstel toezending reactie op verzoek commissie op het PwC-rapport ‘Het onbenut potentieel op de financiering van startups’</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027450.html</link>
<category>Kamerstuk</category>
<title>kst-1027450 : Tweede Kamer der Staten-Generaal</title>
<description>Landelijk afvalbeheerplan; Brief regering; Aanpak sigarettenfilters</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027482.html</link>
<category>Kamerstuk</category>
<title>kst-1027482 : Tweede Kamer der Staten-Generaal</title>
<description>Evaluatie Rijkswet financieel toezicht Curaçao en Sint Maarten; Brief regering; Besluitvorming Rijksministerraad 8 april inzake Evaluatie Rijkswet financieel toezicht Curaçao en Sint Maarten 2021</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027508.html</link>
<category>Kamerstuk</category>
<title>blg-1027508 : Tweede Kamer der Staten-Generaal</title>
<description>Rapportage Raad van Advies</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027514.html</link>
<category>Kamerstuk</category>
<title>kst-1027514 : Tweede Kamer der Staten-Generaal</title>
<description>Omgevingsrecht; Brief regering; Maandrapportage maart 2022 - Aansluiten op het Digitaal Stelsel Omgevingswet</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027483.html</link>
<category>Kamerstuk</category>
<title>blg-1027483 : Tweede Kamer der Staten-Generaal</title>
<description>Advies Evaluatiecommissie 2021 Artikel 33 Rijkswet financieel toezicht Curaçao en Sint Maarten</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027515.html</link>
<category>Kamerstuk</category>
<title>blg-1027515 : Tweede Kamer der Staten-Generaal</title>
<description>Voortgangsoverzicht 'Aanmelding, Aansluiting, Ontvangst &amp;amp; Publicatie Maart 2022</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027547.html</link>
<category>Kamerstuk</category>
<title>kst-1027547 : Tweede Kamer der Staten-Generaal</title>
<description>Kabinetsaanpak Klimaatbeleid; Brief regering; Extern onderzoek koolstoflekkage non-ETS</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027497.html</link>
<category>Kamerstuk</category>
<title>blg-1027497 : Tweede Kamer der Staten-Generaal</title>
<description>Evaluatie Dutch Cycling Embassy</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027484.html</link>
<category>Kamerstuk</category>
<title>kst-1027484 : Tweede Kamer der Staten-Generaal</title>
<description>Maatregelen verkeersveiligheid; Brief regering; Kwartaalrapportage CBR corona-inhaalslag examens 1e kwartaal 2022</description>
<pubDate>Thu, 28 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027326.html</link>
<category>Kamerstuk</category>
<title>kst-1027326 : Tweede Kamer der Staten-Generaal</title>
<description>Nieuwe Commissievoorstellen en initiatieven van de lidstaten van de Europese Unie; Brief regering; Voorlopig akkoord internationaal aanbestedingsinstrument</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027358.html</link>
<category>Kamerstuk</category>
<title>kst-1027358 : Tweede Kamer der Staten-Generaal</title>
<description>Raad Algemene Zaken en Raad Buitenlandse Zaken; Brief regering; Verslag Raad Buitenlandse Zaken van 11 april 2022</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027352.html</link>
<category>Kamerstuk</category>
<title>blg-1027352 : Tweede Kamer der Staten-Generaal</title>
<description>Overzicht beoordeelde betaalverzoeken RRF eerste kwartaal 2022</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027416.html</link>
<category>Kamerstuk</category>
<title>kst-1027416 : Tweede Kamer der Staten-Generaal</title>
<description>Infectieziektenbestrijding; Brief regering; Stand van zaken COVID-19</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027353.html</link>
<category>Kamerstuk</category>
<title>blg-1027353 : Tweede Kamer der Staten-Generaal</title>
<description>Actuele stand van de uitbetaling van subsidies en leningen uit de RRF (na eerste kwartaal 2022)</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027417.html</link>
<category>Kamerstuk</category>
<title>blg-1027417 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota </description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027423.html</link>
<category>Kamerstuk</category>
<title>kst-1027423 : Tweede Kamer der Staten-Generaal</title>
<description>Maatregelen verkeersveiligheid; Brief regering; Toelichting op verkeersongevallencijfers Rijks-N-wegen</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027341.html</link>
<category>Kamerstuk</category>
<title>kst-1027341 : Tweede Kamer der Staten-Generaal</title>
<description>Vergaderingen Interim Committee en Development Committee; Brief regering; Geannoteerde agenda voor de inzet van de Wereldbank voorjaarsvergadering 2022</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027303.html</link>
<category>Kamerstuk</category>
<title>kst-1027303 : Tweede Kamer der Staten-Generaal</title>
<description>Grondstoffenvoorzieningszekerheid; Brief regering; Ontwerpbesluit uitgebreide producentenverantwoordelijkheid textiel</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027354.html</link>
<category>Kamerstuk</category>
<title>kst-1027354 : Tweede Kamer der Staten-Generaal</title>
<description>NAVO; Brief regering; Verslag van de NAVO ministeriële bijeenkomst van 6 en 7 april 2022</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027367.html</link>
<category>Kamerstuk</category>
<title>kst-1027367 : Tweede Kamer der Staten-Generaal</title>
<description>Nieuwe Commissievoorstellen en initiatieven van de lidstaten van de Europese Unie; Brief regering; Kwartaalrapportage lopende EU-wetgevingshandelingen LNV</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027304.html</link>
<category>Kamerstuk</category>
<title>blg-1027304 : Tweede Kamer der Staten-Generaal</title>
<description>Besluit houdende regels voor uitgebreide producentenverantwoordelijkheid voor textielproducten (Besluit uitgebreide producentenverantwoordelijkheid textiel)</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027368.html</link>
<category>Kamerstuk</category>
<title>blg-1027368 : Tweede Kamer der Staten-Generaal</title>
<description>Eerste Kwartaalrapportage 2022 EU-wetgevingshandelingen LNV</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027342.html</link>
<category>Kamerstuk</category>
<title>kst-1027342 : Tweede Kamer der Staten-Generaal</title>
<description>Leven Lang Leren; Brief regering; Verloop openstelling eerste aanvraagtijdvak STAP-budget</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027374.html</link>
<category>Kamerstuk</category>
<title>kst-1027374 : Tweede Kamer der Staten-Generaal</title>
<description>Investeren in Perspectief - Goed voor de Wereld, Goed voor Nederland; Brief regering; Financiële reserves humanitaire hulp</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027343.html</link>
<category>Kamerstuk</category>
<title>blg-1027343 : Tweede Kamer der Staten-Generaal</title>
<description>Factsheet Kerncijfers STAPbudget eerste aanvraagtijdvak</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027305.html</link>
<category>Kamerstuk</category>
<title>blg-1027305 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota's inzake besluit uitgebreide producentenverantwoordelijkheid textiel)</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027369.html</link>
<category>Kamerstuk</category>
<title>blg-1027369 : Tweede Kamer der Staten-Generaal</title>
<description>EU-consultaties: reactie in Q1 2022</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027356.html</link>
<category>Kamerstuk</category>
<title>kst-1027356 : Tweede Kamer der Staten-Generaal</title>
<description>Defensienota; Brief regering; Reactie op verzoek commissie over het behoud van de Johan Willem Friso-kazerne</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027400.html</link>
<category>Kamerstuk</category>
<title>kst-1027400 : Tweede Kamer der Staten-Generaal</title>
<description>Alleenstaande minderjarige asielzoekers; Brief regering; Voortgang samenwerkingsverband Griekenland en de opvang van alleenstaande minderjarige vreemdelingen (amv) in Griekenland</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027350.html</link>
<category>Kamerstuk</category>
<title>kst-1027350 : Tweede Kamer der Staten-Generaal</title>
<description>Raad voor Economische en Financiële Zaken; Brief regering; Overzicht uitbetaling RRF eerste kwartaal 2022</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027363.html</link>
<category>Kamerstuk</category>
<title>kst-1027363 : Tweede Kamer der Staten-Generaal</title>
<description>Integratiebeleid; Brief regering; Beantwoording vragen, gesteld tijdens het Wetgevingsoverleg van 22 november 2021, over Integratie en maatschappelijke samenhang (beleidsartikel 13 van de begroting SZW 2022)</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027344.html</link>
<category>Kamerstuk</category>
<title>kst-1027344 : Tweede Kamer der Staten-Generaal</title>
<description>Veteranenzorg; Brief regering; Reactie op verzoek commissie inzake proefschrift 'Nederland en zijn veteranen 1945-2015'</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027395.html</link>
<category>Kamerstuk</category>
<title>kst-1027395 : Tweede Kamer der Staten-Generaal</title>
<description>Mediation en het rechtsbestel; Brief regering; Aanpassing opdracht aan de Raad voor Rechtsbijstand inschrijvingsvoorwaarden voor mediators</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027357.html</link>
<category>Kamerstuk</category>
<title>kst-1027357 : Tweede Kamer der Staten-Generaal</title>
<description>Europese Raad; Brief regering; Reactie op de motie van het lid Eppink c.s. over de Rapid Deployment Force geen opmaat laten zijn voor een Europees leger (Kamerstuk 21501-20-1787 )</description>
<pubDate>Tue, 26 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-36084-2.html</link>
<category>Kamerstuk</category>
<title>kst-36084-2 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van de Wet beveiliging netwerk- en informatiesystemen in verband met de uitbreiding van de bevoegdheid van de Minister van Justitie en Veiligheid om dreigings- en incidentinformatie over de netwerk- en informatiesystemen van niet-vitale aanbieders te verstrekken aan deze aanbieders en aan organisaties die objectief kenbaar tot taak hebben om andere organisaties of het publiek te informeren over dreigingen en incidenten ten behoeve van deze aanbieders; Voorstel van wet; Voorstel van wet</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027269.html</link>
<category>Kamerstuk</category>
<title>kst-1027269 : Tweede Kamer der Staten-Generaal</title>
<description>Toezichtsverslagen AIVD en MIVD; Brief regering; Onderhoud MIVD-gebouw Frederikkazerne</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027282.html</link>
<category>Kamerstuk</category>
<title>blg-1027282 : Tweede Kamer der Staten-Generaal</title>
<description>Beleidskeuzes uitgelegd</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027238.html</link>
<category>Kamerstuk</category>
<title>blg-1027238 : Tweede Kamer der Staten-Generaal</title>
<description>Verzamelingregeling wijziging bestaande UPV</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027231.html</link>
<category>Kamerstuk</category>
<title>kst-1027231 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van enkele wetten op het gebied van Justitie en Veiligheid in verband met aanpassingen van overwegend technische aard (Verzamelwet Justitie en Veiligheid 2022); Nota n.a.v. het (nader/tweede nader/enz.) verslag; Nota naar aanleiding van het verslag</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027219.html</link>
<category>Kamerstuk</category>
<title>blg-1027219 : Tweede Kamer der Staten-Generaal</title>
<description>Advies Connect2Trust</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027276.html</link>
<category>Kamerstuk</category>
<title>kst-1027276 : Tweede Kamer der Staten-Generaal</title>
<description>Terrorismebestrijding; Brief regering; Dreigingsbeeld Terrorisme Nederland 56</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-36085-1.html</link>
<category>Kamerstuk</category>
<title>kst-36085-1 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van Boek 2 van het Burgerlijk Wetboek en de Wet op het notarisambt in verband met de implementatie van Richtlijn (EU) 2019/1151 van het Europees Parlement en de Raad van 20 juni 2019 tot wijziging van Richtlijn (EU) 2017/1132 met betrekking tot het gebruik van digitale instrumenten en processen in het kader van het vennootschapsrecht (PbEU 2019, L 186); Koninklijke boodschap; Koninklijke boodschap</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-36084-3.html</link>
<category>Kamerstuk</category>
<title>kst-36084-3 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van de Wet beveiliging netwerk- en informatiesystemen in verband met de uitbreiding van de bevoegdheid van de Minister van Justitie en Veiligheid om dreigings- en incidentinformatie over de netwerk- en informatiesystemen van niet-vitale aanbieders te verstrekken aan deze aanbieders en aan organisaties die objectief kenbaar tot taak hebben om andere organisaties of het publiek te informeren over dreigingen en incidenten ten behoeve van deze aanbieders; Memorie van toelichting; Memorie van toelichting</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027232.html</link>
<category>Kamerstuk</category>
<title>blg-1027232 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota </description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027277.html</link>
<category>Kamerstuk</category>
<title>blg-1027277 : Tweede Kamer der Staten-Generaal</title>
<description>Dreigingsbeeld Terrorisme Nederland 56</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027239.html</link>
<category>Kamerstuk</category>
<title>blg-1027239 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027283.html</link>
<category>Kamerstuk</category>
<title>kst-1027283 : Tweede Kamer der Staten-Generaal</title>
<description>Bestrijding internationaal terrorisme; Brief regering; Instellingsbesluit Commissie van onderzoek evacuatieoperatie Kaboel</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027264.html</link>
<category>Kamerstuk</category>
<title>kst-1027264 : Tweede Kamer der Staten-Generaal</title>
<description>Preventief gezondheidsbeleid; Verslag van een commissiedebat; Verslag van een commissiedebat, gehouden op 24 maart 2022, over Leefstijlpreventie</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-36085-2.html</link>
<category>Kamerstuk</category>
<title>kst-36085-2 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van Boek 2 van het Burgerlijk Wetboek en de Wet op het notarisambt in verband met de implementatie van Richtlijn (EU) 2019/1151 van het Europees Parlement en de Raad van 20 juni 2019 tot wijziging van Richtlijn (EU) 2017/1132 met betrekking tot het gebruik van digitale instrumenten en processen in het kader van het vennootschapsrecht (PbEU 2019, L 186); Voorstel van wet; Voorstel van wet</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-36084-4.html</link>
<category>Kamerstuk</category>
<title>kst-36084-4 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van de Wet beveiliging netwerk- en informatiesystemen in verband met de uitbreiding van de bevoegdheid van de Minister van Justitie en Veiligheid om dreigings- en incidentinformatie over de netwerk- en informatiesystemen van niet-vitale aanbieders te verstrekken aan deze aanbieders en aan organisaties die objectief kenbaar tot taak hebben om andere organisaties of het publiek te informeren over dreigingen en incidenten ten behoeve van deze aanbieders; Advies Afdeling advisering Raad van State en Nader rapport; Advies Afdeling advisering Raad van State en Nader rapport</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027220.html</link>
<category>Kamerstuk</category>
<title>blg-1027220 : Tweede Kamer der Staten-Generaal</title>
<description> Advies Cyber Security Raad CSR</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027214.html</link>
<category>Kamerstuk</category>
<title>blg-1027214 : Tweede Kamer der Staten-Generaal</title>
<description>Advies AP</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027284.html</link>
<category>Kamerstuk</category>
<title>blg-1027284 : Tweede Kamer der Staten-Generaal</title>
<description>Instellingsbesluit commissie van onderzoek evacuatieoperatie Kaboel</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027290.html</link>
<category>Kamerstuk</category>
<title>kst-1027290 : Tweede Kamer der Staten-Generaal</title>
<description>Vaststelling van de begrotingsstaten van het Ministerie van Defensie (X) voor het jaar 2022; Brief regering; Diversiteit en Inclusiviteit</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027278.html</link>
<category>Kamerstuk</category>
<title>blg-1027278 : Tweede Kamer der Staten-Generaal</title>
<description>Infographic Dreigingsbeeld Terrorisme Nederland 56</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027271.html</link>
<category>Kamerstuk</category>
<title>kst-1027271 : Tweede Kamer der Staten-Generaal</title>
<description>Voortgezet Onderwijs; Brief regering; Ontwikkelingen Stichtingen voor Persoonlijk Onderwijs</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027265.html</link>
<category>Kamerstuk</category>
<title>kst-1027265 : Tweede Kamer der Staten-Generaal</title>
<description>Vaststelling van de begrotingsstaten van het Ministerie van Landbouw, Natuur en Voedselkwaliteit (XIV) en het Diergezondheidsfonds (F) voor het jaar 2022; Brief regering; Publicatie cijfers Stalbranden 2021</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-36085-3.html</link>
<category>Kamerstuk</category>
<title>kst-36085-3 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van Boek 2 van het Burgerlijk Wetboek en de Wet op het notarisambt in verband met de implementatie van Richtlijn (EU) 2019/1151 van het Europees Parlement en de Raad van 20 juni 2019 tot wijziging van Richtlijn (EU) 2017/1132 met betrekking tot het gebruik van digitale instrumenten en processen in het kader van het vennootschapsrecht (PbEU 2019, L 186); Memorie van toelichting; Memorie van toelichting</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027221.html</link>
<category>Kamerstuk</category>
<title>blg-1027221 : Tweede Kamer der Staten-Generaal</title>
<description>Advies Cyberweerbaarheidscentrum Brainport</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027215.html</link>
<category>Kamerstuk</category>
<title>blg-1027215 : Tweede Kamer der Staten-Generaal</title>
<description>Advies Raad voor de Rechtspraak</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027285.html</link>
<category>Kamerstuk</category>
<title>blg-1027285 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota's inzake instellingsbesluit Commissie van onderzoek evacuatieoperatie Kaboel</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027266.html</link>
<category>Kamerstuk</category>
<title>kst-1027266 : Tweede Kamer der Staten-Generaal</title>
<description>Materieelprojecten; Brief regering; Project ‘Joint Electronic Attack’</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027228.html</link>
<category>Kamerstuk</category>
<title>kst-1027228 : Tweede Kamer der Staten-Generaal</title>
<description>Voorstel van wet van de leden Bromet en Tjeerd de Groot tot wijziging van de Waterschapswet en de Kieswet in verband met het volledig democratiseren van de waterschapsbesturen; Nota van wijziging (initiatiefvoorstel); Derde nota van wijziging</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-36085-4.html</link>
<category>Kamerstuk</category>
<title>kst-36085-4 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van Boek 2 van het Burgerlijk Wetboek en de Wet op het notarisambt in verband met de implementatie van Richtlijn (EU) 2019/1151 van het Europees Parlement en de Raad van 20 juni 2019 tot wijziging van Richtlijn (EU) 2017/1132 met betrekking tot het gebruik van digitale instrumenten en processen in het kader van het vennootschapsrecht (PbEU 2019, L 186); Advies Afdeling advisering Raad van State en Nader rapport; Advies Afdeling advisering Raad van State en Nader rapport</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027222.html</link>
<category>Kamerstuk</category>
<title>blg-1027222 : Tweede Kamer der Staten-Generaal</title>
<description> Advies FERM</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027197.html</link>
<category>Kamerstuk</category>
<title>kst-1027197 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van de begrotingsstaten van het Ministerie van Economische Zaken en Klimaat voor het jaar 2022 (Vijfde incidentele suppletoire begroting inzake aanvullende coronasteunmaatregelen); Verslag (initiatief)wetsvoorstel (nader); Verslag (blanco)</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027273.html</link>
<category>Kamerstuk</category>
<title>kst-1027273 : Tweede Kamer der Staten-Generaal</title>
<description>Navo helikopterproject NH-90; Brief regering; Project Midlife Update NH90 helikopter</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027223.html</link>
<category>Kamerstuk</category>
<title>blg-1027223 : Tweede Kamer der Staten-Generaal</title>
<description>Advies Cyberveilig Nederland</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027217.html</link>
<category>Kamerstuk</category>
<title>blg-1027217 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota inzake wijziging van Boek 2 van het Burgerlijk Wetboek en de Wet op het notarisambt in verband met de implementatie van Richtlijn (EU) 2019/1151 van het Europees Parlement en de Raad van 20 juni 2019 tot wijziging van Richtlijn (EU) 2017/1132 met betrekking tot het gebruik van digitale instrumenten en processen in het kader van het vennootschapsrecht (PbEU 2019, L 186)</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027280.html</link>
<category>Kamerstuk</category>
<title>kst-1027280 : Tweede Kamer der Staten-Generaal</title>
<description>Gaswinning; Brief regering; Verlenging waardevermeerderingsregeling Groningen voorjaar 2022</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-1027236.html</link>
<category>Kamerstuk</category>
<title>kst-1027236 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van de Wet milieubeheer in verband met de implementatie van Richtlijn (EU) 2018/851 van het Europees Parlement en de Raad van 30 mei 2018 tot wijziging van Richtlijn 2008/98/EG betreffende afvalstoffen (PbEU L 150) (Implementatiewet wijziging EU-kaderrichtlijn afvalstoffen); Brief regering; Voorhang Ontwerp-Verzamelregeling wijziging bestaande UPV's</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/kst-36084-1.html</link>
<category>Kamerstuk</category>
<title>kst-36084-1 : Tweede Kamer der Staten-Generaal</title>
<description>Wijziging van de Wet beveiliging netwerk- en informatiesystemen in verband met de uitbreiding van de bevoegdheid van de Minister van Justitie en Veiligheid om dreigings- en incidentinformatie over de netwerk- en informatiesystemen van niet-vitale aanbieders te verstrekken aan deze aanbieders en aan organisaties die objectief kenbaar tot taak hebben om andere organisaties of het publiek te informeren over dreigingen en incidenten ten behoeve van deze aanbieders; Koninklijke boodschap; Koninklijke boodschap</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027281.html</link>
<category>Kamerstuk</category>
<title>blg-1027281 : Tweede Kamer der Staten-Generaal</title>
<description>Verlenging waardevermeerderingsregeling</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027224.html</link>
<category>Kamerstuk</category>
<title>blg-1027224 : Tweede Kamer der Staten-Generaal</title>
<description>Beslisnota </description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
<item>
<link>https://zoek.officielebekendmakingen.nl/blg-1027218.html</link>
<category>Kamerstuk</category>
<title>blg-1027218 : Tweede Kamer der Staten-Generaal</title>
<description>Advies Autoriteit Persoonsgegevens</description>
<pubDate>Mon, 25 Apr 2022 00:00:00 +0200</pubDate>
</item>
</channel>
</rss>
"""
