from rest_framework.views import APIView
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework import status
from .serializers import CallBeginSerializer
from rest_framework import serializers
from offers.models import LeadWall, OfferWebmaster, Webmaster

class CallBeginAPIView(APIView):

    def post(self, request: HttpRequest, *args, **kwargs):
        serializer = CallBeginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            offer_webmaster = OfferWebmaster.objects.get(phone=serializer.validated_data['manager_number'])
            
            processing_status = 'new'
            lead_status = 'on_hold'
        
            description = serializer.validated_data.get('description', '')
            description_extra = ", ".join(filter(None, [serializer.validated_data.get(f'q{i}') for i in range(1, 6)]))

            for i in LeadWall.objects.filter(phone=self.phone).exclude(id=self.id):
                if i.offer_webmaster.phone != self.offer_webmaster.phone: 
                    continue
            # if LeadWall.objects.filter(phone=self.phone).exclude(id=self.id).exclude(offer_webmaster=self.offer_webmaster).exists():
                self.processing_status = 'duplicate'
                self.status = 'cancelled'

            LeadWall.objects.create(
                offer_webmaster=offer_webmaster, # через таблицу
                name="Call",
                phone=serializer.validated_data['client_number'],
                description=f"[Создан через Звонки] {description}" if description else "[Создан через Звонки]",
                description_extra=description_extra,
                sub_1=serializer.validated_data.get('sub_1'),
                sub_2=serializer.validated_data.get('sub_2'),
                sub_3=serializer.validated_data.get('sub_3'),
                sub_4=serializer.validated_data.get('sub_4'),
                sub_5=serializer.validated_data.get('sub_5'),
                processing_status=processing_status,
                status=lead_status
            ).save()



            return Response({"detail": "Успех"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_422_UNPROCESSABLE_ENTITY)

