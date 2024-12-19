<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header text-center">
            <h2 v-if="isSignup">Sign Up</h2>
            <h2 v-else>Login</h2>
          </div>
          <div class="card-body">
            <form @submit.prevent="isSignup ? signup() : login()">
              <div class="mb-3">
                <label for="username" class="form-label">Username:</label>
                <input
                  v-model="username"
                  id="username"
                  type="text"
                  class="form-control"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password:</label>
                <input
                  v-model="password"
                  id="password"
                  type="password"
                  class="form-control"
                  required
                />
              </div>
              <div class="text-center">
                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                  {{ isSignup ? "Sign Up" : "Login" }}
                </button>
              </div>
            </form>
            <p v-if="error" class="text-danger text-center mt-3">{{ error }}</p>
            <p v-if="loading" class="text-center text-primary">Processing...</p>
          </div>
          <!-- Logs Section -->
          <div class="logs mt-3">
            <h5 class="text-center">Logs</h5>
            <ul class="list-group">
              <li v-for="log in logs" :key="log.id" class="list-group-item">
                <strong>{{ log.label }}:</strong> {{ log.message }}
              </li>
            </ul>
          </div>
          <div class="card-footer text-center">
            <p>
              <span v-if="isSignup">Already have an account?</span>
              <span v-else>Don't have an account?</span>
              <button @click="toggleSignup" class="btn btn-link text-decoration-none">
                {{ isSignup ? "Login" : "Sign Up" }}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { generateSalt, calculateVerifier, modExp, hash } from "../srpHelpers";

const N = BigInt(23); // Small prime for demonstration
const g = BigInt(5);

export default {
  data() {
    return {
      username: "",
      password: "",
      isSignup: false,
      error: "",
      loading: false,
      logs: [], // Store logs with labels
    };
  },
  methods: {
    logMessage(label, message) {
      this.logs.push({ id: Date.now(), label, message }); // Add labeled logs with unique IDs
    },
    toggleSignup() {
      this.isSignup = !this.isSignup;
      this.error = "";
      this.logs = []; // Clear logs when switching modes
    },
    async signup() {
      try {
        if (!this.username || !this.password) {
          this.error = "Both username and password are required.";
          return;
        }

        const salt = generateSalt();
        const verifier = await calculateVerifier(this.password, salt);

        // Log computed values
        this.logMessage("Generated Salt", salt);
        this.logMessage("Computed Verifier", verifier);

        await axios.post("http://127.0.0.1:5000/register", {
          username: this.username,
          salt,
          verifier,
        });

        this.logMessage("Status", "Registration successful");
        alert("Registration successful. Please log in.");
        this.toggleSignup();
      } catch (error) {
        this.error = error.response?.data?.message || "Signup failed.";
        this.logMessage("Error during signup", this.error);
      }
    },
    async login() {
      if (!this.username || !this.password) {
        this.error = "Both username and password are required.";
        return;
      }

      this.loading = true;
      this.logs = []; // Clear logs before new login attempt

      try {
        this.logMessage("Status", "Initiating login...");
        const { data } = await axios.post("http://127.0.0.1:5000/login/initiate", {
          username: this.username,
        });

        const { salt, B } = data;
        this.logMessage("Received Salt", salt);
        this.logMessage("Received B", B);

        const a = BigInt(Math.floor(Math.random() * 1e9));
        const A = modExp(g, a, N);

        this.logMessage("Computed A", A);
        this.logMessage("Generated Private Value a", a);

        const u = BigInt(`0x${await hash(`${A}:${B}`)}`) % N;
        const x = BigInt(`0x${await hash(`${salt}:${this.password}`)}`);
        const S_client = modExp(BigInt(B), a + u * x, N);
        const K_client = await hash(`${S_client}`);

        this.logMessage("Scrambling Parameter u", u);
        this.logMessage("Computed x", x);
        this.logMessage("Shared Secret S_client", S_client);
        this.logMessage("Session Key K_client", K_client);

        const verifyResponse = await axios.post("http://127.0.0.1:5000/login/verify", {
          username: this.username,
          A: A.toString(),
        });

        this.logMessage("Server Response", JSON.stringify(verifyResponse.data));

        if (verifyResponse.data.K_server === K_client) {
          alert("Login successful");
        } else {
          throw new Error("Verification failed");
        }
      } catch (error) {
        this.error = error.response?.data?.message || "Login failed.";
        this.logMessage("Error during login", this.error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style>
.container {
  max-width: 500px;
}
.card {
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
.logs {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 8px;
}
.logs ul {
  max-height: 200px;
  overflow-y: auto;
}
.logs li {
  font-family: "Courier New", Courier, monospace;
  margin: 5px 0;
}
.btn-link {
  color: #007bff;
}
</style>
