from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from django.http import HttpRequest
import hashlib

class Postback(APIView):
    def get(self, request: HttpRequest) -> Response:

        partner_id = 0
        secret = ""
        if hashlib.new("sha256", f"{request.GET}-{partner_id}".encode(), secret).digest() == request.headers.get('X-FL-POSTBACK-SIGN'):

            print(request.GET)
            return Response(status=HTTP_200_OK)
        return Response(status=HTTP_403_FORBIDDEN)