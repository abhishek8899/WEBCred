# _author_ = Shriyansh Agrawal

from bs4 import BeautifulSoup

import requests
import re

import threading
global i,urls,check_hyperlink,check_ratio,check_link_ads,broken_links,cookie
i=0
cookie =1
check_ratio = 0
check_hyperlink=0
check_link_ads = 0
broken_links = 0

urls = [
    "http://www.ffiec.gov/cybersecurity.htm",
    "https://www.openssl.org/docs/",
    "https://www.first.org",
    "https://securityblog.redhat.com/",
    "https://threatpost.com/",
    "http://www.sophos.com/en-us/security-news-trends",
    "https://blogs.rsa.com/",
    "https://apwg.org/",
    "http://www.cybersecurity.alabama.gov/",
    "http://www.symantec.com/connect/blogs/discover?community-id=691",
    "http://www.digitalthreat.net/2010/05/information-security-models-for-confidentiality-and-integrity/",
    "http://www.itsecurity.com/dictionary/all/",
    "https://www.schneier.com/cryptography.html",
    "http://www.iplocation.net/",
    "http://www.iso.org/iso/home/standards/management-standards/iso27001.htm",
    "https://www.kuppingercole.com/blog/kuppinger/information-rights-management-microsoft-gives-it-a-new-push-just-in-time-to-succeed",
    "http://www.cisco.com/c/en/us/td/docs/ios/sec_data_plane/configuration/guide/12_4/sec_data_plane_12_4_book.html",
    "https://www.freebsd.org/doc/handbook/index.html",
    "http://www.cgisecurity.com/owasp/html/index.html",
    "http://csrc.nist.gov/",
    "http://disa.mil/Network-Services/Data",
    "http://wiki.openssl.org/",
    "http://www.isg.rhul.ac.uk/tls/",
    "http://www.cryptographyworld.com/",
    "http://www.w3.org/TR/xmlsec-algorithms/",
    "http://niccs.us-cert.gov/glossary",
    "https://www.schneier.com/essays/",
    "http://securitywatch.pcmag.com/",
    "https://www.torproject.org/",
    "http://resources.infosecinstitute.com",
    "http://www.esslsecurity.com/",
    "http://stackoverflow.com/questions/tagged/security",
    "http://docs.saltstack.com/en/latest/",
    "https://saltthepass.com/#help-about",
    "http://crypto.stackexchange.com/",
    "http://www.biometrics.gov/",
    "http://www.biometricsinstitute.org/pages/types-of-biometrics.html",
    "http://support.microsoft.com/en-us/kb/246071",
    "http://www.garykessler.net/library/fsc_stego.html",
    "https://technet.microsoft.com/en-us/library/cc179103.aspx",
    "http://cs.stanford.edu/people/eroberts/courses/soco/projects/2000-01/risc/whatis/",
    "http://www.gammassl.co.uk/research/chinesewall.php",
    "http://www.softpanorama.org/Access_control/Security_models/",
    "http://www.openpgp.org/",
    "http://www.quadibloc.com/crypto/jscrypt.htm",
    "http://search.cpan.org/dist/Crypt-Loki97/Loki97.pm",
    "https://www.fastmail.com/help/technical/ssltlsstarttls.html",
    "http://www.ietf.org/rfc/rfc4880.txt",
    "https://tools.ietf.org/html/rfc2595",
    "http://www.pcmag.com/article2/0,2817,2407168,00.asp",
    "http://www.pcmag.com/article2/0,2817,2372364,00.asp",
    "https://technet.microsoft.com/en-us/library/hh994558%28v=ws.10%29.aspx",
    "https://technet.microsoft.com/en-us/library/hh994561(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/dd883248(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc755284(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc731416(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/ee706526(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc731004(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc731515(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc771395(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/jj865680(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/ff641731(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc753173(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc721923(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc731549(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc732077(v=ws.10).aspx",
    "https://technet.microsoft.com/en-us/library/cc772066(v=ws.10).aspx",
    "https://twitter.com/bruce_schneier",
    "http://www.isaccouncil.org/memberisacs.html",
    "https://tools.ietf.org/",
    "http://www.sqlsecurity.co",
    "https://technet.microsoft.com/en-us/library/security/dn610807.aspx",
    "http://searchsecurity.techtarget.in/",
    "http://www.bmc.com/support/security/",
    "https://portal.reisac.org/SitePages/Index.aspx",
    "http://www.infosecisland.com/",
    "http://www.infosecblog.org/",
    "https://isc.sans.edu/",
    "http://www.northropgrumman.com",
    "https://ics-cert.us-cert.gov/Standards-and-References",
    "http://www.information-age.com/",
    "https://europaysolutions.com/fraud-risk-management/fraud-prevention-suite/",
    "http://www.idrbt.ac.in/",
    "https://cve.mitre.org/",
    "http://www.ibm.com/developerworks/websphere/zones/was/security/",
    "https://cryptoworks21.uwaterloo.ca/cryptography",
    "http://www.fortinet.com",
    "https://crackstation.net/hashing-security.htm",
    "http://www.enterprisedb.com/docs/en/9.3/pg/sql-security-label.html",
    "http://www.arubanetworks.com/products/security/",
    "http://cyfy.org/tag/security/",
    "https://access.redhat.com/security/cve/",
    "http://www.crypto.com",
    "http://www2.schneider-electric.com/sites/corporate/en/support/cybersecurity/cybersecurity.page",
    "http://www.govinfosecurity.com",
    "http://www.wisegeek.com/what-is-tls.htm",
    "http://www.governmentsecurity.org/",
    "http://www.wired.com/category/threatlevel",
    "http://www.austinfosec.com",
    "http://www.wired.com/2014/11/hacker-lexicon-whats-dark-web/",
]

