import requests

API_URL = "http://localhost:8000/appointments"
JWT_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtJX3VfdkJ0RmdRZHNFdEhiSDFOZCJ9.eyJpc3MiOiJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMjgzNjk0NzY0NDMxNzUwMDA1NSIsImF1ZCI6WyJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS9hcGkvdjIvIiwiaHR0cHM6Ly9kZXYteDdqeDBiZDRrNXZuMmp1ci51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzQzOTIyNzgyLCJleHAiOjE3NDM5Mjk5ODIsInNjb3BlIjoib3BlbmlkIGVtYWlsIiwiYXpwIjoiZ2VMSU5BZ3phRlVCV24xSmU2VDBMdkUzaDZNaXE0TTYifQ.fIlXQiPwF_pdXRsu4nVcesywF16M99bYdstk3WY6dYLnNQ6_yviSzmsLEJs2LaStH_MJep6NmHxtWrniSACP66-4McM3sZa3nOTsEHqTagoJ9_IPrllj9fjNzEAMcmeOOCxizgImI30OHz0c7pgXKE0AgQYmwD7b4Pk78tK4KhASZVvvYiQ6bdcXVv2u9YAO2264dq6vV6SqQm9Eoso87jj_vI6WK2a7Zt-MHHoDuVlTVqB2sLbvZOgMi_VBvu9h4UYacn-fHHwHc5j59NAZBb5cqAouv9zb3wjiSeMlmiEEhR81ZLVQixVLu4Xs1l7iovXtsE6DLu1UHJ3sTBsxoQ"
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
