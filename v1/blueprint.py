from flask import Blueprint
from flask_restful import Api

from v1.resources.images import ImagesInfoResource
from v1.resources.images import ImagesInfoAsyncResource
from v1.resources.images import BatchPredictResource

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

####### IMAGES INFO ENDPOINT #######
api.add_resource(ImagesInfoResource, '/v1/images_info/')
api.add_resource(ImagesInfoAsyncResource, '/v1/images_info_async/')

####### BATCH PREDICT ENDPOINT #####
api.add_resource(BatchPredictResource, '/v1/batch_predict/')
