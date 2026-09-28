import AnalyticsConsent from './analytics-consent';
import './analytics-consent.css';

export const metadata = {title: 'KINQ'};
export const viewport = {themeColor: '#b2ff1a'};
export const dynamic = 'force-dynamic';

export default async function RootLayout({children}) {
  let siteId = '';
  try {
    const api = process.env.KINQ_API_URL || 'http://127.0.0.1:8000';
    const response = await fetch(`${api}/api/public/settings/analytics`, {cache: 'no-store'});
    if (response.ok) siteId = (await response.json()).site_id || '';
  } catch { /* Keep the site available if analytics settings cannot be read. */ }
  return <html lang="fr"><body>{children}<AnalyticsConsent siteId={siteId}/></body></html>;
}
