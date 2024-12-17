import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    id: null,
    username: null,
    token: null,
    isAuthenticated: false,
    otpVerified: false,
    isAdmin: false
  }),

  actions: {
    setUser(userData) {
      console.log('Setting user data:', userData);
      
      this.id = userData.id;
      this.username = userData.username;
      this.token = userData.token;
      this.isAuthenticated = true;
      
      this.$patch({ isAdmin: userData.username === 'danil' });
      
      localStorage.setItem('token', userData.token);
      localStorage.setItem('username', userData.username);
      localStorage.setItem('userId', userData.id);
      localStorage.setItem('isAdmin', String(userData.username === 'danil'));
    },

    clearUser() {
      this.$patch({
        id: null,
        username: null,
        token: null,
        isAuthenticated: false,
        otpVerified: false,
        isAdmin: false
      });
      
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('userId');
      localStorage.removeItem('isAdmin');
    },

    setOTPVerified(status) {
      this.otpVerified = status;
    },

    initializeFromStorage() {
      const token = localStorage.getItem('token');
      const username = localStorage.getItem('username');
      const userId = localStorage.getItem('userId');
      const isAdmin = localStorage.getItem('isAdmin') === 'true';

      if (token && username && userId) {
        this.$patch({
          id: userId,
          username: username,
          token: token,
          isAuthenticated: true,
          isAdmin: isAdmin
        });
      }
    }
  },

  getters: {
    isLoggedIn: (state) => state.isAuthenticated,
    currentUser: (state) => ({
      id: state.id,
      username: state.username
    }),
    getToken: (state) => {
      console.log('Getting token:', state.token);
      return state.token;
    },
    isOTPVerified: (state) => state.otpVerified
  }
}); 