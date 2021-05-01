from anntools import *
from pathlib import Path
import numpy as np


# c = Collection()

# c.load(Path("C:\\Users\\Ileana\\Documents\\Mi quinto\\IA\\Concurso\\Proyectos\\corpora\\2021\\ref\\training\\medline.1200.es.txt"))

PosiblesValoresFrases=['Action', 'Concept', 'Predicate', 'Reference']
PosiblesValoresRelaciones=['in-context', 'subject', 'same-as', 'is-a', 'target', 'entails', 'arg', 'domain', 'has-property', 'in-time', 'in-place', 'causes', 'part-of']
# print(len(PosiblesValoresRelaciones))
def DetectarPosicionInicioSpan(frase:Keyphrase):
    inicio,_=frase.spans[0]
    return len(frase.sentence.text[:inicio].strip().split())

def DetectarSpanPosicionInicio(posicion:int, texto:str):
    procesado=texto.strip().split()
    palabra=procesado[posicion]
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
        nuevalista=[False,]*tamannoMaximo
        frasesSinProcesar.append(nuevalista)

    for k in frases:
        indice1=categorias.index(k.label)
        indice2=DetectarPosicionInicioSpan(k)

        frasesSinProcesar[indice1][indice2]=True
    
    return frasesSinProcesar

def GenerarBajoNivelRelaciones(categorias:List[str], frases:List[Keyphrase],relaciones:List[Relation], tamannoMaximo:int):
    relacionesSinProcesar=[]
    for c in categorias:
        nuevalista=[([False,]*tamannoMaximo),]*tamannoMaximo
        relacionesSinProcesar.append(nuevalista)
    
    dicIDaFrase={}
    for element in frases:
        dicIDaFrase[element.id]=element
    
    for r in relaciones:
        indice1=categorias.index(r.label)
        indice2=DetectarPosicionInicioSpan(dicIDaFrase[r.origin])
        indice3=DetectarPosicionInicioSpan(dicIDaFrase[r.destination])

        relacionesSinProcesar[indice1][indice2][indice3]=True

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

# salida=ObtenerSalida(c.sentences[0])

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
    
    