import pymongo
from pymongo import MongoClient
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')


def iniciarMongoDB():
    url = 'mongodb+srv://natgsarabia:Fsu6t4y5jUfhYQxI@contaminacionbcn.xbosddo.mongodb.net/'

    myClient = pymongo.MongoClient(url)

    myDB = myClient['contaminacionBCN']
    return myDB


#1  FUNCIÓN EXTRAER NOMBRES BARRIOS
def encontrarBarrios(myDB):
    collection=myDB['Estaciones']
    listaBarrios=collection.distinct('Nom_barri')
    return listaBarrios

#2  FUNCIÓN EXTRAER UBICACION ESTACIONES
def informacionEstacion(myDB,barrio): 
    collection=myDB['Estaciones']
    query={'Estacio': barrio}

    informacionEstacion=[]
  
    iter=collection.find(query,{'_id':0, 'nom_cabina':1,'ubicacio':1})
    i=0
    
    for doc in iter:
        if i<1:
            doc=dict(doc)
            valoresDoc=doc.items()
            listaDatos=list(valoresDoc)
            informacionEstacion.append((listaDatos[0][1],listaDatos[1][1]))
            i+=1

    return informacionEstacion


#3 FUNCIÓN BUSQUEDA RESULTADO
def find(myDB,codigoEstacion, diaMes):
    collection=myDB['CalidadAire']
    query={'ESTACIO': codigoEstacion, 'DIA':diaMes}
  
    codigosContaminantesActivos=[]
    cantidadContaminanteAire=[]
    
    iter=collection.find(query,{'_id':0,'CODI_CONTAMINANT':1,'H12':1})
    i=0
    for doc in iter:
        doc=dict(doc)
        valoresDoc=doc.items()
        listaDatos=list(valoresDoc)
        codigosContaminantesActivos.insert(i,listaDatos[0][1])
        cantidadContaminanteAire.insert(i,listaDatos[1][1])
    
    return codigosContaminantesActivos,cantidadContaminanteAire

#4 ENCONTRAR NOMBRE BARRIO
def checkCodigoBarrio(barrioHTML):
    barrios = {
        "el Poblenou":4,
        "Sants":42,
        "la Nova Esquerra de l'Eixample" : 43,
        "la Vila de Gracia" : 44,
        "Sant Pere, Santa Caterina i la Ribera" : 50,
        "la Vall d'Hebron" : 54,
        "Pedralbes":57,
        "Vallvidrera-el Tibidabo-les Planes":58
    }

    return barrios.get(barrioHTML)


#5 FUNCIÓN BUSQUEDA CONTAMINANTES 
def buscarContaminantes(myDB,listaContaminantes):
    nombresContamimantes=[]
    collection=myDB['Contaminantes']
    i=0
    for contaminante in listaContaminantes:
        query={'Codi_Contaminant': contaminante}
        iter=collection.find(query,{'_id':0,'Desc_Contaminant':1,'Unitats':1})
        for dato in iter:
            informacionContaminante=dict(dato)
            valoresDoc=informacionContaminante.items()
            listaDatos=list(valoresDoc)
            nombresContamimantes.insert(i,(listaDatos[0][1],listaDatos[1][1]))
            i+=1
           
    return(nombresContamimantes)





@app.route('/paginaInicio', methods=["GET","POST"])

def index():
    myDB=iniciarMongoDB()
    if request.method=="GET":
        listaBarrios=encontrarBarrios(myDB)
        print(listaBarrios)
        print("___________________________________")
        return render_template("paginaInicio.html",listaBarrios=listaBarrios)

    elif request.method=="POST":
        barrioHTML=request.form.get("barrioHTML")
        barrio=checkCodigoBarrio(barrioHTML)
        print('Nombre barrio '+barrioHTML+"     Codigo: "+str(barrio))
        print("___________________________________")

        diaMes=request.form.get("dia")
        print('Dia mes escogido: '+str(diaMes))
        print("___________________________________")

        informacionCentro=informacionEstacion(myDB,barrio)
        codigosContaminantesActivos,cantidadContaminanteAire=find(myDB, barrio, int(diaMes))
        informacionContaminantes=buscarContaminantes(myDB,codigosContaminantesActivos)
        print(codigosContaminantesActivos)
        
        
    
        return render_template("resultados.html",diaMes=diaMes,barrioHTML=barrioHTML,nombreCabina=informacionCentro[0][0],ubicacionCabina=informacionCentro[0][1],\
                               codigosContaminantesActivos=codigosContaminantesActivos,cantidadContaminanteAire=cantidadContaminanteAire,\
                                informacionContaminantes=informacionContaminantes, bucle=int(len(codigosContaminantesActivos)))

if __name__=='__main__':
    app.run(debug=True)