# urls = [
#     # "https://www.first.org",
#     "http://9gag.com/gif?ref=9nav"
#     # "http://www.ct.gov/dds/lib/dds/images/ddslogo.jpg"
# ]

easylist = open("adlist.txt", "r")
ads_list = easylist.read().split(',')
# print ads_list
# print len(ads_list)
'''
    [Adblock Plus 2.0]
    ! Version: 201702151753
    ! Title: EasyList
    ! Last modified: 15 Feb 2017 17:53 UTC
    ! Expires: 4 days (update frequency)
    ! Homepage: https://easylist.to/
    ! Licence: https://easylist.to/pages/licence.html
    !
    ! Please report any unblocked adverts or problems
    ! in the forums (https://forums.lanik.us/)
    ! or via e-mail (easylist.subscription@gmail.com).
    ! GitHub issues: https://github.com/easylist/easylist/issues
    ! GitHub pull requests: https://github.com/easylist/easylist/pulls
    !
    ! -----------------------General advert blocking filters-----------------------!
    ! *** easylist:easylist/easylist_general_block.txt ***
'''
easylist.close()


def crawler(threadName):
    global urls,i,check_hyperlink,check_ratio,check_ads
    while i<len(urls):
        # print urls
        url = urls[i]
        # print "Started", i
        i+=1
        if url!="" and not ( url.startswith('http://') or url.startswith('https://') ):
            print "Nope"
        else:
            # need to specify header for scrapping otherwise some websites doesn't allow bot to scrap
            hdr = {'User-Agent': 'Mozilla/5.0'}
            # You should use the HEAD Request for this, it asks the webserver for the headers without the body.
            raw  = requests.get(url,headers=hdr)

            data = raw.text
            # to write page in a file
            # filename = url.split("/")[-1] + '.html'
            # with open(filename, 'wb') as f:
                # f.write(data.encode('utf-8'))
            # pass

            # Contact,Help,Email,Recommendations,Sitemap - check for hyperlink
            # idea ->  Scrap web>> parse using Soup>> find_all_lines(having='anchor tag', string=="contacts|Help|Email|Recommendations|Sitemap")>> check if href?>>
            if check_hyperlink==1:
                check_hyperlinks(raw,url)

            # No of Ads links, Image to text ratio - check for img / text size
            if check_ratio==1:
                size_of_image = check_size_ratio(raw,url)


            if check_link_ads==1:
                no_of_ads = check_ads(raw,url)

            if broken_links == 1:
                count  = check_brokenlinks(raw,url)

            if cookie==1:
                check_cookie(raw,url)

            print url

