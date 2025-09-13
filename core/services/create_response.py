from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status

def create_response(data=None, errors=None, message="", status_code=status.HTTP_200_OK):
    """
    Helper function to create a standardized JSON response with a numeric status code.

    This function constructs a JSON response with a consistent structure, 
    including a status indicator, a message, and optional data or error details.
    The HTTP status code is returned as a number instead of using the constants 
    defined in the status module.

    Args:
        data (dict, optional): The data to be included in the response. Defaults to None.
        errors (dict or list, optional): Error details to be included in the response. Defaults to None.
        message (str, optional): A descriptive message for the response. Defaults to "".
        status_code (int, optional): The HTTP status code for the response. Defaults to status.HTTP_200_OK (200).

    Returns:
        rest_framework.response.Response: A Response object containing the formatted JSON.

    Example Usage (Success):
        return create_response(data={"name": "John Doe", "age": 30}, message="User retrieved successfully")

    Example Usage (Error):
        return create_response(errors={"name": ["This field is required"]}, message="User creation failed", status_code=status.HTTP_400_BAD_REQUEST)

    Response Structure:
        {
            "status": "success" | "error",  # Indicates whether the request was successful or not
            "message": str,                 # A descriptive message
            "data": dict,                   # (Optional) The response data
            "errors": dict or list,          # (Optional) Error details
            "status_code": int              # The HTTP status code
        }
    """
    response_data = {
        "status": "success" if errors is None else "error",  
        "message": message,
        "status_code": status_code 
    }
    if data:
        response_data["data"] = data
    if errors:
        response_data["errors"] = errors

    return Response(response_data, status=status_code)  