from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json


# --- Insufficient Authentication/Authorization ---
@csrf_exempt
@require_http_methods(["POST"])
def sell_gold(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    amount = data.get('amount')
    # Missing: No verification if authenticated user owns this account
    return process_gold_sale(user_id, amount)


def process_gold_sale(user_id, amount):
    return JsonResponse({"message": f"Gold sale for user {user_id} processed: {amount}g"})


# --- Weak Session Validation ---
@require_http_methods(["GET"])
def get_current_user(request):
    session_token = request.headers.get('Authorization')
    # No validation of token expiry, signature, etc.
    user_data = decode_token(session_token)  # Trusts any token
    return JsonResponse({"user_id": user_data['user_id']})


def decode_token(token):
    return {'user_id': 'admin'}


# --- SQL Injection ---
@require_http_methods(["GET"])
def update_gold(request):
    user_input = request.GET.get('user_id')
    query = f"UPDATE accounts SET gold_balance = 0 WHERE user_id = {user_input}"
    return JsonResponse({"query": query})


# --- Race Condition OTP ---
otp_cache = {"123": "999999"}


@csrf_exempt
@require_http_methods(["POST"])
def validate_otp(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')
    otp = data.get('otp')
    stored_otp = otp_cache.get(user_id)
    if stored_otp == otp:
        del otp_cache[user_id]
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failure"}, status=403) 