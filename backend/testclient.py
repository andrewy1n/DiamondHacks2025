import requests

API_URL = "https://1c26-128-54-18-77.ngrok-free.app/appointments"
JWT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtJX3VfdkJ0RmdRZHNFdEhiSDFOZCJ9.eyJpc3MiOiJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMjgzNjk0NzY0NDMxNzUwMDA1NSIsImF1ZCI6WyJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS9hcGkvdjIvIiwiaHR0cHM6Ly9kZXYteDdqeDBiZDRrNXZuMmp1ci51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzQzOTQ3ODA4LCJleHAiOjE3NDM5NTUwMDgsInNjb3BlIjoib3BlbmlkIGVtYWlsIiwiYXpwIjoiZ2VMSU5BZ3phRlVCV24xSmU2VDBMdkUzaDZNaXE0TTYifQ.vtb8Kw2AjfXMbFqh3vSEmQMuTjX1-E82lIDprZyPIIHXpT34hSLZu-_U44bqz57z3SaVE2VV07al6-EAjWCL0WFHqynYZHZ2YxDjMUsJZ3bMCBhM2yuc1VRB2TLSIRS1tJKQ7bOogBW-pQ6XdGj2nbIxc6BnUZVxlyigvxYA8WhAd7ErP-PoTyeWbQsh-Iowq4nCEbIBDz-DxMbzFnd4HTSkRQrL1ejdPLp2C22MH6X7byTTrb4hdMSEObRShflgEpKBMW8jRzA49LSAgRLzXXccrkT_P4vAjIZd9CLh1QV5PL9cnfopFSIx0RY0dIwH9JqgTDJM4OLgbdJDRyU-LA"
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}"
}

data = {
  "date": "2025-06-30T20:55:05.926275+00:00",
  "name": "Default Test",
  "note_id": "",
  "transcript_id": ""
}

response = requests.get(API_URL, headers=headers)

if response.status_code == 200:
    print("✅ User Info:")
    print(response.json())
else:
    print(f"❌ Error {response.status_code}: {response.text}")
