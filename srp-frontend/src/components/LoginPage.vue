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
    };
  },
  methods: {
    toggleSignup() {
      this.isSignup = !this.isSignup;
      this.error = "";
    },
    async signup() {
      try {
        if (!this.username || !this.password) {
          this.error = "Both username and password are required.";
          return;
        }

        const salt = generateSalt();
        const verifier = await calculateVerifier(this.password, salt);

        console.log(`Signup -> Salt: ${salt}, Verifier: ${verifier}`);
        console.log(`Password:${this.password}`)

        await axios.post("http://127.0.0.1:5000/register", {
          username: this.username,
          salt,
          verifier,
        });

        alert("Registration successful. Please log in.");
        this.toggleSignup();
      } catch (error) {
        console.error("Error during signup:", error);
        this.error = error.response?.data?.message || "Signup failed.";
      }
    },
    async login() {
      if (!this.username || !this.password) {
        this.error = "Both username and password are required.";
        return;
      }

      this.loading = true;

      try {
        // Step 1: Initiate login
        console.log("Initiating login...");
        const { data } = await axios.post("http://127.0.0.1:5000/login/initiate", {
          username: this.username,
        });

        console.log("Received response from /login/initiate:", data);

        const { salt, B } = data;

        // Step 2: Generate private ephemeral value 'a' and public value 'A'
        const a = BigInt(Math.floor(Math.random() * 1e9));
        const A = modExp(g, a, N);

        console.log(`Computed -> A: ${A}, a: ${a}, B: ${B}`);

        // Step 3: Compute scrambling parameter 'u' and shared secret 'S_client'
        const u = BigInt(`0x${await hash(`${A}:${B}`)}`) % N; // Convert hash result to BigInt
        const x = BigInt(`0x${await hash(`${salt}:${this.password}`)}`); // Convert hash result to BigInt
        const S_client = modExp(BigInt(B), a + u * x, N);
        const K_client = await hash(`${S_client}`);
        console.log(`Password:${this.password}`);
        console.log(
          `Computed -> u: ${u}, x: ${x}, S_client: ${S_client}, K_client: ${K_client}`
        );

        // Step 4: Verify with the server
        console.log("Sending /login/verify request...");
        const verifyResponse = await axios.post("http://127.0.0.1:5000/login/verify", {
          username: this.username,
          A: A.toString(), // Serialize BigInt as string
        });

        console.log("Received response from /login/verify:", verifyResponse.data);

        if (verifyResponse.data.K_server === K_client) {
          alert("Login successful");
        } else {
          throw new Error("Verification failed");
        }
      } catch (error) {
        console.error("Error during login:", error);
        this.error = error.response?.data?.message || "Login failed.";
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
.btn-link {
  color: #007bff;
}
</style>
