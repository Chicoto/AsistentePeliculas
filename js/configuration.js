// Función para mostrar mensajes de alerta
function showAlert(message, type, formType) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Seleccionar el botón según el tipo de formulario
    const button = formType === 'password' 
        ? document.querySelector('button[name="save_password"]')
        : document.querySelector('button[name="save_preferences"]');

    // Insertar la alerta antes del div que contiene el botón
    button.parentElement.insertBefore(alertDiv, button);

    // Auto-cerrar después de 3 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 1500);
}

// Manejar el formulario de preferencias
document.querySelector('button[name="save_preferences"]').addEventListener('click', function (e) {
    e.preventDefault();

    const button = this; // El botón que disparó el evento
    button.disabled = true; // Desactivar el botón temporalmente

    const formData = new FormData();
    formData.append('save_preferences', 'true');

    // Agregar cada preferencia seleccionada al FormData
    document.querySelectorAll('input[name="preferences"]:checked').forEach(checkbox => {
        formData.append('preferences', checkbox.value);
    });

    fetch('/configuration', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta del servidor:', data); // Para debugging
            if (data.success) {
                showAlert('Preferencias actualizadas correctamente', 'success', 'preferences');
            } else {
                showAlert(data.message || 'Error al actualizar las preferencias', 'danger', 'preferences');
            }
        })
        .catch(error => {
            showAlert('Error de conexión', 'danger', 'preferences');
            console.error('Error:', error);
        })
        .finally(() => {
            button.disabled = false; // Habilitar el botón nuevamente
        });
});

// Validación de contraseña
function validatePassword(password) {
    const minLength = 6;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);

    let message = [];

    if (password.length < minLength) {
        message.push("Mínimo 6 caracteres");
    }
    if (!hasUpperCase) {
        message.push("Una mayúscula");
    }
    if (!hasLowerCase) {
        message.push("Una minúscula");
    }
    if (!hasNumbers) {
        message.push("Un número");
    }

    return message.length > 0 ? "La contraseña debe tener: " + message.join(', ') : "";
}

// Manejar el formulario de cambio de contraseña
document.querySelector('button[name="save_password"]').addEventListener('click', function (e) {
    e.preventDefault();

    const button = this; // El botón que disparó el evento
    button.disabled = true; // Desactivar el botón temporalmente

    const password = document.getElementById('password').value;
    const validationMessage = validatePassword(password);

    if (validationMessage) {
        showAlert(validationMessage, 'danger', 'password');
        button.disabled = false; // Habilitar el botón nuevamente si hay error
        return;
    }

    fetch('/configuration', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'password': password,
            'save_password': 'true',
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Contraseña actualizada correctamente', 'success', 'password');
                document.getElementById('password').value = '';
            } else {
                showAlert(data.message || 'Error al actualizar la contraseña', 'danger', 'password');
            }
        })
        .catch(error => {
            showAlert('Error de conexión', 'danger', 'password');
            console.error('Error:', error);
        })
        .finally(() => {
            button.disabled = false; // Habilitar el botón nuevamente
        });
});
