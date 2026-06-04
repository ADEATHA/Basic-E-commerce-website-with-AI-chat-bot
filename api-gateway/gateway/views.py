from django.http import HttpResponse, JsonResponse
import requests
import json as json_lib

SERVICES = {
    'staff':    'http://staff:8000',
    'customer': 'http://customer:8000',
    'product':  'http://product:8000',   # Generic DDD product_service
    'ai':       'http://ai_service:8005',   # AI microservice (segment, recommend, chat)
}

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def proxy_request(request, service_name, path):
    if service_name not in SERVICES:
        return JsonResponse({'error': f'Service "{service_name}" not found'}, status=404)

    # Forward directly to the downstream service path
    target_url = f"{SERVICES[service_name]}/{path}"

    # 1. Handle CORS Preflight (OPTIONS)
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    try:
        headers = {'Content-Type': 'application/json'}
        if request.method == 'GET':
            response_raw = requests.get(target_url, params=request.GET, timeout=60)
        elif request.method == 'POST':
            try:
                body = json_lib.loads(request.body)
            except Exception:
                body = dict(request.POST)
            response_raw = requests.post(target_url, data=json_lib.dumps(body), headers=headers, timeout=60)
        else:
            return JsonResponse({'error': 'Method not supported'}, status=405)

        # 2. Build response with CORS headers
        response = HttpResponse(
            response_raw.content,
            status=response_raw.status_code,
            content_type=response_raw.headers.get('Content-Type', 'application/json'),
        )
        response['Access-Control-Allow-Origin'] = '*'
        return response

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': 'Service unavailable', 'details': str(e)}, status=503)

