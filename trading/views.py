from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import uuid
from .models import UserProfile, Transaction
from .serializers import (
    UserSerializer, UserProfileSerializer, TransactionSerializer,
    RegisterSerializer, ChangePasswordSerializer, ResetPasswordSerializer,
    ConfirmResetPasswordSerializer
)

reset_tokens = {}


def get_gold_price():
    return round(random.uniform(1800, 2000), 2)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'User registered successfully',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, 
                           status=status.HTTP_401_UNAUTHORIZED)
    
    user = authenticate(username=user.username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    else:
        return Response({'error': 'Invalid credentials'}, 
                       status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            reset_token = str(uuid.uuid4())
            reset_tokens[reset_token] = {
                'user_id': user.id,
                'email': email,
                'expires': timezone.now() + timedelta(hours=1)
            }
            return Response({
                'message': 'If the email exists, a reset link has been sent',
                'reset_token': reset_token
            })
        except User.DoesNotExist:
            return Response({
                'message': 'If the email exists, a reset link has been sent'
            })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ConfirmResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']
        
        if reset_token not in reset_tokens:
            return Response({'error': 'Invalid or expired reset token'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        reset_data = reset_tokens[reset_token]
        
        if timezone.now() > reset_data['expires']:
            del reset_tokens[reset_token]
            return Response({'error': 'Reset token has expired'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=reset_data['user_id'])
            user.set_password(new_password)
            user.save()
            
            del reset_tokens[reset_token]
            
            return Response({'message': 'Password reset successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, 
                           status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        
        if not request.user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def authenticate():
    token = request.headers.get('Authorization')
    if not token or token not in user_tokens:
        return None
    return User.query.get(user_tokens[token])


@api_view(['GET'])
@permission_classes([AllowAny])
def price(request):
    return Response({'gold_price': get_gold_price()})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_gold(request):
    amount = request.data.get('amount')
    
    if not amount or float(amount) <= 0:
        return Response({'error': 'Invalid amount'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    amount = float(amount)
    price = get_gold_price()
    total_cost = amount * price
    
    user_profile = request.user.userprofile
    
    if user_profile.cash_balance < total_cost:
        return Response({'error': 'Insufficient funds'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    user_profile.cash_balance -= total_cost
    user_profile.gold_balance += amount
    user_profile.save()
    
    transaction = Transaction.objects.create(
        user=request.user,
        type='buy',
        amount=amount,
        price=price
    )
    
    return Response({
        'message': f'Bought {amount} gold at {price} per unit',
        'cash_balance': float(user_profile.cash_balance),
        'gold_balance': float(user_profile.gold_balance),
        'transaction': TransactionSerializer(transaction).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sell_gold(request):
    amount = request.data.get('amount')
    
    if not amount or float(amount) <= 0:
        return Response({'error': 'Invalid amount'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    amount = float(amount)
    user_profile = request.user.userprofile
    
    if amount > user_profile.gold_balance:
        return Response({'error': 'Insufficient gold balance'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    price = get_gold_price()
    total_gain = amount * price
    
    user_profile.cash_balance += total_gain
    user_profile.gold_balance -= amount
    user_profile.save()
    
    transaction = Transaction.objects.create(
        user=request.user,
        type='sell',
        amount=amount,
        price=price
    )
    
    return Response({
        'message': f'Sold {amount} gold at {price} per unit',
        'cash_balance': float(user_profile.cash_balance),
        'gold_balance': float(user_profile.gold_balance),
        'transaction': TransactionSerializer(transaction).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def balance(request):
    user_profile = request.user.userprofile
    return Response({
        'cash_balance': float(user_profile.cash_balance),
        'gold_balance': float(user_profile.gold_balance)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})
    except:
        return Response({'message': 'Logged out successfully'}) 