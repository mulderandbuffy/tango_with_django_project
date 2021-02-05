from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime

def index(request):
    #Query the database for categories
    #get top 5 categories in descending order (top 5)
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    visitor_cookie_handler(request)

    #Return rendered response
    response = render(request, 'rango/index.html', context=context_dict)
    return response


def about(request):
    #Construct a dictionary to pass the template engine as its context
    #Note the key boldmessage matches to the variable in the html doc!
    context_dict = {'boldmessage': 'This tutorial has been put together by Laura Henry'}

    visitor_cookie_handler(request)

    context_dict['visits'] = request.session['visits']
    print(context_dict)

    

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


@login_required
def add_category(request):
    form = CategoryForm()

    #POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        #Is the form valid
        if form.is_valid():
            #Save
            cat = form.save(commit=True)
            print(cat, cat.slug)
            return redirect('/rango/')
        else:
            #Print any errors to the console
            print(form.errors)
    
    #Render the form with any error messages
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    #Catgeory must exist, redirect otherwise
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:category', kwargs={'category_name_slug': category_name_slug}))

    else:
        print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


def register(request):
    #Was registration successful?
    registered = False

    #We process form data only if the request is POST
    if request.method == 'POST':
        #Get information from the raw form
        #Use both UserForm and UserProfileForm
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            #Save the data
            user = user_form.save()

            #Now we hash the password with set_password() and save the user object
            user.set_password(user.password)
            user.save()

            #UserProfile instance
            #Set attribute ourselvs so commit=False (delays save)
            profile = profile_form.save(commit=False)
            profile.user = user

            #Picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True #Successful registration
        
        else:
            #Invalid form
            print(user_form.errors, profile_form.errors)

    else:
        #Not a POST - create new blank forms for input
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',
                    context= {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

            
def user_login(request):
    #pull information from POST request
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        #Check account details match
        user = authenticate(username=username, password=password)

        if user:
            #Has the account been disabled?
            if user.is_active:
                #Log user in
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse('Your Rango account is disabled')
        else:
            #Invalid Details
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied")
    else:
        #Not a POST - display blank form
        return render(request, 'rango/login.html')


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    print('logging out')
    logout(request)
    print('success')
    return redirect(reverse('rango:index'))

#---------------------------HELPER FUNCTIONS-------------------------------------------------

def visitor_cookie_handler(request):
    #Get number of visits
    #Cookies.get
    #Returns integer value
    visits = int(get_server_side_cookie(request, 'visits','1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    #If it has been more than a day
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        #Update the last visit cookie
        request.session['last_visit'] = str(datetime.now())

    else:
        #Set last visit
        request.session['last_visit'] = last_visit_cookie

    #Set the visits cookie
    request.session['visits'] = visits


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val