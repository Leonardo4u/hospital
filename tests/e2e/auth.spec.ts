import { expect, test } from "@playwright/test";

test.describe("auth", () => {
  test("test_login_valido_redireciona_para_triagem", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/e-mail/i).fill("admin@triagem.local");
    await page.getByLabel(/senha/i).fill("Admin@2024");
    await page.getByRole("button", { name: /entrar/i }).click();
    await expect(page).toHaveURL(/\/triagem$/);
  });

  test("test_login_invalido_exibe_mensagem_de_erro", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/e-mail/i).fill("admin@triagem.local");
    await page.getByLabel(/senha/i).fill("senha-invalida");
    await page.getByRole("button", { name: /entrar/i }).click();
    await expect(page.getByText(/credenciais/i)).toBeVisible();
  });

  test("test_campo_email_invalido_exibe_erro_inline", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/e-mail/i).fill("email-invalido");
    await page.getByLabel(/senha/i).fill("Senha@123");
    await page.getByRole("button", { name: /entrar/i }).click();
    await expect(page.getByText(/e-mail válido|e-mail valido/i)).toBeVisible();
  });

  test("test_logout_redireciona_para_login", async ({ page }) => {
    await page.goto("/triagem");
    await page.evaluate(() => {
      window.localStorage.removeItem("access_token");
      window.localStorage.removeItem("refresh_token");
      window.localStorage.removeItem("profissional");
    });
    await page.goto("/triagem");
    await expect(page).toHaveURL(/\/login$/);
  });

  test("test_rota_protegida_sem_login_redireciona_para_login", async ({ page }) => {
    await page.context().clearCookies();
    await page.evaluate(() => window.localStorage.clear());
    await page.goto("/triagem");
    await expect(page).toHaveURL(/\/login$/);
  });

  test("test_refresh_automatico_mantem_sessao_ativa", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/e-mail/i).fill("admin@triagem.local");
    await page.getByLabel(/senha/i).fill("Admin@2024");
    await page.getByRole("button", { name: /entrar/i }).click();
    await page.evaluate(() => {
      window.localStorage.setItem("access_token", "access-token-expirado");
    });
    await page.reload();
    await expect(page).toHaveURL(/\/triagem$/);
  });
});
