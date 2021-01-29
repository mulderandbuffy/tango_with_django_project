from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page

def index(request):
    #Query the database for categories
    #get top 5 categories in descending order (top 5)
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    #Return rendered response
    #We make use of the shortcut function to make lives easier
    #First parameter is the template
    return(render(request, 'rango/index.html', context=context_dict))

def about(request):
    #Construct a dictionary to pass the template engine as its context
    #Note the key boldmessage matches to the variable in the html doc!
    context_dict = {'boldmessage': 'This tutorial has been put together by Laura Henry'}

    #Return rendered response
    #We make use of the shortcut function to make lives easier
    #First parameter is the template
    return(render(request, 'rango/about.html', context=context_dict))


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        #Retrieve category if it exists
        category = Category.objects.get(slug=category_name_slug)

        #Get associated pages
        #Returns list of pages or empty list
        pages = Page.objects.filter(category=category)

        #Add filter results to the context dictionary as 'pages'
        context_dict['pages'] = pages
        context_dict['category'] = category
        #Context dict used to verify that the category exists
    except Category.DoesNotExist:
        #Context dict is empty and the no catgeory message is displayed
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context = context_dict)
