# custom_exception_handler.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def exceptions_handler(exc, context):
    response = exception_handler(exc, context)
    
    # Handle specific errors not covered by default exception handler
    if response is None:
        return Response({'detail': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if response.status_code == 400:
        response.data['detail'] = 'Bad Request: Please check your data input.'
    elif response.status_code == 401:
        response.data['detail'] = 'Unauthorized: You must be authenticated to access this resource.'
    elif response.status_code == 403:
        response.data['detail'] = 'Forbidden: You do not have permission to perform this action.'
    elif response.status_code == 404:
        response.data['detail'] = 'Not Found: The requested resource was not found.'
    elif response.status_code == 500:
        response.data['detail'] = 'Internal Server Error: Please try again later.'

    return response
