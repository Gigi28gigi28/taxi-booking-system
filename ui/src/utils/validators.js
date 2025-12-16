export const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

/**
 * Validate password
 */
export const isValidPassword = (password) => {
    // At least 8 characters
    return password && password.length >= 8;
};

/**
 * Validate phone number
 */
export const isValidPhone = (phone) => {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    const cleaned = phone.replace(/\D/g, '');
    return phoneRegex.test(phone) && cleaned.length >= 10;
};

/**
 * Validate address
 */
export const isValidAddress = (address) => {
    return address && address.trim().length >= 5;
};

/**
 * Validate required field
 */
export const isRequired = (value) => {
    return value !== null && value !== undefined && value.toString().trim() !== '';
};

/**
 * Validate form data
 */
export const validateForm = (data, rules) => {
    const errors = {};

    Object.keys(rules).forEach(field => {
        const rule = rules[field];
        const value = data[field];

        if (rule.required && !isRequired(value)) {
            errors[field] = `${field} is required`;
        } else if (rule.email && value && !isValidEmail(value)) {
            errors[field] = 'Invalid email format';
        } else if (rule.password && value && !isValidPassword(value)) {
            errors[field] = 'Password must be at least 8 characters';
        } else if (rule.phone && value && !isValidPhone(value)) {
            errors[field] = 'Invalid phone number';
        } else if (rule.minLength && value && value.length < rule.minLength) {
            errors[field] = `Minimum ${rule.minLength} characters required`;
        } else if (rule.maxLength && value && value.length > rule.maxLength) {
            errors[field] = `Maximum ${rule.maxLength} characters allowed`;
        } else if (rule.match && value !== data[rule.match]) {
            errors[field] = `Does not match ${rule.match}`;
        }
    });

    return {
        isValid: Object.keys(errors).length === 0,
        errors
    };
};

