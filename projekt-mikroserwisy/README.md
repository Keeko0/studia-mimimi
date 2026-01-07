wymagania: docker + docker compose

rabbitmq:
http://localhost:8080
login + haslo: guest

service a:
http://localhost:8000/docs

service b:
http://localhost:8001/docs

pytest jest osobno dla service_a i b

how2:
1. w cd \projekt-mikroserwisy odpal komende:
        docker compose up --build
2. poczekaj az sie wszystko odpali
3. wejdz na serwis b i skorzystaj z POSTa 
        https://media.istockphoto.com/id/1977329451/photo/diverse-businesspeople-smiling-while-standing-arm-in-arm-in-an-office.jpg?s=612x612&w=0&k=20&c=FvQFfKBc7iAUPz48tdU_hzvTPCdGSntmdlceDeUuKRs=
4. wejdz na serwis a i uzyj GEta