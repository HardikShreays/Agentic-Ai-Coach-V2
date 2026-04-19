/**
 * Returns a safe in-app path for post-auth navigation. Rejects open redirects.
 */
export function safeRedirectPath(raw: string | null | undefined, fallback = '/predict'): string {
  if (!raw || typeof raw !== 'string') return fallback;
  const decoded = decodeURIComponent(raw.trim());
  if (!decoded.startsWith('/') || decoded.startsWith('//')) return fallback;
  return decoded;
}
