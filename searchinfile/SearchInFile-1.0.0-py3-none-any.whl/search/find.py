
class MyFile():
    def __init__(self, nomeArquivo):
        try:
            self.arquivo = open(f'{nomeArquivo}', 'r', encoding='utf8')
        except:
            pass
        else:
            self.nome = nomeArquivo

            self.totalPalavras = []
            for e in self.arquivo:
                e = e.rstrip()
                self.totalPalavras.append(e.split(" "))  # PALAVRAS POR LINHA
                
            self.arquivo.close()
    
    def exist(self):
        try :
            self.arquivo = open(f'{self.nome}', 'r', encoding='utf8')
        except:
            self.status = False
        else:
            self.arquivo.close()
            self.status = True
        
        return self.status

    def qtdPalavras(self):
        # QUANTIDADE DE PALAVRAS NO ARQUIVO
        self.quantidadePalavras = 0
        for e in self.totalPalavras:
            self.quantidadePalavras += len(e)

        return self.quantidadePalavras


    def maioresPalavras(self):
        # AS 5 MAIORES PALAVRAS (QTD CARACTERES)
        totalPalavrasNew = []
        for linha in self.totalPalavras:
            listaTemp = []
            for palavra in linha:
                for caractere in palavra:
                    if '.' in palavra:
                        listaDeCaracteres = list(palavra)
                        listaDeCaracteres.remove('.')
                        palavra = "".join(listaDeCaracteres)
                    elif '...' in palavra:
                        listaDeCaracteres = list(palavra)
                        listaDeCaracteres.remove('...')
                        palavra = "".join(listaDeCaracteres)
                    elif ',' in palavra:
                        listaDeCaracteres = list(palavra)
                        listaDeCaracteres.remove(',')
                        palavra = "".join(listaDeCaracteres)
                    elif '"' in palavra:
                        listaDeCaracteres = list(palavra)
                        listaDeCaracteres.remove('"')
                        palavra = "".join(listaDeCaracteres)
                    elif ';' in palavra:
                        listaDeCaracteres = list(palavra)
                        listaDeCaracteres.remove(';')
                        palavra = "".join(listaDeCaracteres)
                    elif '(' in palavra:
                        listaDeCaracteres = list(palavra)
                        listaDeCaracteres.remove('(')
                        palavra = "".join(listaDeCaracteres)
                    elif ')' in palavra:
                        listaDeCaracteres = list(palavra)
                        listaDeCaracteres.remove(')')
                        palavra = "".join(listaDeCaracteres)
                    else:
                        listaTemp.append(palavra)
                listaTemp.append(palavra)
            totalPalavrasNew.append(listaTemp)


        self.cincoMaiores = {}

        MaioresDeCadaLinha = {}

        for linha in totalPalavrasNew:
            palavraQtd = {}
            for palavra in linha:
                qtdCaracteres = len(palavra)
                palavraQtd[f'{palavra}'] = qtdCaracteres

            maiorDaLinha = max(palavraQtd.values())

            for palavra, qtd in palavraQtd.items():
                if qtd == maiorDaLinha and qtd not in MaioresDeCadaLinha.values():
                    MaioresDeCadaLinha[f'{palavra}'] = qtd


        maioresDaLinha = list(MaioresDeCadaLinha.values())
        maioresDaLinha.sort(reverse=True)
        maioresDaLinha = maioresDaLinha[:5]

        for palavra, qtd in MaioresDeCadaLinha.items():
            if qtd in maioresDaLinha and len(self.cincoMaiores) < 5:
                self.cincoMaiores[f'{palavra}'] = qtd


        return self.cincoMaiores

            
    def vogalFrequente(self):
        qtdA = 0
        qtdE = 0
        qtdI = 0
        qtdO = 0
        qtdU = 0

        for linha in self.totalPalavras:
            for palavra in linha:
                for caractere in palavra:
                    if 'a' == caractere.lower():
                        qtdA+=1
                    elif 'e' == caractere.lower():
                        qtdE+=1
                    elif 'i' == caractere.lower():
                        qtdI+=1
                    elif 'o' == caractere.lower():
                        qtdO+=1
                    elif 'u' == caractere.lower():
                        qtdU+=1

        self.vogais = {'Vogal A': qtdA, 'Vogal E': qtdE, 'Vogal I': qtdI, 'Vogal O': qtdO, 'Vogal U': qtdU}

        maiorQtd = max(self.vogais.values())

        for tipo, qtd in self.vogais.items():
            if qtd == maiorQtd:
                self.vogalMais = tipo


        return self.vogalMais


        # A LINHA QUE TEM A PALAVRA 'ÇÃO'
    def findString(self, literal):
        self.linhasAchadas = []

        for linha in self.totalPalavras:
            for palavra in linha:
                if literal.lower() in palavra.lower():
                    self.linhasAchadas.append(" ".join(linha))


        return self.linhasAchadas
    

