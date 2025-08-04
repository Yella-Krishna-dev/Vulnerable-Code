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

# In-memory storage for reset tokens (in production, use Redis or database)
reset_tokens = {}


def get_gold_price():
    """Simulate gold price between 1800 and 2000"""
    return round(random.uniform(1800, 2000), 2)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
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
    """Login user"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Allow login with username or email
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
    """Request password reset"""
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # Generate reset token
            reset_token = str(uuid.uuid4())
            reset_tokens[reset_token] = {
                'user_id': user.id,
                'email': email,
                'expires': timezone.now() + timedelta(hours=1)
            }
            # In production, send email here
            return Response({
                'message': 'If the email exists, a reset link has been sent',
                'reset_token': reset_token  # Remove in production
            })
        except User.DoesNotExist:
            # Don't reveal if email exists
            return Response({
                'message': 'If the email exists, a reset link has been sent'
            })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password with token"""
    serializer = ConfirmResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']
        
        if reset_token not in reset_tokens:
            return Response({'error': 'Invalid or expired reset token'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        reset_data = reset_tokens[reset_token]
        
        # Check if token has expired
        if timezone.now() > reset_data['expires']:
            del reset_tokens[reset_token]
            return Response({'error': 'Reset token has expired'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Update user password
        try:
            user = User.objects.get(id=reset_data['user_id'])
            user.set_password(new_password)
            user.save()
            
            # Remove used reset token
            del reset_tokens[reset_token]
            
            return Response({'message': 'Password reset successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, 
                           status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password for authenticated user"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        
        # Verify current password
        if not request.user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_gold_price_view(request):
    """Get current gold price"""
    return Response({'gold_price': get_gold_price()})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_gold(request):
    """Buy gold"""
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
    
    # Update balances
    user_profile.cash_balance -= total_cost
    user_profile.gold_balance += amount
    user_profile.save()
    
    # Create transaction record
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
    """Sell gold"""
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
    
    # Update balances
    user_profile.cash_balance += total_gain
    user_profile.gold_balance -= amount
    user_profile.save()
    
    # Create transaction record
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
def get_balance(request):
    """Get user's balance"""
    user_profile = request.user.userprofile
    return Response({
        'cash_balance': float(user_profile.cash_balance),
        'gold_balance': float(user_profile.gold_balance)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    """Get user's transaction history"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user (delete token)"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})
    except:
        return Response({'message': 'Logged out successfully'}) 