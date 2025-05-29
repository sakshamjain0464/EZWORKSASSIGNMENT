# EZ Works ASSIGNMENT

## 🧾 Overview

EZWorks Assignment Portal is a backend system built using **FastAPI**, designed to handle assignment uploads by "Ops" users and allow "Client" users to securely access and download their files. It includes:

- Role-based access (Client, Ops)
- JWT authentication
- File uploads (by Ops)
- File listing & secure download (by Clients)
- MongoDB integration
- Simulated and real email verification via SMTP

---

## 📁 Project Structure

sakshamjain0464-ezworksassignment/
├── readme.md # Project overview and setup instructions
├── requirements.txt # Python dependencies

└── app/
├── auth.py # Main auth logic (signup, login)
├── db.py # MongoDB database connection
├── main.py # FastAPI app entry point
├── models.py # Pydantic models for request/response

graphql
Copy
Edit
├── routes/ # API route definitions
│ ├── auth.py # Auth routes for client & ops
│ ├── upload.py # File upload route (Ops only)
│ └── files.py # File access/download (Client only)

└── utils/ # Utility functions
├── auth.py # Auth helpers (hashing, verification)
├── jwt.py # JWT token generation & decoding
├── security.py # get_current_user() dependency
└── email.py # Email sending via SMTP

## 🔗 API Endpoints

### 🔐 Authentication & Verification

| Method | Endpoint       | Access | Description                           |
| ------ | -------------- | ------ | ------------------------------------- |
| POST   | /client/signup | Public | Register a new client                 |
| POST   | /ops/signup    | Public | Register a new ops user               |
| POST   | /login         | Public | Login as client or ops, returns JWT   |
| GET    | /verify-email  | Public | Verify email using token in URL query |

---

### 📤 File Upload (Ops Only)

| Method | Endpoint     | Access | Description                           |
| ------ | ------------ | ------ | ------------------------------------- |
| POST   | /upload-file | Ops    | Upload a file (pptx, docx, xlsx, pdf) |

---

### 📁 File Access (Client Only)

| Method | Endpoint                 | Access | Description                             |
| ------ | ------------------------ | ------ | --------------------------------------- |
| GET    | /client/files            | Client | List all files uploaded for this client |
| GET    | /client/download/{token} | Client | Download file via secure tokenized URL  |

> 🛡️ All protected endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.
