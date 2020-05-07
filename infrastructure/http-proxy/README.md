### Starting the HTTP Proxy:
```
docker pull ryantanaka/iris:http-proxy
docker container run -d -e PYTHONUNBUFFERED=1 -p 8000:8000 ryantanaka/iris:http-proxy 
```

### Viewing HTTP Proxy Logs:
```
docker logs iris-http-proxy
```

or to *watch*:
```
docker logs -f iris-http-proxy
```

After running the above command, output showing cache hits/misses can be seen:
```
------------------------------------------------------------
cache hit: http://uc-staging/~tanaka/inputs/Ulysses_by_James_Joyce.txt
[START] copy to self.wfile: ./cache/uc-staging-~tanaka-inputs-Ulysses_by_James_Joyce.txt.cached
127.0.0.1 - - [06/May/2020 23:01:26] "GET http://uc-staging/~tanaka/inputs/Ulysses_by_James_Joyce.txt HTTP/1.1" 200 -
[COMPLETE] copy: ./cache/uc-staging-~tanaka-inputs-Ulysses_by_James_Joyce.txt.cached | 0.0020s
resp time: 0.0021
------------------------------------------------------------
cache hit: http://uc-staging/~tanaka/inputs/Dracula_by_Bram_Stoker.txt
[START] copy to self.wfile: ./cache/uc-staging-~tanaka-inputs-Dracula_by_Bram_Stoker.txt.cached
127.0.0.1 - - [06/May/2020 23:01:26] "GET http://uc-staging/~tanaka/inputs/Dracula_by_Bram_Stoker.txt HTTP/1.1" 200 -
[COMPLETE] copy: ./cache/uc-staging-~tanaka-inputs-Dracula_by_Bram_Stoker.txt.cached | 0.0016s
resp time: 0.0018
------------------------------------------------------------
cache miss: http://uc-staging/~tanaka/inputs/Visual_Signaling_By_Signal_Corps_United_States_Army.txt
[START] req: http://uc-staging/~tanaka/inputs/Visual_Signaling_By_Signal_Corps_United_States_Army.txt
[COMPLETE] req: http://uc-staging/~tanaka/inputs/Visual_Signaling_By_Signal_Corps_United_States_Army.txt | 0.0018s
[START] write: ./cache/uc-staging-~tanaka-inputs-Visual_Signaling_By_Signal_Corps_United_States_Army.txt.cached.temp
[COMPLETE] write: ./cache/uc-staging-~tanaka-inputs-Visual_Signaling_By_Signal_Corps_United_States_Army.txt.cached.temp | 0.0048s
[START] copy to self.wfile: ./cache/uc-staging-~tanaka-inputs-Visual_Signaling_By_Signal_Corps_United_States_Army.txt.cached
127.0.0.1 - - [06/May/2020 23:01:26] "GET http://uc-staging/~tanaka/inputs/Visual_Signaling_By_Signal_Corps_United_States_Army.txt HTTP/1.1" 200 -
[COMPLETE] copy: ./cache/uc-staging-~tanaka-inputs-Visual_Signaling_By_Signal_Corps_United_States_Army.txt.cached | 0.0006s
resp time: 0.0077
------------------------------------------------------------
```
