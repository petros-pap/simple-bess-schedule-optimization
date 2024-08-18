import requests

url = "http://127.0.0.1:5000/schedule"

payload = {
    "prices": {
        "production": {
            "2000-01-01T00:00:00+0100": 7,
            "2000-01-01T01:00:00+0100": 2,
            "2000-01-01T02:00:00+0100": 3,
            "2000-01-01T03:00:00+0100": 4
        },
        "consumption": {
            "2000-01-01T00:00:00+0100": 8,
            "2000-01-01T01:00:00+0100": 3,
            "2000-01-01T02:00:00+0100": 4,
            "2000-01-01T03:00:00+0100": 5
        }
    },
    "soc_start": 20,
    "soc_max": 90,
    "soc_min": 10,
    "soc_target": 40,
    "power_capacity": 10
}
headers = {
    "Content-Type": "application/json",
}

response = requests.request("GET", url, json=payload, headers=headers)

print(response.text)