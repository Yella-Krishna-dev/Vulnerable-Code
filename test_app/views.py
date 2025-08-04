from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.contrib.auth.models import User
from .models import Product, Order
import json


@require_http_methods(["GET"])
def search_products(request):
    search_term = request.GET.get('search', '')
    
    query = f"SELECT * FROM test_app_product WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    
    products = []
    for row in results:
        products.append({
            'id': row[0],
            'name': row[1],
            'price': str(row[2]),
            'description': row[3]
        })
    
    return JsonResponse({'products': products})


@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    data = json.loads(request.body)
    username = data.get('username', '')
    password = data.get('password', '')
    
    query = f"SELECT id, username, email FROM auth_user WHERE username = '{username}' AND password = '{password}'"
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        user = cursor.fetchone()
    
    if user:
        return JsonResponse({
            'success': True,
            'user_id': user[0],
            'username': user[1],
            'email': user[2]
        })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid credentials'})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_order(request):
    order_id = request.GET.get('order_id', '')
    
    query = f"DELETE FROM test_app_order WHERE id = {order_id}"
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        affected_rows = cursor.rowcount
    
    return JsonResponse({
        'success': True,
        'message': f'Deleted {affected_rows} order(s)',
        'query_executed': query
    })


@require_http_methods(["GET"])
def get_user_orders(request):
    user_id = request.GET.get('user_id', '')
    
    query = f"""
    SELECT o.id, u.username, p.name, o.quantity, o.total_price 
    FROM test_app_order o 
    JOIN auth_user u ON o.user_id = u.id 
    JOIN test_app_product p ON o.product_id = p.id 
    WHERE o.user_id = {user_id}
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    
    orders = []
    for row in results:
        orders.append({
            'order_id': row[0],
            'username': row[1],
            'product_name': row[2],
            'quantity': row[3],
            'total_price': str(row[4])
        })
    
    return JsonResponse({'orders': orders})


@csrf_exempt
@require_http_methods(["PUT"])
def update_product(request):
    data = json.loads(request.body)
    product_id = data.get('product_id', '')
    new_price = data.get('new_price', '')
    
    query = f"UPDATE test_app_product SET price = {new_price} WHERE id = {product_id}"
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        affected_rows = cursor.rowcount
    
    return JsonResponse({
        'success': True,
        'message': f'Updated {affected_rows} product(s)',
        'query_executed': query
    })


@require_http_methods(["GET"])
def advanced_search(request):
    name = request.GET.get('name', '')
    min_price = request.GET.get('min_price', '0')
    max_price = request.GET.get('max_price', '999999')
    
    query = f"""
    SELECT * FROM test_app_product 
    WHERE name LIKE '%{name}%' 
    AND price >= {min_price} 
    AND price <= {max_price}
    ORDER BY price DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
    
    products = []
    for row in results:
        products.append({
            'id': row[0],
            'name': row[1],
            'price': str(row[2]),
            'description': row[3]
        })
    
    return JsonResponse({
        'products': products,
        'query_executed': query
    })


@require_http_methods(["GET"])
def get_product_details(request):
    product_id = request.GET.get('product_id', '')
    
    query = f"SELECT id, name, price, description FROM test_app_product WHERE id = {product_id}"
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    
    if result:
        return JsonResponse({
            'id': result[0],
            'name': result[1],
            'price': str(result[2]),
            'description': result[3]
        })
    else:
        return JsonResponse({'error': 'Product not found'})


@require_http_methods(["GET"])
def check_product_exists(request):
    product_name = request.GET.get('product_name', '')
    
    query = f"SELECT COUNT(*) FROM test_app_product WHERE name = '{product_name}'"
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        count = cursor.fetchone()[0]
    
    return JsonResponse({
        'exists': count > 0,
        'count': count,
        'query_executed': query
    }) 