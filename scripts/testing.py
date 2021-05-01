from anntools import *
from pathlib import Path


c = Collection()

c.load(Path("C:\\Users\\Ileana\\Documents\\Mi quinto\\IA\\Concurso\\Proyectos\\corpora\\2021\\ref\\training\\medline.1200.es.txt"))

PosiblesValoresFrases=['Action', 'Concept', 'Predicate', 'Reference']
PosiblesValoresRelaciones=['in-context', 'subject', 'same-as', 'is-a', 'target', 'entails', 'arg', 'domain', 'has-property', 'in-time', 'in-place', 'causes', 'part-of']
# print(len(PosiblesValoresRelaciones))

def ParseaABool(origen):
    listaFinal=[]
    for element in origen:
        if element>=0.5:
            listaFinal.append(True)
        else:
            listaFinal.append(False)
    return listaFinal
    
def DetectarPosicionInicioSpan(frase:Keyphrase):
    inicio,_=frase.spans[0]
    return len(frase.sentence.text[:inicio].strip().split())

def DetectarSpanPosicionInicio(posicion:int, texto:str):
    procesado=texto.strip().split()
    if(posicion>=len(procesado)):
        return (0,0)
    palabra=procesado[posicion].strip('. ,:;()-_?!¿}¡[]"\'{+*-/')
    inicio=0
    for i in range(posicion+1):
        inicio=texto.find(procesado[i],inicio)
    
    
    return (inicio,inicio+len(palabra))

def PreprocesarResultadoAltoNivel(oracion:Sentence):
    dicFrasesPartidas={}
    nuevaoracion=oracion.clone()
    nuevasFrases=[]
    nuevasRelaciones=[]
    contador=0
    for frase in nuevaoracion.keyphrases:
        if len(frase.spans)>1:
            recienAgregadas=[]
            for s in frase.spans:
                nuevospan=[]
                nuevospan.append(s)
                ultima=Keyphrase(nuevaoracion,frase.label,frase.id+500+contador,nuevospan)
                recienAgregadas.append(ultima)
                contador+=1
                dicFrasesPartidas[frase.id]=recienAgregadas
            nuevasFrases.extend(recienAgregadas)

            for i in range(len(recienAgregadas)-1):
                for e in range(i+1,len(recienAgregadas)):
                    nuevaRelacion1=Relation(nuevaoracion,recienAgregadas[i].id,recienAgregadas[e].id,"samebox")
                    nuevaRelacion2=Relation(nuevaoracion,recienAgregadas[e].id,recienAgregadas[i].id,"samebox")
                    nuevasRelaciones.append(nuevaRelacion1)
                    nuevasRelaciones.append(nuevaRelacion2)

        else:
            nuevasFrases.append(frase)

    for relacion in nuevaoracion.relations:
        origenesRelacion=[relacion.origin,]
        destinosRelacion=[relacion.destination,]

        if relacion.origin in dicFrasesPartidas.keys():
            origenesRelacion2=dicFrasesPartidas[relacion.origin]
            origenesRelacion=[]
            for element in origenesRelacion2:
                origenesRelacion.append(element.id)
        
        if relacion.destination in dicFrasesPartidas.keys():
            destinosRelacion2=dicFrasesPartidas[relacion.destination]
            destinosRelacion=[]
            for element in destinosRelacion2:
                destinosRelacion.append(element.id)

        for origen in origenesRelacion:
            for destino in destinosRelacion:
                nuevasRelaciones.append(Relation(nuevaoracion,origen,destino,relacion.label))
                if relacion.label=="same-as":
                    nuevasRelaciones.append(Relation(nuevaoracion,destino,origen,relacion.label))

    nuevaoracion.keyphrases=nuevasFrases
    nuevaoracion.relations=nuevasRelaciones
    return nuevaoracion


def GenerarBajoNivelFrases(categorias:List[str], frases:List[Keyphrase], tamannoMaximo:int):
    frasesSinProcesar=[]
    for element in categorias:
        nuevalista=[]
        for i in range(tamannoMaximo):
            nuevalista.append(False)
        frasesSinProcesar.append(nuevalista)

    for k in frases:
        indice1=categorias.index(k.label)
        indice2=DetectarPosicionInicioSpan(k)

        frasesSinProcesar[indice1][indice2]=True
    
    return frasesSinProcesar

