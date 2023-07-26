import os

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

            collumns = ['Style', 'Noice', 'Place']
            models = []

            for col in collumns:
                model = Net()
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'./ML_Models/model{col}.pytorch')
                state_dict = torch.load(file_path, map_location='cpu')
                model.load_state_dict(state_dict)
                model = model.cpu()
                model.eval()
                models.append(model)

            file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'..{serializer.data["file"]}')
            im = io.imread(file_path)
            im = torch.tensor(im, dtype=torch.float32)
            im.transpose_(0, 2)
            im = torch.unsqueeze(im, 0)

            results = []

            for ml in models:
                results.append(ml(im).tolist())

            output_data = [i[0].index(max(i[0])) for i in results]

            data = Data.objects.last()

            print(data.file.url)

            output_json = {
                'file': file_path,
                'Style': output_data[0],
                'Noice': output_data[1],
                'Place': output_data[2]
            }

            return Response(output_json)
