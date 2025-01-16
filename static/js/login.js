document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorContainer = document.getElementById('errorContainer');

    // Validaciones en tiempo real
    usernameInput.addEventListener('input', function() {
        if (this.value.length < 3) {
            this.classList.add('is-invalid');
            showError(this, 'El nombre de usuario debe tener al menos 3 caracteres');
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
            hideError(this);
        }
    });

    passwordInput.addEventListener('input', function() {
        if (this.value.length < 6) {
            this.classList.add('is-invalid');
            showError(this, 'La contraseña debe tener al menos 6 caracteres');
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
            hideError(this);
        }
    });

    // Función para mostrar errores
    function showError(element, message) {
        const feedback = element.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            const div = document.createElement('div');
            div.className = 'invalid-feedback';
            div.textContent = message;
            element.parentNode.insertBefore(div, element.nextSibling);
        }
    }

    // Función para ocultar errores
    function hideError(element) {
        const feedback = element.nextElementSibling; 
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.remove();
        }
    }

    // Manejo del envío del formulario
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        const formData = {
            username: usernameInput.value,
            password: passwordInput.value
        };

        // Llamada AJAX al backend
        fetch('/login', {
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
        
        if (passwordInput.value.length < 6) {
            showError(passwordInput, 'La contraseña debe tener al menos 6 caracteres');
            isValid = false;
        }

        return isValid;
    }

    // Función para mostrar alertas
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