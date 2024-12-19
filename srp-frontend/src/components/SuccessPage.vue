<template>
  <div class="container mt-5 text-center">
    <h1>Welcome to the Success Page!</h1>
    <p class="text-success">You have successfully logged in.</p>
    <button @click="logout" class="btn btn-danger mt-3">Logout</button>
  </div>
</template>

<script>
export default {
  methods: {
    logout() {
      this.$router.push("/");
    },
  },
};
</script>

<style>
.container {
  max-width: 700px;
}
.card {
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
</style>
