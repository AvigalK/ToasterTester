import requests as rq
import Server as srv

import test_parameters
import datetime

TOKEN = srv.TOKEN

if __name__ == '__main__':
    url = "https://inventory.mudra-server.com/api/v1/inventory/getFullExcel"
    # TODO replace with non hardcoded
    auth = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJJZCI6IjYyNmY3ZmJkMjliNWM2MjZmMzcwNWQzOSIsInJvbGVzIjoiUk9MRV9BRE1JTiIsImlhdCI6MTY1ODMyMzg2MSwiZXhwIjoxODE2MDAzODYxfQ.OH9Dglh368P1GI3RvsX6Y1fV_d6JSygVWACXH6X1IZc"
    headers = {"Authorization": auth}
    response = rq.get(url, headers=headers)
    print(response.status_code)
    now = datetime.datetime.now()
    time = now.strftime("%d%m%y_%H%M%S")

    with open(f"{test_parameters.main_dir}boards_from_server_{time}.csv", "wb+") as file:
        file.write(response.content)

    file.close()
