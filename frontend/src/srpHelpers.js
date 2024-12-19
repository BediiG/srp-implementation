// Generate a random salt
export function generateSalt() {
  return Math.floor(Math.random() * 1e9).toString(); // Generate random salt as a string
}

export function hash(input) {
  // Convert input string to Uint8Array and hash it
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  return crypto.subtle.digest("SHA-256", data).then((hashBuffer) => {
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // Convert buffer to byte array
    return hashArray.map((byte) => byte.toString(16).padStart(2, "0")).join(""); // Convert bytes to hex string
  });
}

// Calculate verifier (v = g^x % N)
export async function calculateVerifier(password, salt) {
  const N = BigInt(23); // Small prime number for demonstration
  const g = BigInt(5);  // Generator value
  const hashInput = `${salt}:${password}`; // Concatenate salt and password

  try {
    // Step 1: Hash salt and password together
    const xHex = await hash(hashInput);
    const x = BigInt(`0x${xHex}`); // Convert hash to BigInt

    // Step 2: Calculate verifier using modular exponentiation
    const verifier = modExp(g, x, N);
    return verifier.toString(); // Return verifier as string for transmission
  } catch (error) {
    console.error("Error calculating verifier:", error);
    throw new Error("Verifier calculation failed");
  }
}

// Modular exponentiation (g^x % N)
export function modExp(base, exp, mod) {
  base = BigInt(base);
  exp = BigInt(exp);
  mod = BigInt(mod);
  let result = BigInt(1); // Initialize result
  while (exp > 0) {
    if (exp % BigInt(2) === BigInt(1)) {
      result = (result * base) % mod; // Multiply when exp is odd
    }
    base = (base * base) % mod; // Square base
    exp = exp / BigInt(2); // Divide exp by 2
  }
  return result;
}
