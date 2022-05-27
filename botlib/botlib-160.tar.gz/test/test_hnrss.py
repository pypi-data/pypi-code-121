# This file is placed in the Public Domain.


"xml tests"



import unittest


from bot.rss import Parser


items = "title,summary,link,pubDate"


class Test_XML(unittest.TestCase):

    def test_xml(self):
        p = Parser()
        res =  p.parse(txt)
        self.assertEqual(len(res), 21)


txt = """ 
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Hacker News: Newest</title><link>https://news.ycombinator.com/newest</link><description>Hacker News RSS</description><docs>https://hnrss.org/</docs><generator>hnrss v1.1-16-gb4aa33c</generator><lastBuildDate>Sun, 01 May 2022 17:07:46 +0000</lastBuildDate><atom:link href="https://hnrss.org/newest" rel="self" type="application/rss+xml"/><item><title><![CDATA[Seashells Have Built Our Cities]]></title><description><![CDATA[
<p>Article URL: <a href="https://www.wsj.com/articles/how-seashells-have-built-our-cities-11651255039">https://www.wsj.com/articles/how-seashells-have-built-our-cities-11651255039</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226629">https://news.ycombinator.com/item?id=31226629</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 17:06:44 +0000</pubDate><link>https://www.wsj.com/articles/how-seashells-have-built-our-cities-11651255039</link><dc:creator>prostoalex</dc:creator><comments>https://news.ycombinator.com/item?id=31226629</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226629</guid></item><item><title><![CDATA[Research helps explain how Ritalin sharpens attention]]></title><description><![CDATA[
<p>Article URL: <a href="https://www.pitt.edu/pittwire/features-articles/ritalin-behavioral-effects">https://www.pitt.edu/pittwire/features-articles/ritalin-behavioral-effects</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226608">https://news.ycombinator.com/item?id=31226608</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 17:03:32 +0000</pubDate><link>https://www.pitt.edu/pittwire/features-articles/ritalin-behavioral-effects</link><dc:creator>laurex</dc:creator><comments>https://news.ycombinator.com/item?id=31226608</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226608</guid></item><item><title><![CDATA[US plans campaign to attract Russian scientists, engineers to America & CERN]]></title><description><![CDATA[
<p>Article URL: <a href="https://sciencebusiness.net/news/us-plans-campaign-attract-russian-scientists-engineers-america">https://sciencebusiness.net/news/us-plans-campaign-attract-russian-scientists-engineers-america</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226590">https://news.ycombinator.com/item?id=31226590</a></p>
<p>Points: 2</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 17:00:51 +0000</pubDate><link>https://sciencebusiness.net/news/us-plans-campaign-attract-russian-scientists-engineers-america</link><dc:creator>walterbell</dc:creator><comments>https://news.ycombinator.com/item?id=31226590</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226590</guid></item><item><title><![CDATA[Espanso: Cross-Platform Text Expander Written in Rust]]></title><description><![CDATA[
<p>Article URL: <a href="https://github.com/federico-terzi/espanso">https://github.com/federico-terzi/espanso</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226589">https://news.ycombinator.com/item?id=31226589</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 17:00:45 +0000</pubDate><link>https://github.com/federico-terzi/espanso</link><dc:creator>behnamoh</dc:creator><comments>https://news.ycombinator.com/item?id=31226589</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226589</guid></item><item><title><![CDATA[The deadly accordion wars of Lesotho]]></title><description><![CDATA[
<p>Article URL: <a href="https://www.bbc.com/news/world-africa-61097386">https://www.bbc.com/news/world-africa-61097386</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226578">https://news.ycombinator.com/item?id=31226578</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:59:56 +0000</pubDate><link>https://www.bbc.com/news/world-africa-61097386</link><dc:creator>Sujan</dc:creator><comments>https://news.ycombinator.com/item?id=31226578</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226578</guid></item><item><title><![CDATA[The Iroquois Confederacy (2019)]]></title><description><![CDATA[
<p>Article URL: <a href="https://www.youtube.com/watch?v=S4gU2Tsv6hY">https://www.youtube.com/watch?v=S4gU2Tsv6hY</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226513">https://news.ycombinator.com/item?id=31226513</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:50:59 +0000</pubDate><link>https://www.youtube.com/watch?v=S4gU2Tsv6hY</link><dc:creator>Tomte</dc:creator><comments>https://news.ycombinator.com/item?id=31226513</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226513</guid></item><item><title><![CDATA[The Better Alternative to Lifetime GATs]]></title><description><![CDATA[
<p>Article URL: <a href="https://sabrinajewson.org/blog/the-better-alternative-to-lifetime-gats">https://sabrinajewson.org/blog/the-better-alternative-to-lifetime-gats</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226506">https://news.ycombinator.com/item?id=31226506</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:50:10 +0000</pubDate><link>https://sabrinajewson.org/blog/the-better-alternative-to-lifetime-gats</link><dc:creator>mlex</dc:creator><comments>https://news.ycombinator.com/item?id=31226506</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226506</guid></item><item><title><![CDATA[An algorithm that screens for child neglect raises concerns]]></title><description><![CDATA[
<p>Article URL: <a href="https://apnews.com/article/child-welfare-algorithm-investigation-9497ee937e0053ad4144a86c68241ef1">https://apnews.com/article/child-welfare-algorithm-investigation-9497ee937e0053ad4144a86c68241ef1</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226491">https://news.ycombinator.com/item?id=31226491</a></p>
<p>Points: 2</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:48:03 +0000</pubDate><link>https://apnews.com/article/child-welfare-algorithm-investigation-9497ee937e0053ad4144a86c68241ef1</link><dc:creator>tareqak</dc:creator><comments>https://news.ycombinator.com/item?id=31226491</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226491</guid></item><item><title><![CDATA[Have People Been Given the Wrong Vaccine?]]></title><description><![CDATA[
<p>Article URL: <a href="https://brownstone.org/articles/have-people-been-given-the-wrong-vaccine/">https://brownstone.org/articles/have-people-been-given-the-wrong-vaccine/</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226474">https://news.ycombinator.com/item?id=31226474</a></p>
<p>Points: 4</p>
<p># Comments: 1</p>
]]></description><pubDate>Sun, 01 May 2022 16:45:29 +0000</pubDate><link>https://brownstone.org/articles/have-people-been-given-the-wrong-vaccine/</link><dc:creator>georgecmu</dc:creator><comments>https://news.ycombinator.com/item?id=31226474</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226474</guid></item><item><title><![CDATA[Bait and Switch: Recycling's Dirty Secret]]></title><description><![CDATA[
<p>Article URL: <a href="https://gem.cbc.ca/media/the-fifth-estate/s47e15">https://gem.cbc.ca/media/the-fifth-estate/s47e15</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226442">https://news.ycombinator.com/item?id=31226442</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:42:48 +0000</pubDate><link>https://gem.cbc.ca/media/the-fifth-estate/s47e15</link><dc:creator>clutch89</dc:creator><comments>https://news.ycombinator.com/item?id=31226442</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226442</guid></item><item><title><![CDATA[Purchase of Commissions in the British Army]]></title><description><![CDATA[
<p>Article URL: <a href="https://en.wikipedia.org/wiki/Purchase_of_commissions_in_the_British_Army">https://en.wikipedia.org/wiki/Purchase_of_commissions_in_the_British_Army</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226416">https://news.ycombinator.com/item?id=31226416</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:40:02 +0000</pubDate><link>https://en.wikipedia.org/wiki/Purchase_of_commissions_in_the_British_Army</link><dc:creator>georgecmu</dc:creator><comments>https://news.ycombinator.com/item?id=31226416</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226416</guid></item><item><title><![CDATA[Chase savings account balance of –$99B has me a little concerned]]></title><description><![CDATA[
<p>Article URL: <a href="https://twitter.com/catboston/status/1520794578244489217">https://twitter.com/catboston/status/1520794578244489217</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226394">https://news.ycombinator.com/item?id=31226394</a></p>
<p>Points: 2</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:36:36 +0000</pubDate><link>https://twitter.com/catboston/status/1520794578244489217</link><dc:creator>ilamont</dc:creator><comments>https://news.ycombinator.com/item?id=31226394</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226394</guid></item><item><title><![CDATA[Ask HN: I am losing hope in humanity. What should I do?]]></title><description><![CDATA[
<p>Greetings,<p>Is losing faith/hope in humanity something others experience as well? 
Is it due to the way i perceive things (i.e. my entourage)? 
Am I in a bubble and I don't see it? How do I get out? 
Should I <i>be</i> in a bubble to keep my sanity? 
How do I build those filters?<p>Please let me know your thoughts and how you're handling it.<p>Things that are making me lose hope:<p>- climate change or how society/corporations/governments are destroying the environment and/or are barely doing anything. All I think about sometimes is how we'll begin to see famines spreading across poor countries until it's all too late... Yet Elon buying Twitter is still in the news till this day.<p>- social inequality is rising year on year. inflation is a killer for poor families that are barely making ends meet. Yet most corporations are announcing lots of profits and they barely give a sh*t about their workers.<p>- workers: all I hear is there's a shortage of workers. shortage, shortage, shortage. But they rarely talk about salaries and wages being so low.<p>- billionaires: ugh, enough about these megalomaniacs.<p>- media: it's feeding people rubbish all the time. All. The. Time.<p>- corruption: it's so wide spread, people have become desensitized. war... famines... I could go on...</p>
<hr>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226391">https://news.ycombinator.com/item?id=31226391</a></p>
<p>Points: 4</p>
<p># Comments: 3</p>
]]></description><pubDate>Sun, 01 May 2022 16:36:06 +0000</pubDate><link>https://news.ycombinator.com/item?id=31226391</link><dc:creator>lma21</dc:creator><comments>https://news.ycombinator.com/item?id=31226391</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226391</guid></item><item><title><![CDATA[Sitefox: Node and cljs back end web framework]]></title><description><![CDATA[
<p>Article URL: <a href="https://github.com/chr15m/sitefox">https://github.com/chr15m/sitefox</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226376">https://news.ycombinator.com/item?id=31226376</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:34:21 +0000</pubDate><link>https://github.com/chr15m/sitefox</link><dc:creator>tosh</dc:creator><comments>https://news.ycombinator.com/item?id=31226376</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226376</guid></item><item><title><![CDATA[Extracting Skill-Centric State Abstractions from Value Functions]]></title><description><![CDATA[
<p>Article URL: <a href="https://ai.googleblog.com/2022/04/extracting-skill-centric-state.html">https://ai.googleblog.com/2022/04/extracting-skill-centric-state.html</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226351">https://news.ycombinator.com/item?id=31226351</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:31:47 +0000</pubDate><link>https://ai.googleblog.com/2022/04/extracting-skill-centric-state.html</link><dc:creator>RafelMri</dc:creator><comments>https://news.ycombinator.com/item?id=31226351</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226351</guid></item><item><title><![CDATA[Wikimedia Foundation stops accepting cryptocurrency donations]]></title><description><![CDATA[
<p>Article URL: <a href="https://twitter.com/molly0xFFF/status/1520793329302183940">https://twitter.com/molly0xFFF/status/1520793329302183940</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226310">https://news.ycombinator.com/item?id=31226310</a></p>
<p>Points: 5</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:26:16 +0000</pubDate><link>https://twitter.com/molly0xFFF/status/1520793329302183940</link><dc:creator>cunidev</dc:creator><comments>https://news.ycombinator.com/item?id=31226310</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226310</guid></item><item><title><![CDATA[The Dark Side of Collaboration]]></title><description><![CDATA[
<p>Article URL: <a href="https://www.scientificamerican.com/article/the-dark-side-of-collaboration/">https://www.scientificamerican.com/article/the-dark-side-of-collaboration/</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226309">https://news.ycombinator.com/item?id=31226309</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:26:09 +0000</pubDate><link>https://www.scientificamerican.com/article/the-dark-side-of-collaboration/</link><dc:creator>amichail</dc:creator><comments>https://news.ycombinator.com/item?id=31226309</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226309</guid></item><item><title><![CDATA[Annual Reviews Are a Terrible Way to Evaluate Employees]]></title><description><![CDATA[
<p>Article URL: <a href="https://www.wsj.com/articles/annual-reviews-are-a-terrible-way-to-evaluate-employees-11651291254">https://www.wsj.com/articles/annual-reviews-are-a-terrible-way-to-evaluate-employees-11651291254</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226302">https://news.ycombinator.com/item?id=31226302</a></p>
<p>Points: 2</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:24:36 +0000</pubDate><link>https://www.wsj.com/articles/annual-reviews-are-a-terrible-way-to-evaluate-employees-11651291254</link><dc:creator>prostoalex</dc:creator><comments>https://news.ycombinator.com/item?id=31226302</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226302</guid></item><item><title><![CDATA[Knockout City April 28th Outage Explained]]></title><description><![CDATA[
<p>Article URL: <a href="https://old.reddit.com/r/KnockoutCity/comments/ue42ma/april_28th_outage_explained/">https://old.reddit.com/r/KnockoutCity/comments/ue42ma/april_28th_outage_explained/</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226266">https://news.ycombinator.com/item?id=31226266</a></p>
<p>Points: 1</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:20:14 +0000</pubDate><link>https://old.reddit.com/r/KnockoutCity/comments/ue42ma/april_28th_outage_explained/</link><dc:creator>funhatch</dc:creator><comments>https://news.ycombinator.com/item?id=31226266</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226266</guid></item><item><title><![CDATA[Covid herd immunity now seems impossible]]></title><description><![CDATA[
<p>Article URL: <a href="https://www.theguardian.com/commentisfree/2022/apr/12/herd-immunity-covid-reinfection-virus-world">https://www.theguardian.com/commentisfree/2022/apr/12/herd-immunity-covid-reinfection-virus-world</a></p>
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=31226262">https://news.ycombinator.com/item?id=31226262</a></p>
<p>Points: 4</p>
<p># Comments: 0</p>
]]></description><pubDate>Sun, 01 May 2022 16:19:43 +0000</pubDate><link>https://www.theguardian.com/commentisfree/2022/apr/12/herd-immunity-covid-reinfection-virus-world</link><dc:creator>LopRabbit</dc:creator><comments>https://news.ycombinator.com/item?id=31226262</comments><guid isPermaLink="false">https://news.ycombinator.com/item?id=31226262</guid></item></channel></rss>
"""