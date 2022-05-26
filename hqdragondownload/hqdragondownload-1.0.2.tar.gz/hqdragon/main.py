import argparse
import requests
from lxml import html
from fpdf import FPDF
import datetime
import os
import time

headers= {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
}

url = "https://hqdragon.com/"

query_search = "pesquisa?nome_hq="

my_parse = argparse.ArgumentParser(description="CLI para baixar hq's.")

my_parse.add_argument("--search", action="store", type=str, help="Pesquisar.")
my_parse.add_argument("--url", action="store", type=str, help="Url da hq.")
my_parse.add_argument("--output", action="store", type=str, help="Nome de saida do pdf.")
my_parse.add_argument("--option", action="store", type=int, help="Opção da pesquisa.")
my_parse.add_argument("--no-pdf", action="store", type=bool, help="Salva apenas as imagens.", default=False)
my_parse.add_argument("--cap", action="store", type=list, help="Define os capitulos.")

args = my_parse.parse_args()

if args.search:
    page = requests.get(headers=headers, url=url+query_search+args.search)
    tree = html.fromstring(page.content)
    titles = tree.xpath("//div[@class='col-sm-6 col-md-3 lista-hqs']/a/text()")
    links = tree.xpath("//div[@class='col-sm-6 col-md-3 lista-hqs']/a/@href")[::2]
    if len(links) == 0:
        print('Nenhum resultado encontrado.')
    else:
        if args.option != None:
            page = requests.get(headers=headers, url=links[args.option])
            tree = html.fromstring(page.content)
            caps = tree.xpath("//table[@class='table table-bordered']/tbody/tr/td/a/@href")[::-1]
        else:
            for idx,title in enumerate(titles):
                print(f'{idx} - {title}')
            
            idx = int(input('Escolha -> '))
            page = requests.get(headers=headers, url=links[idx])
            tree = html.fromstring(page.content)
            caps = tree.xpath("//table[@class='table table-bordered']/tbody/tr/td/a/@href")[::-1]

        if args.output != None:
            if '//' in args.output or '/' in args.output:
                print('output recebe apenas o nome do arquivo.')
                exit()
        file_name = args.output if args.output != None else datetime.datetime.now().strftime('%d_%m_%Y__%H_%M_%S')
        print("[+]Downloading...[+]")
        for idx,cap in enumerate(caps):
            if args.cap != None:
                if int(cap.split('/')[-1]) not in [int(x) for x in args.cap if x != ',']:
                    continue
            page=requests.get(cap, headers=headers)
            tree=html.fromstring(page.content)
            pags=[x.replace('Pag. ','') for x in tree.xpath('//*[@id="paginas"]/option/text()')]
            path_name =file_name+'_'+cap.split('/')[-1]
            os.mkdir(path_name)
            for pag in pags:
                adj_file = "0"+pag if int(pag) < 10 else pag
                img_src=tree.xpath(f'//img[@pag="{pag}"]/@src')[0]
                img_data = requests.get(img_src,headers=headers).content
                with open(path_name+'/'+f'image{pag}.jpg', 'wb') as img:
                    img.write(img_data)

                time.sleep(1.5)

            if args.no_pdf == False or args.no_pdf == None:
                paths = [x for x in os.listdir('.') if file_name in x and '.pdf' not in x]
                for path in paths:
                    imgs = os.listdir(path)
                    pdf = FPDF()
                    for img in imgs:
                        pdf.add_page()
                        pdf.image(path+'/'+img,0,0,210,297)
                    pdf.output(f'{path}.pdf',"F")
                for path in paths:
                    imgs = os.listdir(path)
                    for img in imgs:
                        os.remove(path+'/'+img)
                    os.rmdir(path)

                print("[+]Finished...[+]")

elif args.url:
    page = requests.get(headers=headers, url=args.url)
    tree = html.fromstring(page.content)
    caps = tree.xpath("//table[@class='table table-bordered']/tbody/tr/td/a/@href")[::-1]

    if args.output != None:
        if '//' in args.output or '/' in args.output:
            print('output recebe apenas o nome do arquivo.')
            exit()
    file_name = args.output if args.output != None else datetime.datetime.now().strftime('%d_%m_%Y__%H_%M_%S')
    print("[+]Downloading...[+]")
    for idx,cap in enumerate(caps):
        if args.cap != None:
            if int(cap.split('/')[-1]) not in [int(x) for x in args.cap if x != ',']:
                continue
        page=requests.get(cap, headers=headers)
        tree=html.fromstring(page.content)
        pags=[x.replace('Pag. ','') for x in tree.xpath('//*[@id="paginas"]/option/text()')]
        path_name =file_name+'_'+cap.split('/')[-1]
        os.mkdir(path_name)
        for pag in pags:
            adj_file = "0"+pag if int(pag) < 10 else pag
            img_src=tree.xpath(f'//img[@pag="{pag}"]/@src')[0]
            img_data = requests.get(img_src,headers=headers).content
            with open(path_name+'/'+f'image{pag}.jpg', 'wb') as img:
                img.write(img_data)

            time.sleep(1.5)

        if args.no_pdf == False or args.no_pdf == None:
            paths = [x for x in os.listdir('.') if file_name in x and '.pdf' not in x]
            for path in paths:
                imgs = os.listdir(path)
                pdf = FPDF()
                for img in imgs:
                    pdf.add_page()
                    pdf.image(path+'/'+img,0,0,210,297)
                pdf.output(f'{path}.pdf',"F")
            for path in paths:
                imgs = os.listdir(path)
                for img in imgs:
                    os.remove(path+'/'+img)
                os.rmdir(path)

            print("[+]Finished...[+]")

else:
    template ="""
    Exemplos:
    1. $python .\main.py --search "superman" --option 1 --no-pdf True
    2. $python .\main.py --search "superman" --option 1 --cap 2 --output "superman"
    3. $python .\main.py --search "superman" --option 1 --cap 1,2 --no-pdf True
    4. $python .\main.py --url "https://hqdragon.com/hq/nju4mq/6581-a-morte-do-superman" --cap 2 --output "superman"

    $python .\main.py -h
    """
    print(template)