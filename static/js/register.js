document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const errorContainer = document.getElementById('errorContainer');

    // Validación de nombre de usuario
    usernameInput.addEventListener('input', function() {
        if (this.value.length < 3) {
            this.classList.add('is-invalid');
            showError(this, 'El nombre de usuario debe tener al menos 3 caracteres');
        } else {
            // Verificar si el usuario ya existe
            checkUsername(this.value);
        }
    });

    // Validación de contraseña
    passwordInput.addEventListener('input', function() {
        validatePassword(this.value);
    });

    // Validación de confirmación de contraseña
    confirmPasswordInput.addEventListener('input', function() {
        if (this.value !== passwordInput.value) {
            this.classList.add('is-invalid');
            showError(this, 'Las contraseñas no coinciden');
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
            hideError(this);
        }
    });

    // Función para validar la fortaleza de la contraseña
    function validatePassword(password) {
        const minLength = 6;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        
        let message = [];
        
        if (password.length < minLength) {
            message.push('Mínimo 6 caracteres');
        }
        if (!hasUpperCase) {
            message.push('Una mayúscula');
        }
        if (!hasLowerCase) {
            message.push('Una minúscula');
        }
        if (!hasNumbers) {
            message.push('Un número');
        }

        if (message.length > 0) {
            passwordInput.classList.add('is-invalid');
            showError(passwordInput, 'La contraseña debe tener: ' + message.join(', '));
            return false;
        } else {
            passwordInput.classList.remove('is-invalid');
            passwordInput.classList.add('is-valid');
            hideError(passwordInput);
            return true;
        }
    }

    // Verificar disponibilidad del nombre de usuario
    function checkUsername(username) {
        fetch(`/check-username?username=${username}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.available) {
                usernameInput.classList.remove('is-invalid');
                usernameInput.classList.add('is-valid');
                hideError(usernameInput);
            } else {
                usernameInput.classList.add('is-invalid');
                showError(usernameInput, 'Este nombre de usuario ya está en uso');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Manejo del envío del formulario
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        const formData = {
            username: usernameInput.value,
            password: passwordInput.value,
            confirm_password: confirmPasswordInput.value
        };

        // Llamada AJAX al backend
        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                showAlert(data.message, 'danger');
            }
        })
        .catch(error => {
            showAlert('Error en el servidor. Por favor, intenta más tarde.', 'danger');
        });
    });

    // Validación del formulario completo
    function validateForm() {
        let isValid = true;
        
        if (usernameInput.value.length < 3) {
            showError(usernameInput, 'El nombre de usuario debe tener al menos 3 caracteres');
            isValid = false;
        }
        
        if (!validatePassword(passwordInput.value)) {
            isValid = false;
        }
        
        if (confirmPasswordInput.value !== passwordInput.value) {
            showError(confirmPasswordInput, 'Las contraseñas no coinciden');
            isValid = false;
        }

        return isValid;
    }

    // Funciones auxiliares
    function showError(element, message) {
        const feedback = element.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            const div = document.createElement('div');
            div.className = 'invalid-feedback';
            div.textContent = message;
            element.parentNode.insertBefore(div, element.nextSibling);
        }
    }

    function hideError(element) {
        const feedback = element.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.remove();
        }
    }

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        errorContainer.innerHTML = '';
        errorContainer.appendChild(alertDiv);
    }
});