from rest_framework import viewsets, permissions, generics, serializers
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer, UserSerializer
from .forms import ProductForm

# -----------------------------
# ✅ Frontend Views
# -----------------------------

def homepage(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def login_options(request):
    return render(request, 'login_options.html')

from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')  # Custom admin dashboard view
        else:
            return render(request, 'adminlogin.html', {'error': 'Invalid credentials or not admin.'})
    return render(request, 'adminlogin.html')


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            return render(request, 'user_login.html', {
                'error': 'Invalid credentials',
                'next': request.POST.get('next', '')
            })

    return render(request, 'user_login.html', {
        'next': request.GET.get('next', '')
    })


from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'User with this email already exists.'
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('user_login')  # or any success page
    return render(request, 'register.html')


@login_required
def review_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')
        if Review.objects.filter(product=product, user=request.user).exists():
            return render(request, 'review.html', {
                'product': product,
                'error': 'You already reviewed this product.'
            })
        Review.objects.create(product=product, user=request.user, rating=rating, feedback=feedback)
        return redirect('home')
    return render(request, 'review.html', {'product': product})
# -----------------------------
# ✅ Admin Panel Views
# -----------------------------

# Check if user is staff (admin)
def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    products = Product.objects.all()
    return render(request, 'admin_dashboard.html', {'products': products})

@user_passes_test(is_admin)
@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'addproduct.html', {'form': form})

@user_passes_test(is_admin)
@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'updateproduct.html', {'form': form})

@user_passes_test(is_admin)
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return render(request, 'delete.html', {'product': product})

# -----------------------------
# ✅ REST API Views
# -----------------------------

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'user_id': token.user_id,
            'is_staff': token.user.is_staff
        })

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        user = self.request.user
        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError("You already reviewed this product.")
        serializer.save(user=user)
