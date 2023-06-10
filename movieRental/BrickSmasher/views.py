from django.db.models import F
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Movie, Rental


def home(request):
    return render(request, 'home.html')


def account_creation(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            error_message = f"User with email {email} already exists."
            return render(request, 'account_creation.html', {'message': error_message})
        except User.DoesNotExist:
            user = User(first_name=first_name, last_name=last_name, email=email)
            user.save()
            success_message = "Account created successfully!"
            return render(request, 'account_creation.html', {'message': success_message})

    return render(request, 'account_creation.html')


def manage_movies(request):
    if request.method == 'POST':
        movie_title = request.POST.get('movie_title')

        if not movie_title or movie_title.isspace():
            error_message = "Movie title is required."
            return render(request, 'manage_movies.html', {'message': error_message})

        try:
            movie = Movie.objects.get(title=movie_title)
            error_message = f"Movie with title {movie_title} already exists."
            return render(request, 'manage_movies.html', {'message': error_message})
        except Movie.DoesNotExist:
            movie = Movie(title=movie_title, stock=1, checked_out=0)
            movie.save()
            movies = Movie.objects.all()
            return render(request, 'manage_movies.html', {'movies': movies})

    movies = Movie.objects.all()
    return render(request, 'manage_movies.html', {'movies': movies})


def rent_return_movies(request):
    if request.method == 'POST':
        member_email = request.POST.get('member_email')

        try:
            user = User.objects.get(email=member_email)
            rented_movies = Rental.objects.filter(user=user)
            available_movies = Movie.objects.exclude(rental__user=user).filter(stock__gt=F('checked_out'))

            context = {
                'member': user,
                'rented_movies': rented_movies,
                'available_movies': available_movies
            }
            return render(request, 'rent_return_movies.html', context)
        except User.DoesNotExist:
            message = 'Member not found.'
            return render(request, 'rent_return_movies.html', {'message': message})

    return render(request, 'rent_return_movies.html')


@csrf_exempt
def dbUser(request):
    if request.method == 'GET':
        email = request.GET.get('email')

        try:
            user = User.objects.get(email=email)
            data = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
            return JsonResponse(data)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    elif request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        try:
            user = User.objects.get(email=email)
            return JsonResponse({'error': 'User with email already exists'}, status=400)
        except User.DoesNotExist:
            user = User(first_name=first_name, last_name=last_name, email=email)
            user.save()
            data = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
            return JsonResponse(data, status=201)

@csrf_exempt
def dbMovie(request):
    if request.method == 'GET':
        movies = Movie.objects.all()
        movie_list = []
        for movie in movies:
            movie_data = {
                'id': movie.id,
                'title': movie.title,
                'stock': movie.stock,
                'checked_out': movie.checked_out
            }
            movie_list.append(movie_data)
        return JsonResponse(movie_list, safe=False)

    elif request.method == 'POST':
        action = request.POST.get('action')

        if action == 'new':
            title = request.POST.get('title')
            if not title or title.isspace():
                return JsonResponse({'error': 'Movie title is required'}, status=400)

            try:
                movie = Movie.objects.get(title=title)
                return JsonResponse({'error': f'Movie with title {title} already exists'}, status=400)
            except Movie.DoesNotExist:
                movie = Movie(title=title, stock=1, checked_out=0)
                movie.save()

        elif action == 'add':
            movie_id = request.POST.get('movie_id')
            try:
                movie = Movie.objects.get(id=movie_id)
                movie.stock += 1
                movie.save()
            except Movie.DoesNotExist:
                return JsonResponse({'error': 'Invalid movie ID'}, status=400)

        elif action == 'remove':
            movie_id = request.POST.get('movie_id')
            try:
                movie = Movie.objects.get(id=movie_id)
                if movie.stock > 1:
                    movie.stock -= 1
                    movie.save()
                else:
                    movie.delete()
            except Movie.DoesNotExist:
                return JsonResponse({'error': 'Invalid movie ID'}, status=400)

        movies = Movie.objects.all()
        movie_list = []
        for movie in movies:
            movie_data = {
                'id': movie.id,
                'title': movie.title,
                'stock': movie.stock,
                'checked_out': movie.checked_out
            }
            movie_list.append(movie_data)
        return JsonResponse(movie_list, safe=False)

@csrf_exempt
def dbRent(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        movie_id = request.GET.get('movie_id')

        try:
            if user_id and movie_id:
                rental = Rental.objects.get(user_id=user_id, movie_id=movie_id)
                rental_data = {
                    'id': rental.id,
                    'user_id': rental.user_id,
                    'movie_id': rental.movie_id,
                    'rented_at': rental.rented_at
                }
                return JsonResponse([rental_data], safe=False)
            elif user_id:
                rentals = Rental.objects.filter(user_id=user_id)
                rental_list = []
                for rental in rentals:
                    rental_data = {
                        'id': rental.id,
                        'user_id': rental.user_id,
                        'movie_id': rental.movie_id,
                        'rented_at': rental.rented_at
                    }
                    rental_list.append(rental_data)
                return JsonResponse(rental_list, safe=False)
            elif movie_id:
                rentals = Rental.objects.filter(movie_id=movie_id)
                rental_list = []
                for rental in rentals:
                    rental_data = {
                        'id': rental.id,
                        'user_id': rental.user_id,
                        'movie_id': rental.movie_id,
                        'rented_at': rental.rented_at
                    }
                    rental_list.append(rental_data)
                return JsonResponse(rental_list, safe=False)
            else:
                rentals = Rental.objects.all()
                rental_list = []
                for rental in rentals:
                    rental_data = {
                        'id': rental.id,
                        'user_id': rental.user_id,
                        'movie_id': rental.movie_id,
                        'rented_at': rental.rented_at
                    }
                    rental_list.append(rental_data)
                return JsonResponse(rental_list, safe=False)
        except Rental.DoesNotExist:
            return JsonResponse({'error': 'Rental not found'}, status=404)

    elif request.method == 'POST':
        user_id = request.POST.get('user_id')
        movie_id = request.POST.get('movie_id')
        action = request.POST.get('action')

        if action == 'rent':
            try:
                user = User.objects.get(id=user_id)
                movie = Movie.objects.get(id=movie_id)
                rental_count = Rental.objects.filter(user_id=user_id).count()
                if rental_count >= 3:
                    return JsonResponse({'error': 'Maximum rental limit reached'}, status=400)
                if movie.checked_out >= movie.stock:
                    return JsonResponse({'error': 'No copies available for rental'}, status=400)
                rental = Rental(user=user, movie=movie)
                rental.save()
                movie.checked_out += 1
                movie.save()
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid user ID'}, status=400)
            except Movie.DoesNotExist:
                return JsonResponse({'error': 'Invalid movie ID'}, status=400)

        elif action == 'return':
            try:
                rental = Rental.objects.get(user_id=user_id, movie_id=movie_id)
                movie = Movie.objects.get(id=movie_id)
                rental.delete()
                movie.checked_out -= 1
                movie.save()
            except Rental.DoesNotExist:
                return JsonResponse({'error': 'Rental not found'}, status=400)
            except Movie.DoesNotExist:
                return JsonResponse({'error': 'Invalid movie ID'}, status=400)

        rentals = Rental.objects.all()
        rental_list = []
        for rental in rentals:
            rental_data = {
                'id': rental.id,
                'user_id': rental.user_id,
                'movie_id': rental.movie_id,
                'rented_at': rental.rented_at
            }
            rental_list.append(rental_data)
        return JsonResponse(rental_list, safe=False)
