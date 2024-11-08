function validateEmail() {
    const emailInput = document.getElementById('email');
    const errorMessage = document.getElementById('error-message');
    const email = emailInput.value;

    //Regular expression for basic email validation
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
      errorMessage.textContent = 'Please enter a valid email address.';
      errorMessage.style.display = 'block';
      return false; //prevent form submission
    } else {
      errorMessage.style.display = 'none'; // hide error message
      return true; //allow form submission
    }
  }