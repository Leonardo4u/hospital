export function validarEmail(email: string): string | null {
  const valor = email.trim();
  if (valor.length === 0) {
    return "Informe o e-mail.";
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(valor)) {
    return "Informe um e-mail válido.";
  }

  return null;
}

export function validarSenha(senha: string): string | null {
  if (senha.trim().length === 0) {
    return "Informe a senha.";
  }

  if (senha.length < 8) {
    return "A senha deve ter no mínimo 8 caracteres.";
  }

  return null;
}

export function validarCRM(crm: string): string | null {
  const valor = crm.trim();
  if (valor.length === 0) {
    return null;
  }

  const crmRegex = /^CRM\/[A-Z]{2}\s\d{4,10}$/;
  if (!crmRegex.test(valor)) {
    return "Use o formato CRM/UF 123456.";
  }

  return null;
}
