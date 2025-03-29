import jwt

import datetime

d = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=10000)

t = jwt.encode({"sub": "yes", "else": "yes", "exp": d}, "YES", algorithm="HS256")
print(jwt.decode(t, "YES", algorithms=["HS256"]))
print(jwt.decode(None, "YES", algorithms=["HS256"]))