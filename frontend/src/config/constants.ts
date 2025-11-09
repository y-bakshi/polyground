export const DEMO_USER_ID = '1'
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'
const rawMockFlag = import.meta.env.VITE_USE_MOCK as string | undefined
export const USE_MOCK_DATA = rawMockFlag === undefined ? false : rawMockFlag.toLowerCase() === 'true'
