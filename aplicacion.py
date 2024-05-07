from flask import Flask, render_template, abort, redirect, request
import os
import requests

app = Flask(__name__)
port = os.getenv("PORT")

@app.route('/', methods=["GET","POST"])
def inicio():
    r=requests.get("http://api.ctan.es/v1/Consorcios/consorcios")
    consorcios=[]
    for i in r.json()["consorcios"]:
        consorcio = {}
        consorcio["id"] = i["idConsorcio"]
        consorcio["nombre"] = i["nombre"]
        consorcios.append(consorcio)
    if request.method == "GET":
        return render_template("inicio.html",consorcios=consorcios)
    elif request.method == "POST":
        consorcio = int(request.form.get("consorcio"))
        r=requests.get("http://api.ctan.es/v1/Consorcios/"+str(consorcio)+"/municipios/")
        municipios=[]
        for i in r.json()["municipios"]:
            municipio = {}
            municipio["id"] = i["idMunicipio"]
            municipio["nombre"] = i["datos"]
            municipios.append(municipio)
        return render_template("inicio.html",seleccionado=consorcio,consorcios=consorcios,municipios=municipios)

@app.route('/lineas', methods=["GET","POST"])
def lineas():
    consorcio = int(request.form.get("consorcio"))
    municipio = int(request.form.get("municipio"))
    fecha = request.form.get("fecha")
    r=requests.get("http://api.ctan.es/v1/Consorcios/"+str(consorcio)+"/municipios/"+str(municipio)+"/lineas")
    p=requests.get("http://api.ctan.es/v1/Consorcios/"+str(consorcio)+"/paradas")
    lineas=[]
    for i in r.json()["lineas"]:
        linea = {}
        linea["id"] = i["idLinea"]
        linea["nombre"] = i["nombre"]
        linea["modo"] = i["modo"]
        lineas.append(linea)
    paradas=[]
    for i in p.json()["paradas"]:
        parada={}
        if i["idMunicipio"] == str(municipio):
            parada["nombre"]=i["nombre"]
            parada["id"]=i["idParada"]
            parada["latitud"]=i["latitud"]
            parada["longitud"]=i["longitud"]
            paradas.append(parada)
    return render_template("lineas.html",lista=lineas,consorcio=consorcio,municipio=municipio,fecha=fecha,paradas=paradas)

@app.route('/horarios')
def horarios():
    error =False
    consorcio = int(request.args.get("consorcio"))
    linea = int(request.args.get("linea"))
    fecha= request.args.get("fecha")
    dia = fecha[8:]
    mes = fecha[5:7]
    r=requests.get("http://api.ctan.es/v1/Consorcios/"+str(consorcio)+"/horarios_lineas?dia="+str(dia)+"&frecuencia=&lang=ES&linea="+str(linea)+"&mes="+str(mes))
    n=requests.get("http://api.ctan.es/v1/Consorcios/"+str(consorcio)+"/lineas/"+str(linea)+"/noticias")
    p=requests.get("http://api.ctan.es/v1/Consorcios/"+str(consorcio)+"/lineas/"+str(linea)+"/paradas")
    idalv = []
    idafs = []
    try:
        for i in r.json()["planificadores"][0]["horarioIda"]:
            if i["frecuencia"] == "LV":
                idalv.append(i["horas"])
            else:
                idafs.append(i["horas"])
    except:
        error=True
    noticias=[]
    if n:
        for i in n.json()["noticias"]:
            noticia={}
            noticia["categoria"]=i["categoria"]
            noticia["titulo"]=i["titulo"]
            noticia["resumen"]=i["resumen"]
            noticias.append(noticia)
    paradas=[]
    for i in p.json()["paradas"]:
        parada={}
        parada["nombre"]=i["nombre"]
        paradas.append(parada)
    return render_template("horarios.html",idalv=idalv,idafs=idafs,error=error,noticias=noticias,paradas=paradas)

@app.route('/paradas')
def paradas():
    consorcio = int(request.args.get("consorcio"))
    parada = int(request.args.get("parada"))
    fecha= request.args.get("fecha")
    r=requests.get("http://api.ctan.es/v1/Consorcios/"+str(consorcio)+"/paradas/"+str(parada))
    datosparada=r.json()
    return render_template("paradas.html",parada=datosparada)


app.run("0.0.0.0",port,debug=True)