def GenerarBajoNivelRelaciones(categorias:List[str], frases:List[Keyphrase],relaciones:List[Relation], tamannoMaximo:int):
    relacionesSinProcesar=[]
    for c in categorias:
        nuevalista1=[]
        for i in range(tamannoMaximo):
            nuevalista2=[]
            for e in range(tamannoMaximo):
                nuevalista2.append(False)
            nuevalista1.append(nuevalista2)
        relacionesSinProcesar.append(nuevalista1)
    
    dicIDaFrase={}
    for element in frases:
        dicIDaFrase[element.id]=element
    
    for r in relaciones:
        indice1=categorias.index(r.label)
        indice2=DetectarPosicionInicioSpan(dicIDaFrase[r.origin])
        indice3=DetectarPosicionInicioSpan(dicIDaFrase[r.destination])
        if indice1==0 and indice2==0 and indice3==9:
            indice1=categorias.index(r.label)
            indice2=DetectarPosicionInicioSpan(dicIDaFrase[r.origin])
            indice3=DetectarPosicionInicioSpan(dicIDaFrase[r.destination])
        print(relacionesSinProcesar[0][0][9])

        relacionesSinProcesar[indice1][indice2][indice3]=True
        if(relacionesSinProcesar[0][0][9]):
            print(indice1)
            print(indice2)
            print(indice3)

    return relacionesSinProcesar

def GenerarBajoNivelBool(categoriasFrases:List[str], categoriasRelaciones:List[str], frases:List[Keyphrase], relaciones:List[Relation], tamannoMaximo:int):
    frasessSinProcesar=GenerarBajoNivelFrases(categoriasFrases,frases,tamannoMaximo)
    relacionesSinProcesar=GenerarBajoNivelRelaciones(categoriasRelaciones,frases,relaciones,tamannoMaximo)

    salidaBool=[]
    for i in frasessSinProcesar:
        for elemento in i:
            salidaBool.append(elemento)

    for i in relacionesSinProcesar:
        for e in i:
            for elemento in e:
                salidaBool.append(elemento)

    return salidaBool

def TamannoFrasesBajoNivel(cantidadCategorias:int, tammanoMaximo:int):
    return cantidadCategorias*tammanoMaximo

def TamannoRelacionesBajoNivel(cantidadCategorias:int, tammanoMaximo:int):
    return tamannoMaximo*tammanoMaximo*cantidadCategorias

def ObtenerEntrada(oracion:Sentence):
    return oracion.text

def ObtenerSalidaFinalBool(oracion:Sentence):
    oracion2=PreprocesarResultadoAltoNivel(oracion)
    categoriasRelaciones=PosiblesValoresRelaciones.copy()
    categoriasRelaciones.append("samebox")
    salidaBool=GenerarBajoNivelBool(PosiblesValoresFrases,categoriasRelaciones,oracion2.keyphrases, oracion2.relations, 100)
    return salidaBool

def AgregarCombinacion(lista, idinicio,idfinal):
    for elem in lista:
        if idinicio in elem and idfinal in elem:
            return
        if idinicio in elem:
            elem.append(idfinal)
            elem.sort()
            return
        if idfinal in elem:
            elem.append(idinicio)
            elem.sort()
            return
    elem.append([idinicio,idfinal].sort())

def BoolAFrasesMio(oracion:Sentence, lista:List[bool], categorias:List[str], tamannoMaximo:int):
    countID=0
    listaFrases=[]
    for i in range(len(categorias)):
        for j in range(tamannoMaximo):
            if(lista[i*tamannoMaximo+j]):
                nuevaFrase=Keyphrase(oracion,categorias[i],countID,[DetectarSpanPosicionInicio(j,oracion.text)])
                countID+=1
                listaFrases.append(nuevaFrase)
    
    return listaFrases

