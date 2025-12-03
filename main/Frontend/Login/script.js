// ==========================================
// CRUD User Management System - Login Page
// ==========================================

// Initialize localStorage with sample users if empty
function initializeUsers() {
  if (!localStorage.getItem('users')) {
    const sampleUsers = [
      { id: 1, username: 'testuser', email: 'test@example.com', password: 'password123' }
    ];
    localStorage.setItem('users', JSON.stringify(sampleUsers));
  }
}

// Get all users
function getAllUsers() {
  return JSON.parse(localStorage.getItem('users')) || [];
}

// Get user by username
function getUserByUsername(username) {
  const users = getAllUsers();
  return users.find(u => u.username === username);
}

// Create new user (Register)
function createUser(username, email, password) {
  const users = getAllUsers();
  
  // Check if user already exists
  if (users.some(u => u.username === username)) {
    return { success: false, message: 'Username already exists!' };
  }
  
  if (users.some(u => u.email === email)) {
    return { success: false, message: 'Email already registered!' };
  }
  
  const newUser = {
    id: users.length > 0 ? Math.max(...users.map(u => u.id)) + 1 : 1,
    username,
    email,
    password
  };
  
  users.push(newUser);
  localStorage.setItem('users', JSON.stringify(users));
  return { success: true, message: 'Account created successfully!', user: newUser };
}

// Read user (Login)
function loginUser(username, password) {
  const user = getUserByUsername(username);
  
  if (!user) {
    return { success: false, message: 'Username not found!' };
  }
  
  if (user.password !== password) {
    return { success: false, message: 'Incorrect password!' };
  }
  
  // Store logged-in user
  localStorage.setItem('currentUser', JSON.stringify(user));
  return { success: true, message: 'Login successful!', user };
}

// Update user profile
function updateUser(userId, username, email) {
  const users = getAllUsers();
  const userIndex = users.findIndex(u => u.id === userId);
  
  if (userIndex === -1) {
    return { success: false, message: 'User not found!' };
  }
  
  // Check if new username already exists (excluding current user)
  if (users.some(u => u.username === username && u.id !== userId)) {
    return { success: false, message: 'Username already taken!' };
  }
  
  // Check if new email already exists (excluding current user)
  if (users.some(u => u.email === email && u.id !== userId)) {
    return { success: false, message: 'Email already in use!' };
  }
  
  users[userIndex].username = username;
  users[userIndex].email = email;
  localStorage.setItem('users', JSON.stringify(users));
  
  // Update current user if logged in
  const currentUser = JSON.parse(localStorage.getItem('currentUser'));
  if (currentUser && currentUser.id === userId) {
    localStorage.setItem('currentUser', JSON.stringify(users[userIndex]));
  }
  
  return { success: true, message: 'Profile updated!', user: users[userIndex] };
}

// Delete user account
function deleteUser(userId) {
  const users = getAllUsers();
  const newUsers = users.filter(u => u.id !== userId);
  
  if (newUsers.length === users.length) {
    return { success: false, message: 'User not found!' };
  }
  
  localStorage.setItem('users', JSON.stringify(newUsers));
  localStorage.removeItem('currentUser');
  return { success: true, message: 'Account deleted!' };
}
function loginUser(username, password) {
  const user = getUserByUsername(username);
  
  if (!user) {
    return { success: false, message: 'Username not found!' };
  }
  
  if (user.password !== password) {
    return { success: false, message: 'Incorrect password!' };
  }
  
  // Store logged-in user
  localStorage.setItem('currentUser', JSON.stringify(user));
  return { success: true, message: 'Login successful!', user };
}

// Update user profile
function updateUser(userId, username, email) {
  const users = getAllUsers();
  const userIndex = users.findIndex(u => u.id === userId);
  
  if (userIndex === -1) {
    return { success: false, message: 'User not found!' };
  }
  
  // Check if new username already exists (excluding current user)
  if (users.some(u => u.username === username && u.id !== userId)) {
    return { success: false, message: 'Username already taken!' };
  }
  
  // Check if new email already exists (excluding current user)
  if (users.some(u => u.email === email && u.id !== userId)) {
    return { success: false, message: 'Email already in use!' };
  }
  
  users[userIndex].username = username;
  users[userIndex].email = email;
  localStorage.setItem('users', JSON.stringify(users));
  
  // Update current user if logged in
  const currentUser = JSON.parse(localStorage.getItem('currentUser'));
  if (currentUser && currentUser.id === userId) {
    localStorage.setItem('currentUser', JSON.stringify(users[userIndex]));
  }
  
  return { success: true, message: 'Profile updated!', user: users[userIndex] };
}

// Delete user account
function deleteUser(userId) {
  const users = getAllUsers();
  const newUsers = users.filter(u => u.id !== userId);
  
  if (newUsers.length === users.length) {
    return { success: false, message: 'User not found!' };
  }
  
  localStorage.setItem('users', JSON.stringify(newUsers));
  localStorage.removeItem('currentUser');
  return { success: true, message: 'Account deleted!' };
}

// ==========================================
// DOM Elements
// ==========================================

