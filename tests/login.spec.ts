import { test, expect } from '@playwright/test';

test.describe('broker portal login', () => {
  test('logs in and reaches the dashboard', async ({ page }) => {
    await page.goto('/');
    await page.fill('#username', 'advisor.jane');
    await page.fill('#password', 'demo-password');
    await page.click('#login-btn');

    await expect(page).toHaveURL(/dashboard\.html/);
    await expect(page.locator('#welcome-heading')).toContainText('advisor.jane');
  });

  test('shows an error on empty credentials', async ({ page }) => {
    await page.goto('/');
    await page.click('#login-btn');
    await expect(page.locator('#login-error')).toBeVisible();
  });
});
