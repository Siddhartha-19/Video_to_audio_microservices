import os, requests
import datetime
def validate_token(request):
    if "Authorization" not in request.headers:
        return None,"cannot find the token"
    header=request.headers["Authorization"]
    print(os.environ.get("AUTH_SERVICE_ADDRESS"))
    response=requests.post(
       url= "http://"+'127.0.0.1:3000'+"/validate",
        headers={"Authorization":header}
    )
    if response.status_code==200:
        decoded=response.json()
        return decoded,None
    else:
        return None,"some problem"
        

        








