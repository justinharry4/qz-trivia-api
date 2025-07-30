from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET", "HEAD", "OPTIONS"])
def health_check(request):
    return Response({"status": "OK"}, status.HTTP_200_OK)
