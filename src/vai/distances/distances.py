import json, math, os, urllib.request
TRACKS = {"ARV":(59.6567,12.6243),"AXE":(58.3995,13.5643),"BER":(62.4158,17.2165),"BON":(65.8152,21.708),"BOL":(61.3417,16.3351),"DAR":(63.02083,17.80417),"ESK":(59.4386,16.6143),"FAR":(59.40972,13.50222),"GAV":(60.6903,17.1342),"HAG":(61.7767,17.1078),"HAL":(56.6927,12.9259),"HOT":(64.112,16.2031),"JGR":(55.5735,13.0624),"KAL":(56.6669,16.2736),"KAS":(56.2355,14.8318),"LIN":(59.6001,15.2384),"LYC":(64.5563,18.6937),"MAP":(58.3597,15.2926),"OVI":(62.9975,14.396389),"ROM":(60.44972,15.49722),"RAT":(60.885833,15.118889),"SKE":(64.7324,20.9502),"SOL":(59.3668,17.9462),"SOT":(63.2907,18.6397),"TIN":(56.5099,15.0029),"UMA":(63.8102,20.1949),"VAG":(57.5043,14.1399),"VIS":(57.617,18.327),"ABY":(57.6495,12.0035),"AMA":(59.0306,12.7054),"AAR":(59.3906,12.1605),"ORO":(59.2181843,15.1578643),"OST":(63.1638,14.6713)}
ALIASES = {"solvalla":"SOL","åby":"ABY","aby":"ABY","jägersro":"JGR","jagersro":"JGR","axevalla":"AXE","bergsåker":"BER","bergsaker":"BER","halmstad":"HAL","mantorp":"MAP","eskilstuna":"ESK","färjestad":"FAR","farjestad":"FAR","gävle":"GAV","gavle":"GAV","kalmar":"KAL","romme":"ROM","örebro":"ORO","orebro":"ORO","umåker":"UMA","umaker":"UMA","östersund":"OST","ostersund":"OST","boden":"BON","årjäng":"AAR","arjang":"AAR","bollnäs":"BOL","bollnas":"BOL","rättvik":"RAT","rattvik":"RAT","dannero":"DAR","solänget":"SOT","solanget":"SOT","hagmyren":"HAG","arvika":"ARV","visby":"VIS","vaggeryd":"VAG","tingsryd":"TIN","skellefteå":"SKE","skelleftea":"SKE","karlshamn":"KAS","lindesberg":"LIN","lycksele":"LYC","hoting":"HOT","oviken":"OVI","åmål":"AMA","amal":"AMA"}
_c = {}
def road_km(a, b):
    if a == b: return 0
    k = tuple(sorted((a, b)))
    if k in _c: return _c[k]
    (la,lo),(lb,lob) = TRACKS[a], TRACKS[b]
    try:
        if os.environ.get("VAI_NO_OSRM"): raise RuntimeError("offline")
        u = f"https://router.project-osrm.org/route/v1/driving/{lo},{la};{lob},{lb}?overview=false"
        km = round(json.load(urllib.request.urlopen(u, timeout=10))["routes"][0]["distance"]/1000)
    except Exception:
        p1,p2 = math.radians(la), math.radians(lb)
        h = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(math.radians(lob-lo)/2)**2
        km = round(2*6371*math.asin(math.sqrt(h))*1.3)
    _c[k] = km; return km
