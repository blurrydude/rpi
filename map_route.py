import requests
import json

gkey = "AIzaSyC5hXF812g3uaht1RyAdhymWcRN5KeGDXg"

addresses = []
priority_addresses = []
do_priority = True

def lookup(address):
    address_lookup_url = "https://maps.googleapis.com/maps/api/geocode/json?address="+address+'&key='+gkey
    response = requests.get(address_lookup_url)
    data = json.loads(response.text)
    print(address)
    print(response.text)
    lat = data["results"][0]["geometry"]["location"]["lat"]
    lng = data["results"][0]["geometry"]["location"]["lng"]
    coords = str(lat)+","+str(lng)
    return coords

def get_distance(address1, address2):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+address1+"&destinations="+address2+"&units=imperial&key="+gkey
    response = requests.get(url)
    data = json.loads(response.text)
    print(address1+", "+address2)
    print(response.text)
    if "rows" not in data.keys() or len(data["rows"]) == 0 or "elements" not in data["rows"][0].keys() or len(data["rows"][0]["elements"]) == 0 or "distance" not in data["rows"][0]["elements"][0].keys():
        return 1000000
    return round(data["rows"][0]["elements"][0]["distance"]["value"] / 1609.34, 2)

def get_distance_matrix(addresses):
    address_distances = []
    for x in range(len(addresses)):
        address1 = addresses[x]
        distances = []
        for y in range(len(addresses)):
            address2 = addresses[y]
            if address1 == address2:
                continue
            distance = get_distance(address1, address2)
            distances.append({
                "address": address2,
                "distance": distance
            })
        address_distances.append({
            "address": address1,
            "distances": distances
        })
    return address_distances

def log(message, first=False):
    if first is True:
        file = open("map_route_log.txt", mode='w')
    else:
        file = open("map_route_log.txt", mode='a')
    file.write(message+'\n')
    file.close()

def get_addresses():
    global addresses
    global priority_addresses
    while True:
        print("Please enter a street level address and ZIP (i.e. 123 Main St 45429). Leave blank to continue: ")
        data = input()
        if data == "":
            if len(addresses) == 0 and len(priority_addresses) == 0:
                load_address_file()
            return
        addresses.append(data)
        print("Is this a priority address? (y or n): ")
        answer = input()
        if answer == "y":
            priority_addresses.append(data)

def load_address_file():
    global addresses
    global priority_addresses
    file = open("addresses.txt")
    addresses = []
    priority_addresses = []
    for line in file.readlines():
        a = line.strip('\n')
        if " priority" in a and do_priority is True:
            a = a.replace(' priority','')
            priority_addresses.append(a)
        if len(a) > 1:
            addresses.append(a)

if __name__ == "__main__":
    addresses = []
    priority_addresses = []
    get_addresses()
    log("all stops:",True)
    log(json.dumps(addresses))
    log("----------------------------------------------------------------------------------------------")
    log("priority stops:")
    log(json.dumps(priority_addresses))
    #["4223 Schrubb Drive 45429", "774 Ardella Ave 44306", "1016 Pool Ave 45377", "2379 Bushwick 45439"]
    matrix = get_distance_matrix(addresses)
    log("----------------------------------------------------------------------------------------------")
    log("distance matrix:")
    log(json.dumps(matrix))
    log("----------------------------------------------------------------------------------------------")
    log("starting point:")
    i = 0
    route = []
    used = []
    stop = matrix[0]
    done = False
    miles_driven = 0
    while done is False:
        is_last_stop = True
        for a in range(len(stop["distances"])):
            if stop["distances"][a]["address"] not in used:
                is_last_stop = False
                break
        if is_last_stop is True:
            route.append(stop)
            log("last stop:")
            log(stop["address"])
            distance_to_home = get_distance(stop["address"], matrix[0]["address"])
            log("distance to home: "+str(distance_to_home))
            miles_driven = miles_driven + distance_to_home
            log("total drive miles: "+str(miles_driven))
            log("----------------------------------------------------------------------------------------------")
            route.append(matrix[0])
            done = True
        else:
            next_stop = None
            route.append(stop)
            used.append(stop["address"])
            log(stop["address"])

            priority_stops = []
            non_priority_stops = []
            for x in range(len(stop["distances"])):
                tstop = stop["distances"][x]
                if tstop["address"] in priority_addresses:
                    priority_stops.append(tstop)
                else:
                    non_priority_stops.append(tstop)
            
            for x in range(len(priority_stops)):
                potential_stop = priority_stops[x]
                log("    potential stop: "+potential_stop["address"] +" @ " + str(potential_stop["distance"]) + " miles")
                if (next_stop is None or potential_stop["distance"] < next_stop["distance"]) and potential_stop["address"] not in used:
                    next_stop = potential_stop
            if next_stop is None:
                for x in range(len(non_priority_stops)):
                    potential_stop = non_priority_stops[x]
                    log("    potential stop: "+potential_stop["address"] +" @ " + str(potential_stop["distance"]) + " miles")
                    if (next_stop is None or potential_stop["distance"] < next_stop["distance"]) and potential_stop["address"] not in used:
                        next_stop = potential_stop

            log("next stop: "+next_stop["address"])
            log("distance to next stop: "+str(next_stop["distance"]))
            miles_driven = miles_driven + next_stop["distance"]
            log("----------------------------------------------------------------------------------------------")
            for y in range(len(matrix)):
                if matrix[y]["address"] == next_stop["address"]:
                    stop = matrix[y]
    # print(json.dumps(route))
    maps_url = "https://www.google.com/maps/dir/"
    for stop in route:
        coords = lookup(stop["address"])
        maps_url = maps_url + coords+"/"
    log("Map URL: "+maps_url)
    print("Map URL: "+maps_url)
        