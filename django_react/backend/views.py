from rest_framework.response import Response
from rest_framework.views import APIView
import torch

from .serializers import *
from .ML_Models.model3 import Net
from skimage import io


# Create your views here.
class DataCreate(APIView):
    def post(self, request):
        serializer = DataSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            print(serializer.data)

            collumns = ['Style', 'Noice', 'Place']
            models = []

            for col in collumns:
                model = Net()
                model.load_state_dict(torch.load(f'/Users/nikita/PycharmProjects/back/django_react/backend/ML_Models'
                                                 f'/model{col}.pytorch'))
                model.eval()
                models.append(model)

            im = io.imread(f'/Users/nikita/PycharmProjects/back/django_react{serializer.data["file"]}')
            im = torch.tensor(im, dtype=torch.float32)
            im.transpose_(0, 2)
            im = torch.unsqueeze(im, 0)

            results = []

            for ml in models:
                results.append(ml(im).tolist())

            output_data = [i[0].index(max(i[0])) for i in results]

            output_json = {
                'file': serializer.data["file"],
                'Style': output_data[0],
                'Noice': output_data[1],
                'Place': output_data[2]
            }

            return Response(output_json)
