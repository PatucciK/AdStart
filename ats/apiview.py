from rest_framework.views import APIView
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework import status
from .serializers import CallBeginSerializer
from rest_framework import serializers

class CallBeginAPIView(APIView):

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = CallBeginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Успех"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_422_UNPROCESSABLE_ENTITY)

