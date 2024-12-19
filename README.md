# Secure Remote Password (SRP) Authentication Demo

This project demonstrates an implementation of the Secure Remote Password (SRP) protocol using a Vue.js frontend and a Flask backend. The SRP protocol is a cryptographic method for securely authenticating users without transmitting their passwords.

## Table of Contents
- [Technologies Used](#technologies-used)
- [SRP Protocol Explanation](#srp-protocol-explanation)
- [Function Responsibilities](#function-responsibilities)
- [Installation Guide](#installation-guide)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)

---

## Technologies Used

### Frontend:
- **Vue.js**: Framework for building the user interface.
- **Axios**: HTTP client for communication with the backend.
- **Bootstrap**: CSS framework for responsive styling.

### Backend:
- **Flask**: Python web framework for serving APIs.
- **SQLAlchemy**: ORM for database management (SQLite).
- **Flask-CORS**: For handling cross-origin requests.

### Cryptographic Functions:
- **SHA-256 Hashing**: For secure hash computations.
- **Modular Exponentiation**: Used to compute values securely within the protocol.

---

## SRP Protocol Explanation

The Secure Remote Password (SRP) protocol allows secure authentication without exposing the password to the server. Below are the key steps:

1. **Registration:**
   - The client generates a `salt` and computes a `verifier` based on the user's password.
   - These values are sent to the server for storage.

2. **Authentication:**
   - **Step 1: Client Initialization**
     - The client generates a private ephemeral value `a` and computes the public value `A`.
     - The server generates its private ephemeral value `b` and computes the public value `B`.
     - The server sends `salt` and `B` to the client.
   - **Step 2: Shared Secret Computation**
     - Both the client and server compute a shared secret `S` using their respective values and the agreed protocol.
   - **Step 3: Session Key Verification**
     - Both compute a session key `K` derived from the shared secret `S`.
     - The client and server verify their session keys to ensure correctness.

---

## Function Responsibilities

### Frontend:
1. **generateSalt:**
   - Generates a random salt for secure password storage.

2. **calculateVerifier:**
   - Computes the verifier `v = g^x % N` using the password and salt.

3. **hash:**
   - Performs SHA-256 hashing of inputs.

4. **modExp:**
   - Computes modular exponentiation for SRP computations.

5. **signup:**
   - Handles user registration by sending `username`, `salt`, and `verifier` to the backend.

6. **login:**
   - Handles the login process by performing the SRP protocol steps, including:
     - Sending the public value `A`.
     - Computing the shared secret `S` and session key `K`.
     - Verifying the server response.

### Backend:
1. **register:**
   - Stores `username`, `salt`, and `verifier` in the database during registration.

2. **login_initiate:**
   - Generates server-side ephemeral values `b` and `B`, sends `salt` and `B` to the client.

3. **login_verify:**
   - Computes the server-side shared secret `S` and session key `K`.
   - Verifies the session key against the client.

4. **Ephemeral Storage:**
   - Temporary storage for server-side ephemeral values `b` during authentication.

---

## Installation Guide

### Prerequisites:
- **Node.js**: Required for running the Vue.js frontend.
- **Python 3.9+**: Required for running the Flask backend.

### Clone the Repository:
```bash
git clone <repository-url>
cd <repository-name>
```

### Backend Setup:
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask app:
   ```bash
   python app.py
   ```

### Frontend Setup:
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Vue.js app:
   ```bash
   npm run dev
   ```

---

## Running the Project
1. Start the backend server.
2. Start the frontend server.
3. Open the browser at `http://localhost:5173` to view the application.

---

## Project Structure
```
root
├── backend
│   ├── app.py           # Flask app with SRP implementation
│   ├── requirements.txt # Backend dependencies
│   └── auth.db          # SQLite database
├── frontend
│   ├── src
│   │   ├── App.vue      # Main Vue component
│   │   ├── components
│   │   │   └── Login.vue # Login/Signup Component
│   │   └── srpHelpers.js # Helper functions for SRP
│   ├── package.json     # Frontend dependencies
│   └── public
│       └── index.html   # Main HTML file
└── README.md            # Project documentation
```

---

## Notes
- **Demo Values:** Small prime `N` and generator `g` are used for simplicity; in production, these should be replaced with large, secure values.
- **Logs:** Computation logs are displayed in the frontend for debugging and demonstration purposes.