def BoolARelacionesMio(oracion:Sentence, lista:List[bool], Frases:List[Keyphrase],categoriasRelaciones:List[str], tamannoMaximo:int):
    listarelaciones=[]
    dicFrases={}
    for i in Frases:
        dicFrases[i.spans[0]]=i
        
    for i in range(len(categoriasRelaciones)):
        for e in range((tamannoMaximo)):
            for j in range((tamannoMaximo)):
                if(lista[i*tamannoMaximo*tamannoMaximo+e*tamannoMaximo+j]):
                    spanOrigen=DetectarSpanPosicionInicio(e,oracion.text)
                    spanDestino=DetectarSpanPosicionInicio(j,oracion.text)
                    if spanOrigen==(0,0) or spanDestino==(0,0) or not (spanOrigen in dicFrases.keys() and spanDestino in dicFrases.keys()):
                        continue
                    nuevaRelacion=Relation(oracion,dicFrases[DetectarSpanPosicionInicio(e,oracion.text)].id,dicFrases[DetectarSpanPosicionInicio(j,oracion.text)].id,categoriasRelaciones[i])
                    listarelaciones.append(nuevaRelacion)
    return listarelaciones

def OracionIntermedia(oracion:Sentence,lista:List[bool], categoriasFrases:List[str], categoriasRelaciones:List[str],tamannoMaximo:int):
    nuevaOracion=oracion.clone()
    nuevaOracion.keyphrases=[]
    nuevaOracion.relations=[]

    copiaRelaciones=categoriasRelaciones.copy()
    if copiaRelaciones[-1]!="samebox":
        copiaRelaciones.append("samebox")

    frasesBajoNivel=lista[:TamannoFrasesBajoNivel(len(categoriasFrases),tamannoMaximo)]
    relacionesBajoNivel=lista[TamannoFrasesBajoNivel(len(categoriasFrases),tamannoMaximo):]

    nuevasFrases=BoolAFrasesMio(nuevaOracion, frasesBajoNivel,categoriasFrases, tamannoMaximo)
    nuevasRelaciones=BoolARelacionesMio(nuevaOracion,relacionesBajoNivel,nuevasFrases,copiaRelaciones,tamannoMaximo)

    nuevaOracion.keyphrases=nuevasFrases
    nuevaOracion.relations=nuevasRelaciones

    return nuevaOracion

def MezclaBaseKeyphrases(frase1:Keyphrase, frase2:Keyphrase):
    spansFinales=frase1.spans.copy()
    spansNuevos=[]
    for s in frase2.spans:
        if s in frase1.spans:
            continue
        spansNuevos.append(s)
    spansFinales.extend(spansNuevos)
    
    nuevaFrase=Keyphrase(frase1.sentence,frase1.label,frase1.id,spansFinales)
    return nuevaFrase

def ComparaKeyphrases(frase1:Keyphrase, frase2:Keyphrase):
    menorspan1=99999
    for i in frase1.spans:
        inicio,_=i
        if inicio<menorspan1:
            menorspan1=inicio

    menorspan2=99999
    for i in frase2.spans:
        inicio,_=i
        if inicio<menorspan2:
            menorspan2=inicio

    return menorspan1<menorspan2

def mezclaKeyphrases(frase1:Keyphrase, frase2:Keyphrase):
    if ComparaKeyphrases(frase1,frase2):
        return MezclaBaseKeyphrases(frase1,frase2)
    return MezclaBaseKeyphrases(frase2,frase1)