class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        crawler(self.name)

# limited to single thread otherwise it become asynchronous
for i in range(1):
    thread = myThread(1, i)
    thread.start()

def check_hyperlinks(raw,url):
    data = raw.text
    soup = BeautifulSoup(data,"html.parser")

    for link in soup.find_all(string=re.compile("language",re.I)):
        links = link.get('href')
        if links:
            print 'lan',
            # break

    # for link in soup.find_all('a', string=re.compile("contact",re.I)):
    #     links = link.get('href')
    #     if links:
    #         print 'contact',
    #         break
    #
    # for link in soup.find_all('a', string=re.compile("email",re.I)):
    #     links = link.get('href')
    #     if links:
    #         print 'email',
    #         break
    #
    # for link in soup.find_all('a', string=re.compile("help",re.I)):
    #     links = link.get('href')
    #     if links:
    #         print 'help',
    #         break
    #
    # for link in soup.find_all('a', string=re.compile("recommend",re.I)):
    #     links = link.get('href')
    #     if links:
    #         print 'recommend',
    #         break
    #
    # for link in soup.find_all('a', string=re.compile("sitemap",re.I)):
    #     links = link.get('href')
    #     if links:
    #         print 'sitemap',
    #         break

    print url

def check_size_ratio(raw,url):
    ratio  = 'Not defined'
    # in bytes
    if not raw:
        print "cannot extract raw of",url
        return

    # print raw.headers
    data = raw.text
    # if raw.headers['Content-Length']:
    try:
        txt_size = int(raw.headers['Content-Length'])
    except:
        txt_size =0

    soup = BeautifulSoup(data,"html.parser")
    # total_img_size of images
    total_img_size = int(0)
    for link in soup.find_all('img',src=True):
        links = link.get('src')
        if links!="":
            if not links.startswith('http://') or links.startswith('https://'):
                links = url+links
                # print links

            hdr = {'User-Agent': 'Mozilla/5.0'}
            r  = requests.get(links,headers=hdr)
            try:
                size = r.headers['Content-Length']
            except:
                size=0
            total_img_size = total_img_size + int(size)
            # print size,link

            try:
                ratio = total_img_size/txt_size
            except:
                ratio = 'Not defined'
    print total_img_size,url,txt_size
    print ratio

def check_ads(raw,url):

    # print ads for ads in ads_list
    # return
    data = raw.text
    soup = BeautifulSoup(data,'html.parser')
    count = 0

    for link in soup.find_all('a'):
        href = link.get('href')
        if  href.startswith('http://') or href.startswith('https://'):
            print href
            # for ads in ads_list:
            #     print str(ads)
            x = re.findall(r"(?=("+'|'.join(ads_list)+r"))",href)
            if x:
                print x,len(x)
                # if re.match(ads,href):
                #     print link
                #     count += 1


    print 'ad count=',count,
    return count

def check_brokenlinks(raw,url):
    data = raw.text
    soup = BeautifulSoup(data,'html.parser')
    count = 0
    total_links  = 0
    total_external_links=0
    for link in soup.find_all('a',href=True):
            href = link.get('href')
            total_links+=1
            if  href.startswith('http://') or href.startswith('https://'):
                total_external_links +=1
                # now only allowed for external links
                # href = url+href
                hdr = {'User-Agent': 'Mozilla/5.0'}
                # header os mentioned because some robots don't allow bot to crawl their pages
                # print raw
                raw  = requests.head(url,headers=hdr)
                raw  = ((str(raw).split(' ')[1]).split(']')[0])
                raw = int(raw.split('[')[1])
                # print  raw
                if raw>300:
                    #  success response code are only b/w 200-300
                    count +=1
    print  'total_links =',total_links,'total_external_links =',total_external_links,'broken_links =',count,
    return  count

def check_cookie(raw,url):
    cookies = raw.cookies
    print cookies
    if cookies:
        print 'yes website installs cookie on client system'
        return 1
    else:
        return 0