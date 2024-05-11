from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Q

def Base(request):

    if request.user.groups.filter(name="vendedor").exists():
        grupo = "vendedor"
    elif request.user.groups.filter(name="bodeguero").exists():
        grupo = "bodeguero"
    elif request.user.groups.filter(name="contador").exists():
        grupo = "contador"
    else:
        grupo = "cliente"

    usuario = request.user
    carrito = Carrito.objects.filter(estado=False,usuario=usuario).first()
    contador=Carrito_item.objects.filter(id_carrito=carrito).count()

    context = {
        "grupo": grupo,
        "contador":contador
    }

    return render(request,'base.html', context)

# VISTA LOGIN
def Login(request):

    return render(request,'login.html')


def Woi(request):

    return render(request, 'woi.html')


# VISTA LANDING
def Landing(request):

    usuario = request.user
    carrito = Carrito.objects.filter(estado=False,usuario=usuario).first()
    contador=Carrito_item.objects.filter(id_carrito=carrito).count()

    context = {
        "contador" : contador
    }
    return render(request, 'landing.html',context)

# formulario para registrarse
class FormularioRegistro(UserCreationForm):
    email = forms.EmailField(
        max_length=254, help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
# VISTA REGISTRO
def Register(request):

    if request.method == "POST":
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("landing")
    else:
        form = FormularioRegistro()

    return render(request, 'registration/register.html',{"form":form})
    
#VISTA PARA AGREGAR NUEVOS PRODUCTOS
@login_required
def Agregar(request):
    if request.user.groups.filter(name="vendedor").exists():
        grupo = "vendedor"
    elif request.user.groups.filter(name="bodeguero").exists():
        grupo = "bodeguero"
    elif request.user.groups.filter(name="contador").exists():
        grupo = "contador"
    else:
        grupo = "cliente"


    cat = Categoria.objects.raw("select * from website_categoria")

    if request.method == "POST":
        nombre_producto = request.POST["nombre"]
        precio = request.POST["precio"]
        descripcion = request.POST["descripción"]
        categoria = request.POST["categoria"]
        objCategoria = Categoria.objects.get(id_categoria=categoria)
        objProducto = Producto.objects.create(
            nombre_producto=nombre_producto,
            precio=precio,
            descripcion=descripcion,
            id_categoria=objCategoria,
        )

        imagen = request.FILES.get("imagen")
        Imagen_producto.objects.create(
            imagen_producto=imagen,
            id_producto=objProducto
        )
        context = {
            "mensaje": "Oferta publicada exitosamente",
            "grupo": grupo,
            "cat": cat,
            }
        return render(request, "agregar.html", context)
    else:
        context = {
            "grupo": grupo,
            "cat": cat,
            }
        return render(request, "agregar.html", context)
    
def Catalogo(request):
    usuario = request.user
    carrito = Carrito.objects.filter(estado=False,usuario=usuario).first()
    contador=Carrito_item.objects.filter(id_carrito=carrito).count()

    productos = Producto.objects.all()
    marcas = Marca.objects.all()
    categorias = Categoria.objects.all()

    palabra_clave = request.GET.get('palabra_clave')
    tipo_producto = request.GET.get('tipo_producto')
    marca = request.GET.get('marca')
    precio = request.GET.get('precio')
    stock_disponible = request.GET.get('stock_disponible')

    if palabra_clave:
        productos = productos.filter(Q(nombre_producto__icontains=palabra_clave) | Q(descripcion__icontains=palabra_clave))
    if tipo_producto:
        productos = productos.filter(id_categoria=tipo_producto)
    if marca:
        productos = productos.filter(id_marca=marca)
    if precio==1:
        productos = productos.order_by('precio')
    elif precio==2:
        productos = productos.order_by('-precio')

    context = {     
        "productos": productos,
        "marcas": marcas,
        "categorias" : categorias,
        "contador" : contador
    }   

    return render(request, 'catalogo.html', context)

@login_required
def VerCarrito(request):

    carro = Carrito.objects.filter(usuario=request.user,estado=False).first()
    contCarrito=Carrito_item.objects.filter(id_carrito=carro)
    contador=Carrito_item.objects.filter(id_carrito=carro).count()
    subTotal= sum([item.cantidad* item.id_producto.precio for item in contCarrito])
    total=subTotal+2500
    context={
        'contCarrito':contCarrito,
        'subTotal':subTotal,
        'total':total,
        'carro':carro,
        'contador':contador,
    }

    return render(request, 'carrito.html',context )

@login_required
def AñadirCarritoCompra(request):
    if request.method == 'POST':
        usuario=request.user.id
        id_producto=request.POST['id_producto']
        prod=Producto.objects.filter(id_producto=id_producto).first()
        cantidad=request.POST['cantidad']
        if Carrito.objects.filter(usuario=usuario,estado=False).first() == None:
            Carrito.objects.create(usuario=usuario)

        carrito = Carrito.objects.filter(usuario=usuario,estado=False).first()
        if Carrito_item.objects.filter(id_carrito=carrito,id_producto=prod).first():
            carrito_item=Carrito_item.objects.filter(id_carrito=carrito,id_producto=id_producto).first()
            carrito_item.cantidad+=int(cantidad)
            carrito_item.save()
            messages.success(request,'Agregado correctamente')
            return redirect('catalogo')
        else:
            Carrito_item.objects.create(id_carrito=carrito,id_producto=prod,cantidad=cantidad)
            messages.success(request,'Agregado correctamente')
            return redirect('catalogo')

    return render(request,'catalogo.html') 

@login_required
def ActualizarCantidadCarrito(request):
    if request.method=='POST':
        usuario=request.user
        car= request.POST.get('id_carrito')
        cantidad= request.POST.get('cantidad')
        prod = request.POST.get('id_producto')
        carItem=Carrito_item.objects.filter(id_carrito=car,id_producto=prod).first()
        carItem.cantidad=cantidad
        carItem.save()
        return redirect('VerCarrito')
    return render(request,'mainCarrito.html')

@login_required
def QuitarCarritoCompra(request):
    if request.method == 'POST':
        usuario=request.user
        carrito = Carrito.objects.filter(usuario=usuario,estado=False)
        if request.POST.get('borrarUno'):
            id_producto=request.POST['id_producto']
            id_carrito=request.POST['id_carrito']
            carrito_item = Carrito_item.objects.filter(id_carrito=id_carrito,id_producto=id_producto)
            carrito_item.delete()
            messages.success(request,'Eliminado correctamente')
            return redirect('VerCarrito')        
        elif request.POST.get('borrarTodo'):
            carrito.delete()
            Carrito.objects.create(estado=False,usuario=usuario)
            messages.success(request,'Eliminado Correctamente')
            return redirect('VerCarrito')
    return render(request,'mainCarrito.html')
