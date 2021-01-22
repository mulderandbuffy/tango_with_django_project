from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    #Construct a dictionary to pass the template engine as its context
    #Note the key boldmessage matches to the variable in the html doc!
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}

    #Return rendered response
    #We make use of the shortcut function to make lives easier
    #First parameter is the template
    return(render(request, 'rango/index.html', context=context_dict))

def about(request):
    return HttpResponse("Rango says here is the about page. <a href='/rango/'>Index</a>")