def PostProcesaOracionIntermedia(oracion:Sentence):
    dicFrases={}
    dicSpans={}
    dicUnida={}
    dicSameAs={}
    frasesFinales=[]
    relacionesFinales=[]
    for f in oracion.keyphrases:
        dicFrases[f.id]=f
        for s in f.spans:
            dicSpans[s]=f

    for r in oracion.relations:
        if r.origin==r.destination:
            continue
        if r.label=="samebox":    
            if r.origin>r.destination:
                temp=r.origin
                r.origin=r.destination
                r.destination=temp
                mezcladas=mezclaKeyphrases(dicFrases[r.origin],dicFrases[r.destination])
                dicFrases[r.origin]=mezcladas
                dicFrases[r.destination]=mezcladas
            dicUnida[r.destination]=r.origin

        elif r.label=="same-as":
            if not ComparaKeyphrases(r.from_phrase,r.to_phrase):
                temp=r.origin
                r.origin=r.destination
                r.destination=temp
                if((r.origin,r.destination) in dicSameAs.keys()):
                    continue
                dicSameAs[(r.origin,r.destination)]=True
                relacionesFinales.append(r)
        
        else:
            relacionesFinales.append(r)

    dicFrasesFinal={}

    for k in dicFrases.keys():
        dicFrasesFinal[dicFrases[k].id]=dicFrases[k]

    for k in dicFrasesFinal.keys():
        frasesFinales.append(dicFrasesFinal[k])
        
    nuevaOracion=oracion.clone()
    nuevaOracion.keyphrases=frasesFinales
    nuevaOracion.relations=relacionesFinales

    relacionesFinalesDic={}
    for r in relacionesFinales:
        if r.origin in dicFrases.keys() and dicFrases[r.origin].id!=r.origin:
            r.origin=dicFrases[r.origin].id
        if r.destination in dicFrases.keys() and dicFrases[r.destination].id!=r.destination:
            r.destination=dicFrases[r.destination].id
        relacionesFinalesDic[(r.origin,r.destination,r.label)]=r
        
    relacionesFinales=[]
    for k in relacionesFinalesDic.keys():
        if relacionesFinalesDic[k].origin!=relacionesFinalesDic[k].destination:
            relacionesFinalesDic[k].sentence=nuevaOracion
            relacionesFinales.append(relacionesFinalesDic[k])
    nuevaOracion.relations=relacionesFinales

    return nuevaOracion

                



def BoolASentenceMio(oracion:Sentence, lista:[bool], categorias:List[str], relaciones:List[str],tamannoMaximo:int):
    nuevaOracion=OracionIntermedia(oracion,lista,categorias,relaciones,tamannoMaximo)
    nuevaOracion2=PostProcesaOracionIntermedia(nuevaOracion)
    return nuevaOracion2


def BoolASentence(oracion:Sentence, lista:List[bool], categorias:List[str], relaciones:List[str],tamannoMaximo:int):
    keyphrases = []
    texto = oracion.text
    for i in range(len(categorias)):
        for j in range(tamannoMaximo):
            if lista[i*tamannoMaximo + j]:
                span = DetectarSpanPosicionInicio(j,texto)
                frase = Keyphrase(sentence = oracion, label=categorias[i], id = len(keyphrases), spans = [span])
                keyphrases.append(frase)
    dictspansfrases = {value.spans[0]: value for value in keyphrases}
    finalfrases = len(categorias)*tamannoMaximo
    kephrasesacombinar = []
    relations = []
    for i in range(len(relaciones)):
        for j in range(tamannoMaximo):
            for g in range(tamannoMaximo):
                if lista[finalfrases + i*(tamannoMaximo**2) + j*tamannoMaximo + g]:
                    spaninicio = DetectarSpanPosicionInicio(j,texto)
                    spanfinal = DetectarSpanPosicionInicio(g,texto)
                    if relaciones[i] is "samebox":
                        AgregarCombinacion(kephrasesacombinar,dictspansfrases[spaninicio].id,dictspansfrases[spanfinal].id)
                    else:   
                        relacion = Relation(sentence = oracion, origin = dictspansfrases[spaninicio].id, destination = dictspansfrases[spanfinal].id, label = relaciones[i])
                        relations.append(relacion)
    for comb in kephrasesacombinar:
        for i in range(1,len(comb)):
            keyphrases[comb[0]].spans.append(keyphrases[comb[i]].spans[0])
            keyphrases[comb[0]].spans.sort()
            keyphrases.pop(comb[i])
            relations = [elem for elem in relations if elem.origin != comb[i] and elem.destination != comb[i]]
    nuevaoracion = oracion.clon()
    nuevaoracion.keyphrases = keyphrases
    nuevaoracion.relations = relations
    return nuevaoracion
    
salida=ObtenerSalidaFinalBool(c.sentences[1])

oracionAnalizada=c.sentences[1]
copia=PosiblesValoresRelaciones.copy()
if copia[-1]!="samebox":
    copia.append("samebox")

denuevo=BoolASentenceMio(c.sentences[1],salida,PosiblesValoresFrases,copia,100)
print(denuevo)

# frases={}
# relaciones={}
# for s in c.sentences:
#     for f in s.keyphrases:
#         frases[f.label]=True
#     for r in s.relations:
#         relaciones[r.label]=True
# print("|--------|")
# print(frases.keys())
# print("--------")
# print(relaciones.keys())
# print("|--------|")
    
    