const loginForm = document.getElementById('loginForm');
const registerBtn = document.getElementById('registerBtn');
const registerModal = document.getElementById('registerModal');
const registerForm = document.getElementById('registerForm');
const dashboardModal = document.getElementById('dashboardModal');
const editModal = document.getElementById('editModal');
const editForm = document.getElementById('editForm');

const loginMessage = document.getElementById('loginMessage');
const registerMessage = document.getElementById('registerMessage');
const dashboardMessage = document.getElementById('dashboardMessage');
const editMessage = document.getElementById('editMessage');

const closeButtons = document.querySelectorAll('.close');
const editBtn = document.getElementById('editBtn');
const deleteBtn = document.getElementById('deleteBtn');
const logoutBtn = document.getElementById('logoutBtn');

// ==========================================
// Modal Functions
// ==========================================

function openModal(modal) {
  modal.style.display = 'block';
}

function closeModal(modal) {
  modal.style.display = 'none';
}

// Close modal when clicking X
closeButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.target.closest('.modal').style.display = 'none';
  });
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal')) {
    e.target.style.display = 'none';
  }
});

// ==========================================
// Login Form Handler
// ==========================================

loginForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  
  if (!username || !password) {
    showMessage(loginMessage, 'Please fill in all fields!', 'error');
    return;
  }
  
  const result = loginUser(username, password);
  
  if (result.success) {
    showMessage(loginMessage, result.message, 'success');
    loginForm.style.display = 'none';
    
    setTimeout(() => {
      showDashboard(result.user);
    }, 500);
  } else {
    showMessage(loginMessage, result.message, 'error');
  }
});

// ==========================================
// Register Form Handler
// ==========================================

registerBtn.addEventListener('click', (e) => {
  e.preventDefault();
  openModal(registerModal);
});

registerForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const username = document.getElementById('regUsername').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const password = document.getElementById('regPassword').value.trim();
  const confirmPassword = document.getElementById('regConfirmPassword').value.trim();
  
  if (!username || !email || !password || !confirmPassword) {
    showMessage(registerMessage, 'Please fill in all fields!', 'error');
    return;
  }
  
  if (password !== confirmPassword) {
    showMessage(registerMessage, 'Passwords do not match!', 'error');
    return;
  }
  
  if (password.length < 6) {
    showMessage(registerMessage, 'Password must be at least 6 characters!', 'error');
    return;
  }
  
  const result = createUser(username, email, password);
  
  if (result.success) {
    showMessage(registerMessage, result.message, 'success');
    // Show popup alert
    alert('✅ Account Created Successfully!\n\nUsername: ' + username + '\n\nYou can now login.');
    setTimeout(() => {
      closeModal(registerModal);
      registerForm.reset();
      document.getElementById('regUsername').focus();
    }, 500);
  } else {
    showMessage(registerMessage, result.message, 'error');
  }
});

// ==========================================
// Dashboard Functions
// ==========================================

function showDashboard(user) {
  document.getElementById('dashUsername').textContent = user.username;
  document.getElementById('dashEmail').textContent = user.email;
  openModal(dashboardModal);
}

editBtn.addEventListener('click', () => {
  const currentUser = JSON.parse(localStorage.getItem('currentUser'));
  document.getElementById('editUsername').value = currentUser.username;
  document.getElementById('editEmail').value = currentUser.email;
  closeModal(dashboardModal);
  openModal(editModal);
});

editForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const currentUser = JSON.parse(localStorage.getItem('currentUser'));
  const newUsername = document.getElementById('editUsername').value.trim();
  const newEmail = document.getElementById('editEmail').value.trim();
  
  if (!newUsername || !newEmail) {
    showMessage(editMessage, 'Please fill in all fields!', 'error');
    return;
  }
  
  const result = updateUser(currentUser.id, newUsername, newEmail);
  
  if (result.success) {
    showMessage(editMessage, result.message, 'success');
    setTimeout(() => {
      closeModal(editModal);
      showDashboard(result.user);
    }, 500);
  } else {
    showMessage(editMessage, result.message, 'error');
  }
});

deleteBtn.addEventListener('click', () => {
  if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    const result = deleteUser(currentUser.id);
    
    if (result.success) {
      showMessage(dashboardMessage, result.message, 'success');
      setTimeout(() => {
        closeModal(dashboardModal);
        logout();
      }, 500);
    } else {
      showMessage(dashboardMessage, result.message, 'error');
    }
  }
});

logoutBtn.addEventListener('click', () => {
  logout();
});

function logout() {
  localStorage.removeItem('currentUser');
  document.getElementById('username').value = '';
  document.getElementById('password').value = '';
  loginForm.style.display = 'block';
  closeModal(dashboardModal);
  closeModal(editModal);
  showMessage(loginMessage, 'Logged out successfully!', 'success');
  setTimeout(() => {
    loginMessage.textContent = '';
    loginMessage.className = 'message';
  }, 2000);
}

// ==========================================
// Utility Functions
// ==========================================

function showMessage(element, message, type) {
  element.textContent = message;
  element.className = `message ${type}`;
}

// Check if user is already logged in
function checkLoggedInUser() {
  const currentUser = localStorage.getItem('currentUser');
  if (currentUser) {
    const user = JSON.parse(currentUser);
    loginForm.style.display = 'none';
    showDashboard(user);
  }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
  initializeUsers();
  checkLoggedInUser();
});
