import { expect, test } from "@playwright/test";

test.describe("triagem", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/e-mail/i).fill("admin@triagem.local");
    await page.getByLabel(/senha/i).fill("Admin@2024");
    await page.getByRole("button", { name: /entrar/i }).click();
  });

  test("test_fluxo_completo_triagem_vermelho", async ({ page }) => {
    await page.getByLabel(/buscar paciente/i).fill("Mariana");
    await page.getByRole("option").first().click();
    await page.getByRole("button", { name: /avancar/i }).click();
    await page.getByLabel(/Frequencia cardiaca/i).fill("160");
    await page.getByLabel(/Pressao sistolica/i).fill("75");
    await page.getByLabel(/Pressao diastolica/i).fill("50");
    await page.getByLabel(/Saturacao O2/i).fill("84");
    await page.getByLabel(/Temperatura/i).fill("36.5");
    await page.getByLabel(/Frequencia respiratoria/i).fill("28");
    await page.getByLabel(/Escala de Glasgow/i).fill("6");
    await page.getByRole("button", { name: /avancar/i }).click();
    await page.getByRole("textbox").fill("Choque com dispneia");
    await page.getByRole("button", { name: /classificar/i }).click();
    await expect(page.getByText(/VERMELHO/i)).toBeVisible();
    await page.getByRole("button", { name: /VERMELHO/i }).click();
    await expect(page.getByText(/Confirmado/i)).toBeVisible();
  });

  test("test_fluxo_completo_triagem_azul", async ({ page }) => {
    await page.getByLabel(/buscar paciente/i).fill("Carlos");
    await page.getByRole("option").first().click();
    await page.getByRole("button", { name: /avancar/i }).click();
    await page.getByLabel(/Frequencia cardiaca/i).fill("68");
    await page.getByLabel(/Pressao sistolica/i).fill("118");
    await page.getByLabel(/Pressao diastolica/i).fill("76");
    await page.getByLabel(/Saturacao O2/i).fill("99");
    await page.getByLabel(/Temperatura/i).fill("36.2");
    await page.getByLabel(/Frequencia respiratoria/i).fill("14");
    await page.getByLabel(/Escala de Glasgow/i).fill("15");
    await page.getByRole("button", { name: /avancar/i }).click();
    await page.getByRole("textbox").fill("Rotina");
    await page.getByRole("button", { name: /classificar/i }).click();
    await expect(page.getByText(/AZUL/i)).toBeVisible();
    await page.getByRole("button", { name: /AZUL/i }).click();
    await expect(page.getByText(/Confirmado/i)).toBeVisible();
  });

  test("test_validacao_impede_avanco_com_glasgow_invalido", async ({ page }) => {
    await page.getByLabel(/buscar paciente/i).fill("Mariana");
    await page.getByRole("option").first().click();
    await page.getByRole("button", { name: /avancar/i }).click();
    await page.getByLabel(/Escala de Glasgow/i).fill("20");
    await expect(page.getByRole("button", { name: /avancar/i })).toBeDisabled();
  });

  test("test_correcao_de_nivel_pelo_profissional", async ({ page }) => {
    await page.getByLabel(/buscar paciente/i).fill("Carlos");
    await page.getByRole("option").first().click();
    await page.getByRole("button", { name: /avancar/i }).click();
    await page.getByLabel(/Frequencia cardiaca/i).fill("70");
    await page.getByLabel(/Pressao sistolica/i).fill("118");
    await page.getByLabel(/Pressao diastolica/i).fill("76");
    await page.getByLabel(/Saturacao O2/i).fill("99");
    await page.getByLabel(/Temperatura/i).fill("36.2");
    await page.getByLabel(/Frequencia respiratoria/i).fill("14");
    await page.getByLabel(/Escala de Glasgow/i).fill("15");
    await page.getByRole("button", { name: /avancar/i }).click();
    await page.getByRole("textbox").fill("Dor leve");
    await page.getByRole("button", { name: /classificar/i }).click();
    await page.getByRole("button", { name: /AMARELO/i }).click();
    await expect(page.getByText(/Corrigido pelo profissional/i)).toBeVisible();
  });

  test("test_historico_atualiza_apos_nova_triagem", async ({ page }) => {
    await page.getByRole("button", { name: /ver historico/i }).click();
    await expect(page.getByText(/Historico/i)).toBeVisible();
  });
});
